import data_processing.utils as utils
import trimesh
import torch
import os
from glob import glob
import numpy as np

class Generator(object):
    def __init__(self, model, cfg, device = torch.device("cuda")):
        self.model = model.to(device)
        self.model.eval()


        self.checkpoint_path = os.path.dirname(__file__) + '/../experiments/{}/checkpoints/'.format(
            cfg['folder_name'])
        self.exp_folder_name = cfg['folder_name']
        self.checkpoint = self.load_checkpoint(cfg['generation']['checkpoint'])
        self.threshold = cfg['generation']['retrieval_threshold']

        self.device = device
        self.resolution = cfg['generation']['retrieval_resolution']
        self.batch_points = cfg['generation']['batch_points']

        self.bbox = cfg['data_bounding_box']
        self.min = self.bbox[::2]
        self.max = self.bbox[1::2]

        grid_points = utils.create_grid_points_from_xyz_bounds(*cfg['data_bounding_box'], self.resolution)

        grid_coords = utils.to_grid_sample_coords(grid_points, self.bbox)

        grid_coords = torch.from_numpy(grid_coords).to(self.device, dtype=torch.float)
        grid_coords = torch.reshape(grid_coords, (1, len(grid_points), 3)).to(self.device)
        self.grid_points_split = torch.split(grid_coords, self.batch_points, dim=1)



    def generate_colors(self, inputs,points):

        p = points.to(self.device).float()
        # p.shape is [1, n_verts, 3] 693016 -> > 21gb gram

        i = inputs.to(self.device).float()
        full_pred = []

        p_batches = torch.split(p, 200000, dim=1)

        for p_batch in p_batches:
            with torch.no_grad():
                pred_rgb = self.model(p_batch,i)
            full_pred.append(pred_rgb.squeeze(0).detach().cpu().transpose(0,1))

        pred_rgb = torch.cat(full_pred, dim=0).numpy()
        pred_rgb.astype(np.int)[0]
        pred_rgb = np.clip(pred_rgb, 0, 255)

        return pred_rgb




    def load_checkpoint(self, checkpoint):
        if checkpoint == -1:
            val_min_npy = os.path.dirname(__file__) + '/../experiments/{}/val_min.npy'.format(
                self.exp_folder_name)
            checkpoint = int(np.load(val_min_npy)[0])
            path = self.checkpoint_path + 'checkpoint_epoch_{}.tar'.format(checkpoint)
        else:
            path = self.checkpoint_path + 'checkpoint_epoch_{}.tar'.format(checkpoint)
        print('Loaded checkpoint from: {}'.format(path))
        torch_checkpoint = torch.load(path)
        self.model.load_state_dict(torch_checkpoint['model_state_dict'])
        return checkpoint