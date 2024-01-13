import struct

#If you don't already know what this script does, then reading the below explainations won't help you at all. Go learn some Wwise.

#The path to the vanilla bnk's you extracted from the vanilla .packs
vanilla_bnk_path = "C:/path/to/extracted/bnks/audio/wwise/english(uk)/"

#The path (and filename) of the bnk you made in wwise, with all of those DialogueEvents that have their IDs the same as the vanilla versions
custom_bnk = "C:/path/to/custom/bnk/foobar_custom_bnk.bnk"

#Where the final bnk is output. It will be just like your custom bnk, but will also have the vanilla decision tree stuff packed inside each DialogueEvent.
output_bnk = "./foobar_custom_bnk.bnk"

# The decision trees are merged in a specific and somewhat limited way, only at the top 'layer' which (so far, always) corresponds to vo_culture
# Each dialogue event in your custom_bnk should only have a single vo_culture. If you have more, then make seperate custom_bnks for each one and run the script multiple times
# Each dialogue event in your custom_bnk needs to have the exact same set up (take the exact same arguments) as its vanilla counterpart

# The decision trees are merged in a non-standard way, with only the new vo_culture node inserted into the existing vanilla decision tree,
#    and then the rest of the nodes just added onto the end of the list
# Wwiser can *parse* it, but it doesn't *display* it properly, with nodes shown as mixed up. Even so, the game does seem to be able to handle things
# I didn't check what Asset Editor shows


# Here are the DialogueEvents it will try to merge, if it can't find one in your custom_bnk, then it will just skip
# The string is the name of the vanilla bnk which contains the vanilla version of the DialogueEvent
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
    
    36016233   : "battle_vo_orders__core.bnk", #battle_vo_order_bat_mode_survival, these four actually have "vo_actor" as the top-level switch, script still works, I think
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
    
    
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_selected_neutral
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_selected_allied
    3969841041 : "campaign_vo__core.bnk", #campaign_vo_selected
    3722163706 : "campaign_vo__core.bnk", #campaign_vo_selected_short
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_selected_fail
    2301359050 : "campaign_vo__core.bnk", #campaign_vo_selected_first_time
    #
    748798295 : "campaign_vo__core.bnk", #campaign_vo_yes
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_yes_short_aggressive
    874013640 : "campaign_vo__core.bnk", #campaign_vo_yes_short
    #
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_no
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_no_short
    #
    2302243677 : "campaign_vo__core.bnk", #campaign_vo_move
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_move_garrisoning
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_move_next_turn
    2334862434 : "campaign_vo__core.bnk", #campaign_vo_attack
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_ship_dock
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_retreat
    #
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_default
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_set_camp
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_march
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_set_camp_raiding
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_raise_dead
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_ambush
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_muster
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_double_time
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_channeling
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_land_raid
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_patrol
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_tunneling
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_astromancy
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_stalking
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_stance_settle
    #
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_created
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_new_commander
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_recruit_units
    #
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_post_battle_victory
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_post_battle_defeat
    #
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_agent_action_success
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_agent_action_failed
    #
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_diplomacy_positive
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_diplomacy_selected
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_diplomacy_negative
    #
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_mounted_creature
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_level_up
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_special_ability
    #
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_skill_weapon_tree_response
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_tech_tree
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_skill_weapon_tree
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_disbanded_neg
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_disbanded_pos
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_disband
    #0000000000 : "campaign_vo__core.bnk", #campaign_vo_cam_tech_tree_response
}


#Extra find+replace thing for audio buses with no known name (does nothing if set to None)
for_those_pesky_audio_buses = [(4109653590, 3600304837), (2201262190, 3569007248)] #None

with open(output_bnk, "wb") as output_file:
    with open(custom_bnk, "rb") as custom_file:
        
        #Reading custom file
        
        #Header
        BKHD = custom_file.read(4).decode('UTF-8')
        assert BKHD == "BKHD"
        BKHD_e = bytes(BKHD,"UTF-8")
        output_file.write(struct.pack("<%ds" % len(BKHD), BKHD_e))
    
        chunk_size  = struct.unpack("<L", custom_file.read(4))[0]
        output_file.write(struct.pack("<L",chunk_size))
        
        version_thingy = struct.unpack("<L", custom_file.read(4))[0]
        if version_thingy != 2147483784:
            version_thingy = 2147483784
        output_file.write(struct.pack("<L",version_thingy))
        
        chunk = custom_file.read(chunk_size - 12)
        output_file.write(chunk)
        
        project_id = struct.unpack("<L", custom_file.read(4))[0]
        if project_id != 2361:
            project_id = 2361
        output_file.write(struct.pack("<L", project_id))
        
        chunk = custom_file.read(4)
        output_file.write(chunk)
        
        HIRC = custom_file.read(4).decode('UTF-8')
        assert HIRC == "HIRC"
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
            if (hirc_type == 15) and (id in dialogue_event_to_vanilla_bnk):
                print("Found the DialogueEvent " + str(id) + " in the custom bnk...")
                dialogue_event_id = id
                vanilla_bnk_filename = dialogue_event_to_vanilla_bnk[id]
                
                chunk = custom_file.read(1)
                output_file.write(chunk)
                
                tree_depth = struct.unpack("<L", custom_file.read(4))[0]
                output_file.write(struct.pack("<L",tree_depth))
                
                custom_arguments = []
                for _ in range(tree_depth):
                    arg =  struct.unpack("<L", custom_file.read(4))[0]
                    custom_arguments.append(arg)
                    output_file.write(struct.pack("<L",arg))
                
                for _ in range(tree_depth):
                    chunk = custom_file.read(1)
                    output_file.write(chunk)
                
                tree_data_size_offset = output_file.tell()
                tree_data_size = struct.unpack("<L", custom_file.read(4))[0] #Needs updating later
                output_file.write(struct.pack("<L",tree_data_size))
                
                chunk = custom_file.read(1)
                output_file.write(chunk)
                
                #The custom bnk's decision tree
                assert tree_data_size % 12 == 0
                
                custom_decision_tree_nodes = []
                for j in range(int(tree_data_size/12)):
                    key = struct.unpack("<L", custom_file.read(4))[0]
                    children_uIdx = struct.unpack("<H", custom_file.read(2))[0]
                    children_uCount = struct.unpack("<H", custom_file.read(2))[0]
                    if j == 0:
                        assert children_uCount == 1
                    uWeight = struct.unpack("<H", custom_file.read(2))[0]
                    uProbability = struct.unpack("<H", custom_file.read(2))[0]
                    custom_decision_tree_nodes.append([key, children_uIdx, children_uCount, uWeight, uProbability])
                
                
                
                #Vanilla bnk time
                
                vanilla_decision_tree_nodes = []
                 
                #Reading vanilla bnk
                with open(vanilla_bnk_path + vanilla_bnk_filename, "rb") as vanilla_file:
                    
                    #Header
                    BKHD = vanilla_file.read(4).decode('UTF-8')
                    assert BKHD == "BKHD"
                    chunk_size  = struct.unpack("<L", vanilla_file.read(4))[0]
                    vanilla_file.read(chunk_size)
                    HIRC = vanilla_file.read(4).decode('UTF-8')
                    assert HIRC == "HIRC"
                    chunk_size = struct.unpack("<L", vanilla_file.read(4))[0]
                    num_items = struct.unpack("<L", vanilla_file.read(4))[0]
                    
                    #All the HIRC items
                    for _ in range(num_items):
                        hirc_type = struct.unpack("<b", vanilla_file.read(1))[0]
                        section_size = struct.unpack("<L", vanilla_file.read(4))[0]
                        id = struct.unpack("<L", vanilla_file.read(4))[0]
                        
                        
                        #If we find the dialogue event in question...
                        if (hirc_type == 15) and (id == dialogue_event_id):
                            print("...and found the DialogueEvent in the provided vanilla bnk...")
                            
                            vanilla_file.read(1)
                            tree_depth = struct.unpack("<L", vanilla_file.read(4))[0]
                            
                            vanilla_arguments = []
                            for _ in range(tree_depth):
                                arg =  struct.unpack("<L", vanilla_file.read(4))[0]
                                vanilla_arguments.append(arg)
                            
                            assert vanilla_arguments == custom_arguments
                    
                    
                            for _ in range(tree_depth):
                                vanilla_file.read(1)
                                
                            tree_data_size = struct.unpack("<L", vanilla_file.read(4))[0]
                            vanilla_file.read(1)
                            
                            #The vanilla bnk's decision tree
                            assert tree_data_size % 12 == 0
                            for _ in range(int(tree_data_size/12)):
                                key = struct.unpack("<L", vanilla_file.read(4))[0]
                                children_uIdx = struct.unpack("<H", vanilla_file.read(2))[0]
                                children_uCount = struct.unpack("<H", vanilla_file.read(2))[0]
                                uWeight = struct.unpack("<H", vanilla_file.read(2))[0]
                                uProbability = struct.unpack("<H", vanilla_file.read(2))[0]
                                vanilla_decision_tree_nodes.append([key, children_uIdx, children_uCount, uWeight, uProbability])
                                
                            #vanilla_file.read(2)
                            break #don't need to keep reading
                            
                        #Otherwise, skip ahead to the next HIRC itrm
                        else:
                            vanilla_file.read(section_size - 4)
                
                
                
                ########################################
                ### The main merge bullshit is here! ###
                ########################################
                
                
                #Compile a list of all leaf ids in the vanilla decision tree, for later
                def extract_leaf_ids(tree, depth, current_index=0):
                    if depth == 0:
                        # Reached the leaf nodes, return the id
                        return [(tree[current_index][1], tree[current_index][2])]
                    
                    ids = []
                    children_index = tree[current_index][1]
                    children_count = tree[current_index][2]
                    
                    #secondary checks, since a leaf can occur before max depth
                    if (children_index > len(vanilla_decision_tree_nodes) #Impossibly large amout of children
                    or children_count > len(vanilla_decision_tree_nodes)  #Impossibly large index
                    or children_index < current_index):                   #Index goes "backwards", also impossible
                        return [(tree[current_index][1], tree[current_index][2])]
                    
                    
                    for i in range(children_count):
                        # Recursively traverse each child
                        child_ids = extract_leaf_ids(tree, depth - 1, children_index + i)
                        ids.extend(child_ids)
                    
                    return ids
 
                leaf_ids = extract_leaf_ids(vanilla_decision_tree_nodes, tree_depth)
                    
                
                
                
                #Take the 2nd custom node (corresponding to the new culture)
                #Update that node's children_uIdx so it points to the end of the vanilla list
                main_custom_node = custom_decision_tree_nodes[1]
                culture_id = main_custom_node[0]
                
                main_custom_node[1] = len(vanilla_decision_tree_nodes)
                
                
                #Figure out where the node should be in the first part of the vanilla list
                limit = vanilla_decision_tree_nodes[0][2] #Only check the first part (immediate children of the first vanilla node)
                insert_at = limit
                for n,node in enumerate(vanilla_decision_tree_nodes[0:limit]):
                    id = node[0]
                    if id > culture_id:
                        insert_at = n
                        break;
                    
                #And insert it into the vanilla list
                vanilla_decision_tree_nodes.insert(insert_at, main_custom_node)
                
                #Then update the very first vanilla node so it has +1 children
                vanilla_decision_tree_nodes[0][2] += 1
                
                
                #Then we update the children_uIdx (increment by 1) for all except the first
                for k,node in enumerate(vanilla_decision_tree_nodes[1:]):
                    if (node[1],node[2]) in leaf_ids:
                        pass #it's a leaf, so do nothing
                    else:
                        node[1] += 1
                
                
                #Then we tack-on the rest of the custom nodes to the end
                #Also update their children_uIdx
                custom_decision_tree_nodes_ = custom_decision_tree_nodes[2:]
                for node in custom_decision_tree_nodes_:
                    if (node[2] > len(vanilla_decision_tree_nodes) or node[1] > len(vanilla_decision_tree_nodes)):
                        pass #it's a leaf, probably, so do nothing
                    else:
                        node[1] += len(vanilla_decision_tree_nodes) - 2
                
                vanilla_decision_tree_nodes.extend(custom_decision_tree_nodes_)
                
                
                #Write to the output
                for node in vanilla_decision_tree_nodes:
                    (key, children_uIdx, children_uCount, uWeight, uProbability) = node
                    output_file.write(struct.pack("<L",key))
                        
                    output_file.write(struct.pack("<H",children_uIdx))
                    output_file.write(struct.pack("<H",children_uCount))
                    output_file.write(struct.pack("<H",uWeight))
                    output_file.write(struct.pack("<H",uProbability))


                #Go back and update TreeDataSize
                bookmark_offset = output_file.tell()
                output_file.seek(tree_data_size_offset)
                output_file.write(struct.pack("<L",len(vanilla_decision_tree_nodes)*12))
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
                
                print("...so it's a success, I guess")
                
                
            #If it not the event we are looking for in the custom bnk, then skip ahead to the next HIRC item
            else:
                chunk = custom_file.read(section_size - 4)
                output_file.write(chunk)
                
        
        #Ands finally, go back and update the HIRC chunk size
        hirc_chunk_size = output_file.tell() - hirc_chunk_size_offset - 4
        output_file.seek(hirc_chunk_size_offset)
        output_file.write(struct.pack("<L",hirc_chunk_size))
        


#Extra thing for an audio bus with no known name
if for_those_pesky_audio_buses != None:
    with open(output_bnk, 'rb') as file:
        content = file.read()

    # Assuming int32 is 4 bytes
    for a in for_those_pesky_audio_buses:
        old_bytes = struct.pack('<L', a[0])
        new_bytes = struct.pack('<L', a[1])

        # Replace all instances of old_value with new_value
        content = content.replace(old_bytes, new_bytes)

    with open(output_bnk, 'wb') as file:
        file.write(content)