import json
from random import choice
import click
import petastorm
from src.utils import read_yaml
from src.models.train_model import (train_cnn_transformer, train_neural_baseline,
                                    train_autoencoder, train_sand,
                                    train_bert, train_longformer)
from src.models.baselines import train_xgboost

def validate_yaml_or_json(ctx, param, value):
    if value is None:
        return
    try:
        return read_yaml(value)
    except FileNotFoundError:
        try:
            return json.loads(value)
        except json.decoder.JSONDecodeError:
            raise click.BadParameter('dataset_args needs to be either a json string or a path to a config .yaml')

nerual_options = [
        click.Option(('--n_epochs',), default = 10, help='Number of training epochs'),
        click.Option(('--hidden_size',), default = 768),
        click.Option(('--num_attention_heads',), default = 4),
        click.Option(('--num_hidden_layers',), default = 4),
        click.Option(('--max_length',), default = 24*60+1),
        click.Option(('--max_position_embeddings',), default = 2048),
        # Training Args:
        click.Option(('--pos_class_weight',), default = 1),
        click.Option(('--neg_class_weight',), default = 1),
        click.Option(('--train_batch_size',), default = 20),
        click.Option(('--eval_batch_size',), default = 60),
        click.Option(('--no_early_stopping',), is_flag=True),
        click.Option(('--warmup_steps',), default = 500),
        click.Option(('--weight_decay',), default = 0.1),
        click.Option(('--eval_frac',), default = None, type=float),
        click.Option(('--learning_rate',), default = 5e-5),
        click.Option(('--sinu_position_encoding',), is_flag=True, default=False),
        click.Option(('--classification_threshold',), default = 0.5),
        click.Option(('--no_eval_during_training',), is_flag=True, default = False),
]

universal_options = [
    click.Option(("--task_config",), type=str, help = "path to config yaml for task",callback=validate_yaml_or_json),
    click.Option(("--task_name",), type=str, help = "name of task in src/models/tasks.py"),
    click.Option(("--model_path",), type=click.Path(file_okay=False,exists=True),
                  help = "path containing a checkpoint-X directory and a model_config.json"),
    click.Option(('--no_wandb',), is_flag=True),
    click.Option(('--tune',), is_flag=True),
    click.Option(('--notes',), type=str, default=None),
    click.Option(('--dataset_args',), default=None,callback=validate_yaml_or_json),
    click.Option(('--activity_level',),type=click.Choice(["day","minute"]), default="minute"),
    click.Option(('--data_location',), default=None,type=click.Path(exists=True)),
    click.Option(('--limit_train_frac',), default=None,type=float,help="Truncate the training data so <limit_train_frac>"),
    click.Option(('--look_for_cached_datareader',), is_flag=True, default=False),
    click.Option(('--cached_task_path',),type=str),
    click.Option(('--datareader_ray_obj_ref',), default=None),
    click.Option(('--task_ray_obj_ref',), default=None),
    click.Option(('--only_with_lab_results',),is_flag=True, default=None),
]

petastorm_options = [
    click.Option(("--train_path",), type=click.Path(file_okay=False,exists=True),
                  help = "path containing petastorm dataset for training"),
    click.Option(("--eval_path",), type=click.Path(file_okay=False,exists=True),
                  help = "path containing petastorm dataset for evaluation"),
    click.Option(("--test_path",), type=click.Path(file_okay=False,exists=True),
                  help = "path containing petastorm dataset for testing"),
]

loss_options = [
    click.Option(("--loss_fn",), type=str, default="CrossEntropyLoss"),
    click.Option(("--focal_alpha",),default=0.25),
    click.Option(("--focal_gamma",),default=2.0)
]
class BaseCommand(click.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = self.params + universal_options

class NeuralCommand(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = self.params + nerual_options 

    
class CNNTransformer(NeuralCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cnn_transformer_params = [
            click.Option(("--reset_cls_params",),is_flag=True, help="Reset the parameters in a the classifcation layer after loading pretrained model"),
            click.Option(("--freeze_encoder",),is_flag=True, help="Freeze the encoder during training"),
            click.Option(("--use_huggingface",),is_flag=True, help="Run the job with huggingface rather than pytorch lightning")
        ]
        self.params = self.params + loss_options + cnn_transformer_params + petastorm_options


@click.command(cls=CNNTransformer, name="train-cnn-transformer")
def train_cnn_transformer_command(*args, **kwargs):
    train_cnn_transformer(*args,**kwargs)


@click.command(cls=BaseCommand,name="train-neural-baseline")
@click.argument("model_name")
@click.option("--n_epochs", default=10)
@click.option("--pos_class_weight", default=100)
@click.option("--neg_class_weight", default=1)
@click.option("--eval_frac", default=0.15)
@click.option("--no_early_stopping",is_flag=True)
def train_neural_baseline_command(*args,**kwargs):
    train_neural_baseline(*args,**kwargs)


@click.command(cls=NeuralCommand,name="train-autoencoder")
@click.argument("model_name")
def train_autoencoder_command(*args, **kwargs):
    train_autoencoder(*args,**kwargs)

@click.command(cls=NeuralCommand,name="train-sand")
def train_sand_command(*args,**kwargs):
    train_sand(*args,**kwargs)


@click.command(cls=NeuralCommand, name="train-bert")
def train_bert_command(*args,**kwargs):
    train_bert(*args,**kwargs)

@click.command(cls=NeuralCommand, name="train-longformer")
def train_longformer_command(*args,**kwargs):
    train_longformer(*args,**kwargs)

@click.command(cls=BaseCommand, name="train-xgboost")
@click.option("--add_features_path", type = click.Path(dir_okay=False), default=None)
def train_xgboost_command(*args,**kwargs):
    train_xgboost(*args,**kwargs)


MODEL_COMMANDS = [train_cnn_transformer_command,
                  train_autoencoder_command,
                  train_neural_baseline_command,
                  train_longformer_command,
                  train_sand_command,
                  train_xgboost_command]