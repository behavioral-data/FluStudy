import click
import wandb
import os

import pytorch_lightning as pl
from pytorch_lightning.loggers.wandb import WandbLogger

from petastorm import make_reader
from petastorm.pytorch import DataLoader as PetastormDataLoader

from src.models.models import CNNToTransformerEncoder
from src.models.tasks import get_task_with_name
from src.models.commands import validate_yaml_or_json

@click.command(name='main', context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.argument("ckpt_path",type=click.Path(exists=True, dir_okay=False))
@click.argument("task_config", type=str, callback=validate_yaml_or_json)
@click.argument("predict_path",type=click.Path(exists=True))
@click.option("--wandb_mode",type=str, default="offline")
@click.option("--notes",type=str, default=None)
@click.pass_context
def main(ctx, ckpt_path, task_config, predict_path, wandb_mode="offline",
        notes=None):
    os.environ["WANDB_MODE"] = wandb_mode

    extra_args = {ctx.args[i][2:]: ctx.args[i+1] for i in range(0, len(ctx.args), 2)}
    model = CNNToTransformerEncoder.load_from_checkpoint(ckpt_path,**extra_args) #TODO support other models
    task =  get_task_with_name(task_config["task_name"])(dataset_args = task_config["dataset_args"],
                                                         activity_level="minute",
                                                         backend="petastorm",
                                                         test_path=predict_path)

    local_rank = os.environ.get("LOCAL_RANK",0)
    if local_rank == 0:
        logger = WandbLogger(project="flu",
                                entity="mikeamerrill",
                                log_model=True,
                                notes=notes,
                                reinit=True)

        logger.experiment.summary["task"] = task.get_name()
        logger.experiment.summary["model"] = model.base_model_prefix
        logger.experiment.config.update(model.hparams)
    else:
        logger = True


    trainer = pl.Trainer(logger=logger,

                         gpus = -1,
                         accelerator="ddp",
                         terminate_on_nan=True,
                         num_sanity_val_steps=0,
                         limit_train_batches=10)

    with PetastormDataLoader(make_reader(task.test_url,transform_spec=task.transform),
                                   batch_size=3*model.batch_size) as test_dataset:
        trainer.test(model,test_dataloaders=test_dataset)


if __name__ == "__main__":
    main()