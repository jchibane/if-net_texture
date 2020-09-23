import argparse
import concurrent.futures
import itertools
import logging
import pathlib
import sys

import numpy as np

from . import data
from . import utils


logger = logging.getLogger(__name__)


def _do_convert(args):
    mesh = data.load_mesh(args.input)
    data.save_mesh(args.output, mesh)


def _do_shoot(args):
    mesh = data.load_mesh(str(args.input))

    has_min_holes = args.min_holes is not None
    has_max_holes = args.max_holes is not None
    if has_min_holes != has_max_holes:
        raise ValueError("--min-holes and --max-holes must be set together")
    n_holes = ((args.min_holes, args.max_holes)
               if has_min_holes
               else args.holes)

    has_min_dropout = args.min_dropout is not None
    has_max_dropout = args.max_dropout is not None
    if has_min_dropout != has_max_dropout:
        raise ValueError(
            "--min-dropout and --max-dropout must be set together")
    dropout = ((args.min_dropout, args.max_dropout)
               if has_min_dropout
               else args.dropout)

    mask_faces = (np.load(args.mask) if args.mask is not None
                  else None)
    faces = None if mask_faces is None else mesh.faces
    point_indices = utils.shoot_holes(mesh.vertices,
                                      n_holes,
                                      dropout,
                                      mask_faces=mask_faces,
                                      faces=faces)
    shot = utils.remove_points(mesh, point_indices)
    shot.save(str(args.output))


def identify_meshes(dir_):
    """List meshes and identify the challenge/track in a directory tree."""
    meshes_track1 = list(dir_.glob("**/*_normalized.npz"))
    meshes_track2 = list(dir_.glob("**/fusion_textured.npz"))
    meshes_challenge2 = list(dir_.glob("**/model_*.obj"))
    if meshes_track1:
        meshes = sorted(meshes_track1)
        challenge = 1
        track = 1
    elif meshes_track2:
        meshes = sorted(meshes_track2)
        challenge = 1
        track = 2
    elif meshes_challenge2:
        meshes = sorted(meshes_challenge2)
        challenge = 2
        track = None
    else:
        meshes = []
        challenge = None
        track = None

    return meshes, challenge, track


def shoot_helper(mesh_index,
                 path,
                 n_holes,
                 dropout,
                 shape_seeds,
                 n_meshes,
                 input_dir,
                 output_dir,
                 mask_dir=None,
                 ):
    logger.info(f"{mesh_index + 1}/{n_meshes} -------- TEST ------------ processing {path}")

    rel_path = path.relative_to(input_dir)

    # Lazily load the mesh and mask when it is sure they are needed.
    mesh_cached = None
    mask_cached = None

    def make_name_suffix(shape_index, n_shapes):
        if n_shapes == 1:
            return "partial"
        else:
            # Assuming 0 <= shape_index <= 99.
            return f"partial-{shape_index:02d}"

    def load_mask(rel_path):
        mask_name = f"{rel_path.stem}-mask.npy"
        mask_rel_path = rel_path.with_name(mask_name)
        mask_path = mask_dir / mask_rel_path
        logger.info(f"loading mask {mask_path}")
        mask_faces = np.load(mask_path)
        return mask_faces

    n_shapes = len(shape_seeds)
    for shape_index, shape_seed in enumerate(shape_seeds):
        out_name_suffix = make_name_suffix(shape_index, n_shapes)
        out_name = f"{rel_path.stem}-{out_name_suffix}.npz"
        out_rel_path = rel_path.with_name(out_name)
        out_path = output_dir / out_rel_path

        if out_path.exists():
            logger.warning(f"shape exists, skipping {out_path}")
            continue

        logger.info(f"generating shape {shape_index + 1}/{n_shapes}")

        out_path.parent.mkdir(parents=True, exist_ok=True)

        if mesh_cached is None:
            mesh_cached = data.load_mesh(str(path))
        if mask_cached is None and mask_dir is not None:
            mask_cached = load_mask(rel_path)

        mesh = mesh_cached
        mask = mask_cached

        logger.info(f"TEST shape seed = {shape_seed}")
        shape_rng = np.random.default_rng(shape_seed)
        point_indices = utils.shoot_holes(mesh.vertices,
                                          n_holes,
                                          dropout,
                                          mask_faces=mask,
                                          faces=mesh.faces,
                                          rng=shape_rng)
        partial = utils.remove_points(mesh, point_indices)

        logger.info(f"{shape_index + 1}/{n_shapes} saving {out_path}")
        partial.save(str(out_path))


def _do_shoot_dir(args):
    """Generate partial data in a directory tree of meshes.

    An independent PRNG is used for each partial shape. Independent seeds are
    created in advance for each partial shape. The process is thus reproducible
    and can also be interrupted and resumed without generating all the previous
    shapes.
    """
    input_dir = args.input_dir
    output_dir = args.output_dir
    mask_dir = args.mask_dir
    seed = args.seed
    n_holes = args.holes
    dropout = args.dropout
    n_shapes = args.n_shapes
    n_workers = args.n_workers

    logger.info("generating partial data in directory tree")
    logger.info(f"input dir = {input_dir}")
    logger.info(f"output dir = {output_dir}")
    logger.info(f"mask dir = {mask_dir}")
    logger.info(f"seed = {seed}")
    logger.info(f"holes = {n_holes}")
    logger.info(f"dropout = {dropout}")
    logger.info(f"n_shapes = {n_shapes}")
    logger.info(f"n_workers = {n_workers}")

    mesh_paths, challenge, track = identify_meshes(input_dir)
    if challenge is None:
        raise ValueError(f"could not identify meshes in {input_dir}")
    logger.info(f"detected challenge {challenge} track {track}")
    n_meshes = len(mesh_paths)
    logger.info(f"found {n_meshes} meshes")

    logger.info(f"setting random seed {seed}")
    rng = np.random.default_rng(seed)

    # Create in advance the individual initial random states for each partial
    # shape to be generated so that the process of generation can be
    # - resumed without regenerating the previous shapes,
    # - parallelised.
    seeds = rng.integers(1e12, size=(n_meshes, n_shapes))

    mesh_indices = range(n_meshes)
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:
        executor.map(
            shoot_helper,
            mesh_indices,
            mesh_paths,
            itertools.repeat(n_holes),
            itertools.repeat(dropout),
            seeds.tolist(),
            itertools.repeat(n_meshes),
            itertools.repeat(input_dir),
            itertools.repeat(output_dir),
            itertools.repeat(mask_dir),
        )


def _parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_convert = subparsers.add_parser(
        "convert",
        help="Convert between mesh formats.",
    )
    parser_convert.add_argument("input", type=pathlib.Path)
    parser_convert.add_argument("output", type=pathlib.Path)
    parser_convert.set_defaults(func=_do_convert)

    parser_shoot = subparsers.add_parser(
        "shoot",
        help="Generate partial data with the shooting method.",
    )
    parser_shoot.add_argument("input", type=pathlib.Path)
    parser_shoot.add_argument("output", type=pathlib.Path)
    parser_shoot.add_argument(
        "--holes", type=int, default=40,
        help="Number of holes to shoot.",
    )
    parser_shoot.add_argument(
        "--min-holes", type=int, default=None,
        help="Minimum number of holes to generate."
             " (Supersedes --holes and requires --max-holes.)",
    )
    parser_shoot.add_argument(
        "--max-holes", type=int, default=None,
        help="Maximum number of holes to generate."
             " (Supersedes --holes and requires --min-holes.)",
    )
    parser_shoot.add_argument(
        "--dropout", type=float, default=2e-2,
        help="Proportion of points of the mesh to remove in a single hole.",
    )
    parser_shoot.add_argument(
        "--min-dropout", type=float, default=None,
        help="Minimum proportion of points of the mesh to remove in a single "
             "hole."
             " (Supersedes --dropout and requires --max-dropout.)",
    )
    parser_shoot.add_argument(
        "--max-dropout", type=float, default=None,
        help="Maximum proportion of points of the mesh to remove in a single "
             "hole."
             " (Supersedes --dropout and requires --min-dropout.)",
    )
    parser_shoot.add_argument(
        "--mask", type=pathlib.Path,
        help=" (optional) Path to the mask (.npy) to generate holes only on"
             " regions considered for evaluation.",
    )
    parser_shoot.set_defaults(func=_do_shoot)

    parser_shoot_dir = subparsers.add_parser(
        "shoot_dir",
        help="Generate partial data with the shooting method for a directory"
             " tree of meshes."
    )
    parser_shoot_dir.add_argument("input_dir", type=pathlib.Path)
    parser_shoot_dir.add_argument("output_dir", type=pathlib.Path)
    parser_shoot_dir.add_argument(
        "--mask-dir",
        type=pathlib.Path,
        help=" (optional) Directory tree with the masks (.npy). If defined,"
             " the partial data is created only on the non-masked faces of the"
             " meshes. (Only valid for challenge 1.)",
    )
    parser_shoot_dir.add_argument(
        "--holes",
        type=int,
        default=40,
        help="Number of holes to shoot.",
    )
    parser_shoot_dir.add_argument(
        "--dropout",
        type=float,
        default=2e-2,
        help="Proportion of points of the mesh to remove in a single hole.",
    )
    parser_shoot_dir.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Initial state for the pseudo random number generator."
             " If not set, the initial state is not set explicitly.",
    )
    parser_shoot_dir.add_argument(
        "-n", "--n-shapes",
        type=int,
        default=1,
        help="Number of partial shapes to generate per mesh."
             " If n = 1 (default), the shape is saved as"
             " '<mesh_name>-partial.npz'."
             " If n > 1, the shapes are saved as '<mesh_name>-partial-XY.npz'"
             ", with XY as 00, 01, 02... (assuming n <= 99).",
    )
    parser_shoot_dir.add_argument(
        "--n-workers",
        type=int,
        default=None,
        help="Number of parallel processes. By default, the number of"
             " available processors.",
    )
    parser_shoot_dir.set_defaults(func=_do_shoot_dir)

    args = parser.parse_args()

    # Ensure the help message is displayed when no command is provided.
    if "func" not in args:
        parser.print_help()
        sys.exit(1)

    return args


def main():
    args = _parse_args()
    args.func(args)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
