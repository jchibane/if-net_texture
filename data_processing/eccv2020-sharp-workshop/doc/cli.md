# Command line interface and tools

Display help on available commands:

```bash
$ python -m sharp
```

Display help on a specific command, e.g. `convert`:

```bash
$ python -m sharp convert -h
```


## Convert between mesh formats

Supported formats: `.obj`, `.npz`.

```bash
$ python -m sharp convert shoot path/to/input.obj path/to/output.npz
$ python -m sharp convert path/to/input.npz path/to/output.obj
```


## Generate partial data

Supported formats: `.obj`, `.npz`.


### Holes shooting on a single mesh

Usage example:

```bash
# Shoot 40 holes with each hole removing 2% of the points of the mesh.
$ python -m sharp shoot path/to/input.(npz|obj) path/to/output.(npz|obj) --holes 40 --dropout 0.02 [--mask path/to/mask.npy]
```

--mask: (optional) path to the mask (.npy) to generate holes only on regions considered for evaluation (only challenge 1).
As mentioned in the [evaluation doc](https://gitlab.uni.lu/asaint/eccv2020-sharp-workshop/-/blob/update-instructions/doc/evaluation.md#challenge-specific-criteria),
challenge 1 is evaluated on specific regions of the body mesh:

- Track 1: head and hands are ignored, rest of the body is considered
- Track 2: hands, ears, and feet are considered, rest of the body is ignored

A mask is defined per face as boolean information: 0 if the face is to be ignored, and 1 if the face is to be kept.


### Holes shooting on a directory tree of meshes

Usage examples:

```bash
# Shoot 40 holes with each hole removing 2% of the points of the mesh.
$ python -m sharp shoot_dir path/to/input_directory path/to/output_directory --holes 40 --dropout 0.02 [--mask-dir path/to/mask_directory] [--seed seed_value] [--n-workers n_workers] [--n-shapes n_shapes]
```

--mask-dir: (optional) Directory tree with the masks (.npy). If defined, the partial data is created only on the non-masked faces of the meshes (only challenge 1).

--seed: Initial state for the pseudo random number generator. If not set, the initial state is not set explicitly.

--n-workers: Number of parallel processes. By default, the number of available processors.

-n: (or --n-shapes) Number of partial shapes to generate per mesh. Default is 1.
