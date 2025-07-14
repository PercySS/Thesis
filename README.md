# This is a repo for my thesis project

## First Part

Python tool for transfomring '.obj' files:

- It does uniform scaling so objects can be fitted into destination objects
- Moves the objects in the center of the destination object so it is aligned

## Usage

````bash
python part1_bb.py object_to_transform.obj destination_object.obj
````

The results are saved in directory `patched/` with the name `<objecct_to_move>_moved.obj`.

## Example

````bash
python part1_bb.py chair.obj table.obj
````

## Requirements

- Python 3.8+

## Functionality

- Computes the bounding box and center of both objects.
- Computes the scale factor needed to fit the object into the destination object.
- Applies the scale factor to the object.
- Moves the object to the center of the destination object.
- Saves the transformed object in the `patched/` directory.

## Output

- Correct scale and position of the object.
- Position in the correct center of the destination object.
