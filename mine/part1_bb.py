import sys 
import os

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

def get_moved_filename(input_filename):
    base, ext = os.path.splitext(input_filename)
    return f"{base}_moved{ext}"


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

    scale_factor = min(scale_x, scale_y, scale_z)

    return scale_factor

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


def main():
    if len(sys.argv) != 3:
        print("Usage: python move_into.py <object_to_move.obj> <destination.obj>")
        sys.exit(1)

    object_to_move = sys.argv[1]
    destination = sys.argv[2]

    # Compute bounding box and center for both objects
    bbox_move, center_move = compute_bbox_and_center(object_to_move)
    bbox_dest, center_dest = compute_bbox_and_center(destination)

    # Compute scale factor
    scale = compute_scale_factor_from_bbox(bbox_move, bbox_dest)
    print(f"Scale factor: {scale}")

    # Scale the object to move and save it to a temporary file
    scaled_filename = get_moved_filename(object_to_move)
    scale_object(object_to_move, scale, scaled_filename)

    # Re-compute bounding box and center for the scaled object
    _, center_scaled = compute_bbox_and_center(scaled_filename)

    # Create the patched dir if it doesn't exist
    os.makedirs("patched", exist_ok=True)

    # Move the scaled object to the center of the destination object
    final_output = os.path.join("patched", os.path.basename(scaled_filename))
    move_object_to_center(scaled_filename, center_scaled, center_dest, final_output)

    print(f"Final moved & scaled object saved to {final_output}")

    # Clean up the temporary scaled file
    if os.path.exists(scaled_filename):
        os.remove(scaled_filename)
 
    
if __name__ == "__main__":    
    main()
                
            