import models.local_model as model
import models.dataloader as dataloader
import numpy as np
import argparse
from models.generation import Generator
import config.config_loader as cfg_loader
import os
import trimesh
import torch
from data_processing import utils
from tqdm import tqdm



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generation Model'
    )

    parser.add_argument('config', type=str, help='Path to config file.')
    args = parser.parse_args()

    cfg = cfg_loader.load(args.config)

    net = model.get_models()[cfg['model']]()

    dataloader = dataloader.VoxelizedDataset('test', cfg, generation = True, num_workers=0).get_loader()

    gen = Generator(net, cfg)


    out_path = 'experiments/{}/evaluation_{}/'.format(cfg['folder_name'], gen.checkpoint)


    for data in tqdm(dataloader):


        try:
            inputs = data['inputs']
            path = data['path'][0]
        except:
            print('none')
            continue


        path = os.path.normpath(path)
        challange = path.split(os.sep)[-4]
        split = path.split(os.sep)[-3]
        gt_file_name = path.split(os.sep)[-2]
        basename = path.split(os.sep)[-1]
        filename_partial = os.path.splitext(path.split(os.sep)[-1])[0]

        file_out_path = out_path + '/{}/'.format(gt_file_name)
        os.makedirs(file_out_path, exist_ok=True)

        if os.path.exists(file_out_path + 'colored_surface_reconstuction.obj'):
            continue


        path_surface = os.path.join(cfg['data_path'], split, gt_file_name, gt_file_name + '_normalized.obj')

        mesh = trimesh.load(path_surface)
        
        # create new uncolored mesh for color prediction
        pred_mesh = trimesh.Trimesh(mesh.vertices, mesh.faces)
        
        # colors will be attached per vertex
        # subdivide in order to have high enough number of vertices for good texture representation
        pred_mesh = pred_mesh.subdivide().subdivide()

        pred_verts_gird_coords = utils.to_grid_sample_coords( pred_mesh.vertices, cfg['data_bounding_box'])
        pred_verts_gird_coords = torch.tensor(pred_verts_gird_coords).unsqueeze(0)


        colors_pred_surface = gen.generate_colors(inputs, pred_verts_gird_coords)

        # attach predicted colors to the mesh
        pred_mesh.visual.vertex_colors = colors_pred_surface

        pred_mesh.export( file_out_path + f'{filename_partial}_color_reconstruction.obj')