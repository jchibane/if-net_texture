# Evaluation

## Quantitative

Notation:

- $`Y`$: the ground truth complete reference mesh,
- $`Y'`$: the estimated complete mesh.

The quality of the estimation, $`Y'`$, is evaluated quantitatively with respect
to the ground truth, $`Y`$, using three criterions:

### 1. Surface-to-surface distances

Consist of two directed distances:

1. $`d_{ER}`$ is computed from the estimation to the reference
2. $`d_{RE}`$ is computed from the reference to the estimation.

These distances are inspired from [1] but have been adpated to fit the problem at hand.
The directed distance $`d_{AB}`$ between meshes $`A`$ and $`B`$ is
approximated in practice by sampling points on $`A`$ and computing their
distances to the nearest triangles in mesh $`B`$.

The directed distances $`d_{RE}`$ and $`d_{ER}`$ are given by,
```math
d_{ER}(Y',Y) = \sum_{y' \in Y'} d(y', Y) ,\\
d_{RE}(Y,Y') = \sum_{y \in Y} d(y, Y') ,
```
where $`y'`$ are the sampled points on the estimated surface $`Y'`$ and $`y`$ are the sampled points on the reference surface $`Y`$.

In the two directions, the shape and texture reconstruction errors are measured separately.
For the shape error, the distance,
```math
d(a, B) = d_{shape}(a, B) ,
```
operates on the 3D positions directly and computes a point-to-triangle distance between the sampled point $`a`$ on the source surface $`A`$
and its nearest triangle on the target surface $`B`$.
For the texture error, the distance,
```math
d(a, B)  = d_{tex}(a, B) ,
```
operates on the interpolated texture values at the source and target 3D positions used to compute the shape distance.

This results in two shape distance values ($`d_{ER}^{shape}`$, $`d_{RE}^{shape}`$) and two texture distance values ($`d_{ER}^{tex}`$, $`d_{RE}^{tex}`$).
Good estimations are expected to have low shape and texture distance values.

### 2. Surface hit-rates
ith the point-to-triangle distance used above.
Consist of two rates that are computed in two directions:

1. $`h_{ER}`$ computed from estimation to reference
2. $`h_{RE}`$ computed from reference to estimation.

The hit-rate $`h_{AB}`$ indicates the amount of points sampled on the surface of a source mesh $`A`$ that have
a correspondence on the target mesh $`B`$. A point in mesh $`A`$ has a correspondence (hit) in mesh  $`B`$ if
its projection on the plane of the nearest triangle in $`B`$ intersects the triangle.

Let us consider:

- $`H_{AB}`$: number of points of the source mesh $`A`$ that hit the target $`B`$
- $`M_{AB}`$: number of points of the source mesh $`A`$ that miss the target $`B`$.

The hit-rate from $`A`$ to $`B`ith the point-to-triangle distance used above.$ is then given by,
```math
h_{AB} = \frac{H_{AB}}{H_{AB} + M_{AB}} .
```
In the two directions, the hit-rate is a score with a value in [0,1]. Good estimations are expected to have high hit-rates.


### 3. Surface area score

Consists of a score that quantifies the similarity between
the surface area of the estimation and that of the reference. The surface area of the estimated mesh and the reference mesh
denoted as $`A_{E}`$ and $`A_{R}`$, respectively, are computed by summing over the areas of the triangles of each mesh.
These areas are then normalized as follows,
```math
\bar{A_{R}} = \frac{A_{R}}{A_{R} + A_{E}} , \\
\bar{A_{E}} = \frac{A_{E}}{A_{R} + A_{E}} .
```

The area score  $`S_a`$ is then given by,

```math
S_a = 1 - | \bar{A_{R}} - \bar{A_{E}} | .
```

This score results in a value in [0,1]. Good estimations are expected to have high area scores.


### Final score

Consists of a combination of the three measures explained above.

The shape and texture scores are computed as follows,

```math
S_s = \frac{1}{2} [ \Phi_{k_1}(d_{ER}^{shape}(Y',Y)) h_{ER} + \Phi_{k_2}(d_{RE}^{shape}(Y,Y')) h_{RE} ] , \\
S_t = \frac{1}{2} [ \Phi_{k_3}(d_{ER}^{tex}(Y',Y)) h_{ER} + \Phi_{k_4}(d_{RE}^{tex}(Y,Y')) h_{RE} ] ,
```

where $`\Phi_{k_i}(d) = e^{-k_id^2}`$ maps a distance $`d`$ to a score in [0,1]. The parameters $`k_i`$ are chosen
according to some conducted baselines.

The final score is finally given by,

```math
S = \frac{1}{2} S_a(S_s + S_t) .
```

### Challenge-specific criteria

| challenge(/track) | shape | texture | note                      |
| -                 | -     | -       | -                         |
| 1/1               | Yes   | Yes     | hands and head ignored    |
| 1/2               | Yes   | No      | only hands, feet and ears |
| 2                 | Yes   | Yes     | -                         |


## References

[1] Jensen, Rasmus, et al.
  "Large scale multi-view stereopsis evaluation."
  Proceedings of the IEEE Conference on Computer Vision and Pattern
  Recognition.
  2014.
