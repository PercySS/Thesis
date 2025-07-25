# This is a repo for my thesis project

## First Part

Python tool for transfomring '.obj' files:

- It does uniform scaling so objects can be fitted into destination objects and not be distorted.
- Moves the objects in the center of the destination object so it is aligned.
- Optionally rotates the object if specified in the config file.

## Usage

````bash
python part1_bb.py log_file.json
````

The results are saved in directory `patched/` with the name `<object_to_move>_moved.obj`.

## Example

````bash
python part1_bb.py log_files/log1.json
````

## Requirements

- Python 3.8+

## Functionality

- Computes the bounding box and center of both objects.
- Computes the scale factor needed to fit the object into the destination object.
- Applies the scale factor to the object.
- Moves the object to the center of the destination object.
- Optionally rotates the object if a rotation is specified in the config file.
- Saves the transformed object in the `patched/` directory.

## Output

- Correct scale and position of the object.
- Position in the correct center of the destination object.
- 3d object is saved in the `patched/` directory with the name `<object_to_move>_moved.obj`.
