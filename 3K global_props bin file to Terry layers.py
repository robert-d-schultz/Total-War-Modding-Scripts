import struct
from collections import defaultdict
import random, string
from mathutils import Matrix
import math
import os.path
import numpy as np
from itertools import groupby

#used for naming the xml outputs, maybe other stuff
map_name = "3k_dlc07_main_map" #ie. cr_combi_expanded_map_1


#not actually the map name, but the terrain folder the map stuff is in
#used to retrieve those river models
vanilla_map_name = "3k_dlc07_main_map"

#campaign names are only used for water plane materials (the text overlay part is basically per-campaign)
campaign_name = "3k_dlc07_main" # ie. cr_combi_expanded
vanilla_campaign_name = "3k_dlc07_main" #ie. wh3_main_combi

xml_output_folder = "./terry_layer_output/"

binary_file_path = "C:/Users/rob/Desktop/terrain/campaigns/3k_dlc07_main_map/global_props.bin"

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
    '''set_bits = [i for i, bit in enumerate(bin(culture_mask)[:1:-1]) if bit == '1']
    
    # Mapping of bit index to cultures
    culture_mapping = {
        6: "wh_dlc03_bst_beastmen",
        7: "wh_main_brt_bretonnia",
    }
    
    
    # Get the cultures for the set bits and join them with commas
    cultures = [culture_mapping.get(bit_index, "") for bit_index in set_bits]'''
    return "" #",".join(cultures)

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
    def __init__(self, path, object_transform, culture_mask, is_decal, apply_to_terrain, apply_to_objects, has_height_patch, apply_height_patch, visible_inside_snow_region, visible_outside_snow_region, visible_inside_destruction_region, visible_outside_destruction_region, visible_in_unseen_shroud, visible_in_seen_shroud, no_culling):
        self.path = path
        self.object_transform = object_transform
        self.culture_mask = culture_mask
        self.is_decal = is_decal
        self.apply_to_terrain = apply_to_terrain
        self.apply_to_objects = apply_to_objects
        self.has_height_patch = has_height_patch
        self.apply_height_patch = apply_height_patch
        self.visible_inside_snow_region = visible_inside_snow_region
        self.visible_outside_snow_region = visible_outside_snow_region
        self.visible_inside_destruction_region = visible_inside_destruction_region
        self.visible_outside_destruction_region = visible_outside_destruction_region
        self.visible_in_unseen_shroud = visible_in_unseen_shroud
        self.visible_in_seen_shroud = visible_in_seen_shroud
        self.no_culling = no_culling
        
    def __eq__(self, other):
        return (self.path == other.path and self.object_transform == other.object_transform)
    
    #Combine the masks of two props
    def combine(self, other):
        if (self.path != other.path) or (self.object_transform != other.object_transform):
            raise RuntimeError("You're trying to combine the masks of two different objects. That doesn't really make sense!")
            
        #Bitwise OR to combine the masks
        self.culture_mask = self.culture_mask | other.culture_mask
        
class BMDVFX:
    def __init__(self, vfx_name, object_transform, culture_mask, visible_inside_snow_region, visible_outside_snow_region, visible_inside_destruction_region, visible_outside_destruction_region, visible_in_unseen_shroud, visible_in_seen_shroud, no_culling):
        self.vfx_name = vfx_name
        self.object_transform = object_transform
        self.culture_mask = culture_mask
        self.visible_inside_snow_region = visible_inside_snow_region
        self.visible_outside_snow_region = visible_outside_snow_region
        self.visible_inside_destruction_region = visible_inside_destruction_region
        self.visible_outside_destruction_region = visible_outside_destruction_region
        self.visible_in_unseen_shroud = visible_in_unseen_shroud
        self.visible_in_seen_shroud = visible_in_seen_shroud
        self.no_culling = no_culling
        
    def __eq__(self, other):
        return (self.vfx_name == other.vfx_name and self.object_transform == other.object_transform)
    
    #Combine the masks of two vfx
    def combine(self, other):
        if (self.vfx_name != other.vfx_name) or (self.object_transform != other.object_transform):
            raise RuntimeError("You're trying to combine the masks of two different objects. That doesn't really make sense!")
            
        #Bitwise OR to combine the masks
        self.culture_mask = self.culture_mask | other.culture_mask
        
class BMDLightProbe:
    def __init__(self, object_transform, radius):
        self.object_transform = object_transform
        self.radius = radius

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
        self.visible_inside_snow_region = True
        self.visible_outside_snow_region = True
        self.visible_inside_destruction_region = True
        self.visible_outside_destruction_region = True
        self.visible_in_unseen_shroud = False
        self.visible_in_seen_shroud = True
        self.no_culling = False
        
    def __eq__(self, other):
        return (self.r == other.r and self.g == other.g and self.b == other.b and self.object_transform == other.object_transform)
    
    #Combine the masks of two point lights
    def combine(self, other):
        if (self.r != other.r) or (self.g != other.g) or (self.g != other.g) or (self.object_transform != other.object_transform):
            raise RuntimeError("You're trying to combine the masks of two different objects. That doesn't really make sense!")
            
        #Bitwise OR to combine the masks
        self.culture_mask = self.culture_mask | other.culture_mask
        
class BMDPolyMesh:
    def __init__(self, object_transform, culture_mask, material, vertices):
        self.object_transform = object_transform
        self.culture_mask = culture_mask
        self.material = material
        self.vertices = vertices
        self.visible_inside_snow_region = True
        self.visible_outside_snow_region = True
        self.visible_inside_destruction_region = True
        self.visible_outside_destruction_region = True
        self.visible_in_unseen_shroud = False
        self.visible_in_seen_shroud = True
        self.no_culling = False
        
    def __eq__(self, other):
        return (self.material == other.material and self.object_transform == other.object_transform and self.vertices == other.vertices )
    
    #Combine the masks of two polymesh
    def combine(self, other):
        if (self.material != other.material) or (self.object_transform != other.object_transform) or (self.vertices != other.vertices):
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
        self.visible_inside_snow_region = True
        self.visible_outside_snow_region = True
        self.visible_inside_destruction_region = True
        self.visible_outside_destruction_region = True
        self.visible_in_unseen_shroud = False
        self.visible_in_seen_shroud = True
        self.no_culling = False
        
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
    def __init__(self, csc_name, object_transform, culture_mask, visible_inside_snow_region, visible_outside_snow_region, visible_inside_destruction_region, visible_outside_destruction_region, visible_in_unseen_shroud, visible_in_seen_shroud, no_culling):
        self.csc_name = csc_name
        self.object_transform = object_transform
        self.culture_mask = culture_mask
        self.visible_inside_snow_region = visible_inside_snow_region
        self.visible_outside_snow_region = visible_outside_snow_region
        self.visible_inside_destruction_region = visible_inside_destruction_region
        self.visible_outside_destruction_region = visible_outside_destruction_region
        self.visible_in_unseen_shroud = visible_in_unseen_shroud
        self.visible_in_seen_shroud = visible_in_seen_shroud
        self.no_culling = no_culling
        
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
            xml_file.write("<layer version=\"35\">\n\t<entities>")
            
            #write props
            for prop in compiled_bmd.prop_list:
                write_prop(xml_file, prop)

            #write vfxs
            for vfx in compiled_bmd.vfx_list:
                write_vfx(xml_file, vfx)
                
            #write light_probes
            for light_probe in compiled_bmd.light_probe_list:
                write_light_probe(xml_file, light_probe)
                        
            #write point_lights
            for point_light in compiled_bmd.point_light_list:
                write_point_light(xml_file, point_light)
                
            #write polymeshs
            for polymesh in compiled_bmd.polymesh_list:
                write_polymesh(xml_file, polymesh)
                
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
        
        
    def write_campaign_properties(xml_file, prop):
        xml_file.write(f"\n\t\t\t<ECCampaignProperties visible_inside_snow_region=\"{prop.visible_inside_snow_region}\" visible_outside_snow_region=\"{prop.visible_outside_snow_region}\" visible_inside_destruction_region=\"{prop.visible_inside_destruction_region}\" visible_outside_destruction_region=\"{prop.visible_outside_destruction_region}\" visible_in_unseen_shroud=\"{prop.visible_in_unseen_shroud}\" visible_in_seen_shroud=\"{prop.visible_in_seen_shroud}\" no_culling=\"{prop.no_culling}\" culture_mask=\"{parse_culture_mask(prop.culture_mask)}\" season_mask=\"\"/>")
            
            
            
            
    def write_prop(xml_file, prop):
        #fix river models
        if (vanilla_map_name in prop.path) and ("river" in prop.path):
            print("replaced river")
            prop.path = prop.path.replace(vanilla_map_name, map_name)
        
        #Write
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
                        
        if (prop.is_decal):
            xml_file.write(f"\n\t\t\t<ECDecal model_path=\"{prop.path}\" parallax_scale=\"0\" tiling=\"0\" tiling_affects_alpha=\"false\" normal_mode=\"DNM_DECAL_OVERRIDE\""
                + f" apply_to_terrain=\"{prop.apply_to_terrain}\" apply_to_objects=\"{prop.apply_to_objects}\" render_above_snow=\"false\"/>")
        else:
            xml_file.write("\n\t\t\t<ECPropMesh/>")
            xml_file.write(f"\n\t\t\t<ECMesh model_path=\"{prop.path}\" opacity=\"1\"/>")
            xml_file.write(f"\n\t\t\t<ECMeshRenderSettings inherit_from_parent=\"false\" cast_shadow=\"true\" tint_colour=\"255 255 255 255\" set_tint_colour_from_colour_overlay=\"false\" receive_decals=\"{prop.apply_to_objects}\" faction_colour=\"255 255 255 255\"/>")
        
        xml_file.write(f"\n\t\t\t<ECPropHeightPatch has_height_patch=\"{prop.has_height_patch}\" apply_height_patch=\"{prop.apply_height_patch}\"/>")
                        
        write_campaign_properties(xml_file, prop)
                        
        write_object_transform(xml_file, prop.object_transform)
        
        xml_file.write("\n\t\t</entity>")
        
        
    def write_vfx(xml_file, vfx):
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
        
        xml_file.write(f"\n\t\t\t<ECVFX vfx=\"{vfx.vfx_name}\" autoplay=\"true\" scale=\"1\" instance_name=\"\"/>")
        
        write_campaign_properties(xml_file, vfx)
                        
        write_object_transform(xml_file, vfx.object_transform)
        
        xml_file.write("\n\t\t</entity>")
    
    
    
    
    def write_light_probe(xml_file, light_probe):
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
        
        xml_file.write(f"\n\t\t\t<ECLightProbe/>")
        
        write_object_transform(xml_file, light_probe.object_transform)
        
        xml_file.write(f"\n\t\t\t<ECDoubleSphere radius=\"{light_probe.radius}\"/>")
          
        xml_file.write("\n\t\t</entity>")
    

    
    
    
    def write_point_light(xml_file, point_light):
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
        
        xml_file.write(f"\n\t\t\t<ECPointLight colour=\"{int(point_light.r*255)} {int(point_light.g*255)} {int(point_light.b*255)} 255\" colour_scale=\"{point_light.color_scale}\" radius=\"{point_light.radius}\" animation_type=\"{point_light.anim_type}\" animation_speed_scale=\"{point_light.anim_scale1} {point_light.anim_scale2}\" colour_min=\"{point_light.color_min}\" random_offset=\"{point_light.rand_offset}\" falloff_type=\"{point_light.falloff_type}\" for_light_probes_only=\"{point_light.light_probes_only}\"/>")

        write_campaign_properties(xml_file, point_light)
        
        write_object_transform(xml_file, point_light.object_transform)
  
        xml_file.write("\n\t\t</entity>")
    
    
    
    
    def write_polymesh(xml_file, polymesh):
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
                        
        xml_file.write(f"\n\t\t\t<ECPolygonMesh material=\"{polymesh.material}\" affects_mesh_optimization=\"false\"/>")

        write_campaign_properties(xml_file, polymesh)
        
        write_object_transform(xml_file, polymesh.object_transform)
        
        xml_file.write("\n\t\t\t<ECPolyline>")
        xml_file.write("\n\t\t\t\t<polyline closed=\"true\">")
        for v in polymesh.vertices:
            xml_file.write(f"\n\t\t\t\t\t<point x=\"{v[0]}\" y=\"{v[2]}\"/>")
        xml_file.write("\n\t\t\t\t</polyline>")
        xml_file.write("\n\t\t\t</ECPolyline>")
        
        xml_file.write("\n\t\t</entity>")
    
    
    
    
    def write_sound_emitter(xml_file, sound_emitter):
        xml_file.write("\n\t\t<entity id=\"" + "1" + ''.join(random.choice("01234567890abcdef") for _ in range(14)) + "\">")
                        
        xml_file.write(f"\n\t\t\t<ECSoundMarker key=\"{sound_emitter.sound_name}\" />")

        write_object_transform(xml_file, sound_emitter.object_transform)
        
        write_campaign_properties(xml_file, sound_emitter)
        
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

        write_object_transform(xml_file, composite_scene.object_transform)
        
        write_campaign_properties(xml_file, composite_scene)
        
        xml_file.write("\n\t\t</entity>")
    
    
    
    
    
    #In Terry you can set an object to have a certain culture mask (or season mask)
    #But in the global_props.bin... well I don't know how it works for 3k exactly
    #But in WH3, each object was like split apart by it's culture mask and stored seperately
    #So this tries to undo that, makes it much cleaner looking inside Terry
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

        fastbin0 = binary_file.read(8).decode('UTF-8') #"FASTBIN0"
        assert fastbin0 == "FASTBIN0", f"{fastbin0} doesn't say FASTBIN0"
        
        bin_version = struct.unpack("<H", binary_file.read(2))[0]
        assert bin_version == 35, f"{bin_version} is the wrong Fastbin version, dummy"
        
        
        #Enums (building_level/time_of_day)
        binary_file.read(2)
        binary_file.read(4) #some float
        num_enum_types = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_enum_types):
            binary_file.read(2) #version
            enum_type_name_length = struct.unpack("<H", binary_file.read(2))[0]
            enum_type_name = binary_file.read(enum_type_name_length).decode('UTF-8')
            
            num_enums = struct.unpack("<L", binary_file.read(4))[0]
            for _ in range(num_enums):
                enum_name_length = struct.unpack("<H", binary_file.read(2))[0]
                enum_name = binary_file.read(enum_name_length).decode('UTF-8')
        
        #Seasons
        binary_file.read(2)
        num_seasons = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_seasons):
            season_name_length = struct.unpack("<H", binary_file.read(2))[0]
            season_name = binary_file.read(season_name_length).decode('UTF-8')
        
        
        #Unknown/Irrelevent
        binary_file.read(47)
        
        
        #BMD
        binary_file.read(2)
        num_bmds = struct.unpack("<L", binary_file.read(4))[0]
        root_bmds = []
        for _ in range(num_bmds):
            version = struct.unpack("<H", binary_file.read(2))[0]
            
            bmd_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bmd_name = binary_file.read(bmd_name_length).decode('UTF-8')
            
            binary_file.read(64) #stuff we don't care about
            
            binary_file.read(4) #season mask, perhaps
            
            culture_mask = struct.unpack("<l", binary_file.read(4))[0] #half sized culture mask? maybe pdlc mask?
            
            region_name_length = struct.unpack("<H", binary_file.read(2))[0]
            region_name = binary_file.read(region_name_length).decode('UTF-8')
            
            binary_file.read(1) #dunno what this is, null-terminated string??
             
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            binary_file.read(28) #more stuff we dont care about
            
            root_bmds.append((region_name, bmd_name, culture_mask))
            
            
        root_bmds_sorted = sorted(root_bmds, key=lambda x: x[0])
        
        grouped_root_bmds = []
        for key, group in groupby(root_bmds_sorted, key=lambda x: x[0]):
            grouped_items = [(item[1], item[2]) for item in group]
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
                list_file.write("\n\t\t\t\t<ECLayerFile/>")
                list_file.write("\n\t\t\t\t<ECLayer/>")
                list_file.write("\n\t\t\t\t<ECLayerExport export=\"true\" export_as_separate_file_if_not_meta_tagged=\"false\" buildings_have_linked_destruction=\"false\"/>")
                list_file.write("\n\t\t\t</entity>")
        
        
    

    def process_bmd(entity_name, culture_mask):
        region_name = entity_name.split(".")[1]
            
        entity_offset = entity_offsets[entity_name]
        binary_file.seek(beginning_offset + entity_offset)
                
        fastbin0 = binary_file.read(8).decode('UTF-8') #"FASTBIN0"
        assert fastbin0 == "FASTBIN0", f"{fastbin0} doesn't say FASTBIN0"
        
        bin_version = struct.unpack("<H", binary_file.read(2))[0]
        assert bin_version == 35, f"{bin_version} is the wrong Fastbin version, dummy"
        
        #Enums (building_level/time_of_day)
        binary_file.read(2)
        binary_file.read(4) #some float
        num_enum_types = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_enum_types):
            binary_file.read(2) #version
            enum_type_name_length = struct.unpack("<H", binary_file.read(2))[0]
            enum_type_name = binary_file.read(enum_type_name_length).decode('UTF-8')
            
            num_enums = struct.unpack("<L", binary_file.read(4))[0]
            for _ in range(num_enums):
                enum_name_length = struct.unpack("<H", binary_file.read(2))[0]
                enum_name = binary_file.read(enum_name_length).decode('UTF-8')
        
        #Seasons
        binary_file.read(2)
        num_seasons = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_seasons):
            season_name_length = struct.unpack("<H", binary_file.read(2))[0]
            season_name = binary_file.read(season_name_length).decode('UTF-8')
        
        #Unknown/Irrelevent
        binary_file.read(47)
        
        
        
        compiled_bmd = CompiledBMDObject(region_name)
        
        
        
        #BMD section, some recursion in here
        binary_file.read(2)
        num_bmds = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_bmds):
            version = struct.unpack("<H", binary_file.read(2))[0]
            
            bmd_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bmd_name = binary_file.read(bmd_name_length).decode('UTF-8')
            
            binary_file.read(64) #stuff we don't care about
            
            binary_file.read(4) #season mask, perhaps
            
            culture_mask__ = struct.unpack("<l", binary_file.read(4))[0] #half sized culture mask? maybe pdlc mask?
            
            #Recursion here
            r = binary_file.tell()
            output = process_bmd(bmd_name, culture_mask__)
            compiled_bmd.add(output)
            binary_file.seek(r)
            
            region_name_length = struct.unpack("<H", binary_file.read(2))[0]
            region_name = binary_file.read(region_name_length).decode('UTF-8')
            
            binary_file.read(1) #dunno what this is, null-termainted string??
             
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            binary_file.read(28) #more stuff we dont care about
            
            
            
        #Unknown stuff
        binary_file.read(14)
        binary_file.read(14)
        
        
        
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
            version = struct.unpack("<H", binary_file.read(2))[0]
            
            index = struct.unpack("<L", binary_file.read(4))[0]
            path = prop_types[index]
            
            
            #Unknown stuff
            binary_file.read(18) 
            
            
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

            #Booleans, really not sure about these for 3K
            is_decal = struct.unpack("<B", binary_file.read(1))[0] == 1
            logical_decal = struct.unpack("<B", binary_file.read(1))[0] == 1
            is_fauna = struct.unpack("<B", binary_file.read(1))[0] == 1                
            visible_inside_snow_region = struct.unpack("<B", binary_file.read(1))[0] == 1
            visible_outside_snow_region = struct.unpack("<B", binary_file.read(1))[0] == 1
            visible_inside_destruction_region = struct.unpack("<B", binary_file.read(1))[0] == 1
            visible_outside_destruction_region = struct.unpack("<B", binary_file.read(1))[0] == 1
            animated = struct.unpack("<B", binary_file.read(1))[0] == 1
            
            decal_parallax_scale = struct.unpack("<f", binary_file.read(4))[0]
            decal_tiling = struct.unpack("<f", binary_file.read(4))[0]
            decal_override_gbuffer_normal = struct.unpack("<B", binary_file.read(1))[0] == 1
            
            
            flags_version = struct.unpack("<H", binary_file.read(2))[0]
            binary_file.read(1)
            binary_file.read(1) #"active"?
            
            binary_file.read(3)#three unknown booleans?
            
            binary_file.read(4) #possibly bit-wise seasons mask?
            
            visible_in_seen_shroud = struct.unpack("<B", binary_file.read(1))[0] == 1
            visible_in_unseen_shroud = struct.unpack("<B", binary_file.read(1))[0] == 1
                
            visible_in_shroud = struct.unpack("<B", binary_file.read(1))[0] == 1
            apply_to_terrain = struct.unpack("<B", binary_file.read(1))[0] == 0
            apply_to_objects = struct.unpack("<B", binary_file.read(1))[0] == 1
                            
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
                        
            #unknowns
            binary_file.read(4)
            
            casts_shadow = struct.unpack("<B", binary_file.read(1))[0] == 1
            has_height_patch = struct.unpack("<B", binary_file.read(1))[0] == 1
            
            binary_file.read(4) #tint color (RGBA?)
            binary_file.read(4) #faction color (RGBA?)
            binary_file.read(1) #alpha
            
            binary_file.read(8) #unknown
            
            apply_height_patch = struct.unpack("<B", binary_file.read(1))[0] == 1
            
            
            
            object_trans = BMDObjectTransform(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot, x_scale, y_scale, z_scale)
            
            bmd_prop = BMDProp(path, object_trans, 0, is_decal, apply_to_terrain, apply_to_objects, has_height_patch, apply_height_patch, visible_inside_snow_region, visible_outside_snow_region, visible_inside_destruction_region, visible_outside_destruction_region, visible_in_unseen_shroud, visible_in_seen_shroud, False)
            
            compiled_bmd.prop_list.append(bmd_prop)
        
        
            
        
        
        #VFX
        binary_file.read(2)
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
            
            
            emission_rate = struct.unpack("<f", binary_file.read(4))[0]
            instance_name_length = struct.unpack("<H", binary_file.read(2))[0]
            instance_name = binary_file.read(instance_name_length).decode('UTF-8')
            
            
            flags_version = struct.unpack("<H", binary_file.read(2))[0]
            binary_file.read(1)
            binary_file.read(1) #"active"?
            
            binary_file.read(3)#three unknown booleans?
            
            binary_file.read(4) #possibly bit-wise seasons mask?
            
            #One of these can't be here?
            visible_in_seen_shroud = struct.unpack("<B", binary_file.read(1))[0] == 1
            #visible_in_unseen_shroud = struct.unpack("<B", binary_file.read(1))[0] == 1
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
                
            autoplay = struct.unpack("<B", binary_file.read(1))[0] == 1
            
            binary_file.read(27)
            
            
            object_trans = BMDObjectTransform(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot, x_scale, y_scale, z_scale)
            
            bmd_vfx = BMDVFX(vfx_name, object_trans, 0, True, True, True, True, False, True, False)
            
            compiled_bmd.vfx_list.append(bmd_vfx)
        
        
        
        #Unknown stuff, also probably unused
        binary_file.read(26)
        
        
        
        #Light probe
        binary_file.read(2)
        num_light_probes = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_light_probes):
            version = struct.unpack("<H", binary_file.read(2))[0]
            
            x_pos = struct.unpack("<f", binary_file.read(4))[0]
            y_pos = struct.unpack("<f", binary_file.read(4))[0]
            z_pos = struct.unpack("<f", binary_file.read(4))[0]
            radius = struct.unpack("<f", binary_file.read(4))[0]
            
            binary_file.read(1)
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            binary_file.read(18) #unknown stuff
            
            
            object_trans = BMDObjectTransform(x_pos, y_pos, z_pos)
            
            bmd_light_probe = BMDLightProbe(object_trans, radius)
            
            compiled_bmd.light_probe_list.append(bmd_light_probe)
            
        
        
        # Terrain hole triangles
        binary_file.read(2)
        num_terrain_holes = struct.unpack("<L", binary_file.read(4))[0]
        assert num_terrain_holes == 0 #It's 0 for 3K, hooray
        
        
        
        #Point Light
        binary_file.read(2)
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
        
            binary_file.read(1) #zero
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            light_probes_only = struct.unpack("<B", binary_file.read(1))[0] == 1
            
            #unknown
            binary_file.read(34)
            
            
            object_trans = BMDObjectTransform(x, y, z)
            
            bmd_point_light = BMDPointLight(object_trans, 0, r, g, b, anim_type, anim_scale1, anim_scale2, color_min, rand_offset, falloff_type, light_probes_only, color_scale, radius)
            
            compiled_bmd.point_light_list.append(bmd_point_light)
            

            
        #BuildingProjectileEmitter (unused in campaign)
        binary_file.read(6)
        
        
        #Playable area
        binary_file.read(2)
        binary_file.read(21)
        
        
        #Polymesh
        binary_file.read(2)
        num_polymesh = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_polymesh):
            version = struct.unpack("<H", binary_file.read(2))[0]
            
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
            
            #Water plane material overrides if necessary
            #if (vanilla_campaign_name + "_campaign_blood_river.xml.material" in material):
            #    material = "materials/environment/campaign_sea/" + campaign_name + "_campaign_blood_river.xml.material"
            
            bhm_name_length = struct.unpack("<H", binary_file.read(2))[0]
            bhm_name = binary_file.read(bhm_name_length).decode('UTF-8')
            
            binary_file.read(18)#more stuff
            binary_file.read(4)#some int
            
            object_trans = BMDObjectTransform(0,vertices[0][1],0)
            
            bmd_polymesh = BMDPolyMesh(object_trans, 0, material, vertices)
            
            compiled_bmd.polymesh_list.append(bmd_polymesh)



        #unknown
        binary_file.read(6)
            
            
        
        #Spot Light
        binary_file.read(2)
        num_spot_lights = struct.unpack("<L", binary_file.read(4))[0]
        assert num_spot_lights == 0 #It's 0 for 3K, hooray




        #Sound emitters, sfx
        binary_file.read(2)
        num_sfxs = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_sfxs):
            version = struct.unpack("<H", binary_file.read(2))[0]
            
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
                
            binary_file.read(26)
            
            
            object_trans = BMDObjectTransform(coords[0][0], coords[0][1], coords[0][2])
            
            bmd_sound_emitter = BMDSoundEmitter(sound_name, object_trans, 0, SST_type, coords, radius)
            
            compiled_bmd.sound_emitter_list.append(bmd_sound_emitter)
            

    
        
        #composite scenes, csc
        binary_file.read(2)
        num_cscs = struct.unpack("<L", binary_file.read(4))[0]
        for _ in range(num_cscs):
            version = struct.unpack("<H", binary_file.read(2))[0]
            
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
            
            binary_file.read(35)
            
                        
            object_trans = BMDObjectTransform(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot, x_scale, y_scale, z_scale)
            
            bmd_composite_scene = BMDCompositeScene(csc_name, object_trans, 0, True, True, True, True, False, True, False)
            
            compiled_bmd.composite_scene_list.append(bmd_composite_scene)
            
            
        #Don't forget to return the bmd object!
        return compiled_bmd
            
                

    
    #Start
    process_root_bmd()
        