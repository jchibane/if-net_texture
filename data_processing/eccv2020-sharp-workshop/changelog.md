# Changlog

## [1.4.1] - 2020-07-24

### Added

- Add an optional `--seed` argument to `python -m sharp shoot` for
  repeatability.

### Changed

- Make `python -m sharp shoot` faster, especially for larger meshes.


## [1.4.0] - 2020-07-22

### Added

- Support masks (i.e. ROI's) in the shooting method for generating partial
  data.
- Routine to generate partial data on a directory tree.
- Make generation of partial data repeatble (with the `--seed` CLI option).

### Changed

- Clarify the final evaluation metric in the documentation.
- Clarify the CLI in the documentation.
- Require numpy>=1.17.0 for the updated pseudo-random number generation API.
- Support saving vertex colors in a .npz.

### Fixed

- Fixed memory leak in the shooting method for generating partial data that
  made repeated calls to `sharp.utils.shoot_holes()` crash after some time.
- Prevent black seams in the texture when generating partial data.

### Removed

- Drop the 'cut' method for generating partial data.


## [1.3.0] - 2020-07-13

### Changed

- Set entry point for the CLI at the top level of the module.

### Fixed

- Support saving a mesh as .npz without texture information.
- Various bugs in the method for shooting holes.


## [1.2.0] - 2020-06-10

### Changed

- Clarify instructions.


## [1.1.0] - 2020-04-18

### Added

- Support i/o for npz meshes.

### Changed

- Organise into module.


## [1.0.0] - 2020-04-09

### Added

- Initial release.
