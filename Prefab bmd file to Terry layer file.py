import struct
from collections import defaultdict
import random, string
from mathutils import Matrix
import math
import os.path
import numpy as np


# Adjust these two things

#input file
binary_file_path = "C:\\Users\\rob\\Desktop\\prefabs\\campaign\\empire_minor_2.bmd"

#output file
xml_filepath = "./output.layer"


###########################################################
## Warning! messy code below! Avoid looking too closely! ##
###########################################################

def parse_culture_mask(culture_mask):
    #culture mask is 8 bytes that need to be read bit by bit
    
    # Get the positions of the set bits (bits set to 1)
    bit_index = next((i for i, bit in enumerate(bin(culture_mask)[:1:-1]) if bit == '1'), None)
    
    return {
        0: "",
        6: "wh_dlc03_bst_beastmen",
        7: "wh_main_brt_bretonnia",
        8: "wh_main_chs_chaos",
        9: "wh_main_dwf_dwarfs",
        10: "wh_main_emp_empire",
        11: "wh_main_grn_greenskins",
        12: "wh_main_vmp_vampire_counts",
        13: "wh_dlc05_wef_wood_elves",
        17: "wh2_main_def_dark_elves",
        18: "wh2_main_hef_high_elves",
        19: "wh2_main_lzd_lizardmen",
        20: "wh2_main_skv_skaven",
        21: "wh2_dlc09_tmb_tomb_kings",
        22: "wh2_main_rogue",
        23: "wh3_main_ksl_kislev",
        24: "wh3_main_ogr_ogre_kingdoms",
        25: "wh2_dlc11_cst_vampire_coast",
        27: "wh3_main_kho_khorne",
        28: "wh3_main_tze_tzeentch",
        29: "wh3_main_nur_nurgle",
        30: "wh3_main_sla_slaanesh",
        31: "wh3_main_dae_daemons",
        32: "wh3_main_cth_cathay",
        33: "wh_dlc08_nor_norsca",
        34: "wh3_dlc23_chd_chaos_dwarfs"
    }.get(bit_index, "")
    
with open(binary_file_path, 'rb') as binary_file:
    
    culture_mask = 0 #I think we assume this
    
    with open(xml_filepath, 'w') as xml_file:
        xml_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<layer version=\"41\">\n\t<entities>")
        #BMD section, recursion in here
        binary_file.read(8) #Fastbin0
        binary_file.read(40)
        num_bmds = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_bmds):
            binary_file.read(2) #version
            bmd_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bmd_name = binary_file.read(bmd_name_length).decode('UTF-8')
            
            binary_file.read(68) #stuff
            
            culture_mask_ = struct.unpack("<q", binary_file.read(8))[0]
            
            #Recursion here
            r = binary_file.tell()
            some_function(bmd_name, culture_mask_)
            binary_file.seek(r)
            
            region_name_length = struct.unpack("<H", binary_file.read(2))[0]
            region_name = binary_file.read(region_name_length).decode('UTF-8')
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            binary_file.read(8) #more stuff
            
        binary_file.read(30)
        
        
        #List of paths to RMV2 and wsmodels
        prop_types = []
        num_prop_types = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_prop_types):
            prop_type_path_length = struct.unpack("<H", binary_file.read(2))[0]
            prop_type_path = binary_file.read(prop_type_path_length).decode('UTF-8')
            prop_types.append(prop_type_path)
        
 
        #Prop info
        num_props = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_props):
            version = struct.unpack("<H", binary_file.read(2))[0]
            
            index = struct.unpack("<L", binary_file.read(4))[0]
            
            
            #3x3 matrix for rotation/scale
            col1 = struct.unpack("<fff", binary_file.read(12))
            col2 = struct.unpack("<fff", binary_file.read(12))
            col3 = struct.unpack("<fff", binary_file.read(12))
            matrix = Matrix([col1,col2,col3])
            matrix.transpose() #correct for col/row
            
            #rotation
            (x_rot,y_rot,z_rot) = matrix.to_euler()
            x_rot = math.degrees(x_rot)
            y_rot = math.degrees(y_rot)
            z_rot = math.degrees(z_rot)
            
            #scale
            (x_scale,y_scale,z_scale) = matrix.to_scale()
            
            #And then offsets for position
            x_pos = struct.unpack("<f", binary_file.read(4))[0]
            y_pos = struct.unpack("<f", binary_file.read(4))[0]
            z_pos = struct.unpack("<f", binary_file.read(4))[0]

            #Booleans
            is_decal = struct.unpack("<B", binary_file.read(1))[0] == 1
            binary_file.read(24)
            
            visible_in_tactical = False
            only_visible_in_tactical = False
            if (version > 21):
                visible_in_tactical = struct.unpack("<B", binary_file.read(1))[0] == 1
                only_visible_in_tactical = struct.unpack("<B", binary_file.read(1))[0] == 1
                
            visible_in_shroud = struct.unpack("<B", binary_file.read(1))[0] == 1
            apply_to_terrain = struct.unpack("<B", binary_file.read(1))[0] == 1
            apply_to_objects = struct.unpack("<B", binary_file.read(1))[0] == 1
            render_above_snow = struct.unpack("<B", binary_file.read(1))[0] == 1
            
            #render_above_snow
            
            #Stuff we can skip past for now
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            binary_file.read(9)
            
            no_culling = False
            if (version > 21):
                no_culling = struct.unpack("<B", binary_file.read(1))[0] == 1
                
            binary_file.read(6)

            
            #Write
            xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
            
            path = prop_types[index]
                            
            if (is_decal):
                xml_file.write(f"\n\t\t\t<ECDecal model_path=\"{path}\" parallax_scale=\"0\" tiling=\"0\" normal_mode=\"DNM_BLEND\" apply_to_terrain=\"{apply_to_terrain}\" apply_to_objects=\"{apply_to_objects}\" render_above_snow=\"{render_above_snow}\"/>")
            else:
                xml_file.write("\n\t\t\t<ECPropMesh/>")
                xml_file.write(f"\n\t\t\t<ECMesh model_path=\"{path}\" opacity=\"1\"/>")
                xml_file.write(f"\n\t\t\t<ECMeshRenderSettings receive_decals=\"{apply_to_objects}\"/>")
            
            xml_file.write(f"\n\t\t\t<ECVisibilitySettingsCampaign visible_in_tactical_view=\"{visible_in_tactical}\" visible_in_tactical_view_only=\"{only_visible_in_tactical}\"/>")
                            
            xml_file.write(f"\n\t\t\t<ECCampaignProperties visible_in_shroud=\"{visible_in_shroud}\" no_culling=\"{no_culling}\" culture_mask=\"" + parse_culture_mask(culture_mask) + "\"/>")
                            
            xml_file.write("\n\t\t\t<ECTransform")
            xml_file.write(f" position=\"{x_pos} {y_pos} {z_pos}\"")
            xml_file.write(f" rotation=\"{x_rot} {y_rot} {z_rot}\"")
            xml_file.write(f" scale=\"{x_scale} {y_scale} {z_scale}\"")
            xml_file.write(f" pivot=\"0 0 0\"/>")
            
            xml_file.write("\n\t\t</entity>")
        
        
        binary_file.read(2)
        
        #VFX
        num_vfxs = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_vfxs):
            version = struct.unpack("<H", binary_file.read(2))[0]
            
            vfx_name_length = struct.unpack("<H", binary_file.read(2))[0]
            vfx_name = binary_file.read(vfx_name_length).decode('UTF-8')
            
            #3x3 matrix for rotation/scale
            col1 = struct.unpack("<fff", binary_file.read(12))
            col2 = struct.unpack("<fff", binary_file.read(12))
            col3 = struct.unpack("<fff", binary_file.read(12))
            matrix = Matrix([col1,col2,col3])
            matrix.transpose() #correct for col/row
            
            #rotation
            (x_rot,y_rot,z_rot) = matrix.to_euler()
            x_rot = math.degrees(x_rot)
            y_rot = math.degrees(y_rot)
            z_rot = math.degrees(z_rot)
            
            #scale
            (x_scale,y_scale,z_scale) = matrix.to_scale()
            
            #And then offsets for position
            x_pos = struct.unpack("<f", binary_file.read(4))[0]
            y_pos = struct.unpack("<f", binary_file.read(4))[0]
            z_pos = struct.unpack("<f", binary_file.read(4))[0]
            
            
            #Stuff we can skip past for now
            binary_file.read(14)
            if (version > 10):
                binary_file.read(2)
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            binary_file.read(9)
            visible_in_shroud = struct.unpack("<B", binary_file.read(1))[0] == 1
            binary_file.read(4)
            visible_in_shroud_only = struct.unpack("<B", binary_file.read(1))[0] == 0
            
            #Write
            xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
                            
            xml_file.write(f"\n\t\t\t<ECVFX vfx=\"{vfx_name}\" autoplay=\"true\" scale=\"{y_scale}\" instance_name=\"\"/>")
            
            xml_file.write(f"\n\t\t\t<ECCampaignProperties visible_in_shroud=\"{visible_in_shroud}\" visible_in_shroud_only=\"{visible_in_shroud_only}\" culture_mask=\"" + parse_culture_mask(culture_mask) + "\"/>")
                            
            xml_file.write("\n\t\t\t<ECTransform")
            xml_file.write(f" position=\"{x_pos} {y_pos} {z_pos}\"")
            xml_file.write(f" rotation=\"{x_rot} {y_rot} {z_rot}\"")
            xml_file.write(f" scale=\"{x_scale} {y_scale} {z_scale}\"")
            xml_file.write(f" pivot=\"0 0 0\"/>")
            
            xml_file.write("\n\t\t</entity>")
        
        
        #Unknown stuff, also probably unused
        binary_file.read(28)
        
        #Light probe
        num_light_probes = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_light_probes):
            binary_file.read(2) #version
            x_pos = struct.unpack("<f", binary_file.read(4))[0]
            y_pos = struct.unpack("<f", binary_file.read(4))[0]
            z_pos = struct.unpack("<f", binary_file.read(4))[0]
            outer_radius = struct.unpack("<f", binary_file.read(4))[0]
            inner_radius = struct.unpack("<f", binary_file.read(4))[0]
            binary_file.read(1)
            is_primary = struct.unpack("<B", binary_file.read(1))[0] == 1
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            #Write
            xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
            
            xml_file.write(f"\n\t\t\t<ECLightProbe primary=\"{is_primary}\"/>")
            
            xml_file.write("\n\t\t\t<ECTransform")
            xml_file.write(f" position=\"{x_pos} {y_pos} {z_pos}\"")
            xml_file.write(f" rotation=\"0 0 0\"")
            xml_file.write(f" scale=\"1 1 1\"")
            xml_file.write(f" pivot=\"0 0 0\"/>")
            
            xml_file.write(f"\n\t\t\t<ECDoubleSphere inner_radius=\"{inner_radius}\" outer_radius=\"{outer_radius}\"/>")
              
            xml_file.write("\n\t\t</entity>")
            
            
        binary_file.read(2) #Unknown
        
        
        # Terrain hole triangles
        num_terrain_holes = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_terrain_holes):
            version = struct.unpack("<H", binary_file.read(2))[0] #version
                             
            (x1,y1,z1) = struct.unpack("<fff", binary_file.read(12))
            (x2,y2,z2) = struct.unpack("<fff", binary_file.read(12))
            (x3,y3,z3) = struct.unpack("<fff", binary_file.read(12))
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            #booleans and stuff
            if (version > 2):
                binary_file.read(10)
            
            
            
            #Something annoying because Terry only has flat holes, but they can be rotated...
            v1 = np.array((x1,y1,z1))
            v2 = np.array((x2,y2,z2))
            v3 = np.array((x3,y3,z3))
            
            # Calculate the normal vector of the triangle
            normal = np.cross(v2 - v1, v3 - v1)
            normal /= np.linalg.norm(normal)

            # Calculate the angle between the normal vector and the y-axis
            angle = np.arccos(normal[1])

            # Calculate the rotation axis by taking the cross product of the normal vector and the y-axis
            rotation_axis = np.cross(normal, [0, 1, 0])
            rotation_axis /= np.linalg.norm(rotation_axis)

            # Create the rotation matrix
            rotation_matrix = np.eye(3)
            rotation_matrix[:3, :3] = np.eye(3) * np.cos(angle) + np.outer(rotation_axis, rotation_axis) * (1 - np.cos(angle)) + np.sin(angle) * np.array([[0, -rotation_axis[2], rotation_axis[1]],
                                                                                                                                                        [rotation_axis[2], 0, -rotation_axis[0]],
                                                                                                                                                        [-rotation_axis[1], rotation_axis[0], 0]])

            # Apply the rotation matrix to all vertices
            rotated_vertex1 = np.dot(rotation_matrix, v1)
            rotated_vertex2 = np.dot(rotation_matrix, v2)
            rotated_vertex3 = np.dot(rotation_matrix, v3)

            # Convert the rotation matrix to Euler angles in degrees
            inverse_rotation_matrix = np.linalg.inv(rotation_matrix)
            (x_rot,y_rot,z_rot) = Matrix(inverse_rotation_matrix).to_euler()

            #The output
            (x1_,y1_,z1_) = rotated_vertex1
            (x2_,y2_,z2_) = rotated_vertex2
            (x3_,y3_,z3_) = rotated_vertex3
            x_rot = math.degrees(x_rot)
            y_rot = math.degrees(y_rot)
            z_rot = math.degrees(z_rot)
            
            if np.isnan(x1_):
                x1_ = x1
            if np.isnan(y1_):
                y1_ = y1
            if np.isnan(z1_):
                z1_ = z1
            if np.isnan(x2_):
                x2_ = x2
            if np.isnan(y2_):
                y2_ = y2
            if np.isnan(z2_):
                z2_ = z2
            if np.isnan(x3_):
                x3_ = x3
            if np.isnan(y3_):
                y3_ = y3
            if np.isnan(z3_):
                z3_ = z3
            
            
            #Write
            xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
                            
            xml_file.write(f"\n\t\t\t<ECTerrainHole/>")
            
         
            xml_file.write("\n\t\t\t<ECTransform")
            xml_file.write(f" position=\"{x1} {y1} {z1}\"")
            xml_file.write(f" rotation=\"{x_rot} {y_rot} {z_rot}\"")
            xml_file.write(f" scale=\"1 1 1\"")
            xml_file.write(f" pivot=\"0 0 0\"/>")
            
            xml_file.write(f"\n\t\t\t<ECCampaignProperties visible_in_shroud=\"true\" no_culling=\"true\" culture_mask=\"" + parse_culture_mask(culture_mask) + "\"/>")
               
            
            xml_file.write("\n\t\t\t<ECPolyline>")
            xml_file.write("\n\t\t\t\t<polyline closed=\"true\">")
            xml_file.write(f"\n\t\t\t\t\t<point x=\"{x1_-x1_}\" y=\"{z1_-z1_}\" />")
            xml_file.write(f"\n\t\t\t\t\t<point x=\"{x2_-x1_}\" y=\"{z2_-z1_}\" />")
            xml_file.write(f"\n\t\t\t\t\t<point x=\"{x3_-x1_}\" y=\"{z3_-z1_}\" />")
            xml_file.write("\n\t\t\t\t</polyline>")
            xml_file.write("\n\t\t\t</ECPolyline>")
            
            xml_file.write("\n\t\t</entity>")
            
            
        binary_file.read(2)
        
        
        
        #Point Light
        num_point_lights = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_point_lights):
            version = struct.unpack("<H", binary_file.read(2))[0]
            
            (x,y,z) = struct.unpack("<fff", binary_file.read(12))
            radius = struct.unpack("<f", binary_file.read(4))[0]
            (r,g,b) = struct.unpack("<fff", binary_file.read(12))
            color_scale = struct.unpack("<f", binary_file.read(4))[0]
            
            anim_type = struct.unpack("<B", binary_file.read(1))[0]
            if (anim_type == 0):
                anim_type = "LAT_NONE"
            elif (anim_type == 1):
                anim_type = "LAT_RADIUS_SIN"
            elif (anim_type == 2):
                anim_type = "LAT_RADIUS_SIN_SIN"
                
            anim_scale1 = struct.unpack("<f", binary_file.read(4))[0]
            anim_scale2 = struct.unpack("<f", binary_file.read(4))[0]
            color_min = struct.unpack("<f", binary_file.read(4))[0]
            rand_offset = struct.unpack("<f", binary_file.read(4))[0]                
            
            falloff_type_length = struct.unpack("<H", binary_file.read(2))[0]
            falloff_type = binary_file.read(falloff_type_length).decode('UTF-8')
            
            binary_file.read(1)
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            light_probes_only = struct.unpack("<B", binary_file.read(1))[0] == 1
            binary_file.read(8)
            if (version > 6):
                binary_file.read(10)
            
            #Write
            xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
            
            xml_file.write(f"\n\t\t\t<ECPointLight colour=\"{int(r*255)} {int(g*255)} {int(b*255)} 255\" colour_scale=\"{color_scale}\" radius=\"{radius}\" animation_type=\"{anim_type}\" animation_speed_scale=\"{anim_scale1} {anim_scale2}\" colour_min=\"{color_min}\" random_offset=\"{rand_offset}\" falloff_type=\"{falloff_type}\" for_light_probes_only=\"{light_probes_only}\"/>")
            
            xml_file.write(f"\n\t\t\t<ECCampaignProperties culture_mask=\"" + parse_culture_mask(culture_mask) + "\"/>")
            
            xml_file.write("\n\t\t\t<ECTransform")
            xml_file.write(f" position=\"{x} {y} {z}\"")
            xml_file.write(f" rotation=\"0 0 0\"")
            xml_file.write(f" scale=\"1 1 1\"")
            xml_file.write(f" pivot=\"0 0 0\"/>")
  
            xml_file.write("\n\t\t</entity>")
            
            
        
        binary_file.read(33)
        
        
        #Polymesh
        num_polymesh = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_polymesh):
            version = struct.unpack("<H", binary_file.read(2))[0] #version
            
            #vertices
            vertices = []
            num_vertices = struct.unpack("<L", binary_file.read(4))[0]
            for _ in range(num_vertices):
                (x_vert,y_vert,z_vert) = struct.unpack("<fff", binary_file.read(12))
                vertices.append((x_vert,y_vert,z_vert))
            
            #this not important for our purposes, I think
            num_triangles = struct.unpack("<L", binary_file.read(4))[0]
            for _ in range(num_triangles):
                triangle_indices = struct.unpack("<H", binary_file.read(2))[0]
                
            #material
            material_length = struct.unpack("<H", binary_file.read(2))[0]
            material = binary_file.read(material_length).decode('UTF-8')
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            binary_file.read(8)
            visible_in_tactical = struct.unpack("<B", binary_file.read(1))[0] == 1
            only_visible_in_tactical = struct.unpack("<B", binary_file.read(1))[0] == 1
            
            if (version >= 4):
                #3x3 matrix for rotation/scale
                col1 = struct.unpack("<fff", binary_file.read(12))
                col2 = struct.unpack("<fff", binary_file.read(12))
                col3 = struct.unpack("<fff", binary_file.read(12))
                matrix = Matrix([col1,col2,col3])
                matrix.transpose() #correct for col/row
                
                #rotation
                (x_rot,y_rot,z_rot) = matrix.to_euler()
                x_rot = math.degrees(x_rot)
                y_rot = math.degrees(y_rot)
                z_rot = math.degrees(z_rot)
                
                #scale
                (x_scale,y_scale,z_scale) = matrix.to_scale()
                
                #And then offsets for position
                x_pos = struct.unpack("<f", binary_file.read(4))[0]
                y_pos = struct.unpack("<f", binary_file.read(4))[0]
                z_pos = struct.unpack("<f", binary_file.read(4))[0]
                
                #booleans
                binary_file.read(4)
                visible_in_shroud = struct.unpack("<B", binary_file.read(1))[0] == 1
                binary_file.read(1)
            else:
                #Not sure about this
                (x_rot,y_rot,z_rot) = (0,0,0)
                (x_scale,y_scale,z_scale) = (1,1,1)
                (x_pos,y_pos,z_pos) = (0,vertices[0][1],0)

                
            #Polymesh Write
            xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
                            
            xml_file.write(f"\n\t\t\t<ECPolygonMesh material=\"{material}\" affects_mesh_optimization=\"false\"/>")
            
            xml_file.write(f"<ECVisibilitySettingsCampaign visible_in_tactical_view=\"{visible_in_tactical}\" visible_in_tactical_view_only=\"{only_visible_in_tactical}\"/>")
            
            xml_file.write(f"\n\t\t\t<ECCampaignProperties visible_in_shroud=\"{visible_in_shroud}\" no_culling=\"true\" culture_mask=\"" + parse_culture_mask(culture_mask) + "\"/>")
                            
            xml_file.write("\n\t\t\t<ECTransform")
            xml_file.write(f" position=\"{x_pos} {y_pos} {z_pos}\"")
            xml_file.write(f" rotation=\"{x_rot} {y_rot} {z_rot}\"")
            xml_file.write(f" scale=\"{x_scale} {y_scale} {z_scale}\"")
            xml_file.write(f" pivot=\"0 0 0\"/>")
            
            xml_file.write("\n\t\t\t<ECPolyline>")
            xml_file.write("\n\t\t\t\t<polyline closed=\"true\">")
            for v in vertices:
                xml_file.write(f"\n\t\t\t\t\t<point x=\"{v[0]}\" y=\"{v[2]}\"/>")
            xml_file.write("\n\t\t\t\t</polyline>")
            xml_file.write("\n\t\t\t</ECPolyline>")
            
            xml_file.write("\n\t\t</entity>")
            
            
        
        #Spot Light
        binary_file.read(8)
        num_spot_lights = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_spot_lights):
            binary_file.read(2) #version
            
            (x,y,z) = struct.unpack("<fff", binary_file.read(12))
            (x_rot,y_rot,z_rot,w_rot) = struct.unpack("<ffff", binary_file.read(16))
            ysqr = y_rot * y_rot

            t0 = +2.0 * (w_rot * x_rot + y_rot * z_rot)
            t1 = +1.0 - 2.0 * (x_rot * x_rot + ysqr)
            x_euler = math.degrees(math.atan2(t0, t1))

            t2 = +2.0 * (w_rot * y_rot - z_rot * x_rot)
            t2 = +1.0 if t2 > +1.0 else t2
            t2 = -1.0 if t2 < -1.0 else t2
            y_euler = math.degrees(math.asin(t2))

            t3 = +2.0 * (w_rot * z_rot + x_rot * y_rot)
            t4 = +1.0 - 2.0 * (ysqr + z_rot * z_rot)
            z_euler = math.degrees(math.atan2(t3, t4))
            
            length = struct.unpack("<f", binary_file.read(4))[0]
            inner_angle = struct.unpack("<f", binary_file.read(4))[0]
            outer_angle = struct.unpack("<f", binary_file.read(4))[0]
            (r,g,b) = struct.unpack("<fff", binary_file.read(12))
            intensity = max(r,g,b)
            r = int((r/intensity) * 255)
            g = int((g/intensity) * 255)
            b = int((b/intensity) * 255)
            
            falloff = struct.unpack("<f", binary_file.read(4))[0]
            
            gobo_length = struct.unpack("<H", binary_file.read(2))[0]
            gobo = binary_file.read(gobo_length).decode('UTF-8')
            
            volumetric = struct.unpack("<B", binary_file.read(1))[0] == 1
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            binary_file.read(18)
            
            #Write
            xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
            
            xml_file.write(f"\n\t\t\t<ECSpotLight colour=\"{r} {g} {b} 255\" intensity=\"{intensity}\" length=\"{length}\" inner_angle=\"{math.degrees(inner_angle)}\" outer_angle=\"{math.degrees(outer_angle)}\" falloff=\"{falloff}\" volumetric=\"{volumetric}\" gobo=\"{gobo}\"/>")
            
            xml_file.write(f"\n\t\t\t<ECCampaignProperties culture_mask=\"" + parse_culture_mask(culture_mask) + "\"/>")
               
            xml_file.write("\n\t\t\t<ECTransform")
            xml_file.write(f" position=\"{x} {y} {z}\"")
            xml_file.write(f" rotation=\"{x_euler} {y_euler} {z_euler}\"")
            xml_file.write(f" scale=\"1 1 1\"")
            xml_file.write(f" pivot=\"0 0 0\"/>")
  
            xml_file.write("\n\t\t</entity>")
            
            
        binary_file.read(2)
        
        
        #Sound emitters, sfx
        num_sfxs = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_sfxs):
            binary_file.read(2)
            
            sound_length = struct.unpack("<H", binary_file.read(2))[0]
            sound_name = binary_file.read(sound_length).decode('UTF-8')
            
            SST_type_length = struct.unpack("<H", binary_file.read(2))[0]
            SST_type = binary_file.read(SST_type_length).decode('UTF-8')
            
            coords = []
            num_coords = struct.unpack("<L", binary_file.read(4))[0]
            for _ in range(num_coords):
                (x_vert,y_vert,z_vert) = struct.unpack("<fff", binary_file.read(12))
                coords.append((x_vert,y_vert,z_vert))
                
            
            binary_file.read(4)
            radius = struct.unpack("<f", binary_file.read(4))[0]
            binary_file.read(53)
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            #special culture mask here? not sure if it's in other things too...
            culture_mask__ = struct.unpack("<q", binary_file.read(8))[0]
            
            binary_file.read(32)
            
            SSSSoundMarker_length = struct.unpack("<H", binary_file.read(2))[0]
            SSSSoundMarker_name = binary_file.read(SSSSoundMarker_length).decode('UTF-8')
            
            #Write
            xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
                            
            xml_file.write(f"\n\t\t\t<ECSoundMarker key=\"{sound_name}\" />")

            xml_file.write("\n\t\t\t<ECTransform")
            xml_file.write(f" position=\"{coords[0][0]} {coords[0][1]} {coords[0][2]}\"")
            xml_file.write(f" rotation=\"0 0 0\"")
            xml_file.write(f" scale=\"1 1 1\"")
            xml_file.write(f" pivot=\"0 0 0\"/>")
            
            xml_file.write(f"\n\t\t\t<ECCampaignProperties culture_mask=\"" + parse_culture_mask(culture_mask__) + "\"/>")
            
            if (SST_type == "SST_LINE_LIST"):
                xml_file.write("\n\t\t\t<ECPolyline3D>")
                xml_file.write("\n\t\t\t\t<polyline3d closed=\"false\">")
                for coord in coords:
                    xml_file.write(f"\n\t\t\t\t\t<point x=\"{coord[0]-coords[0][0]}\" y=\"{coord[1]-coords[0][1]}\" z=\"{coord[2]-coords[0][2]}\"/>")
                xml_file.write("\n\t\t\t\t</polyline3d>")
                xml_file.write("\n\t\t\t</ECPolyline3D>")
            elif (SST_type == "SST_MULTI_POINT"):
                xml_file.write("\n\t\t\t<ECPointCloud>")
                xml_file.write("\n\t\t\t\t<point_cloud>")
                for coord in coords:
                    xml_file.write(f"\n\t\t\t\t\t<point x=\"{coord[0]-coords[0][0]}\" y=\"{coord[1]-coords[0][1]}\" z=\"{coord[2]-coords[0][2]}\"/>")
                xml_file.write("\n\t\t\t\t</point_cloud>")
                xml_file.write("\n\t\t\t</ECPointCloud>")
            elif (SST_type == "SST_SPHERE"):
                 xml_file.write("<ECSphere radius=\"{radius}\"/>")
                
            
            xml_file.write("\n\t\t</entity>")
            
            
        #unknown shit
        binary_file.read(2)
        
        
        #composite scenes, csc
        num_cscs = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_cscs):
            binary_file.read(2)
            
            #3x3 matrix for rotation/scale
            col1 = struct.unpack("<fff", binary_file.read(12))
            col2 = struct.unpack("<fff", binary_file.read(12))
            col3 = struct.unpack("<fff", binary_file.read(12))
            matrix = Matrix([col1,col2,col3])
            matrix.transpose() #correct for col/row
            
            #rotation
            (x_rot,y_rot,z_rot) = matrix.to_euler()
            x_rot = math.degrees(x_rot)
            y_rot = math.degrees(y_rot)
            z_rot = math.degrees(z_rot)
            
            #scale
            (x_scale,y_scale,z_scale) = matrix.to_scale()
            
            #And then offsets for position
            x_pos = struct.unpack("<f", binary_file.read(4))[0]
            y_pos = struct.unpack("<f", binary_file.read(4))[0]
            z_pos = struct.unpack("<f", binary_file.read(4))[0]
            
            csc_name_length = struct.unpack("<H", binary_file.read(2))[0]
            csc_name = binary_file.read(csc_name_length).decode('UTF-8')
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            #booleans
            binary_file.read(18)
            
            
            #Write
            xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
            
            xml_file.write(f"\n\t\t\t<ECCompositeScene path=\"{csc_name}\" script_id=\"\" autoplay=\"true\"/>")
            
            xml_file.write("\n\t\t\t<ECTransform")
            xml_file.write(f" position=\"{x_pos} {y_pos} {z_pos}\"")
            xml_file.write(f" rotation=\"{x_rot} {y_rot} {z_rot}\"")
            xml_file.write(f" scale=\"{x_scale} {y_scale} {z_scale}\"")
            xml_file.write(f" pivot=\"0 0 0\"/>")
            
            xml_file.write(f"\n\t\t\t<ECCampaignProperties culture_mask=\"" + parse_culture_mask(culture_mask) + "\"/>")
                            
            xml_file.write("\n\t\t</entity>")




        xml_file.write("\n\t</entities>\n\t<associations>\n\t\t<Logical/>\n\t\t<Transform/>\n\t</associations>\n</layer>")
