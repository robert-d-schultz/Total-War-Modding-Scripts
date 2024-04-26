import struct
from collections import defaultdict
import random, string
from mathutils import Matrix
import math
import os.path
import numpy as np
from itertools import groupby

map_name = "cr_combi_expanded_map_1"
vanilla_map_name = "wh3_main_combi_map_1"

campaign_name = "cr_combi_expanded"
vanilla_campaign_name = "wh3_main_combi"

xml_output_folder = "./terry_layer_output/"

binary_file_path = "C:/path/to/the/global_props.bin"

def read_null_terminated_string(file):
    string = b''

    while True:
        char = file.read(1)
        if char == b'\x00':
            break
        string += char

    return string.decode('utf-8')


def parse_culture_mask(culture_mask):
    #culture mask is 8 bytes that need to be read bit by bit
    
    # Get the positions of the set bits (bits set to 1)
    set_bits = [i for i, bit in enumerate(bin(culture_mask)[:1:-1]) if bit == '1']
    
    # Mapping of bit index to cultures
    culture_mapping = {
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
        34: "wh3_dlc23_chd_chaos_dwarfs",
        63: "*"
    }
    
    # Get the cultures for the set bits and join them with commas
    cultures = [culture_mapping.get(bit_index, "") for bit_index in set_bits]
    return ",".join(cultures)

class CompiledBMDObject:
    def __init__(self, region_name):
        self.region_name = region_name
        self.prop_list = []
        self.vfx_list = []
        self.light_probe_list = []
        self.terrain_hole_tri_list = []
        self.point_light_list = []
        self.polymesh_list = []
        self.spot_light_list = []
        self.sound_emitter_list = []
        self.composite_scene_list = []
        
    def add(self, other):
        if self.region_name != other.region_name:
            raise RuntimeError("You're trying to combine BMD objects from different regions. That's confusing, don't do that!")

        self.prop_list.extend(other.prop_list)
        self.vfx_list.extend(other.vfx_list)
        self.light_probe_list.extend(other.light_probe_list)
        self.terrain_hole_tri_list.extend(other.terrain_hole_tri_list)
        self.point_light_list.extend(other.point_light_list)
        self.polymesh_list.extend(other.polymesh_list)
        self.spot_light_list.extend(other.spot_light_list)
        self.sound_emitter_list.extend(other.sound_emitter_list)
        self.composite_scene_list.extend(other.composite_scene_list)
    
    
class BMDObjectTransform:
    def __init__(self, x_pos, y_pos, z_pos, x_rot=0, y_rot=0, z_rot=0, x_scale=1, y_scale=1, z_scale=1):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.z_pos = z_pos
        self.x_rot = x_rot
        self.y_rot = y_rot
        self.z_rot = z_rot
        self.x_scale = x_scale
        self.y_scale = y_scale
        self.z_scale = z_scale
        
        
    #This can probably fail because of rotation matrix to euler angle conversion stuff
    def __eq__(self, other):
        epsilon = 0.00001
        if not isinstance(other, BMDObjectTransform):
            return NotImplemented
        return (abs(self.x_pos - other.x_pos) < epsilon and 
            abs(self.y_pos - other.y_pos) < epsilon and
            abs(self.z_pos - other.z_pos) < epsilon and
            abs(self.x_rot - other.x_rot) < epsilon and
            abs(self.y_rot - other.y_rot) < epsilon and
            abs(self.z_rot - other.z_rot) < epsilon and
            abs(self.x_scale - other.x_scale) < epsilon and
            abs(self.y_scale - other.y_scale) < epsilon and
            abs(self.z_scale - other.z_scale) < epsilon)
    
    

class BMDProp:
    def __init__(self, path, object_transform, culture_mask, apply_to_terrain, apply_to_objects, render_above_snow, visible_in_tactical, only_visible_in_tactical, apply_height_patch, visible_in_shroud, no_culling, is_decal, visible_in_shroud_only, visible_inside_snow_region, visible_outside_snow_region, visible_inside_destruction_region, visible_outside_destruction_region):
        self.path = path
        self.object_transform = object_transform
        self.culture_mask = culture_mask
        self.apply_to_terrain = apply_to_terrain
        self.apply_to_objects = apply_to_objects
        self.render_above_snow = render_above_snow
        self.visible_in_tactical = visible_in_tactical
        self.only_visible_in_tactical = only_visible_in_tactical
        self.apply_height_patch = apply_height_patch
        self.visible_in_shroud = visible_in_shroud
        self.no_culling = no_culling
        self.is_decal = is_decal
        self.visible_in_shroud_only = visible_in_shroud_only
        self.visible_inside_snow_region = visible_inside_snow_region
        self.visible_outside_snow_region = visible_outside_snow_region
        self.visible_inside_destruction_region = visible_inside_destruction_region
        self.visible_outside_destruction_region = visible_outside_destruction_region
        
    def __eq__(self, other):
        return (self.path == other.path and self.object_transform == other.object_transform)
    
    #Combine the masks of two props
    def combine(self, other):
        if (self.path != other.path) or (self.object_transform != other.object_transform):
            raise RuntimeError("You're trying to combine the masks of two different objects. That doesn't really make sense!")
            
        #Bitwise OR to combine the masks
        self.culture_mask = self.culture_mask | other.culture_mask
        
class BMDVFX:
    def __init__(self, vfx_name, object_transform, culture_mask, visible_in_shroud, visible_in_shroud_only):
        self.vfx_name = vfx_name
        self.object_transform = object_transform
        self.culture_mask = culture_mask
        self.visible_in_shroud = visible_in_shroud
        self.visible_in_shroud_only = visible_in_shroud_only
        
    def __eq__(self, other):
        return (self.vfx_name == other.vfx_name and self.object_transform == other.object_transform)
    
    #Combine the masks of two vfx
    def combine(self, other):
        if (self.vfx_name != other.vfx_name) or (self.object_transform != other.object_transform):
            raise RuntimeError("You're trying to combine the masks of two different objects. That doesn't really make sense!")
            
        #Bitwise OR to combine the masks
        self.culture_mask = self.culture_mask | other.culture_mask
        
class BMDLightProbe:
    def __init__(self, object_transform, is_primary, inner_radius, outer_radius):
        self.object_transform = object_transform
        self.is_primary = is_primary
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        
class BMDTerrainHoleTri:
    def __init__(self, object_transform, culture_mask, vertex2, vertex3):
        self.object_transform = object_transform
        self.culture_mask = culture_mask
        self.vertex2 = vertex2
        self.vertex3 = vertex3
        
    def __eq__(self, other):
        return (self.object_transform == other.object_transform and self.vertex2 == other.vertex2 and self.vertex3 == other.vertex3 )
    
    #Combine the masks of two terrain hole tris
    def combine(self, other):
        if (self.object_transform != other.object_transform) or (self.vertex2 != other.vertex2) or (self.vertex3 != other.vertex3):
            raise RuntimeError("You're trying to combine the masks of two different objects. That doesn't really make sense!")
            
        #Bitwise OR to combine the masks
        self.culture_mask = self.culture_mask | other.culture_mask

class BMDPointLight:
    def __init__(self, object_transform, culture_mask, r, g, b, anim_type, anim_scale1, anim_scale2, color_min, rand_offset, falloff_type, light_probes_only, color_scale, radius):
        self.object_transform = object_transform
        self.culture_mask = culture_mask
        self.r = r
        self.g = g
        self.b = b
        self.anim_type = anim_type
        self.anim_scale1 = anim_scale1
        self.anim_scale2 = anim_scale2
        self.color_min = color_min
        self.rand_offset = rand_offset
        self.falloff_type = falloff_type
        self.light_probes_only = light_probes_only
        self.color_scale = color_scale
        self.radius = radius
        
    def __eq__(self, other):
        return (self.r == other.r and self.g == other.g and self.b == other.b and self.object_transform == other.object_transform)
    
    #Combine the masks of two point lights
    def combine(self, other):
        if (self.r != other.r) or (self.g != other.g) or (self.g != other.g) or (self.object_transform != other.object_transform):
            raise RuntimeError("You're trying to combine the masks of two different objects. That doesn't really make sense!")
            
        #Bitwise OR to combine the masks
        self.culture_mask = self.culture_mask | other.culture_mask
        
class BMDPolyMesh:
    def __init__(self, object_transform, culture_mask, material, vertices, visible_in_tactical, only_visible_in_tactical, visible_in_shroud):
        self.object_transform = object_transform
        self.culture_mask = culture_mask
        self.material = material
        self.vertices = vertices
        self.visible_in_tactical = visible_in_tactical
        self.only_visible_in_tactical = only_visible_in_tactical
        self.visible_in_shroud = visible_in_shroud
        
    def __eq__(self, other):
        return (self.material == other.material and self.object_transform == other.object_transform and self.vertices == other.vertices )
    
    #Combine the masks of two polymesh
    def combine(self, other):
        if (self.material != other.material) or (self.object_transform != other.object_transform) or (self.vertices != other.vertices):
            raise RuntimeError("You're trying to combine the masks of two different objects. That doesn't really make sense!")
            
        #Bitwise OR to combine the masks
        self.culture_mask = self.culture_mask | other.culture_mask
        
class BMDSpotLight:
    def __init__(self, object_transform, culture_mask, r, g, b, intensity, length, inner_angle, outer_angle, falloff, volumetric, gobo):
        self.object_transform = object_transform
        self.culture_mask = culture_mask
        self.r = r
        self.g = g
        self.b = b
        self.intensity = intensity
        self.length = length
        self.inner_angle = inner_angle
        self.outer_angle = outer_angle
        self.falloff = falloff
        self.volumetric = volumetric
        self.gobo = gobo
        
    def __eq__(self, other):
        return (self.r == other.r and self.g == other.g and self.b == other.b and self.object_transform == other.object_transform)
    
    #Combine the masks of two polymesh
    def combine(self, other):
        if (self.r != other.r) or (self.g != other.g) or (self.b != other.b) or (self.object_transform != other.object_transform):
            raise RuntimeError("You're trying to combine the masks of two different objects. That doesn't really make sense!")
            
        #Bitwise OR to combine the masks
        self.culture_mask = self.culture_mask | other.culture_mask
        
class BMDSoundEmitter:
    def __init__(self, sound_name, object_transform, culture_mask, SST_type, coords, radius):
        self.sound_name = sound_name
        self.object_transform = object_transform
        self.culture_mask = culture_mask
        self.SST_type = SST_type
        self.coords = coords
        self.radius = radius
        
    def __eq__(self, other):
        #Don't worry about the other fields... maybe....
        return (self.sound_name == other.sound_name and self.object_transform == other.object_transform)
    
    
    #Combine the masks of two props
    def combine(self, other):
        if (self.sound_name != other.sound_name) or (self.object_transform != other.object_transform):
            raise RuntimeError("You're trying to combine the masks of two different objects. That doesn't really make sense!")
            
        #Bitwise OR to combine the masks
        self.culture_mask = self.culture_mask | other.culture_mask
        
        
class BMDCompositeScene:
    def __init__(self, csc_name, object_transform, culture_mask, visible_in_shroud, no_culling, visible_in_shroud_only):
        self.csc_name = csc_name
        self.object_transform = object_transform
        self.culture_mask = culture_mask
        self.visible_in_shroud = visible_in_shroud
        self.no_culling = no_culling
        self.visible_in_shroud_only = visible_in_shroud_only
        
    def __eq__(self, other):
        #Don't worry about the boolean fields... maybe....
        return (self.csc_name == other.csc_name and self.object_transform == other.object_transform)
    
    
    #Combine the masks of two props
    def combine(self, other):
        if (self.csc_name != other.csc_name) or (self.object_transform != other.object_transform):
            raise RuntimeError("You're trying to combine the masks of two different objects. That doesn't really make sense!")
            
        #Bitwise OR to combine the masks
        self.culture_mask = self.culture_mask | other.culture_mask
        

















with open(binary_file_path, 'rb') as binary_file:
    
    #First go through the header to get all the offsets
    entity_offsets = defaultdict(lambda: 0)
    region_to_layer = defaultdict(lambda: "")
    
    num_entities = struct.unpack("<L", binary_file.read(4))[0]
    for _ in range(num_entities):
        entity_name = read_null_terminated_string(binary_file)
        entity_offset = struct.unpack("<L", binary_file.read(4))[0]
        
        entity_offsets[entity_name] = entity_offset
        
    
    #Record the start of the body's offset
    beginning_offset = binary_file.tell()
        
    
    
    
    
    
    
    
    def write_xml_file(compiled_bmd, region_name, id):
        xml_filepath = xml_output_folder + map_name + "." + id + ".layer"
        with open(xml_filepath, 'w') as xml_file:
            print("Writing " + region_name)
            xml_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
            xml_file.write("<!-- "+ region_name +" -->\n")
            xml_file.write("<layer version=\"41\">\n\t<entities>")
            
            #write props
            for prop in compiled_bmd.prop_list:
                write_prop(xml_file, prop)

            #write vfxs
            for vfx in compiled_bmd.vfx_list:
                write_vfx(xml_file, vfx)
                
            #write light_probes
            for light_probe in compiled_bmd.light_probe_list:
                write_light_probe(xml_file, light_probe)
                
            #write terrain_hole_tris
            for terrain_hole_tri in compiled_bmd.terrain_hole_tri_list:
                write_terrain_hole_tri(xml_file, terrain_hole_tri)
            
            #write point_lights
            for point_light in compiled_bmd.point_light_list:
                write_point_light(xml_file, point_light)
                
            #write polymeshs
            for polymesh in compiled_bmd.polymesh_list:
                write_polymesh(xml_file, polymesh)
                
            #write spot_lights
            for spot_light in compiled_bmd.spot_light_list:
                write_spot_light(xml_file, spot_light)
                
            #write sound_emitters
            for sound_emitter in compiled_bmd.sound_emitter_list:
                write_sound_emitter(xml_file, sound_emitter)
                
            #write composite_scenes
            for composite_scene in compiled_bmd.composite_scene_list:
                write_composite_scene(xml_file, composite_scene)                    
            
            xml_file.write("\n\t</entities>\n\t<associations>\n\t\t<Logical/>\n\t\t<Transform/>\n\t</associations>\n</layer>")
            
            
            
    def write_object_transform(xml_file, object_transform):
        xml_file.write("\n\t\t\t<ECTransform")
        xml_file.write(f" position=\"{np.format_float_positional(object_transform.x_pos,5)} {np.format_float_positional(object_transform.y_pos,5)} {np.format_float_positional(object_transform.z_pos,5)}\"")
        xml_file.write(f" rotation=\"{np.format_float_positional(object_transform.x_rot,5)} {np.format_float_positional(object_transform.y_rot,5)} {np.format_float_positional(object_transform.z_rot,5)}\"")
        xml_file.write(f" scale=\"{np.format_float_positional(object_transform.x_scale,5)} {np.format_float_positional(object_transform.y_scale,5)} {np.format_float_positional(object_transform.z_scale,5)}\"")
        xml_file.write(f" pivot=\"{0} {0} {0}\"/>")
            
            
            
            
    def write_prop(xml_file, prop):
        #fix river models
        if (vanilla_map_name in prop.path) and ("river" in prop.path):
            print("replaced river")
            prop.path = prop.path.replace(vanilla_map_name, map_name)
        
        #Write
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
                        
        if (prop.is_decal):
            xml_file.write(f"\n\t\t\t<ECDecal model_path=\"{prop.path}\" parallax_scale=\"0\" tiling=\"0\" normal_mode=\"DNM_BLEND\""
                + f" apply_to_terrain=\"{prop.apply_to_terrain}\" apply_to_objects=\"{prop.apply_to_objects}\" render_above_snow=\"{prop.render_above_snow}\"/>")
        else:
            xml_file.write("\n\t\t\t<ECPropMesh/>")
            xml_file.write(f"\n\t\t\t<ECMesh model_path=\"{prop.path}\" opacity=\"1\"/>")
            xml_file.write(f"\n\t\t\t<ECMeshRenderSettings receive_decals=\"{prop.apply_to_objects}\"/>")
        
        xml_file.write(f"\n\t\t\t<ECVisibilitySettingsCampaign visible_in_tactical_view=\"{prop.visible_in_tactical}\" visible_in_tactical_view_only=\"{prop.only_visible_in_tactical}\"/>")
        
        xml_file.write(f"\n\t\t\t<ECPropHeightPatch apply_height_patch=\"{prop.apply_height_patch}\" for_camera_height_map_only=\"false\"/>")
                        
        xml_file.write(f"\n\t\t\t<ECCampaignProperties visible_inside_snow_region=\"{prop.visible_inside_snow_region}\" visible_outside_snow_region=\"{prop.visible_outside_snow_region}\" visible_inside_destruction_region=\"{prop.visible_inside_destruction_region}\" visible_outside_destruction_region=\"{prop.visible_outside_destruction_region}\" visible_in_shroud=\"{prop.visible_in_shroud}\" visible_in_shroud_only=\"{prop.visible_in_shroud_only}\" no_culling=\"{prop.no_culling}\" culture_mask=\"{parse_culture_mask(prop.culture_mask)}\"/>")
                        
        write_object_transform(xml_file, prop.object_transform)
        
        xml_file.write("\n\t\t</entity>")
    
    
        
        
    def write_vfx(xml_file, vfx):
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
                        
        xml_file.write(f"\n\t\t\t<ECVisibilitySettingsCampaign visible_in_tactical_view=\"false\" visible_in_tactical_view_only=\"false\"/>")
        
        xml_file.write(f"\n\t\t\t<ECVFX vfx=\"{vfx.vfx_name}\" autoplay=\"true\" scale=\"1\" instance_name=\"\"/>")
        
        xml_file.write(f"\n\t\t\t<ECCampaignProperties visible_in_shroud=\"{vfx.visible_in_shroud}\" visible_in_shroud_only=\"{vfx.visible_in_shroud_only}\" culture_mask=\"{parse_culture_mask(vfx.culture_mask)}\"/>")
                        
        write_object_transform(xml_file, vfx.object_transform)
        
        xml_file.write("\n\t\t</entity>")
    
    
    
    
    def write_light_probe(xml_file, light_probe):
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
        
        xml_file.write(f"\n\t\t\t<ECLightProbe primary=\"{light_probe.is_primary}\"/>")
        
        write_object_transform(xml_file, light_probe.object_transform)
        
        xml_file.write(f"\n\t\t\t<ECDoubleSphere inner_radius=\"{light_probe.inner_radius}\" outer_radius=\"{light_probe.outer_radius}\"/>")
          
        xml_file.write("\n\t\t</entity>")
    
    
    
    
    def write_terrain_hole_tri(xml_file, terrain_hole):
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
                        
        xml_file.write(f"\n\t\t\t<ECTerrainHole/>")
        
     
        write_object_transform(xml_file, terrain_hole.object_transform)
        
        xml_file.write(f"\n\t\t\t<ECVisibilitySettingsCampaign visible_in_tactical_view=\"false\" visible_in_tactical_view_only=\"false\"/>")
        
        xml_file.write(f"\n\t\t\t<ECCampaignProperties visible_in_shroud=\"false\" no_culling=\"false\" culture_mask=\"{parse_culture_mask(terrain_hole.culture_mask)}\"/>")
           
        x1 = 0
        z1 = 0
        
        x2 = terrain_hole.vertex2.x_pos
        z2 = terrain_hole.vertex2.z_pos
        
        x3 = terrain_hole.vertex3.x_pos
        z3 = terrain_hole.vertex3.z_pos
        
        xml_file.write("\n\t\t\t<ECPolyline>")
        xml_file.write("\n\t\t\t\t<polyline closed=\"true\">")
        xml_file.write(f"\n\t\t\t\t\t<point x=\"{np.format_float_positional(x1,5)}\" y=\"{np.format_float_positional(z1,5)}\" />")
        xml_file.write(f"\n\t\t\t\t\t<point x=\"{np.format_float_positional(x2,5)}\" y=\"{np.format_float_positional(z2,5)}\" />")
        xml_file.write(f"\n\t\t\t\t\t<point x=\"{np.format_float_positional(x3,5)}\" y=\"{np.format_float_positional(z3,5)}\" />")
        xml_file.write("\n\t\t\t\t</polyline>")
        xml_file.write("\n\t\t\t</ECPolyline>")
        
        xml_file.write("\n\t\t</entity>")
    
    
    
    
    def write_point_light(xml_file, point_light):
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
        
        xml_file.write(f"\n\t\t\t<ECPointLight colour=\"{int(point_light.r*255)} {int(point_light.g*255)} {int(point_light.b*255)} 255\" colour_scale=\"{point_light.color_scale}\" radius=\"{point_light.radius}\" animation_type=\"{point_light.anim_type}\" animation_speed_scale=\"{point_light.anim_scale1} {point_light.anim_scale2}\" colour_min=\"{point_light.color_min}\" random_offset=\"{point_light.rand_offset}\" falloff_type=\"{point_light.falloff_type}\" for_light_probes_only=\"{point_light.light_probes_only}\"/>")
        
        xml_file.write(f"\n\t\t\t<ECVisibilitySettingsCampaign visible_in_tactical_view=\"false\" visible_in_tactical_view_only=\"false\"/>")
        
        xml_file.write(f"\n\t\t\t<ECCampaignProperties culture_mask=\"{parse_culture_mask(point_light.culture_mask)}\"/>")
        
        write_object_transform(xml_file, point_light.object_transform)
  
        xml_file.write("\n\t\t</entity>")
    
    
    
    
    def write_polymesh(xml_file, polymesh):
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
                        
        xml_file.write(f"\n\t\t\t<ECPolygonMesh material=\"{polymesh.material}\" affects_mesh_optimization=\"false\"/>")
        
        xml_file.write(f"<ECVisibilitySettingsCampaign visible_in_tactical_view=\"{polymesh.visible_in_tactical}\" visible_in_tactical_view_only=\"{polymesh.only_visible_in_tactical}\"/>")
        
        xml_file.write(f"\n\t\t\t<ECCampaignProperties visible_in_shroud=\"{polymesh.visible_in_shroud}\" no_culling=\"true\" culture_mask=\"{parse_culture_mask(polymesh.culture_mask)}\"/>")
                        
        write_object_transform(xml_file, polymesh.object_transform)
        
        xml_file.write("\n\t\t\t<ECPolyline>")
        xml_file.write("\n\t\t\t\t<polyline closed=\"true\">")
        for v in polymesh.vertices:
            xml_file.write(f"\n\t\t\t\t\t<point x=\"{v[0]}\" y=\"{v[2]}\"/>")
        xml_file.write("\n\t\t\t\t</polyline>")
        xml_file.write("\n\t\t\t</ECPolyline>")
        
        xml_file.write("\n\t\t</entity>")
    
    
    
    
    def write_spot_light(xml_file, spot_light):
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
        
        xml_file.write(f"\n\t\t\t<ECSpotLight colour=\"{spot_light.r} {spot_light.g} {spot_light.b} 255\" intensity=\"{spot_light.intensity}\" length=\"{spot_light.length}\" inner_angle=\"{math.degrees(spot_light.inner_angle)}\" outer_angle=\"{math.degrees(spot_light.outer_angle)}\" falloff=\"{spot_light.falloff}\" volumetric=\"{spot_light.volumetric}\" gobo=\"{spot_light.gobo}\"/>")
        
        xml_file.write(f"\n\t\t\t<ECVisibilitySettingsCampaign visible_in_tactical_view=\"false\" visible_in_tactical_view_only=\"false\"/>")
        
        xml_file.write(f"\n\t\t\t<ECCampaignProperties culture_mask=\"{parse_culture_mask(spot_light.culture_mask)}\"/>")
           
        write_object_transform(xml_file, spot_light.object_transform)
  
        xml_file.write("\n\t\t</entity>")
    
    
    
    
    def write_sound_emitter(xml_file, sound_emitter):
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
                        
        xml_file.write(f"\n\t\t\t<ECSoundMarker key=\"{sound_emitter.sound_name}\" />")

        write_object_transform(xml_file, sound_emitter.object_transform)
        
        xml_file.write(f"\n\t\t\t<ECCampaignProperties culture_mask=\"{parse_culture_mask(sound_emitter.culture_mask)}\"/>")
        
        if (sound_emitter.SST_type == "SST_LINE_LIST"):
            xml_file.write("\n\t\t\t<ECPolyline3D>")
            xml_file.write("\n\t\t\t\t<polyline3d closed=\"false\">")
            for coord in sound_emitter.coords:
                xml_file.write(f"\n\t\t\t\t\t<point x=\"{coord[0]-sound_emitter.coords[0][0]}\" y=\"{coord[1]-sound_emitter.coords[0][1]}\" z=\"{coord[2]-sound_emitter.coords[0][2]}\"/>")
            xml_file.write("\n\t\t\t\t</polyline3d>")
            xml_file.write("\n\t\t\t</ECPolyline3D>")
        elif (sound_emitter.SST_type == "SST_MULTI_POINT"):
            xml_file.write("\n\t\t\t<ECPointCloud>")
            xml_file.write("\n\t\t\t\t<point_cloud>")
            for coord in sound_emitter.coords:
                xml_file.write(f"\n\t\t\t\t\t<point x=\"{coord[0]-sound_emitter.coords[0][0]}\" y=\"{coord[1]-sound_emitter.coords[0][1]}\" z=\"{coord[2]-sound_emitter.coords[0][2]}\"/>")
            xml_file.write("\n\t\t\t\t</point_cloud>")
            xml_file.write("\n\t\t\t</ECPointCloud>")
        elif (sound_emitter.SST_type == "SST_SPHERE"):
             xml_file.write("<ECSphere radius=\"{sound_emitter.radius}\"/>")
            
        xml_file.write("\n\t\t</entity>")
    
    
    
    
    def write_composite_scene(xml_file, composite_scene):
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
        
        xml_file.write(f"\n\t\t\t<ECCompositeScene path=\"{composite_scene.csc_name}\" script_id=\"\" autoplay=\"true\"/>")
        
        xml_file.write(f"\n\t\t\t<ECVisibilitySettingsCampaign visible_in_tactical_view=\"false\" visible_in_tactical_view_only=\"false\"/>")
        
        write_object_transform(xml_file, composite_scene.object_transform)
        
        xml_file.write(f"\n\t\t\t<ECCampaignProperties visible_in_shroud=\"{composite_scene.visible_in_shroud}\" visible_in_shroud_only=\"{composite_scene.visible_in_shroud_only}\" no_culling=\"{composite_scene.no_culling}\" culture_mask=\"{parse_culture_mask(composite_scene.culture_mask)}\"/>")
        
        xml_file.write("\n\t\t</entity>")
    
    
    
    
    
    def combine_and_simplify(bmd_object):
        
        print("Combining/Simplifying " + bmd_object.region_name)
        
        
        def do_thing(thing_list):
            end = False
            new_thing_list = []
            for thing in thing_list:
                for new_thing in new_thing_list:
                    if (thing == new_thing):
                        new_thing.combine(thing)
                        end = True
                        break
                if end == True:
                    end = False
                    continue
                else:
                    new_thing_list.append(thing)
                    
            return new_thing_list
        
        
        #Combine props
        new_prop_list = do_thing(bmd_object.prop_list)
                    

        #Combine vfxs
        new_vfx_list = do_thing(bmd_object.vfx_list)
        
            
        #Combine terrain_hole_tris
        new_terrain_hole_tri_list = do_thing(bmd_object.terrain_hole_tri_list)
        
        
        #Combine point_lights
        new_point_light_list = do_thing(bmd_object.point_light_list)
            
            
        #Combine polymeshs
        new_polymesh_list = do_thing(bmd_object.polymesh_list)
            
            
        #Combine spot_lights
        new_spot_light_list = do_thing(bmd_object.spot_light_list)
            
            
        #Combine sound_emitters
        new_sound_emitter_list = do_thing(bmd_object.sound_emitter_list)
            
            
        #Combine composite_scenes
        new_composite_scene_list = do_thing(bmd_object.composite_scene_list)




        bmd_object.prop_list = new_prop_list
        bmd_object.vfx_list = new_vfx_list
        #bmd_object.light_probe_list = new_vfx_list #no culture mask to worry about
        bmd_object.terrain_hole_tri_list = new_terrain_hole_tri_list
        bmd_object.point_light_list = new_point_light_list
        bmd_object.polymesh_list = new_polymesh_list
        bmd_object.spot_light_list = new_spot_light_list
        bmd_object.sound_emitter_list = new_sound_emitter_list
        bmd_object.composite_scene_list = new_composite_scene_list
        
        return bmd_object
    
    
    
    
    def process_root_bmd():
        root_offset = entity_offsets["terrain/campaigns/" + vanilla_map_name + "/bmd_objects.bin"]
        
        binary_file.seek(beginning_offset + root_offset)

        binary_file.read(8) #Fastbin0
        binary_file.read(40)
        num_bmds = struct.unpack("<L", binary_file.read(4))[0]
        root_bmds = []
        for _ in range(num_bmds):
            binary_file.read(2) #version
            bmd_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bmd_name = binary_file.read(bmd_name_length).decode('UTF-8')
            
            binary_file.read(68) #stuff we don't care about
            
            culture_mask = struct.unpack("<q", binary_file.read(8))[0]
            
            region_name_length = struct.unpack("<H", binary_file.read(2))[0]
            region_name = binary_file.read(region_name_length).decode('UTF-8')
             
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            binary_file.read(8) #more stuff we dont care about
            
            root_bmds.append((region_name, bmd_name, culture_mask))
            
            
        root_bmds_sorted = sorted(root_bmds, key=lambda x: x[0])
        
        grouped_root_bmds = []
        for key, group in groupby(root_bmds_sorted, key=lambda x: x[0]):
            # Extract the second and third elements of each tuple in the group
            grouped_items = [(item[1], item[2]) for item in group]
            # Append the grouped data as a tuple to the result list
            grouped_root_bmds.append((key, grouped_items))
        
        for (region_name, foo) in grouped_root_bmds:
            
            regional_bmd_object = CompiledBMDObject(region_name)
            for (bmd_name, culture_mask) in foo:
                output = process_bmd(bmd_name, culture_mask)
                
                output = combine_and_simplify(output) #Merge objects and their culture masks
                
                regional_bmd_object.add(output)
                
            #Don't need to merge out here because.... I think that's how the quadtree is stuctured
            
            #write the xml file
            id = "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14))
            region_to_layer[region_name] = id
            write_xml_file(regional_bmd_object, region_name, id)
            
        
        #There's some more stuff in the file, at the end, but we don't need to worry about it
        
        
        #Format the layer id's so it's ready to be copy+pasted into the project's .terry file
        def get_third_part(key):
            try:
                return key.split('region_', 1)[1]
            except IndexError:
                return key
        
        
        list_filepath = "./terry_file_update.txt"
        with open(list_filepath, 'w') as list_file:
            for region_name in sorted(region_to_layer.keys(), key=get_third_part):
                id = region_to_layer[region_name]
                list_file.write("\n\t\t\t<entity id=\"" + id + "\" name=\"" + region_name + "\">")
                list_file.write("\n\t\t\t\t<ECFileLayer export=\"true\" bmd_export_type=\"\"/>")
                list_file.write("\n\t\t\t</entity>")
        
        
    

    def process_bmd(entity_name, culture_mask):
        region_name = entity_name.split(".")[1]
            
        entity_offset = entity_offsets[entity_name]
        binary_file.seek(beginning_offset + entity_offset)
        
        binary_file.read(8) #Fastbin0
        binary_file.read(40)
        
        
        compiled_bmd = CompiledBMDObject(region_name)
        
        
        
        #BMD section, some recursion in here
        num_bmds = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_bmds):
            binary_file.read(2) #version
            bmd_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bmd_name = binary_file.read(bmd_name_length).decode('UTF-8')
            
            binary_file.read(68) #stuff
            
            culture_mask__ = struct.unpack("<q", binary_file.read(8))[0]
            
            #Recursion here
            r = binary_file.tell()
            output = process_bmd(bmd_name, culture_mask__)
            compiled_bmd.add(output)
            binary_file.seek(r)
            
            region_name_length_ = struct.unpack("<H", binary_file.read(2))[0]
            region_name_ = binary_file.read(region_name_length_).decode('UTF-8')
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            binary_file.read(8) #more stuff
            
            
            
        #Unknown stuff
        binary_file.read(28)
        
        
        
        #Props
        binary_file.read(2)
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
            binary_file.read(2) #version
            
            index = struct.unpack("<L", binary_file.read(4))[0]
            path = prop_types[index]
            
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
            binary_file.read(2)
                
            visible_inside_snow_region = struct.unpack("<B", binary_file.read(1))[0] == 1
            visible_outside_snow_region = struct.unpack("<B", binary_file.read(1))[0] == 1
            visible_inside_destruction_region = struct.unpack("<B", binary_file.read(1))[0] == 1
            visible_outside_destruction_region = struct.unpack("<B", binary_file.read(1))[0] == 1
            
            binary_file.read(18)
            
            visible_in_tactical = struct.unpack("<B", binary_file.read(1))[0] == 1
            only_visible_in_tactical = struct.unpack("<B", binary_file.read(1))[0] == 1
            visible_in_shroud = struct.unpack("<B", binary_file.read(1))[0] == 1
            apply_to_terrain = struct.unpack("<B", binary_file.read(1))[0] == 1
            apply_to_objects = struct.unpack("<B", binary_file.read(1))[0] == 1
            render_above_snow = struct.unpack("<B", binary_file.read(1))[0] == 1
                            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            culture_mask_ = struct.unpack("<q", binary_file.read(8))[0]
            
            if (parse_culture_mask(culture_mask) != ""):
                if (parse_culture_mask(culture_mask_) == ""):
                    culture_mask_ = culture_mask
                else:
                    culture_mask_ = culture_mask_
            else:
                pass

            #dunno
            binary_file.read(1)
            
            no_culling = struct.unpack("<B", binary_file.read(1))[0] == 1
            
            #Height patch related
            has_height_patch = struct.unpack("<B", binary_file.read(1))[0] == 1
            apply_height_patch1 = struct.unpack("<B", binary_file.read(1))[0] == 1
            apply_height_patch = has_height_patch and apply_height_patch1

            binary_file.read(1)
            visible_in_shroud_only = struct.unpack("<B", binary_file.read(1))[0] == 0
            binary_file.read(2)

            
            object_trans = BMDObjectTransform(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot, x_scale, y_scale, z_scale)
            
            bmd_prop = BMDProp(path, object_trans, culture_mask_, apply_to_terrain, apply_to_objects, render_above_snow, visible_in_tactical, only_visible_in_tactical, apply_height_patch, visible_in_shroud, no_culling, is_decal, visible_in_shroud_only, visible_inside_snow_region, visible_outside_snow_region, visible_inside_destruction_region, visible_outside_destruction_region)
            
            compiled_bmd.prop_list.append(bmd_prop)
        
        
            
        
        
        #VFX
        binary_file.read(2)
        num_vfxs = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_vfxs):
            binary_file.read(2) #version
            
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
            binary_file.read(16)
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            culture_mask_ = struct.unpack("<q", binary_file.read(8))[0]
            if (parse_culture_mask(culture_mask) != ""):
                culture_mask_ = culture_mask
                
            binary_file.read(1)
            
            visible_in_shroud = struct.unpack("<B", binary_file.read(1))[0] == 1
            binary_file.read(4)
            visible_in_shroud_only = struct.unpack("<B", binary_file.read(1))[0] == 0
            
            
            object_trans = BMDObjectTransform(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot, x_scale, y_scale, z_scale)
            
            bmd_vfx = BMDVFX(vfx_name, object_trans, culture_mask_, visible_in_shroud, visible_in_shroud_only)
            
            compiled_bmd.vfx_list.append(bmd_vfx)
        
        
        
        #Unknown stuff, also probably unused
        binary_file.read(26)
        
        
        
        #Light probe
        binary_file.read(2)
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
            
            
            object_trans = BMDObjectTransform(x_pos, y_pos, z_pos)
            
            bmd_light_probe = BMDLightProbe(object_trans, is_primary, inner_radius, outer_radius)
            
            compiled_bmd.light_probe_list.append(bmd_light_probe)
            
        
        
        # Terrain hole triangles
        binary_file.read(2)
        num_terrain_holes = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_terrain_holes):
            binary_file.read(2) #version
                             
            (x1,y1,z1) = struct.unpack("<fff", binary_file.read(12))
            (x2,y2,z2) = struct.unpack("<fff", binary_file.read(12))
            (x3,y3,z3) = struct.unpack("<fff", binary_file.read(12))
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            #booleans maybe
            binary_file.read(10)
            
            
            #Need to do some annoying calculations because Terry has terrain holes defined in 2d, but then you can rotate them
            
            offset = np.array((x1,y1,z1))
            
            v1 = np.array((x1,y1,z1)) - offset
            v2 = np.array((x2,y2,z2)) - offset
            v3 = np.array((x3,y3,z3)) - offset
            
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
            (offset_x,offset_y_,offset_z) = offset
            (x1_,y1_,z1_) = rotated_vertex1
            (x2_,y2_,z2_) = rotated_vertex2
            (x3_,y3_,z3_) = rotated_vertex3
            x_rot = math.degrees(x_rot)
            y_rot = math.degrees(y_rot)
            z_rot = math.degrees(z_rot)
            
            if np.isnan(x1_):
                x1_ = v1[0]
            if np.isnan(y1_):
                y1_ = v1[1]
            if np.isnan(z1_):
                z1_ = v1[2]
            if np.isnan(x2_):
                x2_ = v2[0]
            if np.isnan(y2_):
                y2_ = v2[1]
            if np.isnan(z2_):
                z2_ = v2[2]
            if np.isnan(x3_):
                x3_ = v3[0]
            if np.isnan(y3_):
                y3_ = v3[1]
            if np.isnan(z3_):
                z3_ = v3[2]
            
            
            object_trans = BMDObjectTransform(offset_x, offset_y_, offset_z, x_rot, y_rot, z_rot)
            trans2 = BMDObjectTransform(x2_, y2_, z2_)
            trans3 = BMDObjectTransform(x3_, y3_, z3_)
            
            bmd_terrain_hole_tri = BMDTerrainHoleTri(object_trans, culture_mask, trans2, trans3)
            
            compiled_bmd.terrain_hole_tri_list.append(bmd_terrain_hole_tri)
            
            
        
        
        
        
        #Point Light
        binary_file.read(2)
        num_point_lights = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_point_lights):
            binary_file.read(2) #version
            
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
            
            #specific culture mask
            culture_mask_ = struct.unpack("<q", binary_file.read(8))[0]
            if (parse_culture_mask(culture_mask) != ""):
                culture_mask_ = culture_mask
            
            binary_file.read(10)
            
            
            object_trans = BMDObjectTransform(x, y, z)
            
            bmd_point_light = BMDPointLight(object_trans, culture_mask_, r, g, b, anim_type, anim_scale1, anim_scale2, color_min, rand_offset, falloff_type, light_probes_only, color_scale, radius)
            
            compiled_bmd.point_light_list.append(bmd_point_light)
            

            
        #unknown
        binary_file.read(31)
        
        
        #Polymesh
        binary_file.read(2)
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
            
            #Water plane material overrides
            if (vanilla_campaign_name + "_campaign_blood_river.xml.material" in material):
                material = "materials/environment/campaign_sea/" + campaign_name + "_campaign_blood_river.xml.material"
            if (vanilla_campaign_name + "_campaign_water_plane.xml.material" in material):
                material = "materials/environment/campaign_sea/" + campaign_name + "_campaign_water_plane.xml.material"
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            #booleans probably
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
                #Not sure about this stuff
                (x_rot,y_rot,z_rot) = (0,0,0)
                (x_scale,y_scale,z_scale) = (1,1,1)
                (x_pos,y_pos,z_pos) = (0,0,0)
                visible_in_shroud = True
                
            
            object_trans = BMDObjectTransform(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot, x_scale, y_scale, z_scale)
            
            bmd_polymesh = BMDPolyMesh(object_trans, culture_mask, material, vertices, visible_in_tactical, only_visible_in_tactical, visible_in_shroud)
            
            compiled_bmd.polymesh_list.append(bmd_polymesh)



        #unknown
        binary_file.read(6)
            
            
        
        #Spot Light
        binary_file.read(2)
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
            
            #specific culture mask
            culture_mask_ = struct.unpack("<q", binary_file.read(8))[0]
            if (parse_culture_mask(culture_mask) != ""):
                culture_mask_ = culture_mask
                
            #dunno
            binary_file.read(10)
            
            
            object_trans = BMDObjectTransform(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
            
            bmd_spot_light = BMDSpotLight(object_trans, culture_mask_, r, g, b, intensity, length, inner_angle, outer_angle, falloff, volumetric, gobo)
            
            compiled_bmd.spot_light_list.append(bmd_spot_light)
            


        #Sound emitters, sfx
        binary_file.read(2)
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
            
            #specific culture mask
            culture_mask_ = struct.unpack("<q", binary_file.read(8))[0]
            if (parse_culture_mask(culture_mask) != ""):
                culture_mask_ = culture_mask
            
            binary_file.read(32)
            
            SSSSoundMarker_length = struct.unpack("<H", binary_file.read(2))[0]
            SSSSoundMarker_name = binary_file.read(SSSSoundMarker_length).decode('UTF-8')
            
            
            object_trans = BMDObjectTransform(coords[0][0], coords[0][1], coords[0][2])
            
            bmd_sound_emitter = BMDSoundEmitter(sound_name, object_trans, culture_mask_, SST_type, coords, radius)
            
            compiled_bmd.sound_emitter_list.append(bmd_sound_emitter)
            

    
        
        #composite scenes, csc
        binary_file.read(2)
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
            
            #specific culture mask
            culture_mask_ = struct.unpack("<q", binary_file.read(8))[0]
            if (parse_culture_mask(culture_mask) != ""):
                culture_mask_ = culture_mask
            
            #booleans
            binary_file.read(1)
            visible_in_shroud = struct.unpack("<B", binary_file.read(1))[0] == 1
            no_culling = struct.unpack("<B", binary_file.read(1))[0] == 1
            binary_file.read(4)
            visible_in_shroud_only = struct.unpack("<B", binary_file.read(1))[0] == 0
            binary_file.read(2)
            
                        
            object_trans = BMDObjectTransform(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot, x_scale, y_scale, z_scale)
            
            bmd_composite_scene = BMDCompositeScene(csc_name, object_trans, culture_mask_, visible_in_shroud, no_culling, visible_in_shroud_only)
            
            compiled_bmd.composite_scene_list.append(bmd_composite_scene)
            
            
        #Don't forget to return the bmd object!
        return compiled_bmd
            
                

    
    #Start
    process_root_bmd()
