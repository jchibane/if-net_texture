import copy
import numbers

import cv2
import numpy as np
try:
    from scipy.spatial import cKDTree as KDTree
except ImportError:
    from scipy.spatial import KDTree

from .trirender import UVTrianglesRenderer


def slice_by_plane(mesh, center, n):
    c = np.dot(center, n)
    plane_side = lambda x: np.dot(x, n) >= c
    split = np.asarray([plane_side(v) for v in mesh.vertices])
    slice1_indices = np.argwhere(split == True)
    slice2_indices = np.argwhere(split == False)
    return slice1_indices, slice2_indices


def remove_points(mesh, indices, blackoutTexture=True):
    cpy = copy.deepcopy(mesh)
    cpy.vertices = np.delete(mesh.vertices, indices, axis=0)
    if mesh.vertex_colors is not None:
        cpy.vertex_colors = np.delete(mesh.vertex_colors, indices, axis=0)
    if mesh.vertex_normals is not None:
        cpy.vertex_normals = np.delete(
            mesh.vertex_normals, indices, axis=0)

    if mesh.faces is not None:
        face_indices = np.where(
            np.any(np.isin(mesh.faces[:], indices, assume_unique=False),
                   axis=1)
        )[0]
        cpy.faces = np.delete(mesh.faces, face_indices, axis=0)
        fix_indices = np.vectorize(
            lambda x: np.sum(x >= indices))(cpy.faces)
        cpy.faces -= fix_indices

        if mesh.face_normals is not None:
            cpy.face_normals = np.delete(
                mesh.face_normals, face_indices, axis=0)
        unused_uv = None
        if mesh.texture_indices is not None:
            cpy.texture_indices = np.delete(
                mesh.texture_indices, face_indices, axis=0)
            used_uv = np.unique(cpy.texture_indices.flatten())
            all_uv = np.arange(len(mesh.texcoords))
            unused_uv = np.setdiff1d(all_uv, used_uv, assume_unique=True)
            fix_uv_idx = np.vectorize(
                lambda x: np.sum(x >= unused_uv))(cpy.texture_indices)
            cpy.texture_indices -= fix_uv_idx
            cpy.texcoords = np.delete(mesh.texcoords, unused_uv, axis=0)

            # render texture
            if blackoutTexture:
                tri_indices = cpy.texture_indices
                tex_coords = cpy.texcoords
                img = render_texture(mesh.texture, tex_coords, tri_indices)
                # dilate the result to remove sewing
                kernel = np.ones((3, 3), np.uint8)
                texture_f32 = cv2.dilate(img, kernel, iterations=1)
                cpy.texture = texture_f32.astype(np.float64)

        if mesh.faces_normal_indices is not None:
            cpy.faces_normal_indices = np.delete(
                mesh.faces_normal_indices, face_indices, axis=0)
            used_ni = np.unique(cpy.faces_normal_indices.flatten())
            all_ni = np.arange(len(mesh.face_normals))
            unused_ni = np.setdiff1d(all_ni, used_ni, assume_unique=True)
            fix_ni_idx = np.vectorize(lambda x: np.sum(
                x > unused_ni))(cpy.faces_normal_indices)
            cpy.faces_normal_indices -= fix_ni_idx
            cpy.face_normals = np.delete(
                mesh.face_normals, unused_ni, axis=0)

    return cpy


def render_texture(texture, tex_coords, tri_indices):
    if len(texture.shape) == 3 and texture.shape[2] == 4:
        texture = texture[:, :, 0:3]
    elif len(texture.shape) == 2:
        texture = np.concatenate([texture, texture, texture], axis=2)

    renderer = UVTrianglesRenderer.with_standalone_ctx(
        (texture.shape[1], texture.shape[0])
    )

    return renderer.render(tex_coords, tri_indices, texture, True)


def estimate_plane(a, b, c):
    """Estimate the parameters of the plane passing by three points.

    Returns:
        center(float): The center point of the three input points.
        normal(float): The normal to the plane.
    """
    center = (a + b + c) / 3
    normal = np.cross(b - a, c - a)
    assert(np.isclose(np.dot(b - a, normal), np.dot(c - a, normal)))
    return center, normal


def shoot_holes(vertices, n_holes, dropout, mask_faces=None, faces=None,
                rng=None):
    """Generate a partial shape by cutting holes of random location and size.

    Each hole is created by selecting a random point as the center and removing
    the k nearest-neighboring points around it.

    Args:
        vertices: The array of vertices of the mesh.
        n_holes (int or (int, int)): Number of holes to create, or bounds from
            which to randomly draw the number of holes.
        dropout (float or (float, float)): Proportion of points (with respect
            to the total number of points) in each hole, or bounds from which
            to randomly draw the proportions (a different proportion is drawn
            for each hole).
        mask_faces: A boolean mask on the faces. 1 to keep, 0 to ignore. If
                    set, the centers of the holes are sampled only on the
                    non-masked regions.
        faces: The array of faces of the mesh. Required only when `mask_faces`
               is set.
        rng: (optional) An initialised np.random.Generator object. If None, a
             default Generator is created.

    Returns:
        array: Indices of the points defining the holes.
    """
    if rng is None:
        rng = np.random.default_rng()

    if not isinstance(n_holes, numbers.Integral):
        n_holes_min, n_holes_max = n_holes
        n_holes = rng.integers(n_holes_min, n_holes_max)

    if mask_faces is not None:
        valid_vertex_indices = np.unique(faces[mask_faces > 0])
        valid_vertices = vertices[valid_vertex_indices]
    else:
        valid_vertices = vertices

    # Select random hole centers.
    center_indices = rng.choice(len(valid_vertices), size=n_holes)
    centers = valid_vertices[center_indices]

    n_vertices = len(valid_vertices)
    if isinstance(dropout, numbers.Number):
        hole_size = n_vertices * dropout
        hole_sizes = [hole_size] * n_holes
    else:
        hole_size_bounds = n_vertices * np.asarray(dropout)
        hole_sizes = rng.integers(*hole_size_bounds, size=n_holes)

    # Identify the points indices making up the holes.
    kdtree = KDTree(vertices, leafsize=200)
    to_crop = []
    for center, size in zip(centers, hole_sizes):
        _, indices = kdtree.query(center, k=size)
        to_crop.append(indices)
    to_crop = np.unique(np.concatenate(to_crop))

    return to_crop
