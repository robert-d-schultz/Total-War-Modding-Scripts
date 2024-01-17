import struct
import os

#If you don't already know what this script does, then reading the below explainations won't help you at all. Go learn some Wwise.

#Go to the bottom, that's where all the interesting stuff is

# Here are the DialogueEvents it will try to merge, if it can't find one in your custom_bnk, then it will just skip
# The string is the name of the vanilla bnk which contains the vanilla version of the DialogueEvent, you should have those ready in the vanilla_bnk_path
dialogue_event_to_vanilla_bnk = {
    50994472   : "battle_vo_orders__core.bnk", #battle_vo_order_guard_on
    165328208  : "battle_vo_orders__core.bnk", #battle_vo_order_halt
    499731516  : "battle_vo_orders__core.bnk", #battle_vo_order_climb
    855899397  : "battle_vo_orders__core.bnk", #battle_vo_order_withdraw_tactical
    887060879  : "battle_vo_orders__core.bnk", #battle_vo_order_pick_up_engine
    981642494  : "battle_vo_orders__core.bnk", #battle_vo_order_move_alternative
    1084519251 : "battle_vo_orders__core.bnk", #battle_vo_order_withdraw
    1101668428 : "battle_vo_orders__core.bnk", #battle_vo_order_move_siege_tower
    1103581321 : "battle_vo_orders__core.bnk", #battle_vo_order_attack
    1162817219 : "battle_vo_orders__core.bnk", #battle_vo_order_skirmish_off
    1265769398 : "battle_vo_orders__core.bnk", #battle_vo_order_generic_response, there's some extra behind-the-scenes game logic that makes this one play if there isn't anything else
    1410290450 : "battle_vo_orders__core.bnk", #battle_vo_order_fire_at_will_on
    1810228062 : "battle_vo_orders__core.bnk", #battle_vo_order_move
    1847579016 : "battle_vo_orders__core.bnk", #battle_vo_order_fire_at_will_off
    2137941389 : "battle_vo_orders__core.bnk", #battle_vo_order_man_siege_tower
    2179569039 : "battle_vo_orders__core.bnk", #battle_vo_order_move_ram
    2497778159 : "battle_vo_orders__core.bnk", #battle_vo_order_skirmish_on
    2524550281 : "battle_vo_orders__core.bnk", #battle_vo_order_melee_off
    2748360893 : "battle_vo_orders__core.bnk", #battle_vo_order_melee_on
    3907770630 : "battle_vo_orders__core.bnk", #battle_vo_order_guard_off
    4023574001 : "battle_vo_orders__core.bnk", #battle_vo_order_select
    
    36016233   : "battle_vo_orders__core.bnk", #battle_vo_order_bat_mode_survival
    101140468  : "battle_vo_orders__core.bnk", #battle_vo_order_bat_mode_capture_pos
    3962846800 : "battle_vo_orders__core.bnk", #battle_vo_order_bat_mode_capture_neg
    3324576115 : "battle_vo_orders__core.bnk", #battle_vo_order_bat_speeches
    
    1513450116 : "battle_vo_orders__core.bnk", #battle_vo_order_short_order
    177391233  : "battle_vo_orders__core.bnk", #battle_vo_order_special_ability
    2624153851 : "battle_vo_orders__core.bnk", #battle_vo_order_flying_charge
    1102189810 : "battle_vo_orders__core.bnk", #battle_vo_order_change_ammo
    2745514101 : "battle_vo_orders__core.bnk", #battle_vo_order_attack_alternative
    486738506  : "battle_vo_orders__core.bnk", #battle_vo_order_battle_continue_battle
    3044335360 : "battle_vo_orders__core.bnk", #battle_vo_order_battle_quit_battle
    1586929109 : "battle_vo_orders__core.bnk", #battle_vo_order_change_formation
    1809912120 : "battle_vo_orders__core.bnk", #battle_vo_order_formation_lock
    3594811005 : "battle_vo_orders__core.bnk", #battle_vo_order_formation_unlock
    2207577683 : "battle_vo_orders__core.bnk", #battle_vo_order_group_created
    2275058049 : "battle_vo_orders__core.bnk", #battle_vo_order_group_disbanded
    
    
    3969841041 : "campaign_vo__core.bnk", #campaign_vo_selected
    3722163706 : "campaign_vo__core.bnk", #campaign_vo_selected_short
    2301359050 : "campaign_vo__core.bnk", #campaign_vo_selected_first_time
    3052514737 : "campaign_vo__core.bnk", #campaign_vo_selected_neutral
    494034353 : "campaign_vo__core.bnk", #campaign_vo_selected_allied
    1734595768 : "campaign_vo__core.bnk", #campaign_vo_selected_fail
    
    748798295 : "campaign_vo__core.bnk", #campaign_vo_yes
    3556834931 : "campaign_vo__core.bnk", #campaign_vo_yes_short_aggressive
    874013640 : "campaign_vo__core.bnk", #campaign_vo_yes_short
    
    338520419 : "campaign_vo__core.bnk", #campaign_vo_no
    3239914076 : "campaign_vo__core.bnk", #campaign_vo_no_short
    
    2302243677 : "campaign_vo__core.bnk", #campaign_vo_move
    1232162677 : "campaign_vo__core.bnk", #campaign_vo_move_garrisoning
    1281394843 : "campaign_vo__core.bnk", #campaign_vo_move_next_turn
    2334862434 : "campaign_vo__core.bnk", #campaign_vo_attack
    1030810822 : "campaign_vo__core.bnk", #campaign_vo_ship_dock
    793344275 : "campaign_vo__core.bnk", #campaign_vo_retreat
    
    87890740 : "campaign_vo__core.bnk", #campaign_vo_stance_default
    3579612449 : "campaign_vo__core.bnk", #campaign_vo_stance_set_camp
    3204417870 : "campaign_vo__core.bnk", #campaign_vo_stance_march
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_set_camp_raiding
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_raise_dead
    2763670597 : "campaign_vo__core.bnk", #campaign_vo_stance_ambush
    2416584567 : "campaign_vo__core.bnk", #campaign_vo_stance_muster
    2471223478 : "campaign_vo__core.bnk", #campaign_vo_stance_double_time
    1691131338 : "campaign_vo__core.bnk", #campaign_vo_stance_channeling
    2038381937 : "campaign_vo__core.bnk", #campaign_vo_stance_land_raid
    1181966579 : "campaign_vo__core.bnk", #campaign_vo_stance_patrol
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_tunneling
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_astromancy
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_stalking
    789979364 : "campaign_vo__core.bnk", #campaign_vo_stance_settle
    
    1703780730 : "campaign_vo__core.bnk", #campaign_vo_created
    1347700275 : "campaign_vo__core.bnk", #campaign_vo_new_commander
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_recruit_units
    
    1102837942 : "campaign_vo__core.bnk", #campaign_vo_post_battle_victory
    521824557 : "campaign_vo__core.bnk", #campaign_vo_post_battle_defeat
    
    894625206 : "campaign_vo__core.bnk", #campaign_vo_agent_action_success
    2228229582 : "campaign_vo__core.bnk", #campaign_vo_agent_action_failed
    
    3510571822 : "campaign_vo__core.bnk", #campaign_vo_diplomacy_positive
    3540315276 : "campaign_vo__core.bnk", #campaign_vo_diplomacy_selected
    1588578862 : "campaign_vo__core.bnk", #campaign_vo_diplomacy_negative
    
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_mounted_creature
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_level_up
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_special_ability
    
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_skill_weapon_tree_response
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_tech_tree
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_skill_weapon_tree
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_disbanded_neg
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_disbanded_pos
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_disband
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_tech_tree_response
    
    
    #0000000000 : "campaign_vo_conversational__core.bnk", #campaign_vo_cs_post_battle_captives_execute
    #0000000000 : "campaign_vo_conversational__core.bnk", #campaign_vo_cs_post_battle_captives_release
    #0000000000 : "campaign_vo_conversational__core.bnk", #campaign_vo_cs_post_battle_captives_enslave
    
    
    3643531796 : "frontend_vo__core.bnk", #frontend_vo_character_select
}


def compute_wwise_hash(name):
    lower = name.lower().strip()
    bytes_data = lower.encode('utf-8')

    hash_value = 2166136261
    for byte_index in range(len(bytes_data)):
        name_byte = bytes_data[byte_index]
        hash_value = (hash_value * 16777619) & 0xFFFFFFFF
        hash_value = hash_value ^ name_byte

    return hash_value


#This tries to update the decision trees of each DialogueEvent within input_bnk
   #The update involves taking the decision trees from the same DialogueEvent in a vanilla bnk (above, the dialogue_event_to_vanilla_bnk table)
   #And merging the decisions trees together
def merge_vanilla_decision_trees_into_bnk(input_bnk_path, output_bnk_path):
    print("Attempting to merge vanilla decision trees into " + input_bnk_path)
    with open(output_bnk_path, "wb") as output_file:
        with open(input_bnk_path, "rb") as custom_file:
            
            #Reading custom file
            
            #Header
            BKHD = custom_file.read(4).decode('UTF-8')
            assert BKHD == "BKHD", "Invalid header in " + input_bnk_path
            BKHD_e = bytes(BKHD,"UTF-8")
            output_file.write(struct.pack("<%ds" % len(BKHD), BKHD_e))
        
            chunk_size  = struct.unpack("<L", custom_file.read(4))[0]
            output_file.write(struct.pack("<L",chunk_size))
            
            version_thingy = struct.unpack("<L", custom_file.read(4))[0]
            if version_thingy != 2147483784:
                print("Corrected version in header of " + input_bnk_path)
                version_thingy = 2147483784
            output_file.write(struct.pack("<L",version_thingy))
            
            
            bank_id = struct.unpack("<L", custom_file.read(4))[0]
            if bank_id != compute_wwise_hash(os.path.splitext(os.path.basename(output_bnk_path))[0]):
                print("Corrected bank id in header of " + input_bnk_path)
                bank_id = compute_wwise_hash(os.path.splitext(os.path.basename(output_bnk_path))[0])
            output_file.write(struct.pack("<L",bank_id))
            
            chunk = custom_file.read(8)
            output_file.write(chunk)
            
            project_id = struct.unpack("<L", custom_file.read(4))[0]
            if project_id != 2361:
                print("Corrected project id in header of " + input_bnk_path)
                project_id = 2361
            output_file.write(struct.pack("<L", project_id))
            
            chunk = custom_file.read(4)
            output_file.write(chunk)
            
            HIRC = custom_file.read(4).decode('UTF-8')
            assert HIRC == "HIRC", "Invalid header in " + input_bnk_path
            HIRC_e = bytes(HIRC,"UTF-8")
            output_file.write(struct.pack("<%ds" % len(HIRC), HIRC_e))
            
            hirc_chunk_size_offset = output_file.tell()
            chunk_size = struct.unpack("<L", custom_file.read(4))[0] #Needs updating later
            output_file.write(struct.pack("<L",chunk_size))
            
            num_items = struct.unpack("<L", custom_file.read(4))[0]
            output_file.write(struct.pack("<L",num_items))
            
            #All the HIRC items
            for _ in range(num_items):
                hirc_type = struct.unpack("<b", custom_file.read(1))[0]
                output_file.write(struct.pack("<b",hirc_type))
                
                section_size_offset = output_file.tell()
                section_size = struct.unpack("<L", custom_file.read(4))[0] #Needs updating later
                output_file.write(struct.pack("<L",section_size))
                
                id = struct.unpack("<L", custom_file.read(4))[0]
                output_file.write(struct.pack("<L",id))
                
                #If we find the dialogue event in question...
                if (hirc_type == 15):
                    print("Found DialogueEvent " + str(id))
                    if(id in dialogue_event_to_vanilla_bnk):
                        dialogue_event_id = id
                        vanilla_bnk_filename = dialogue_event_to_vanilla_bnk[id]
                        
                        chunk = custom_file.read(1)
                        output_file.write(chunk)
                        
                        custom_tree_depth = struct.unpack("<L", custom_file.read(4))[0]
                        output_file.write(struct.pack("<L",custom_tree_depth))
                        
                        custom_arguments = []
                        for _ in range(custom_tree_depth):
                            arg =  struct.unpack("<L", custom_file.read(4))[0]
                            custom_arguments.append(arg)
                            output_file.write(struct.pack("<L",arg))
                        
                        for _ in range(custom_tree_depth):
                            chunk = custom_file.read(1)
                            output_file.write(chunk)

                        tree_data_size_offset = output_file.tell()
                        tree_data_size = struct.unpack("<L", custom_file.read(4))[0] #Needs updating later
                        output_file.write(struct.pack("<L",tree_data_size))
                        
                        chunk = custom_file.read(1) #This has to be padding or something
                        output_file.write(chunk)
                        
                        #The custom bnk's decision tree
                        assert tree_data_size % 12 == 0, "Decision tree of DialogueEvent " + str(dialogue_event_id) + " is structured wrong"
                        
                        custom_decision_tree_nodes = []
                        for j in range(int(tree_data_size/12)):
                            key = struct.unpack("<L", custom_file.read(4))[0]
                            children_uIdx = struct.unpack("<H", custom_file.read(2))[0]
                            children_uCount = struct.unpack("<H", custom_file.read(2))[0]
                            uWeight = struct.unpack("<H", custom_file.read(2))[0]
                            uProbability = struct.unpack("<H", custom_file.read(2))[0]
                            custom_decision_tree_nodes.append([key, children_uIdx, children_uCount, uWeight, uProbability])
                        
                         
                        #Reading vanilla bnk, return the decision tree of the dialogue event we care about
                        vanilla_decision_tree_nodes = read_and_return_decision_tree(vanilla_bnk_path + vanilla_bnk_filename, dialogue_event_id, custom_tree_depth, custom_arguments)                    
                        
                        
                        #Merge the vanilla and custom decision trees
                        final_tree = merge_decision_trees(custom_decision_tree_nodes, vanilla_decision_tree_nodes, custom_tree_depth)

                        #And finally, write tree
                        def write_node(node):
                            output_file.write(struct.pack("<L",node["key"]))
                            if "audioNodeId" in node:
                                output_file.write(struct.pack("<L",node["audioNodeId"]))
                            else:
                                output_file.write(struct.pack("<H",node["uIdx"]))
                                output_file.write(struct.pack("<H",node["uCount"]))                            
                            output_file.write(struct.pack("<H",node["uWeight"]))
                            output_file.write(struct.pack("<H",node["uProbability"]))
                        
                        for node in final_tree:
                            write_node(node)
                        
                        #Go back and update TreeDataSize
                        bookmark_offset = output_file.tell()
                        tree_data_size = output_file.tell() - tree_data_size_offset - 5 #5? what? its got to be that padding....
                        output_file.seek(tree_data_size_offset)
                        output_file.write(struct.pack("<L",tree_data_size))
                        output_file.seek(bookmark_offset)

                        #Finish off the dialogue event with this
                        chunk = custom_file.read(2)
                        output_file.write(chunk)
                        
                        #Go back and update the DialogueEvent's SectionSize
                        bookmark_offset = output_file.tell()
                        section_size = output_file.tell() - section_size_offset - 4
                        output_file.seek(section_size_offset)
                        output_file.write(struct.pack("<L",section_size))
                        output_file.seek(bookmark_offset)
                        
                        print("   Successful merge?")
                        
                    else:
                        raise Exception("DialogueEvent " + str(id) + " has no entry in the script's dialogue_event_to_vanilla_bnk table")
                        #Really shouldn't skip past this, so raise error
                        #chunk = custom_file.read(section_size - 4)
                        #output_file.write(chunk)
                #If it's not the event we are looking for in the custom bnk, then skip ahead to the next HIRC item
                else:
                    print("Skipping " + str(id) + " since it's not a DialogueEvent")
                    chunk = custom_file.read(section_size - 4)
                    output_file.write(chunk)
                    
            
            #And finally, go back and update the HIRC chunk size
            hirc_chunk_size = output_file.tell() - hirc_chunk_size_offset - 4
            output_file.seek(hirc_chunk_size_offset)
            output_file.write(struct.pack("<L",hirc_chunk_size))
        
        
#Look through bnk_path, find a dialogue_event, check it against expected_tree_depth and expected_arguments, and then return it
def read_and_return_decision_tree(bnk_path, dialogue_event_id, expected_tree_depth=None, expected_arguments=None):
    with open(bnk_path, "rb") as file:
        
        #Header
        BKHD = file.read(4).decode('UTF-8')
        assert BKHD == "BKHD", "Invalid header in " + bnk_path
        chunk_size  = struct.unpack("<L", file.read(4))[0]
        file.read(chunk_size)
        HIRC = file.read(4).decode('UTF-8')
        assert HIRC == "HIRC", "Invalid header in " + bnk_path
        chunk_size = struct.unpack("<L", file.read(4))[0]
        num_items = struct.unpack("<L", file.read(4))[0]
        
        #All the HIRC items
        decision_tree_nodes = []
        for _ in range(num_items):
            hirc_type = struct.unpack("<b", file.read(1))[0]
            section_size = struct.unpack("<L", file.read(4))[0]
            id = struct.unpack("<L", file.read(4))[0]
            
            
            #If we find the dialogue event in question...
            if (hirc_type == 15) and (id == dialogue_event_id):
                
                file.read(1)
                tree_depth = struct.unpack("<L", file.read(4))[0]
                if expected_tree_depth is not None:
                    assert tree_depth == expected_tree_depth, "Tree depths do not match for DialogueEvent " + str(dialogue_event_id)
                
                arguments = []
                for _ in range(tree_depth):
                    arg =  struct.unpack("<L", file.read(4))[0]
                    arguments.append(arg)
                
                if expected_arguments is not None:
                    assert arguments == expected_arguments, "Arguments do not match for DialogueEvent " + str(dialogue_event_id)
        
        
                for _ in range(tree_depth):
                    file.read(1)
                    
                tree_data_size = struct.unpack("<L", file.read(4))[0]
                file.read(1)
                
                #The bnk's decision tree
                assert tree_data_size % 12 == 0, "Decision tree of DialogueEvent " + str(dialogue_event_id) + " is structured wrong"
                
                for _ in range(int(tree_data_size/12)):
                    key = struct.unpack("<L", file.read(4))[0]
                    children_uIdx = struct.unpack("<H", file.read(2))[0]
                    children_uCount = struct.unpack("<H", file.read(2))[0]
                    uWeight = struct.unpack("<H", file.read(2))[0]
                    uProbability = struct.unpack("<H", file.read(2))[0]
                    decision_tree_nodes.append([key, children_uIdx, children_uCount, uWeight, uProbability])
                    
                #file.read(2)
                break #don't need to keep reading
                
            #Otherwise, skip ahead to the next HIRC itrm
            else:
                file.read(section_size - 4)
        
        return decision_tree_nodes

#Extra thing for an audio bus with no known name
def replacement_hack(replacements, bnk_path):
    if replacements != None:
        with open(bnk_path, 'rb') as file:
            content = file.read()

        # Assuming int32 is 4 bytes
        for a in replacements:
            old_bytes = struct.pack('<L', a[0])
            new_bytes = struct.pack('<L', a[1])

            # Replace all instances of old_value with new_value
            content = content.replace(old_bytes, new_bytes)

        with open(bnk_path, 'wb') as file:
            file.write(content)


#Merges dialogue event decision trees
   #Order is a little bit important, the decision_tree_nodes2 get "merged into" decision_tree_nodes1
   #So if there is ever a duplicate node, it will use decision_tree_nodes1's probabilities and weights
   #But those are almost always a default value, so not a real issue if you get it backwards
def merge_decision_trees(decision_tree_nodes1, decision_tree_nodes2, tree_depth):
    def parse_tree(node_list, depth, current_index=0):
        node = node_list[current_index]
        if depth == 0:
            foobar = struct.unpack('<L', b''.join(struct.pack('<H', value) for value in [node[1], node[2]]))[0]
            return {"key": node[0], "audioNodeId": foobar, "uWeight": node[3], "uProbability": node[4]}
                         
        #secondary checks, since a leaf can (rarely) occur before max depth
        if (node[1] > len(node_list) #Impossibly large amout of children
        or node[2] > len(node_list)  #Impossibly large index
        or node[1] < current_index):                   #Index goes "backwards", also impossible
            foobar = struct.unpack('<L', b''.join(struct.pack('<H', value) for value in [node[1], node[2]]))[0]
            return {"key": node[0], "audioNodeId": foobar, "uWeight": node[3], "uProbability": node[4]}
            
        children_index = node[1]
        children_count = node[2]
        
        result = {"key": node[0], "uWeight": node[3], "uProbability": node[4], "children": []}
        
        for i in range(children_count):
            # Recursively traverse each child
            child_node = parse_tree(node_list, depth - 1, children_index + i)
            result["children"].append(child_node)
        
        return result       

    
    #parse the custom tree into some structure
    parsed_tree1 = parse_tree(decision_tree_nodes1, tree_depth)

    
    #parse the vanilla tree into some structure
    parsed_tree2 = parse_tree(decision_tree_nodes2, tree_depth)
    
    
    #combine the two trees
    def combine_tree(node1, node2):
        children1 = node1.get("children", [])
        children2 = node2.get("children", [])

        combined_children = []
        combined_keys = set()

        # Iterate over children of both trees
        for child1 in children1:
            key1 = child1["key"]
            combined_keys.add(key1)
            matching_child2 = next((child2 for child2 in children2 if child2["key"] == key1), None)

            if matching_child2:
                # Recursively combine nodes with the same key
                combined_child = combine_tree(child1, matching_child2)
                combined_children.append(combined_child)
            else:
                # If key is not present in tree2, include the node from tree1
                combined_children.append(child1)

        # Include nodes from tree2 that do not have a matching key in tree1
        for child2 in children2:
            if child2["key"] not in combined_keys:
                combined_children.append(child2)

        if combined_children == []:
            return {
                "key": node1["key"],
                "audioNodeId": node1["key"],
                "uWeight": node1["uWeight"],
                "uProbability": node1["uProbability"],
            }
        else:
            return {
                "key": node1["key"],
                "uWeight": node1["uWeight"],
                "uProbability": node1["uProbability"],
                "children": combined_children
            }
            

    combined_parsed_tree = combine_tree(parsed_tree1, parsed_tree2)
    
    
    #Sort of the combined tree
    def sort_tree(node):
        if "audioNodeId" in node:
            # Leaf node, nothing to sort
            return node

        sorted_children = sorted(node.get("children", []), key=lambda x: x["key"])
        sorted_children = [sort_tree(child) for child in sorted_children]

        return {
            "key": node["key"],
            "uWeight": node["uWeight"],
            "uProbability": node["uProbability"],
            "children": sorted_children
        }

    sorted_combined_tree = sort_tree(combined_parsed_tree)
    
    
    #Assign indices to tree ("siblings-first-depth-second" traversal order)
    count = 0
    def assign_indices(node):
        nonlocal count

        #Assign index to current node if it doesn't have one (root node only, I think?)
        if "index" in node:
            pass #do nothing
        else:
            node["index"] = count 
            count+=1
        
        #Assign indices to children if they don't have one (they never should, I think?)
        if "children" in node:
            for child in node["children"]:
                if "index" in child:
                    raise Exception("Child somehow already had an index, huh?")
                else:
                    child["index"] = count 
                    count+=1
        
            #Then we can recurse into the children
            node["children"] = [assign_indices(child) for child in node["children"]]
            
        return node
                

    indexed_tree = assign_indices(sorted_combined_tree)
        
    
    #Each parent should then have a record of the index of their first child, and how many children
    def update_parents(node):
        if "children" in node:
            if "uIdx" in node:
                raise Exception("Node somehow already had a uIdx, huh?")
            else:
                node["uIdx"] = node["children"][0]["index"]
                
            if "uCount" in node:
                raise Exception("Node somehow already had a uCount, huh?")
            else:
                node["uCount"] = len(node["children"])
                
            #Then we can recurse into the children
            node["children"] = [update_parents(child) for child in node["children"]]
            
        else:
            pass #do nothing
        
        return node
            
            
    updated_tree = update_parents(sorted_combined_tree)
    
    
    #Linearize tree
    def linearize_tree(node):
        if "children" in node:
            children = node["children"]
            node_ = node
            node_.pop("children", None)
            output = [node_]
            for child in children:
                output.extend(linearize_tree(child))
                
            return output
        else:
            return [node]
    linearized_tree = linearize_tree(updated_tree)
    
    
    #Sort linearize tree by index
    sorted_linearized_tree = sorted(linearized_tree, key=lambda x: x["index"])
    
    return sorted_linearized_tree




#Look through bnk_path, return a list of the DialogueEvent ids contained within
def read_and_return_dialogue_event_ids(bnk_path):
    dialouge_event_ids = []
    with open(bnk_path, "rb") as file:
        #Header
        BKHD = file.read(4).decode('UTF-8')
        assert BKHD == "BKHD", "Invalid header in " + bnk_path
        chunk_size  = struct.unpack("<L", file.read(4))[0]
        file.read(chunk_size)
        HIRC = file.read(4).decode('UTF-8')
        assert HIRC == "HIRC", "Invalid header in " + bnk_path
        chunk_size = struct.unpack("<L", file.read(4))[0]
        num_items = struct.unpack("<L", file.read(4))[0]
        
        #All the HIRC items
        decision_tree_nodes = []
        for _ in range(num_items):
            hirc_type = struct.unpack("<b", file.read(1))[0]
            section_size = struct.unpack("<L", file.read(4))[0]
            id = struct.unpack("<L", file.read(4))[0]
            
            
            #If we find a dialogue event, add to list
            if (hirc_type == 15):
                dialouge_event_ids.append(id)
                
            #Skip ahead to next
            file.read(section_size - 4)
        
    return dialouge_event_ids


def return_dialogue_event_chunk(bnk_path, dialogue_event_id):
    with open(bnk_path, "rb") as file:
        #Header
        BKHD = file.read(4).decode('UTF-8')
        assert BKHD == "BKHD", "Invalid header in " + bnk_path
        chunk_size  = struct.unpack("<L", file.read(4))[0]
        file.read(chunk_size)
        HIRC = file.read(4).decode('UTF-8')
        assert HIRC == "HIRC", "Invalid header in " + bnk_path
        chunk_size = struct.unpack("<L", file.read(4))[0]
        num_items = struct.unpack("<L", file.read(4))[0]
        
        #All the HIRC items
        for _ in range(num_items):
            hirc_type = struct.unpack("<b", file.read(1))[0]
            section_size = struct.unpack("<L", file.read(4))[0]
            id = struct.unpack("<L", file.read(4))[0]
            
            #If we find a dialogue event, add to list
            if (hirc_type == 15) and (id == dialogue_event_id):
                file.seek(-9,1) #go back 9
                return file.read(section_size + 5)
                
            #Skip ahead to next
            file.read(section_size - 4)

#Merge a single dialogue event
def merge_dialogue_event(bnk_path1, bnk_path2, output_file, dialogue_event_id):
    with open(bnk_path1, "rb") as file1:
        #Header
        BKHD = file1.read(4).decode('UTF-8')
        assert BKHD == "BKHD", "Invalid header in " + bnk_path1
        chunk_size  = struct.unpack("<L", file1.read(4))[0]
        file1.read(chunk_size)
        HIRC = file1.read(4).decode('UTF-8')
        assert HIRC == "HIRC", "Invalid header in " + bnk_path1
        chunk_size = struct.unpack("<L", file1.read(4))[0]
        num_items = struct.unpack("<L", file1.read(4))[0]
        
        #All the HIRC items
        for _ in range(num_items):
            hirc_type = struct.unpack("<b", file1.read(1))[0]
            section_size = struct.unpack("<L", file1.read(4))[0]
            id = struct.unpack("<L", file1.read(4))[0]
            
            #If we find the dialogue event
            if (hirc_type == 15) and (id == dialogue_event_id):
                output_file.write(struct.pack("<b",hirc_type))
                
                section_size_offset = output_file.tell()
                output_file.write(struct.pack("<L",0)) #0 for now, update later
                
                output_file.write(struct.pack("<L",id))
                
                chunk = file1.read(1)
                output_file.write(chunk)
                
                tree_depth = struct.unpack("<L", file1.read(4))[0]
                output_file.write(struct.pack("<L",tree_depth))
                
                arguments = []
                for _ in range(tree_depth):
                    arg =  struct.unpack("<L", file1.read(4))[0]
                    arguments.append(arg)
                    output_file.write(struct.pack("<L",arg))
                
                for _ in range(tree_depth):
                    chunk = file1.read(1)
                    output_file.write(chunk)

                tree_data_size_offset = output_file.tell()
                tree_data_size = struct.unpack("<L", file1.read(4))[0] #Needs updating later
                output_file.write(struct.pack("<L",tree_data_size))
                
                chunk = file1.read(1) #This has to be padding or something
                output_file.write(chunk)
                
                #The bnk1's decision tree
                assert tree_data_size % 12 == 0, "Decision tree of DialogueEvent " + str(dialogue_event_id) + " is structured wrong"
                
                decision_tree_nodes1 = []
                for j in range(int(tree_data_size/12)):
                    key = struct.unpack("<L", file1.read(4))[0]
                    children_uIdx = struct.unpack("<H", file1.read(2))[0]
                    children_uCount = struct.unpack("<H", file1.read(2))[0]
                    uWeight = struct.unpack("<H", file1.read(2))[0]
                    uProbability = struct.unpack("<H", file1.read(2))[0]
                    decision_tree_nodes1.append([key, children_uIdx, children_uCount, uWeight, uProbability])
                
                 
                #Reading bnk2, return the decision tree of the dialogue event we care about
                decision_tree_nodes2 = read_and_return_decision_tree(bnk_path2, dialogue_event_id, tree_depth, arguments)                    
                
                
                #Merge the vanilla and custom decision trees
                final_tree = merge_decision_trees(decision_tree_nodes1, decision_tree_nodes2, tree_depth)

                #And finally, write tree
                def write_node(node):
                    output_file.write(struct.pack("<L",node["key"]))
                    if "audioNodeId" in node:
                        output_file.write(struct.pack("<L",node["audioNodeId"]))
                    else:
                        output_file.write(struct.pack("<H",node["uIdx"]))
                        output_file.write(struct.pack("<H",node["uCount"]))                            
                    output_file.write(struct.pack("<H",node["uWeight"]))
                    output_file.write(struct.pack("<H",node["uProbability"]))
                
                for node in final_tree:
                    write_node(node)
                
                #Go back and update TreeDataSize
                bookmark_offset = output_file.tell()
                tree_data_size = output_file.tell() - tree_data_size_offset - 5 #5? what? its got to be that padding....
                output_file.seek(tree_data_size_offset)
                output_file.write(struct.pack("<L",tree_data_size))
                output_file.seek(bookmark_offset)

                #Finish off the dialogue event with this
                chunk = file1.read(2)
                output_file.write(chunk)
                
                #Go back and update the DialogueEvent's SectionSize
                bookmark_offset = output_file.tell()
                section_size = output_file.tell() - section_size_offset - 4
                output_file.seek(section_size_offset)
                output_file.write(struct.pack("<L",section_size))
                output_file.seek(bookmark_offset)            
            else:
                #Skip ahead to next
                file1.read(section_size - 4)

#This takes in two bnks (ideally, custom bnks that haven't been merged with the vanilla decision trees yet)
   #And then compiles them into a single bnk that only contains the DialoguEvents
   #If it finds the same DialogueEvent in each, then it will merge their decision trees
   #It discards any Sound or RandomContainers, etc.
def merge_bnks_together(bnk_path1, bnk_path2, output_bnk_path):
    print("Attempting to merge " + bnk_path1 + " and " + bnk_path2 + " into a single bnk")
    
    #First find all the DialoguEvent ids in file1
    dialogue_event_ids1 = read_and_return_dialogue_event_ids(bnk_path1)
        
    
    #Do the same for file2
    dialogue_event_ids2 = read_and_return_dialogue_event_ids(bnk_path2)

    dialogue_event_ids_combined = dialogue_event_ids1 + dialogue_event_ids2
    dialogue_event_ids_combined = list(set(dialogue_event_ids_combined))
    dialogue_event_ids_combined = sorted(dialogue_event_ids_combined)
        
    with open(output_bnk_path, "wb") as output_file:
            
            #Header
            BKHD_e = bytes("BKHD","UTF-8")
            output_file.write(struct.pack("<%ds" % len("BKHD"), BKHD_e))
        
            chunk_size  = 24
            output_file.write(struct.pack("<L",chunk_size))

            version_thingy = 2147483784
            output_file.write(struct.pack("<L",version_thingy))
            
            bank_id = compute_wwise_hash(os.path.splitext(os.path.basename(output_bnk_path))[0])
            output_file.write(struct.pack("<L",bank_id))
            
            language_id = 550298558
            output_file.write(struct.pack("<L",language_id))
            
            alt_values = 16
            output_file.write(struct.pack("<L",alt_values))
            
            project_id = 2361
            output_file.write(struct.pack("<L", project_id))
            
            padding = 0
            output_file.write(struct.pack("<L", padding))

            HIRC_e = bytes("HIRC","UTF-8")
            output_file.write(struct.pack("<%ds" % len("HIRC"), HIRC_e))
            
            hirc_chunk_size_offset = output_file.tell()
            output_file.write(struct.pack("<L", 0)) #0 for now, will get updated later
            
            hirc_num_items = len(dialogue_event_ids_combined)
            output_file.write(struct.pack("<L",hirc_num_items))
            
            for dialogue_event_id in dialogue_event_ids_combined:
                
                if dialogue_event_id in dialogue_event_ids1:
                    if dialogue_event_id in dialogue_event_ids2:
                        #read file1, merge-in file2's stuff
                        merge_dialogue_event(bnk_path1, bnk_path2, output_file, dialogue_event_id)
                    else:
                        #just copy-over file1's dialogue event, unedited
                        output_file.write(return_dialogue_event_chunk(bnk_path1, dialogue_event_id))
                elif dialogue_event_id in dialogue_event_ids2:
                    #just copy-over file2's dialogue event, unedited
                    output_file.write(return_dialogue_event_chunk(bnk_path2, dialogue_event_id))   
            
            #And finally, go back and update the HIRC chunk size
            hirc_chunk_size = output_file.tell() - hirc_chunk_size_offset - 4
            output_file.seek(hirc_chunk_size_offset)
            output_file.write(struct.pack("<L",hirc_chunk_size))



def read_and_return_non_dialogue_event_ids(bnk_path):
    event_ids = []
    with open(bnk_path, "rb") as file:
        #Header
        BKHD = file.read(4).decode('UTF-8')
        assert BKHD == "BKHD", "Invalid header in " + bnk_path
        chunk_size  = struct.unpack("<L", file.read(4))[0]
        file.read(chunk_size)
        HIRC = file.read(4).decode('UTF-8')
        assert HIRC == "HIRC", "Invalid header in " + bnk_path
        chunk_size = struct.unpack("<L", file.read(4))[0]
        num_items = struct.unpack("<L", file.read(4))[0]
        
        #All the HIRC items
        decision_tree_nodes = []
        for _ in range(num_items):
            hirc_type = struct.unpack("<b", file.read(1))[0]
            section_size = struct.unpack("<L", file.read(4))[0]
            id = struct.unpack("<L", file.read(4))[0]
            
            
            #If we find a NON dialogue event, add to list
            if (hirc_type != 15): #I think this is correct....
                event_ids.append(id)
                
            #Skip ahead to next
            file.read(section_size - 4)
        
    return event_ids


def scramble_ids(bnk_path):
    event_ids = read_and_return_non_dialogue_event_ids(bnk_path)
    
    replacement_pairs = []
    for event_id in event_ids:
        #Concat the bnk's name and the event_id, then run it through the hash.....
        #Doing it this way so it's deterministic
        new_id = compute_wwise_hash(os.path.splitext(os.path.basename(bnk_path))[0] + str(event_id))
        replacement_pairs.append((event_id, new_id))
        
    replacement_hack(replacement_pairs, bnk_path)    
        
        
        
        
        
        
        
        

#1. Scramble IDs (you MUST do this)
#WWise can reuse IDs since they are assigned the moment something is created inside the program
#So if you, for instance, use someone else's project as a template, all of the existing objects will continue to have the same IDs
#Run this on your custom bnk to guarentee we don't run into any collisions between bnks
#This scrambling is deterministic (bnk's name is an input) so you'll get the same output IDs if run twice
scramble_ids("C:/path/to/bnk/foobar.bnk")


#2. Merge together custom .bnks
#Only the audio compatibility mod should do this step
#It discards all non-DialogueEvent WWise objects
custom_bnk1 = "C:/path/to/bnk1/foobar1.bnk"
custom_bnk2 = "C:/path/to/bnk2/foobar2.bnk"
merge_bnks_together(custom_bnk1, custom_bnk2, "./combined_foobar.bnk")


#3. Merge-in the vanilla decision trees
#The path to the vanilla bnk's you extracted from the vanilla .packs
vanilla_bnk_path = "C:/path/to/extracted/bnks/"

#The path (and filename) of the bnk you made in wwise, with all of those DialogueEvents that have their IDs (and arguments) the same as the vanilla versions
custom_bnk = "C:/path/to/bnk/foobar.bnk"

#Where the final bnk is output. It will be just like your custom bnk, but with the addition of the vanilla decision tree stuff packed inside each DialogueEvent.
output_bnk = "./output_foobar.bnk"

merge_vanilla_decision_trees_into_bnk(custom_bnk, output_bnk)


#4. Extra find+replace thing for audio buses with no known name
#In WWise I have them like this:
#4109653590 named "replace_3600304837"
#2201262190 named "replace_3569007248"
#148818222 named "replace_77155641"
pesky_audio_buses = [ (4109653590, 3600304837), #battle
                      (2201262190, 3569007248), #campaign
                      (148818222,77155641),     #possibly diplomacy related, but used in campaign_vo stuff, maybe... unclear...
                      (3972830624,4047594850),  #frontend
                    ]
replacement_hack(pesky_audio_buses, output_bnk)