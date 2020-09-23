from __future__ import division
from torch.utils.data import Dataset
import os
import numpy as np
import pickle
import imp
import trimesh
import torch



class VoxelizedDataset(Dataset):


    def __init__(self, mode, cfg, generation = False, num_workers = 12):

        self.path = cfg['data_path']
        self.mode = mode
        self.data = np.load(cfg['split_file'])[mode]
        self.res = cfg['input_resolution']
        self.bbox_str = cfg['data_bounding_box_str']
        self.bbox = cfg['data_bounding_box']
        self.num_gt_rgb_samples = cfg['preprocessing']['color_sampling']['sample_number']

        self.sample_points_per_object = cfg['training']['sample_points_per_object']
        if generation:
            self.batch_size = 1
        else:
            self.batch_size = cfg['training']['batch_size']
        self.num_workers = num_workers
        if cfg['input_type'] == 'voxels':
            self.voxelized_pointcloud = False
        else:
            self.voxelized_pointcloud = True
            self.pointcloud_samples = cfg['input_points_number']



    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        path = self.data[idx]

        path = os.path.normpath(path)
        challange = path.split(os.sep)[-4]
        split = path.split(os.sep)[-3]
        gt_file_name = path.split(os.sep)[-2]
        full_file_name = os.path.splitext(path.split(os.sep)[-1])[0]

        voxel_path = os.path.join(self.path, split, gt_file_name,\
                   '{}_voxelized_colored_point_cloud_res{}_points{}_bbox{}.npz'\
            .format(full_file_name, self.res, self.pointcloud_samples, self.bbox_str))


        R = np.load(voxel_path)['R']
        G = np.load(voxel_path)['G']
        B = np.load(voxel_path)['B']
        S = np.load(voxel_path)['S']

        R = np.reshape(R, (self.res,)*3)
        G = np.reshape(G, (self.res,)*3)
        B = np.reshape(B, (self.res,)*3)
        S = np.reshape(S, (self.res,)*3)
        input = np.array([R,G,B,S])

        if self.mode == 'test':
            return { 'inputs': np.array(input, dtype=np.float32), 'path' : path}


        rgb_samples_path = os.path.join(self.path, split, gt_file_name,\
                   '{}_normalized_color_samples{}_bbox{}.npz' \
                   .format(gt_file_name, self.num_gt_rgb_samples, self.bbox_str))
                   
        rgb_samples_npz = np.load(rgb_samples_path)
        rgb_coords = rgb_samples_npz['grid_coords']
        rgb_values = rgb_samples_npz['colors']
        subsample_indices = np.random.randint(0, len(rgb_values), self.sample_points_per_object)
        rgb_coords = rgb_coords[subsample_indices]
        rgb_values = rgb_values[subsample_indices]


        return {'grid_coords':np.array(rgb_coords, dtype=np.float32),'rgb': np.array(rgb_values, dtype=np.float32), 'inputs': np.array(input, dtype=np.float32), 'path' : path}

    def get_loader(self, shuffle =True):

        return torch.utils.data.DataLoader(
                self, batch_size=self.batch_size, num_workers=self.num_workers, shuffle=shuffle,
                worker_init_fn=self.worker_init_fn)

    def worker_init_fn(self, worker_id):
        random_data = os.urandom(4)
        base_seed = int.from_bytes(random_data, byteorder="big")
        np.random.seed(base_seed + worker_id)