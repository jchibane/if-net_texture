# Data formats

## Meshes

The meshes of generic objects are stored as [.obj](#wavefront-obj-mesh).

The body scans are textured 3D meshes stored in [.npz](#npz-mesh) archives.

The texture is encoded as a
[texture atlas](https://en.wikipedia.org/wiki/Texture_atlas).

| scan              | texture atlas |
| -                 | -             |
| ![][texture-scan] | ![][texture]  |

[texture-scan]: data/3dbodytex2-texture_atlas-scan-small.png
[texture]: data/3dbodytex2-texture_atlas-small.png

### Wavefront OBJ mesh

See [Wavefront `.obj`](https://en.wikipedia.org/wiki/Wavefront_.obj_file).

### Npz mesh

This format stores the numpy arrays defining the mesh inside a
[(compressed)](https://numpy.org/doc/stable/reference/generated/numpy.savez_compressed.html)
[numpy `.npz`](https://numpy.org/doc/stable/reference/generated/numpy.savez.html)
archive.

The following arrays inside the `.npz` define a mesh:

* `vertices`, float (N, 3):
    The 3D positions of the vertices.
    N varies across the meshes.
* `faces`, int (20000, 3):
    The vertex indices defining the faces in 3D space (i.e. triplets of indices
    into the `vertices` array). Fixed number of faces (20000) for all meshes.
* `texcoords`, float (Nt, 2):
    The 2D positions of the vertices in the texture atlas (Nt > N).
* `texcoords_indices`, int (20000, 3):
    The vertex indices defining the faces in the UV space (2D texture image)
    (i.e. triplets of indices into the `texcoords` array). Fixed number of
    faces (20000) for all meshes
* `texture`, uint8 (2048, 2048, 3):
    The RGB texture image.

Fields not described above should not be relied upon.

The mesh can be loaded with [`numpy.load`][np.load].
For example:

```python
  import numpy as np
  mesh = np.load("name.npz", allow_pickle=True)
  mesh["vertices"]
  mesh["faces"]
  # ...
```

[np.load]: https://numpy.org/doc/stable/reference/generated/numpy.load.html

## Body landmarks

3D positions of detected body landmarks are provided
in the training data of [Challenge 1](challenge_1.md).
They are stored in files with name `landmarks3d.txt`.
The format is plain text and tabular, with one landmark per row and one space
between columns:

```
  name x y z
```

with `name`, the name of the landmark, and `(x, y, z)`, its 3D position in
the frame of reference of the scan or mesh.
If the landmark was not detected, the coordinates are `nan`.

For example,

```
  elbow_left 1.234 0.123 0.389
  finger_thumb_top_left nan nan nan
  ...
```
