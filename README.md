SeattleFluStudy
==============================

## Getting Started
------------

### Installation
1. Clone this repo: `git clone https://github.com/behavioral-data/SeattleFluStudy.git`
2. cd into it:  `cd SeattleFluStudy`
3. Build the conda environment: `make create_environment` (requires conda)


### Getting Our Data 
Data for this study is closed. TODO writeup about how to get it and run a job

### Running your first job 
This project was designed to be run primarily from the command line (although it _could_ be run from a notebook, e.g. by importing `src` ). You can run a simple job with:
``` bash
python src train-cnn-transformer\
        --task_config src/data/task_configs/PredictFluPos.yaml\
        --model_config model_configs/small_embedding.yaml\
        --n_epochs 1 --val_epochs 1\
        --train_path $PWD/data/debug/petastorm_datasets/debug\
        --eval_path $PWD/data/debug/petastorm_datasets/debug
```
###  [Optional] Weights and Biases Integration:

By default this project integrates with Weights and Biases. If you would like to ignore this integration and use some other logging infrasturcture, run commands with the `--no_wandb` flag.

In order to set up this integration, add the following to `.env` (and, of course, install wandb):
```
WANDB_USERNAME=<your username>
WANDB_PROJECT=<the name of the WandB project you want to save results to>
```

## Basic Commands
----
### Training a model from sratch:
Let's go back to that "first job":
```bash
python src train-cnn-transformer\
        --task_config src/data/task_configs/PredictFluPos.yaml\
        --model_config model_configs/small_embedding.yaml\
        --n_epochs 1 --val_epochs 1\
        --train_path $PWD/data/debug/petastorm_datasets/debug\
        --eval_path $PWD/data/debug/petastorm_datasets/debug
```


This command demonstrates the three core components of a training command:
1. A task config (e.g. `src/data/task_configs/PredictFluPos.yaml`)
2. A model config (e.g. `model_configs/small_embedding.yaml`)
3. A dataset (e.g. `$PWD/data/debug/petastorm_datasets/debug`), used here for both training and validation

### Loading a model:
Let's say that you wanted to train a model on the same task as above, but rather than starting from scratch you wanted to use a pretrained model as your initialization. This is accomplished through the `--model_path` flag:

```bash
python src train-cnn-transformer\
        --task_config src/data/task_configs/PredictFluPos.yaml\
        --model_config model_configs/small_embedding.yaml\
        --n_epochs 1 --val_epochs 1\
        --train_path $PWD/data/debug/petastorm_datasets/debug\
        --eval_path $PWD/data/debug/petastorm_datasets/debug\
        --model_path models/debug.ckpt
```

### Evaluating a model:
What if you want to evaluate an existing model on a task? The best way to do this is with the `predict.py` script. This script loads model weights from a checkpoint and runs the model on a given task. 
```bash
python src/models/predict.py models/debug.ckpt src/data/task_configs/PredictFluPos.yaml $PWD/data/debug/petastorm_datasets/debug
```


## Why is this project set up like this?
------------
Great question. For a more satisfying answer than can be provided here, look to the [original cookiecutter page](https://drivendata.github.io/cookiecutter-data-science/): 

One thing that I really like about using the setup is that it's really easy to modularize code.
Say that you wrote some really handy function in `src/visualization.py` that you wanted to use in a notebook. One option might have been to write your notebook in the main directory, and use `src` as a module. This is all well and good for notebook, but what if you have several? A more heinous (and common!) idea might have been to copy and paste over the code to your notebook. 
However, since we turned `src` into a module and added it to the PATH in `make create_environment`, we can just do something like this in our notebook, no matter where it is in the project:
```
from src.visualization import handy_viz
handy_viz(df)
```
Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

## A note on hyperparameter tuning:
All models in this paper were trained with a randomized hyperparameter sweep using a withheld validation set. For CNN modules, we experimented with kernel sizes as large as 63, stride sizes as large as 256, depths as deep as eight layers, and as many as 32 output channels. For transformers modules, we experimented pre-computed and fixed positional embeddings, up to twelve layers of stacked transformers, and up to nine-head attention. We also tried dropout rates between 0.0 and 0.5. In total, over five hundred model configurations were tested before setting on the final configuration of kernel sizes of 5,5,2, stride sizes of 5,3,2, output channels of 8,16,32, two transformer layers each with four heads, and dropout of 0.4.  We tried Adam learning rates from 1 to $1e-6$, and found that $5e-4$ worked best. This relatively small learning rate seemed to be important for limiting overfitting. We also conducted a hyperparameter sweep for XGBoost models, and found little low to hyperparameters, and that $\eta=1$ and a maximum depth of six worked best. Further, we experimented with window sizes ranging from three to ten days, and found that the model overfitted on both ends of this range, with best performance at seven days. 
