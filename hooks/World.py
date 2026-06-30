# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from typing import Any
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation
from .Options import Victory

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat, remove_specific_item

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################



# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    return False

def before_generate_early(world: World, multiworld: MultiWorld, player: int) -> None:
    """
    This is the earliest hook called during generation, before anything else is done.
    Use it to check or modify incompatible options, or to set up variables for later use.
    """
    pass

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove: list[str] = [] # List of location names
    regions_to_remove: list[str] = [] # List of region names

    # Add your code here to calculate which locations to remove
    victory = get_option_value(multiworld, player, "victory_condition")
    lrskip = get_option_value(multiworld, player, "lr_skip") or False
    small = get_option_value(multiworld, player, "small_monster_toggle") or False
    
    if victory == Victory.option_arkveld:
        locationNamesToRemove = [
            "Zoh Shia Investigation - Reward 1", "Zoh Shia Investigation - Reward 2", 
            "Incomplete Creation - Reward 1", "Incomplete Creation - Reward 2",
            "Planetes Protocol - Reward 1", "Planetes Protocol - Reward 2",
            "Specter of Their Sins - Reward 1", "Specter of Their Sins - Reward 2"
            ]
    elif victory == Victory.option_zoh_shia:
        locationNamesToRemove = [
            "Incomplete Creation - Reward 1", "Incomplete Creation - Reward 2",
            "Planetes Protocol - Reward 1", "Planetes Protocol - Reward 2",
            "Specter of Their Sins - Reward 1", "Specter of Their Sins - Reward 2"
            ]
        
    elif victory == Victory.option_omega:
        locationNamesToRemove = [
            "Specter of Their Sins - Reward 1", "Specter of Their Sins - Reward 2"
            ]
    
    if lrskip:
        regions_to_remove = [
                "1* Quests", "2* Quests", "3* Quests"
            ]
        
    if not small:
        for location in world.location_name_to_location.items():
            if "Small Monster" in location[1]["category"]:
                locationNamesToRemove += [location[1]["name"]]

    for region in multiworld.regions:
        if region.player == player:
            if region.name in regions_to_remove:
                for location in list(region.locations):
                        region.locations.remove(location)
                    
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)

# This hook allows you to access the item names & counts before the items are created. Use this to increase/decrease the amount of a specific item in the pool
# Valid item_config key/values:
# {"Item Name": 5} <- This will create qty 5 items using all the default settings
# {"Item Name": {"useful": 7}} <- This will create qty 7 items and force them to be classified as useful
# {"Item Name": {"progression": 2, "useful": 1}} <- This will create 3 items, with 2 classified as progression and 1 as useful
# {"Item Name": {0b0110: 5}} <- If you know the special flag for the item classes, you can also define non-standard options. This setup
#       will create 5 items that are the "useful trap" class
# {"Item Name": {ItemClassification.useful: 5}} <- You can also use the classification directly
def before_create_items_all(item_config: dict[str, int|dict], world: World, multiworld: MultiWorld, player: int) -> dict[str, int|dict]:
    return item_config

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    items_to_remove = []
    
    victory = get_option_value(multiworld, player, "victory_condition")
    
    victory_item = next(i for i in item_pool if i.name == "Hunt Complete !")
    if victory == Victory.option_arkveld:
        victory_location_name = "The Chains of Life - Reward 1"
        items_to_remove += ["Zoh Shia Permit", "Omega Traces", "Omega Permit", "Gogmazios Permit"]
        
    elif victory == Victory.option_zoh_shia:
        victory_location_name = "Zoh Shia Investigation - Reward 1"
        items_to_remove += ["Omega Traces", "Omega Permit", "Gogmazios Permit"]
        
    elif victory == Victory.option_omega:
        victory_location_name = "Planetes Protocol - Reward 1"
        items_to_remove += ["Gogmazios Permit"]
        
    elif victory == Victory.option_gogmazios:
        victory_location_name = "Specter of Their Sins - Reward 1"
    
    full_weapon_list = ["Greatsword", "Longsword", "Sword and Shield", "Dual Blades", "Hammer", "Hunting Horn", "Lance", "Gunlance", "Switch Axe", "Charge Blade", "Insect Glaive", "Light Bowgun", "Heavy Bowgun", "Bow"]
    weapon_list = world.options.weapon_option
    
    cond_weapons_val = world.options.condense_weapons
    cond_armor_val = world.options.condense_armors        
    main_weapon_val = world.options.main_weapon
    main_weapon = full_weapon_list[main_weapon_val]
    
    if cond_weapons_val:
        for weapon in full_weapon_list:
            for i in range(0, 8):
                items_to_remove += [f"Progressive {weapon}"]
    else:
        for i in range(0, 8):
            items_to_remove += [f"Progressive Weapon"]
            
        for weapon in weapon_list:
            full_weapon_list.remove(weapon)
            
        for weapon in full_weapon_list:
            for i in range(0, 8):
                items_to_remove += [f"Progressive {weapon}"]
                
    if cond_armor_val:
        for piece in ["Helmet", "Chest", "Arms", "Waist", "Legs"]:
            for i in range(0, 8):
                items_to_remove += [f"Progressive {piece}"]
    else:
        for i in range(0, 8):
            items_to_remove += [f"Progressive Armor"]
    
    if not cond_weapons_val :
        if main_weapon in weapon_list:
            for i in range(0, 2):
                item_pool.append(world.create_item(f"Progressive {main_weapon}"))
        else:
            for i in range(0, 2):
                item_pool.append(world.create_item("Main Weapon wrongly defined in yaml, not worth fussing over it, free pass for a weapon rarity"))
            
    extra_weapons_val = world.options.extra_weapons
    if cond_weapons_val:
        if extra_weapons_val != 0:
            for i in range(0, extra_weapons_val):
                item_pool.append(world.create_item("Progressive Weapon"))
    else:
        if extra_weapons_val != 0:
            for weapon in weapon_list:
                for i in range(0, extra_weapons_val):
                    item_pool.append(world.create_item(f"Progressive {weapon}"))
            
    mantle_val = world.options.mantle_toggle
    if not mantle_val:
        for mantle in ["Ghilie Mantle", "Mending Mantle", "Rocksteady Mantle", "Evasion Mantle", "Corrupted Mantle"]:
            items_to_remove += [mantle]
            
    for item_name in items_to_remove:
        item = next(i for i in item_pool if i.name == item_name)
        item_pool.remove(item)
        
    try:
        location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == victory_location_name)
    except StopIteration:
        print("could not find location", victory_location_name)
        raise StopIteration()
    location.place_locked_item(victory_item)
    item_pool.remove(victory_item)
    
    location_count = len(multiworld.get_unfilled_locations(player=player))
    multiworld.random.shuffle(item_pool)
    while len(item_pool) > location_count - 1:
        try:
            item = next(i for i in item_pool if world.item_name_to_item[i.name].get('filler', False))
        except StopIteration:
            break
        item_pool.remove(item)
    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    starting_items = []
    
    lr_skip_val = world.options.lr_skip
    cond_weapons_val = world.options.condense_weapons
    cond_armor_val = world.options.condense_armors
    weapon_list = world.options.weapon_option

    # if they put in something other than a number, make it a number and the default of 0
    if lr_skip_val:
        starting_items += [{
            "items": ["Quest Rank Star"],
            "random": 4
        }]
        
        for region in ["Windward Plains Access", "Scarlet Forest Access", "Oilwell Basin Access", "Iceshard Cliffs Access", "Ruins of Wyveria Access"]:
            starting_items += [{
                "items": [f"{region}"],
                "random": 1
            }]
        
        starting_items += [{
            "items": ["Windward Plains Access", "Scarlet Forest Access", "Oilwell Basin Access", "Iceshard Cliffs Access"],
            "random": 1
        }]
        
        if cond_weapons_val :
            starting_items += [{
                "items": ["Progressive Weapon"],
                "random": 4
            }]
        else:
            for weapon in weapon_list:
                starting_items += [{
                    "items": [f"Progressive {weapon}"],
                    "random": 4
                }]
        if cond_armor_val :
            starting_items += [{
                "items": ["Progressive Armor"],
                "random": 4
            }]
        else:
            for piece in ["Helmet", "Chest", "Arms", "Waist", "Legs"]:
                starting_items += [{
                    "items": [f"Progressive {piece}"],
                    "random": 4
                }]
    else:
        starting_items += [{
            "items": ["Quest Rank Star"],
            "random": 1
        }]
        
        starting_items += [{
            "items": ["Windward Plains Access", "Scarlet Forest Access"],
            "random": 1
        }]
        
        if cond_weapons_val :
            starting_items += [{
                "items": ["Progressive Weapon"],
                "random": 1
            }]
        else:
            for weapon in weapon_list:
                starting_items += [{
                    "items": [f"Progressive {weapon}"],
                    "random": 1
                }]
        if cond_armor_val :
            starting_items += [{
                "items": ["Progressive Armor"],
                "random": 1
            }]
        else:
            for piece in ["Helmet", "Chest", "Arms", "Waist", "Legs"]:
                starting_items += [{
                    "items": [f"Progressive {piece}"],
                    "random": 1
                }]

    for starting in starting_items:
        possible_item_names = starting['items']
        
        # remove any duplicate names from the list of possible items
        possible_item_names = set(possible_item_names)

        # we add the list of items that have this specific category to our possible items
        possible_items = [
            i for i in item_pool 
                if i.name in possible_item_names
        ]
        
        # pick a random possible item(s) to start with, then precollect them and,
        #   since we just took them, remove them from the item pool
        for _ in range(starting['random']): # loops from 0 to starting['random'] - 1
            random_starting_item = world.random.choice(possible_items)
            multiworld.push_precollected(random_starting_item)
            possible_items.remove(random_starting_item) # don't allow choosing the exact same item again
            item_pool.remove(random_starting_item) # remove it from the pool since we're starting with it

    # once we're done with everything, return our modified item pool
    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # remove_specific_item(item_pool, item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    trap_to_replace = []
    
    active_traps = world.options.active_traps
    full_trap_list = ["Paratoad", "Dung Pod", "Farcaster", "Take Cover !", "So Thirsty...", "So Hungry...", "Won't raise an exception for this but check your enabled traps in yaml"]
    active_traps_list = []
    
    if not active_traps:
        active_traps = ["Won't raise an exception for this but check your enabled traps in yaml"]
    
    for trap in full_trap_list:
        if trap not in active_traps:
            trap_to_replace += [trap]
        else:
            active_traps_list += [trap]
    
    for trap_name in trap_to_replace:
        for i in item_pool.copy():
            if i.name == trap_name:
                replacement_trap = world.random.choice(active_traps_list)
                item_pool.remove(i)
                item_pool.append(world.create_item(replacement_trap))
    
    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run every time an item is added to the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be cancelled/undone in after_remove_item
def after_collect_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you add to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] += 1
    pass

# This method is run every time an item is removed from the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be first done in after_collect_item
def after_remove_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you undo the addition to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] -= 1
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass

# This is called when you want to add information to the hint text
def before_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:

    ### Example way to use this hook:
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string

    pass

def after_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    pass

def hook_interpret_slot_data(world: World, player: int, slot_data: dict[str, Any]) -> dict[str, Any]:
    """
        Called when Universal Tracker wants to perform a fake generation
        Use this if you want to use or modify the slot_data for passed into re_gen_passthrough
    """
    return slot_data
