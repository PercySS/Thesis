import sys
import os
import json
import math
import shutil

def compute_bbox_and_center(obj_file):
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')
    min_z = float('inf')
    max_z = float('-inf')

    with open(obj_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if parts and parts[0] == 'v':
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
                min_z = min(min_z, z)
                max_z = max(max_z, z)

    bbox = {
        'min_x': min_x, 'max_x': max_x,
        'min_y': min_y, 'max_y': max_y,
        'min_z': min_z, 'max_z': max_z
    }

    center = (
        (min_x + max_x) / 2,
        (min_y + max_y) / 2,
        (min_z + max_z) / 2
    )

    return bbox, center

def get_temp_filename(input_filename, suffix):
    base = os.path.basename(input_filename)
    name, ext = os.path.splitext(base)
    return os.path.join("temp", f"{name}_{suffix}{ext}")

def move_object_to_center(object_file, current_center, destination_center, output_file):
    cx, cy, cz = current_center
    dx, dy, dz = destination_center

    with open(object_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            parts = line.strip().split()
            if parts and parts[0] == 'v':
                x = float(parts[1]) - cx + dx
                y = float(parts[2]) - cy + dy
                z = float(parts[3]) - cz + dz
                f_out.write(f"v {x} {y} {z}\n")
            else:
                f_out.write(line)

def compute_scale_factor_from_bbox(bbox_obj, bbox_dest):
    size_obj_x = bbox_obj['max_x'] - bbox_obj['min_x']
    size_obj_y = bbox_obj['max_y'] - bbox_obj['min_y']
    size_obj_z = bbox_obj['max_z'] - bbox_obj['min_z']

    size_dest_x = bbox_dest['max_x'] - bbox_dest['min_x']
    size_dest_y = bbox_dest['max_y'] - bbox_dest['min_y']
    size_dest_z = bbox_dest['max_z'] - bbox_dest['min_z']

    if size_obj_x == 0 or size_obj_y == 0 or size_obj_z == 0:
        raise ValueError("Object to move has zero size in at least one dimension.")

    scale_x = size_dest_x / size_obj_x
    scale_y = size_dest_y / size_obj_y
    scale_z = size_dest_z / size_obj_z

    return min(scale_x, scale_y, scale_z)

def scale_object(object_file, scale_factor, output_file):
    with open(object_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            parts = line.strip().split()
            if parts and parts[0] == 'v':
                x = float(parts[1]) * scale_factor
                y = float(parts[2]) * scale_factor
                z = float(parts[3]) * scale_factor
                f_out.write(f"v {x} {y} {z}\n")
            else:
                f_out.write(line)

def rotate_object(object_file, rotation_angles, output_file):
    rx = math.radians(rotation_angles.get('x', 0))
    ry = math.radians(rotation_angles.get('y', 0))
    rz = math.radians(rotation_angles.get('z', 0))

    cos_x = math.cos(rx)
    sin_x = math.sin(rx)
    cos_y = math.cos(ry)
    sin_y = math.sin(ry)
    cos_z = math.cos(rz)
    sin_z = math.sin(rz)

    with open(object_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            parts = line.strip().split()
            if parts and parts[0] == 'v':
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])

                # Rotate around X
                y_new = y * cos_x - z * sin_x
                z_new = y * sin_x + z * cos_x
                y, z = y_new, z_new

                # Rotate around Y
                x_new = x * cos_y + z * sin_y
                z_new = -x * sin_y + z * cos_y
                x, z = x_new, z_new

                # Rotate around Z
                x_new = x * cos_z - y * sin_z
                y_new = x * sin_z + y * cos_z
                x, y = x_new, y_new

                f_out.write(f"v {x} {y} {z}\n")
            else:
                f_out.write(line)

def main():
    if len(sys.argv) != 2:
        print("Usage: python move_into.py <config.json>")
        sys.exit(1)

    config_file = sys.argv[1]

    with open(config_file, 'r') as f:
        config = json.load(f)

    object_to_move = config.get("object_to_move")
    destination = config.get("destination")

    if not object_to_move or not destination:
        print("Error: 'object_to_move' and 'destination' must be specified in the config file.")
        sys.exit(1)

    os.makedirs("temp", exist_ok=True)
    os.makedirs("patched", exist_ok=True)

    # Compute bounding boxes and centers
    bbox_move, _ = compute_bbox_and_center(object_to_move)
    bbox_dest, center_dest = compute_bbox_and_center(destination)

    # Scale
    scale = compute_scale_factor_from_bbox(bbox_move, bbox_dest)
    print(f"Scale factor: {scale}")
    scaled_file = get_temp_filename(object_to_move, "scaled")
    scale_object(object_to_move, scale, scaled_file)

    # Optional rotation
    if "rotation" in config:
        rotated_file = get_temp_filename(object_to_move, "rotated")
        rotate_object(scaled_file, config["rotation"], rotated_file)
        os.remove(scaled_file)
        transformed_file = rotated_file
    else:
        transformed_file = scaled_file

    # Move
    _, center_transformed = compute_bbox_and_center(transformed_file)
    final_output = os.path.join("patched", os.path.basename(object_to_move).replace(".obj", "_moved.obj"))
    move_object_to_center(transformed_file, center_transformed, center_dest, final_output)

    print(f"Final moved, scaled & rotated object saved to {final_output}")

    # Cleanup
    if os.path.exists(transformed_file):
        os.remove(transformed_file)

    if os.path.exists("temp"): 
        shutil.rmtree("temp")

if __name__ == "__main__":
    main()
