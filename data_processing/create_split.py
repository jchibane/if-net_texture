from glob import glob
import random
import numpy as np
import config.config_loader as cfg_loader
import argparse
import random
import os

parser = argparse.ArgumentParser(
    description='Generates a data split file.'
)

parser.add_argument('config', type=str, help='Path to config file.')
args = parser.parse_args()

cfg = cfg_loader.load(args.config)
    
train_all = glob(os.path.join(cfg['data_path'], 'train', cfg['preprocessing']['voxelized_colored_pointcloud_sampling']['input_files_regex'][3:]))
random.shuffle(train_all)
val = train_all[:int(len(train_all)*0.1)]
train = train_all[int(len(train_all)*0.1):]

test =  glob(os.path.join(cfg['data_path'], 'test', cfg['preprocessing']['voxelized_colored_pointcloud_sampling']['input_files_regex'][3:]))

split_dict = {'train':train, 'test':test, 'val':val}

np.savez(cfg['split_file'], **split_dict)
