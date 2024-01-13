# Total-War-Modding-Scripts
A collection of python scripts I write for my Total War Modding.

Some of these will be contained in a .blend file, opened in Blender.

I'll also add some 010 Editor templates I've created.


## Prefab bmd file to Terry layer file.py

Only tested with Warhammer 3 .bmd,

Input a *campaign* prefab bmd, it will output an xml file that you can open in Terry


## global_props bin file to Terry layers.py

Only tested with Warhammer 3.
Input a campaign's global_props.bin, it will output a bunch of xml Terry layers, one for each region in the campaign map
Put the xml layers in your Terry project's folder, and then copy+paste the stuff in terry_file_update.txt into your project's .terry file.
This might be missing a few things, but whatever is missing is very hard to notice when in-game.


## battle catchment map to png.py 

Use on the three blm_catchments: blm_catchment_override.compressed_map, blm_catchment_override_settlement_standard.compressed_map, blm_catchment_override_settlement_unfortified.compressed_map

Transforming the png's back into their .compressed_map state can be done with BOB.

You really shouldn't do this though to edit which battle maps are used for each location, instead use Frodo's Map Replacer Framework.


## global props bin.bt

A template for use in 010 editor.


## prefab_bmd.bt

A template for use in 010 editor. Again, this has only been tested with campaign prefabs, like settlements, Battle prebads might have a few things more.


## S2TW_animation_import_export.blend 

For Shogun 2 Total War

Imports/exports animations, does not read/display models!


## merge_wwise_dialogue_events_v1.py

Where to even begin explaining what this does....
To use it, you need to have created a .bnk file using the wwise program. If you only used that .bnk in a mod .pack, it would effectively overwrite all of the vanilla voicelines.
But, if you run this script, you can then add a bit of stuff from a vanilla .bnk file, and avoid overwriting stuff. The end result is new voicelines.

This script merges-in the decision trees of the (relevent) vanilla Dialogue Events. It merges them into the existing decision trees of your custom .bnk file.
