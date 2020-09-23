import models.local_model as model
import models.dataloader as dataloader
from models import training
import argparse
import torch
import config.config_loader as cfg_loader

parser = argparse.ArgumentParser(
    description='Train Model'
)

parser.add_argument('config', type=str, help='Path to config file.')
args = parser.parse_args()


cfg = cfg_loader.load(args.config)

net = model.get_models()[cfg['model']]()

train_dataset = dataloader.VoxelizedDataset('train', cfg)

val_dataset = dataloader.VoxelizedDataset('val', cfg)

trainer = training.Trainer(net,torch.device("cuda"),train_dataset, val_dataset, cfg['folder_name'], optimizer=cfg['training']['optimizer'])
trainer.train_model(1500)
