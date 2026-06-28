#!/usr/bin/env python3
"""
Songs of Syx - Race Generator
Exact formatting matching HUMAN.txt – tabs, commas, spacing.
"""

import os
import sys
import argparse
import shutil

# ============================================
# DEFAULTS (overridden by GUI or CLI)
# ============================================
DEFAULTS = {
    "HEIGHT": 6,
    "WIDTH": 9,
    "BABY_DAYS": 12,
    "CHILD_DAYS": 80,
    "CORPSE_DECAY": "true",
    "SLEEPS": "true",
    "SLAVE_PRICE": 11,
    "SLAVE_PRICE_RECOVERY": 0.5,
    "RAID_MERCINARY": 1.0,
    "TOURIST_OCCURENCE": 1.0,
    "TOURIST_CREDITS": 0.75,
    "POPULATION_MAX": 1.0,
    "POPULATION_GROWTH": 0.075,
    "CHALLENGE": "Medium",
    # Default stats block - with trailing comma after last entry
    "STATS_RAW": '''\tACCESS_NOISE: {
\t\tCITIZEN: 0.5,
\t\tINVERTED: true,
\t},
\tACCESS_SPACE: {
\t\tCITIZEN: 0.5,
\t},
\tSTORED_GEM: {
\t\tCITIZEN: 1,
\t\tSLAVE: 0,
\t\tNOBLE: 1,
\t\tPRIO: 10,
\t},
\tMONUMENTS_MONUMENT_SCULPTURE: {
\t\tCITIZEN: 0.5,
\t\tSLAVE: 0.5,
\t\tPRIO: 10,
\t\tMULTIPLIER: 8,
\t},
\tMONUMENTS_MONUMENT_NATURE: {
\t\tCITIZEN: 0.5,
\t\tSLAVE: 0.5,
\t\tPRIO: 10,
\t\tMULTIPLIER: 8,
\t},'''
}

# ============================================
# EXACT TEMPLATES – MATCHING HUMAN.txt
# ============================================

MAIN_CONFIG_TEMPLATE = '''PLAYABLE: true,
PROPERTIES: {{
\tHEIGHT: {HEIGHT},
\tWIDTH: {WIDTH},
\tBABY_DAYS: {BABY_DAYS},
\tCHILD_DAYS: {CHILD_DAYS},
\tCORPSE_DECAY: {CORPSE_DECAY},
\tSLEEPS: {SLEEPS},
\tSLAVE_PRICE: {SLAVE_PRICE},
\tSLAVE_PRICE_RECOVERY: {SLAVE_PRICE_RECOVERY},
\tRAID_MERCINARY: {RAID_MERCINARY},
}},
BIO_FILE: Normal,
BIO_FILE_SPECIFIC: Human,
KING_FILE: Normal,
WORLD_NAME_FILE: Misc,
RAID_TEXT_FILE: Normal,
RAIDER_NAME_FILE: Normal,
TOURIST: {{
\tOCCURENCE: {TOURIST_OCCURENCE},
\tCREDITS: {TOURIST_CREDITS},
\tTOURIST_TEXT_FILE: NORMAL,
}},
HOME: NORMAL,
TECH: [
\t*,
],
PREFERRED: {{
\tFOOD: [
{FOOD_LIST}
\t],
\tDRINK: [
{DRINK_LIST}
\t],
\tROAD: {{
{ROAD_DICT}
\t}},
\tSTRUCTURE: {{
{STRUCTURE_DICT}
\t}},
\tPOOL: {{
{POOL_DICT}
\t}},
\tWORK: {{
{WORK_DICT}
\t}},
\tOTHER_RACES: {{
{OTHER_RACES_DICT}
\t}},
\tOTHER_RACES_REVERSE: {{
\t\t*: 1,
\t}},
\tBUILDING_OVERRIDE: {{
{BUILDING_OVERRIDE_DICT}
\t}},
}},
POPULATION: {{
\tMAX: {POPULATION_MAX},
\tGROWTH: {POPULATION_GROWTH},
\tCLIMATE: {{
\t\tCOLD: {CLIMATE_COLD},
\t\tTEMPERATE: {CLIMATE_TEMPERATE},
\t\tHOT: {CLIMATE_HOT},
\t}},
\tTERRAIN: {{
\t\tMOUNTAIN: {TERRAIN_MOUNTAIN},
\t\tFOREST: {TERRAIN_FOREST},
\t\tNONE: {TERRAIN_NONE},
\t}},
}},
TRAITS: {{
{TRAITS_DICT}
}},
RESOURCE: {{
{RESOURCE_DICT}
}},

STATS: {{
{STATS_RAW}
}},
SPRITE_FILE: {RACE_UPPER},
ICON_SMALL: 24->race->{RACE_NAME}->0,
ICON_BIG: 32->race->{RACE_NAME}->0,

BOOST: {{
{BOOST_DICT}
}},

EQUIPMENT_NOT_ENABLED: [
{EQUIPMENT_NOT_ENABLED_LIST}
],

EQUIPMENT_ENABLED: [
{EQUIPMENT_ENABLED_LIST}
],
'''

TEXT_RACE_TEMPLATE = '''NAME: "{RACE_NAME}",
NAMES: "{RACE_NAMES}",
POSSESSIVE: "{RACE_NAME}",
POSSESSIVES: "{RACE_NAME}",
PRONOUN_HE: ["he", "she",],
PRONOUN_HEC: ["He", "She",],
PRONOUN_HIM: ["him", "her",],
PRONOUN_HIMC: ["Him", "Her",],
PRONOUN_HIS: ["his", "her",],
PRONOUN_HISC: ["His", "Her",],
PRONOUN_HIMSELF: ["himself", "herself",],
PRONOUN_HIMSELFC: ["Himself", "Herself",],
PRONOUN_CHILD: ["son", "daughter",],
PRONOUN_CHILDC: ["Son", "Daughter",],

HELLO: [
{HELLO_LIST}
],
GOODBYE: [
{GOODBYE_LIST}
],
CURSE: [
{CURSE_LIST}
],
INSULT: [
{INSULT_LIST}
],
INSULTING: [
{INSULTING_LIST}
],
LORD: [
{LORD_LIST}
],
CITY: [
{CITY_LIST}
],
OTHERS: [
{OTHERS_LIST}
],
SELVES: [
{SELVES_LIST}
],
SELF: [
{SELF_LIST}
],
CHILDREN: [
{CHILDREN_LIST}
],

DESC: 
"{DESC_TEXT}"
",
DESC_LONG:
"{DESC_LONG_TEXT}"
",

ARMY_NAMES: [
{ARMY_NAMES_LIST}
],

CHALLENGE: "{CHALLENGE}",

PROS: [
{PROS_LIST}
],

CONS: [
{CONS_LIST}
],
'''


# ============================================
# FORMATTING HELPERS – EXACT RULES
# ============================================

def format_list_tabs(items, indent_tabs=2):
    """
    Format a list with tabs, exactly as in HUMAN.txt.
    - Each item on its own line, indented with tabs.
    - Trailing comma after every item (including last).
    - If empty, returns an empty string (so nothing between brackets).
    """
    if not items:
        return ""
    prefix = "\t" * indent_tabs
    lines = []
    for item in items:
        lines.append(f"{prefix}{item},")
    return "\n".join(lines)


def format_dict_tabs(d, indent_tabs=2):
    """
    Format a dict with tabs, exactly as in HUMAN.txt.
    - Format: "\tKEY: value," on each line.
    - Trailing comma after every pair.
    - If empty, returns empty string.
    - Converts Python bool True/False to lowercase "true"/"false".
    """
    if not d:
        return ""
    prefix = "\t" * indent_tabs
    lines = []
    for k, v in d.items():
        # Handle boolean values
        if isinstance(v, bool):
            v_str = "true" if v else "false"
        elif isinstance(v, str):
            v_str = v
        else:
            v_str = str(v)
        lines.append(f"{prefix}{k}: {v_str},")
    return "\n".join(lines)


def format_equipment_list(items):
    """
    Format equipment list – items on separate lines, indented with tab, trailing comma.
    If empty, returns an empty string (so brackets will be empty with just newline).
    """
    if not items:
        return ""
    return "\n\t".join(f"{item}," for item in items)


def format_cultural_list(items):
    """
    Format a cultural list (HELLO, GOODBYE, etc.) – each item on new line,
    indented with one tab, wrapped in quotes, with trailing comma.
    If empty, returns empty string.
    """
    if not items:
        return ""
    return "\n\t".join(f'"{item}",' for item in items)


# ============================================
# MAIN GENERATION
# ============================================

def generate_race(race_name, output_dir="assets", copy_sprite=False, template_race="HUMAN"):
    race_upper = race_name.upper()
    race_lower = race_name.lower()
    race_plural = race_name + "s" if not race_name.endswith("s") else race_name

    # --------------------------------------------------------------------
    # 1. Build substitution for MAIN_CONFIG_TEMPLATE
    # --------------------------------------------------------------------
    subs_main = {}

    # Simple properties
    simple_keys = [
        "HEIGHT", "WIDTH", "BABY_DAYS", "CHILD_DAYS", "CORPSE_DECAY", "SLEEPS",
        "SLAVE_PRICE", "SLAVE_PRICE_RECOVERY", "RAID_MERCINARY",
        "TOURIST_OCCURENCE", "TOURIST_CREDITS", "POPULATION_MAX", "POPULATION_GROWTH"
    ]
    for k in simple_keys:
        val = DEFAULTS.get(k, "")
        if isinstance(val, bool):
            subs_main[k] = "true" if val else "false"
        else:
            subs_main[k] = str(val)

    subs_main["RACE_NAME"] = race_name
    subs_main["RACE_UPPER"] = race_upper

    # Climate
    climate = DEFAULTS.get("CLIMATE", {})
    subs_main["CLIMATE_COLD"] = str(climate.get("COLD", 0.8))
    subs_main["CLIMATE_TEMPERATE"] = str(climate.get("TEMPERATE", 1.0))
    subs_main["CLIMATE_HOT"] = str(climate.get("HOT", 0.8))

    # Terrain
    terrain = DEFAULTS.get("TERRAIN", {})
    subs_main["TERRAIN_MOUNTAIN"] = str(terrain.get("MOUNTAIN", 0.2))
    subs_main["TERRAIN_FOREST"] = str(terrain.get("FOREST", 0.2))
    subs_main["TERRAIN_NONE"] = str(terrain.get("NONE", 1.5))

    # Lists and dicts
    subs_main["FOOD_LIST"] = format_list_tabs(DEFAULTS.get("FOOD", []), indent_tabs=2)
    subs_main["DRINK_LIST"] = format_list_tabs(DEFAULTS.get("DRINK", []), indent_tabs=2)
    subs_main["ROAD_DICT"] = format_dict_tabs(DEFAULTS.get("ROAD", {}), indent_tabs=2)
    subs_main["STRUCTURE_DICT"] = format_dict_tabs(DEFAULTS.get("STRUCTURE", {}), indent_tabs=2)
    subs_main["POOL_DICT"] = format_dict_tabs(DEFAULTS.get("POOL", {}), indent_tabs=2)
    subs_main["WORK_DICT"] = format_dict_tabs(DEFAULTS.get("WORK", {}), indent_tabs=2)
    subs_main["OTHER_RACES_DICT"] = format_dict_tabs(DEFAULTS.get("OTHER_RACES", {}), indent_tabs=2)
    subs_main["BUILDING_OVERRIDE_DICT"] = format_dict_tabs(DEFAULTS.get("BUILDING_OVERRIDE", {}), indent_tabs=2)

    subs_main["TRAITS_DICT"] = format_dict_tabs(DEFAULTS.get("TRAITS", {}), indent_tabs=1)
    subs_main["RESOURCE_DICT"] = format_dict_tabs(DEFAULTS.get("RESOURCE", {}), indent_tabs=1)
    subs_main["BOOST_DICT"] = format_dict_tabs(DEFAULTS.get("BOOST", {}), indent_tabs=1)

    # Equipment
    equip_enabled = DEFAULTS.get("EQUIPMENT_ENABLED", [])
    equip_disabled = DEFAULTS.get("EQUIPMENT_NOT_ENABLED", [])
    subs_main["EQUIPMENT_ENABLED_LIST"] = format_equipment_list(equip_enabled)
    subs_main["EQUIPMENT_NOT_ENABLED_LIST"] = format_equipment_list(equip_disabled)

    # Stats – get from DEFAULTS or use the default
    stats_raw = DEFAULTS.get("STATS_RAW", "")
    if not stats_raw:
        stats_raw = DEFAULTS["STATS_RAW"]
    subs_main["STATS_RAW"] = stats_raw

    # --------------------------------------------------------------------
    # 2. Build substitution for TEXT_RACE_TEMPLATE
    # --------------------------------------------------------------------
    subs_text = {}
    subs_text["RACE_NAME"] = race_name
    subs_text["RACE_NAMES"] = DEFAULTS.get("IDENTITY", {}).get("NAMES", race_plural)
    subs_text["RACE_UPPER"] = race_upper

    # Pronouns – exact format: ["word1", "word2",]
    identity = DEFAULTS.get("IDENTITY", {})
    pronoun_keys = ["HE", "HEC", "HIM", "HIMC", "HIS", "HISC", "HIMSELF", "HIMSELFC", "CHILD", "CHILDC"]
    for key in pronoun_keys:
        items = identity.get(key, ["he", "she"] if "HE" in key else ["him", "her"])
        if items:
            quoted = ', '.join(f'"{w}"' for w in items)
            subs_text[f"PRONOUN_{key}"] = quoted + "," if items else ""
        else:
            subs_text[f"PRONOUN_{key}"] = ""

    # Cultural lists
    cultural_fields = ["HELLO", "GOODBYE", "CURSE", "INSULT", "INSULTING",
                       "LORD", "CITY", "OTHERS", "SELVES", "SELF", "CHILDREN"]
    for field in cultural_fields:
        items = DEFAULTS.get(field, [])
        subs_text[f"{field}_LIST"] = format_cultural_list(items)

    # Army names, pros, cons
    army = DEFAULTS.get("ARMY_NAMES", [])
    subs_text["ARMY_NAMES_LIST"] = format_cultural_list(army)

    pros = DEFAULTS.get("PROS", [])
    subs_text["PROS_LIST"] = format_cultural_list(pros)

    cons = DEFAULTS.get("CONS", [])
    subs_text["CONS_LIST"] = format_cultural_list(cons)

    # Descriptions – exact format with `",` on its own line
    desc_text = DEFAULTS.get("DESC_TEXT", f"{race_name}s, said to be the last creation of the gods. Excel at intelligent jobs and are decent farmers. They can be a constant headache with insanity, criminal behavior, and demands for lavish surroundings.")
    desc_long_text = DEFAULTS.get("DESC_LONG_TEXT", f"{race_name}s are regarded as the final creation of the Astarii, possessing free will and a flexible mind. Ancient {race_lower}s were immortal, but when they sided with Aminion in the second war of the gods, they were punished with mortality.\n{race_name}s make excellent researchers and administrators. They are also fairly good at farming.\n\nBread, Meat, Mushrooms, and Eggs are their favorite foods.")
    
    subs_text["DESC_TEXT"] = desc_text
    subs_text["DESC_LONG_TEXT"] = desc_long_text
    subs_text["CHALLENGE"] = DEFAULTS.get("CHALLENGE", "Medium")

    # --------------------------------------------------------------------
    # 3. Create folders
    # --------------------------------------------------------------------
    create_folder_structure(race_name, output_dir, copy_sprite, template_race)

    # --------------------------------------------------------------------
    # 4. Write files
    # --------------------------------------------------------------------
    main_content = MAIN_CONFIG_TEMPLATE.format(**subs_main)
    main_path = os.path.join(output_dir, f"init/race/{race_upper}.txt")
    os.makedirs(os.path.dirname(main_path), exist_ok=True)
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_content)

    text_content = TEXT_RACE_TEMPLATE.format(**subs_text)
    text_path = os.path.join(output_dir, f"text/race/{race_upper}.txt")
    os.makedirs(os.path.dirname(text_path), exist_ok=True)
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text_content)

    print(f"\n✅ Race '{race_name}' generated successfully!")
    print(f"   Main config: {main_path}")
    print(f"   Cultural file: {text_path}")


# ============================================
# FOLDER STRUCTURE
# ============================================

def create_folder_structure(race_name, output_dir="assets", copy_sprite=False, template_race="HUMAN"):
    race_upper = race_name.upper()

    folders = [
        "init/animal", "init/battle", "init/config", "init/disease", "init/event",
        "init/player", "init/race", "init/race/home", "init/religion", "init/resource",
        "init/room", "init/script", "init/settlement", "init/stats", "init/tech", "init/world",

        "text/animal", "text/campaign", "text/config", "text/dictionary", "text/disease",
        "text/event", "text/misc", "text/names", "text/names/world", "text/player",
        "text/race", "text/race/bio", "text/race/bio/specific", "text/race/king",
        "text/race/raider", "text/race/raider/message", "text/race/raider/name",
        "text/race/tourist", "text/religion", "text/resource", "text/room",
        "text/script", "text/settlement", "text/stats", "text/tech", "text/wiki", "text/world",

        "sprite/animal", "sprite/font", "sprite/game", "sprite/icon", "sprite/image",
        "sprite/menu", "sprite/race", "sprite/resource", "sprite/room",
        "sprite/settlement", "sprite/textures", "sprite/ui", "sprite/world",

        "sprite/race/battle", "sprite/race/extra", "sprite/race/face",
        "sprite/race/infant", "sprite/race/misc", "sprite/race/skeleton",
        "sprite/race/sleep", "sprite/race/worldcamp",
    ]

    print("\n📁 Creating folder structure...")
    for folder in folders:
        os.makedirs(os.path.join(output_dir, folder), exist_ok=True)

    # README
    readme_path = os.path.join(output_dir, "sprite", f"README_{race_upper}.txt")
    with open(readme_path, "w") as f:
        f.write(f"# Race: {race_name} (ID: {race_upper})\n\n")
        f.write("Place your sprite files here:\n")
        f.write(f"- sprite/race/{race_upper}.spr\n")
        f.write(f"- sprite/icon/24->race->{race_name}->0.png\n")
        f.write(f"- sprite/icon/32->race->{race_name}->0.png\n")

    if copy_sprite:
        print(f"   Copying sprites from {template_race}...")
        template_upper = template_race.upper()
        template_lower = template_race.lower()

        for ext in [".spr", ".png"]:
            src = os.path.join(output_dir, f"sprite/race/{template_upper}{ext}")
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(output_dir, f"sprite/race/{race_upper}{ext}"))
                print(f"     - Copied {template_upper}{ext}")

        for size in ["24", "32"]:
            src = os.path.join(output_dir, f"sprite/icon/{size}->race->{template_lower}->0.png")
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(output_dir, f"sprite/icon/{size}->race->{race_name}->0.png"))
                print(f"     - Copied {size}->race->{template_lower}->0.png")

    print("   ✅ Folder structure created.")


# ============================================
# CLI
# ============================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a new Songs of Syx race.")
    parser.add_argument("race_name", help="Name of the new race (e.g., Elf)")
    parser.add_argument("--output", "-o", default="assets", help="Output directory (default: assets)")
    parser.add_argument("--copy-sprites", "-c", action="store_true", help="Copy sprites from template")
    parser.add_argument("--template", "-t", default="HUMAN", help="Template race (default: HUMAN)")
    args = parser.parse_args()

    if not args.race_name.replace("_", "").isalpha():
        print("Error: Race name must contain only letters and underscores.")
        sys.exit(1)

    generate_race(args.race_name, args.output, args.copy_sprites, args.template)