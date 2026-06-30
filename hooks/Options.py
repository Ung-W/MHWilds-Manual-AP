# Object classes from AP that represent different types of options that you can create
from Options import Option, FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, OptionGroup, PerGameCommonOptions, OptionList
# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value
from typing import Type, Any


####################################################################
# NOTE: At the time that options are created, Manual has no concept of the multiworld or its own world.
#       Options are defined before the world is even created.
#
# Example of creating your own option:
#
#   class MakeThePlayerOP(Toggle):
#       """Should the player be overpowered? Probably not, but you can choose for this to do... something!"""
#       display_name = "Make me OP"
#
#   options["make_op"] = MakeThePlayerOP
#
#
# Then, to see if the option is set, you can call is_option_enabled or get_option_value.
#####################################################################


# To add an option, use the before_options_defined hook below and something like this:
#   options["total_characters_to_win_with"] = TotalCharactersToWinWith
#
class Victory(Choice):
    """
        Choose your final hunt (victory token in Reward 1 of final quest) :
            - Arkveld (default) : 7* Optional Quest
            - Zoh Shia : 8* Optional Quest
            - Omega : 8* Optional Quest (also add Nerscylla Clone 7* Optional Quest)
            - Gogmazios : 9* Event Quest"
    """
    display_name = "Final Quest"
    option_arkveld = 0
    option_zoh_shia = 1
    option_omega = 2
    option_gogmazios = 3
    default = 0
    
class LRSkip(Toggle):
    """Skip all LR quest and gives access to Rarity 4 Equipment from the start"""
    display_name = "Skip LR"
    default = False

class CondenseWeapons(Toggle):
    """Condense all weapon trees into a single one"""
    display_name = "Overall Weapon Tree"
    default = False
    
class CondenseArmors(Toggle):
    """Condense all armor trees into a single one"""
    display_name = "Overall Armor Tree"
    default = False
    
class SmallMonsterQuests(Toggle):
    """Toggle Small Monster Quests as locations"""
    display_name = "Small Monster Quests"
    default = False
    
class weaponOption(OptionList):
    """
        Toggle weapon types to be included in the pool.
        won't do anything if condense_weapons is enabled.
        
        This does not guarantee that you'll always have 8 upgrades of one weapon.
        Here are the number of locations guaranteed in this world available for useful items.
        Total Locations : 130
        - (8 weapons upgrades for max)
          Gogmazios goal + Small Monster Quests + No LR Skip = 130 locations - 1 Victory location - 4 Endgame Unlocks - 8 Quest Star = 117 locations
            without Small Monster Quests : - 28 locations (14 Quests with 2 reward)
            without armors condesed : - 40 locations for Armor Upgrades
            with armors condesed : - 8 locations for Armor Upgrades
            with mantles : - 5 locations for Mantles (random because mantles are also useful)
        - (4 weapons upgrades for max)
          Gogmazios goal + Small Monster Quests + LR Skip = 82 locations - 1 Victory location - 4 Endgame Unlocks - 4 Quest Star = 73 locations
            without Small Monster Quests : - 14 locations (7 Quests with 2 reward)
            without armors condesed : - 25 locations for Armor Upgrades
            with armors condesed : - 5 locations for Armor Upgrades
            with mantles : - 5 locations for Mantles (random because mantles are also useful)
            
        possible values are : "Greatsword", "Longsword", "Sword and Shield", "Dual Blades", "Hammer", "Hunting Horn", "Lance", "Gunlance", "Switch Axe", "Charge Blade", "Insect Glaive", "Light Bowgun", "Heavy Bowgun", "Bow"
    """
    display_name = "Weapon Types"
    default = ["Greatsword", "Longsword", "Sword and Shield", "Dual Blades", "Hammer", "Hunting Horn", "Lance", "Gunlance", "Switch Axe", "Charge Blade", "Insect Glaive", "Light Bowgun", "Heavy Bowgun", "Bow"]

class MainWeapon(Choice):
    """
        Choose your main weapon, this will add 2 more copy of it in the pool.
        Won't do anything if condense_weapons is enabled.
    """
    display_name = "Main Weapon"
    option_Greatsword = 0
    option_Longsword = 1
    option_Sword_and_Shield = 2
    option_Dual_Blades = 3
    option_Hammer = 4
    option_Hunting_Horn = 5
    option_Lance = 6
    option_Gunlance = 7
    option_Switch_Axe = 8
    option_Charge_Blade = 9
    option_Insect_Glaive = 10
    option_Light_Bowgun = 11
    option_Heavy_Bowgun = 12
    option_Bow = 13
    default = 0 
    
class ExtraWeapons(Choice):
    """
        Number of extra weapons to include in the pool.
    """
    display_name = "Extra Weapons"
    option_0 = 0
    option_1 = 1
    option_2 = 2
    option_3 = 3
    option_4 = 4
    option_5 = 5
    option_6 = 6
    option_7 = 7
    option_8 = 8
    default = 0
    
class MantleToggle(Toggle):
    """
        Toggle mantles to be included in the pool.
    """
    display_name = "Mantles"
    default = True
    
class ActiveTraps(OptionList):
    """
        Toggle traps to be included in the pool, remove the ones you don't want included in the pool.
        possible values are :
        - "Paratoad" : Stay still for 5 seconds
        - "Dung Pod" : Throw a dung pod at the monster (if available)
        - "Farcaster" : Teleport to Base Camp
        - "Take Cover !" : Equip one of your mantle immediately if available, if you already equipped one, ignore this.
        - "So Thirsty..." : Drink a potion of your choice immediately if available
        - "So Hungry..." : Pull up the grill and make a meal or grill meat
    """
    display_name = "Traps"
    default = ["Paratoad", "Dung Pod", "Farcaster", "Take Cover !", "So Thirsty...", "So Hungry..."]

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["victory_condition"] = Victory
    options["small_monster_toggle"] = SmallMonsterQuests
    options["lr_skip"] = LRSkip
    options["condense_armors"] = CondenseArmors
    options["mantle_toggle"] = MantleToggle
    options["condense_weapons"] = CondenseWeapons
    options["weapon_option"] = weaponOption
    options["main_weapon"] = MainWeapon
    options["extra_weapons"] = ExtraWeapons
    options["active_traps"] = ActiveTraps
    return options

# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: Type[PerGameCommonOptions]):
    # To access a modifiable version of options check the dict in options.type_hints
    # For example if you want to change DLC_enabled's display name you would do:
    # options.type_hints["DLC_enabled"].display_name = "New Display Name"

    #  Here's an example on how to add your aliases to the generated goal
    # options.type_hints['goal'].aliases.update({"example": 0, "second_alias": 1})
    # options.type_hints['goal'].options.update({"example": 0, "second_alias": 1})  #for an alias to be valid it must also be in options

    pass

# Use this Hook if you want to add your Option to an Option group (existing or not)
def before_option_groups_created(groups: dict[str, list[Type[Option[Any]]]]) -> dict[str, list[Type[Option[Any]]]]:
    # Uses the format groups['GroupName'] = [TotalCharactersToWinWith]
    return groups

def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups
