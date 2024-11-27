import struct
from PIL import Image

#This script can merge two trees.campaign_tree_list files
#It can also filter a .campaign_tree_list file using a black and white mask (trees within black regions are removed)
#It's currently set up to load one file, filter it, and then merge a second file into it

# Inputs
tree_file_1 = "path/to/first/trees.campaign_tree_list"
tree_file_2 = "path/to/second/trees.campaign_tree_list"

#This is binary, black and white image, it can be any size. Twice the size of the tree tif is ideal.
tree_merge_mask = "./tree_merge_mask.png"


# Outputs
campaign_tree_list = "./trees.campaign_tree_list"






tree_groups = {}  # keyed by subtype
map_width, map_height = 0, 0

def load_trees(file_path):
    global map_width, map_height
    with open(file_path, 'rb') as f:
        # Read header
        magic_number = struct.unpack("<L", f.read(4))[0]
        if magic_number != 4:
            raise ValueError(f"Unexpected magic number: {magic_number}")

        _ = struct.unpack("<L", f.read(4))  # Version
        _ = struct.unpack("<L", f.read(4))  # Padding

        width, height = struct.unpack("<ff", f.read(8))

        # Save map dimensions
        if width > map_width:
            map_width = width
        if height > map_height:
            map_height = height

        # Read tree groups
        num_tree_groups = struct.unpack("<L", f.read(4))[0]

        for _ in range(num_tree_groups):
            name_len = struct.unpack("<H", f.read(2))[0]
            subtype = f.read(name_len).decode('utf-8')

            num_trees = struct.unpack("<L", f.read(4))[0]
            for _ in range(num_trees):
                x, y, z = struct.unpack("<fff", f.read(12))
                is_removable = struct.unpack("<b", f.read(1))[0]
                orientation = struct.unpack("<b", f.read(1))[0]
                season_mask = struct.unpack("<b", f.read(1))[0]

                tree_data = {
                    "x": x,
                    "y": y,
                    "z": z,
                    "orientation": orientation,
                    "is_removable": is_removable,
                    "season_mask": season_mask,
                }
                if subtype not in tree_groups:
                    tree_groups[subtype] = []                    
                tree_groups[subtype].append(tree_data)

def filter_trees(mask_file_path):
    global tree_groups
    # Load the mask image
    mask_image = Image.open(mask_file_path).convert("L")
    mask_width, mask_height = mask_image.size
    mask_pixels = mask_image.load()

    # Scale factor for mapping mask dimensions to tree map dimensions
    scale_x = mask_width / map_width
    scale_z = mask_height / map_height

    # Filter the trees
    filtered_tree_groups = {}
    for subtype, trees in tree_groups.items():
        filtered_trees = []
        for tree in trees:
            # Map tree coordinates to mask pixels, flipping the Y-axis
            mask_x = int(tree["x"] * scale_x)
            mask_z = mask_height - int(tree["z"] * scale_z) - 1

            # Ensure the coordinates are within the mask bounds
            if 0 <= mask_x < mask_width and 0 <= mask_z < mask_height:
                # Keep the tree if the mask pixel is white (255)
                if mask_pixels[mask_x, mask_z] > 127:
                    filtered_trees.append(tree)
        
        if filtered_trees:
            filtered_tree_groups[subtype] = filtered_trees

    # Replace the tree_groups with the filtered version
    tree_groups = filtered_tree_groups


# 1. Load the first file
load_trees(tree_file_1)

# 2. Filter the first file's trees using the tree_merge_mask
filter_trees(tree_merge_mask)

# 3. Load the second file
load_trees(tree_file_2)

# 4. Write the final trees.campaign_tree_list using the combined tree data
with open(campaign_tree_list, 'wb') as f:
    # Magic number and version
    f.write(struct.pack("<L", 4))
    f.write(struct.pack("<L", 0))
    f.write(struct.pack("<L", 0))

    f.write(struct.pack("<f", map_width))
    f.write(struct.pack("<f", map_height))

    # Write tree groups
    f.write(struct.pack("<L", len(tree_groups)))
    for subtype, tree_list in tree_groups.items():
        tree_group_name = subtype.encode('utf-8')
        f.write(struct.pack("<H", len(tree_group_name)))
        f.write(tree_group_name)

        f.write(struct.pack("<L", len(tree_list)))
        for tree in tree_list:
            f.write(struct.pack("<fff", tree["x"], tree["y"], tree["z"]))
            f.write(struct.pack("<b", tree["is_removable"]))
            f.write(struct.pack("<b", tree["orientation"]))
            f.write(struct.pack("<b", tree["season_mask"]))
