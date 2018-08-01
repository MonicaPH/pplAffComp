"""Tunes hyperparameters for the SSVAE"""

import os
import torch
import ray
from ray.tune import register_trainable, run_experiments, grid_search

from utils.trainables import SSVAETrainable

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
NUM_GPUS = int(torch.cuda.device_count())
USE_CUDA = torch.cuda.is_available()
EMBED_PATH = os.path.join(CODE_DIR, "..", "glove", "glove.6B.50d.txt")

if __name__ == "__main__":
    ray.init(num_gpus=NUM_GPUS)
    register_trainable("ssvae_trainable", SSVAETrainable)
    run_experiments(
    {
        "mvae_train": {
            "run": "ssvae_trainable",
            "stop": {
                "training_iteration": 1000
            },
            "config": {
                "dataset": "word",
                "batch_size": 32,
                "unsup_ratio": grid_search([1,2,3,4,5]),
                "lr": grid_search([1e-4, 5e-5]),
                "z_dim": grid_search(range(10,26,5)),
                "hidden_layers": [200],
                "aux_loss_mult": grid_search([1,3,10,30]), 
                # "beta_fn": (lambda e : 1.0),
                "embed_path": EMBED_PATH,
                "normalize_embeddings": False,
                "use_cuda": USE_CUDA,
            },
            "trial_resources": {"cpu": 2, "gpu": 1},
            "checkpoint_freq": 100,
        }
    },
    verbose=False)
