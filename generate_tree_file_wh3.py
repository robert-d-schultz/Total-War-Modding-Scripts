from PIL import Image, ImageFile
import struct
import math
import random
import numpy as np

#There's really not a good reason to use this script...


# Inputs

#Copy+paste the campaign_tree_ids db table into a txt file, don't format it
tree_database_file = "./WH3_tree_db.txt"

tree_tif_file = "path/to/<campaign map name>.tree.<that jumble of letters and numbers>.tif"
heightmap_file = "path/to/<campaign map name>.height.<that other jumble of letters and numbers>.tif"

#From playable areas table I guess
real_map_width = 1367.396
real_map_height = 1368.743



# Outputs
campaign_tree_list = "./trees.campaign_tree_list"





#Hash function being used, chatGPT made it, I'm pretty sure it sucks
def hash_funct(x, y, seed=0):
    """Custom hash function for (x, y) coordinates with optional seed."""
    h = x * 0x45d9f3b + y * 0x119de1f + seed * 0x344c569
    h = (h ^ (h >> 16)) & 0xFFFFFFFF  # Mix bits
    return h



# Prevent PIL's decompression bomb error
Image.MAX_IMAGE_PIXELS = None  # Removes the pixel limit warning for very large images
ImageFile.LOAD_TRUNCATED_IMAGES = True  # Handles any potential truncation issues



# 1. Read/parse the tree database file
tree_subtype_data = {}

with open(tree_database_file, 'r') as f:
    lines = f.readlines()

for line in lines:
    parts = line.strip().split()
    if len(parts) != 4:
        continue  # Skip invalid lines

    subtype, is_removable, season, hex_color = parts
    hex_color = hex_color.lower()
    is_removable = int(is_removable.lower() == 'true')  # Convert to 1 or 0
    season = -1 #Just ignore it for WH3, -1 for ALL, but it's probably 0=SPRING,1=SUMMER, etc.

    if hex_color not in tree_subtype_data:
        tree_subtype_data[hex_color] = []

    tree_subtype_data[hex_color].append({
        "subtype": subtype,
        "is_removable": is_removable,
        "season": season,
    })



# 2. Open and read the trees.png and heightmap.png
tree_tif = Image.open(tree_tif_file).convert("RGB")  # Convert indexed to RGB
tree_color_data = tree_tif.load()
tree_tif_width, tree_tif_height = tree_tif.size



heightmap_tif = Image.open(heightmap_file)

# Debug information about the image
#print("Heightmap mode:", heightmap_tif.mode)
#print("Heightmap info:", heightmap_tif.info)

# Convert heightmap to a NumPy array and ensure it's 32-bit float
heightmap_data = np.array(heightmap_tif, dtype=np.float32)

# Check for NaNs in the heightmap
if np.isnan(heightmap_data).any():
    #print("NaNs found in the heightmap data.")
    nan_indices = np.where(np.isnan(heightmap_data))
    #print("Indices of NaNs:", nan_indices)

# Replace NaNs with a default height value (e.g., 0.0)
heightmap_data = np.nan_to_num(heightmap_data, nan=0.0)



# 3. Step through each pixel in trees.tif, match it to a tree subtype, and find its height
tree_groups = {}  # Keyed by subtype

for y in range(0, tree_tif_height, 2):  # Step by 2 for clusters
    for x in range(0, tree_tif_width, 2):  
        # Generate deterministic random-like index for which pixel in the 2x2 block to keep
        keep_index = hash_funct(x, y, 0) % 4  # Result is 0, 1, 2, or 3

        for dy in range(2):  # Iterate through the 2x2 cluster
            for dx in range(2):
                pixel_x, pixel_y = x + dx, y + dy
                if pixel_x >= tree_tif_width or pixel_y >= tree_tif_height:
                    continue  # Skip if out of bounds

                # Skip this pixel unless it's the one to keep
                cluster_index = dy * 2 + dx
                if cluster_index != keep_index:
                    continue

                # Process the kept pixel
                r, g, b = tree_color_data[pixel_x, pixel_y]
                hex_color = f"{r:02x}{g:02x}{b:02x}"

                if hex_color in tree_subtype_data:
                    subtypes = tree_subtype_data[hex_color]
                    if not subtypes:
                        continue

                    # Determine subtype and orientation as before
                    subtype_hash = hash_funct(pixel_x, pixel_y, 1) % len(subtypes)
                    subtype_data = subtypes[subtype_hash]
                    subtype = subtype_data["subtype"]

                    orientation = hash_funct(pixel_x, pixel_y, 3) % 4

                    # Randomized position within the pixel
                    x_coord = pixel_x + (hash_funct(pixel_x, pixel_y, 5) % 1000) / 1000.0
                    z_coord = pixel_y + (hash_funct(pixel_x, pixel_y, 7) % 1000) / 1000.0

                    # Scale coordinates to heightmap
                    heightmap_x = int((x_coord / tree_tif_width) * heightmap_data.shape[1])
                    heightmap_y = int((z_coord / tree_tif_height) * heightmap_data.shape[0])

                    heightmap_x = max(0, min(heightmap_x, heightmap_data.shape[1] - 1))
                    heightmap_y = max(0, min(heightmap_y, heightmap_data.shape[0] - 1))
                    height = heightmap_data[heightmap_y, heightmap_x]
                    if not math.isfinite(height):
                        height = 0.0

                    #Scale the final x,z coordinates to real map size
                    x_coord = x_coord * real_map_width/tree_tif_width
                    z_coord = z_coord * real_map_height/tree_tif_height
            
                    #And finally, mirror vertically because tifs are weird
                    z_coord = real_map_height - z_coord

                    # Create tree data
                    tree_data = {
                        "x": x_coord,
                        "y": height,
                        "z": z_coord,
                        "orientation": orientation,
                        "is_removable": subtype_data["is_removable"],
                        "season_mask": subtype_data["season"],
                    }

                    if subtype not in tree_groups:
                        tree_groups[subtype] = []
                    tree_groups[subtype].append(tree_data)



# 4. Write the final trees.campaign_tree_list
with open(campaign_tree_list, 'wb') as f:
    # Magic number and version
    f.write(struct.pack("<L", 4))
    f.write(struct.pack("<L", 0))
    f.write(struct.pack("<L", 0))

    f.write(struct.pack("<f", real_map_width))
    f.write(struct.pack("<f", real_map_height))

    # Write tree groups
    f.write(struct.pack("<L", len(tree_groups)))
    for subtype, tree_list in tree_groups.items():
        tree_group_name = subtype.encode('utf-8')  # Use subtype as the group name
        f.write(struct.pack("<H", len(tree_group_name)))
        f.write(tree_group_name)

        f.write(struct.pack("<L", len(tree_list)))
        for tree in tree_list:
            f.write(struct.pack("<fff", tree["x"], tree["y"], tree["z"]))
            f.write(struct.pack("<b", tree["is_removable"]))
            f.write(struct.pack("<b", tree["orientation"]))
            f.write(struct.pack("<b", tree["season_mask"]))