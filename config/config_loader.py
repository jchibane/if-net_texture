import yaml
import numpy as np

def load(path):
    with open('config/default_values.yaml', 'r') as f:
        default_cfg = yaml.load(f, yaml.FullLoader)

    with open(path, 'r') as f:
        cfg = yaml.load(f, yaml.FullLoader)

    default_cfg.update(cfg)
    cfg = default_cfg

    cfg['data_bounding_box'] = np.array(cfg['data_bounding_box'])
    cfg['data_bounding_box_str'] = ",".join(str(x) for x in cfg['data_bounding_box'])


    return cfg