import struct
import numpy as np
import math
from PIL import Image

# Define the data type for the RGBA values
dtype_tuple = np.dtype([('r', np.uint8), ('g', np.uint8), ('b', np.uint8), ('a', np.uint8)])

# Paths to the binary file and the output image file
binary_file = "path\\to\\file\\blm_catchment_override.compressed_map"
output_file = './catchment_output.png'

with open(binary_file, 'rb') as f:                                             
    f.read(8)  # magic number
    f.read(2)  # version
    map_width = struct.unpack("<L", f.read(4))[0]
    map_height = struct.unpack("<L", f.read(4))[0]
    block_width = struct.unpack("<L", f.read(4))[0]
    block_height = struct.unpack("<L", f.read(4))[0]
    f.read(24)
    RLE_CARD32_length = struct.unpack("<H", f.read(2))[0]
    RLE_CARD32 = f.read(RLE_CARD32_length).decode('UTF-8')

    offset_count = struct.unpack("<L", f.read(4))[0]
    f.seek(offset_count * 4, 1)  # Skip offsets

    length_count = struct.unpack("<L", f.read(4))[0]
    f.seek(length_count * 2, 1)  # Skip lengths


    # Initialize an empty array for storing image data
    image_data = np.empty((0, math.ceil(map_width/block_width) * block_width), dtype=dtype_tuple)

    row = np.empty((block_height, 0), dtype=dtype_tuple)
    
    block = []
    block_count = struct.unpack("<L", f.read(4))[0]                       
    for _ in range(int(block_count / 6)):
        run_length = struct.unpack("<H", f.read(2))[0]
        b = struct.unpack("<B", f.read(1))[0]
        g = struct.unpack("<B", f.read(1))[0]
        r = struct.unpack("<B", f.read(1))[0]
        a = struct.unpack("<B", f.read(1))[0]
        
        for _ in range(run_length):
            block.append((r,g,b,a))
        
        
        if len(block) == (block_width * block_height):
            arr = np.array(block, dtype=dtype_tuple)
            reshaped = arr.reshape((block_height, block_width))
            row = np.hstack((row.copy(), reshaped.copy()))
            
            if row.shape[1] >= map_width:
                image_data = np.vstack((image_data.copy(), row.copy()))
                row = np.empty((block_height, 0), dtype=dtype_tuple)
            
            block = []
        else:
            continue    

    image = Image.fromarray(image_data, 'RGBA')
    
    #crop to final size
    image = image.crop((0, 0, map_width, map_height))
    
    image.save(output_file)