# Source To Module Policy

## Source validation
Reject:
- missing source directory
- empty directory with no usable files
- source folder containing only noise

## Noise examples
- `__pycache__/`
- `.pytest_cache/`
- `.DS_Store`
- `Thumbs.db`
- `node_modules/`
- `dist/`
- `build/`

## Builder report
The report must include:
- source path
- workspace path
- inferred project/package
- packaged ZIP path
- warnings
- stage outputs
