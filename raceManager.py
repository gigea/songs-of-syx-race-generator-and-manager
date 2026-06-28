#!/usr/bin/env python3
"""
Songs of Syx - Race Editor
Load, edit and save existing races from the base game or any mod.
Self-contained – no external dependencies beyond Python standard library + tkinter.
"""

import os
import sys
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

# =============================================================================
# CONFIGURATION – edit these paths to match your installation
# =============================================================================
BASE_GAME_PATH = r"C:\Games-C\Songs of Syx"
MODS_PATH = r"C:\Users\Rida\AppData\Roaming\songsofsyx\mods"

# =============================================================================
# FORMATTING HELPERS & TEMPLATES (copied from generate_race.py)
# =============================================================================

# --- Templates ---
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

# --- Formatting helpers ---
def format_list_tabs(items, indent_tabs=2):
    if not items:
        return ""
    prefix = "\t" * indent_tabs
    lines = [f"{prefix}{item}," for item in items]
    return "\n".join(lines)

def format_dict_tabs(d, indent_tabs=2):
    if not d:
        return ""
    prefix = "\t" * indent_tabs
    lines = []
    for k, v in d.items():
        if isinstance(v, bool):
            v_str = "true" if v else "false"
        elif isinstance(v, str):
            v_str = v
        else:
            v_str = str(v)
        lines.append(f"{prefix}{k}: {v_str},")
    return "\n".join(lines)

def format_equipment_list(items):
    if not items:
        return ""
    return "\n\t".join(f"{item}," for item in items)

def format_cultural_list(items):
    if not items:
        return ""
    return "\n\t".join(f'"{item}",' for item in items)

# =============================================================================
# PARSER – converts the custom config format to Python dicts
# =============================================================================

class RaceParser:
    @staticmethod
    def parse_main_file(filepath):
        return RaceParser._parse_file(filepath, is_main=True)

    @staticmethod
    def parse_text_file(filepath):
        return RaceParser._parse_file(filepath, is_main=False)

    @staticmethod
    def _parse_file(filepath, is_main):
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        # Tokenizer with improved handling of identifiers like "24->race->Human->0"
        tokens = []
        i = 0
        length = len(text)
        line_no = 1
        col = 1
        in_string = False
        escape = False
        current_token = ''

        while i < length:
            ch = text[i]

            if in_string:
                if escape:
                    escape = False
                    current_token += ch
                elif ch == '\\':
                    escape = True
                    current_token += ch
                elif ch == '"':
                    in_string = False
                    current_token += ch
                    tokens.append(('STRING', current_token, line_no, col))
                    current_token = ''
                else:
                    current_token += ch
                i += 1
                continue

            if ch in ' \t':
                i += 1
                col += 1
                continue

            if ch == '\n':
                line_no += 1
                col = 1
                i += 1
                continue

            if ch == '"':
                in_string = True
                current_token = '"'
                i += 1
                col += 1
                continue

            # Try to parse a number
            if ch.isdigit() or (ch == '-' and i+1 < length and text[i+1].isdigit()):
                start_i = i
                start_col = col
                num_str = ''
                # collect digits and optional dot
                while i < length and (text[i].isdigit() or text[i] == '.'):
                    num_str += text[i]
                    i += 1
                    col += 1
                # Check if next char is part of an identifier (letter, '_', '*', '-', '>')
                # If so, we need to treat the whole as identifier
                if i < length and (text[i].isalpha() or text[i] in '_*-'):
                    # Revert and treat as identifier
                    i = start_i
                    col = start_col
                    ident = ''
                    while i < length and (text[i].isalnum() or text[i] in '_*-.'):
                        ident += text[i]
                        i += 1
                        col += 1
                    tokens.append(('IDENTIFIER', ident, line_no, col))
                else:
                    # It's a number
                    if '.' in num_str:
                        tokens.append(('NUMBER', num_str, line_no, col))
                    else:
                        tokens.append(('NUMBER', num_str, line_no, col))
                continue

            # Identifiers (letters, underscore, star, also hyphen and greater-than if not starting with digit)
            if ch.isalpha() or ch == '_' or ch == '*':
                ident = ''
                while i < length and (text[i].isalnum() or text[i] in '_*-.'):
                    ident += text[i]
                    i += 1
                    col += len(ident)
                # Check if boolean
                if ident.lower() == 'true':
                    tokens.append(('BOOLEAN', True, line_no, col))
                elif ident.lower() == 'false':
                    tokens.append(('BOOLEAN', False, line_no, col))
                else:
                    tokens.append(('IDENTIFIER', ident, line_no, col))
                continue

            # Single character tokens
            if ch in '{}[],:':
                tokens.append((ch, ch, line_no, col))
                i += 1
                col += 1
                continue

            # Skip any other characters (shouldn't happen)
            i += 1
            col += 1

        # Parser
        class _Parser:
            def __init__(self, tokens):
                self.tokens = tokens
                self.pos = 0

            def peek(self):
                if self.pos < len(self.tokens):
                    return self.tokens[self.pos]
                return None

            def next_token(self):
                tok = self.peek()
                if tok:
                    self.pos += 1
                return tok

            def expect(self, typ, value=None):
                tok = self.next_token()
                if not tok:
                    raise SyntaxError(f"Expected {typ} but got EOF")
                if tok[0] != typ and (value is not None and tok[1] != value):
                    raise SyntaxError(f"Expected {typ}:{value} but got {tok[0]}:{tok[1]}")
                return tok

            def parse(self):
                result = {}
                while self.peek():
                    tok = self.peek()
                    if tok[0] == 'IDENTIFIER':
                        key = tok[1]
                        self.next_token()
                        self.expect(':')
                        value = self.parse_value()
                        result[key] = value
                    else:
                        self.next_token()
                return result

            def parse_value(self):
                tok = self.peek()
                if tok is None:
                    return None
                if tok[0] == '{':
                    return self.parse_dict()
                elif tok[0] == '[':
                    return self.parse_list()
                elif tok[0] == 'BOOLEAN':
                    self.next_token()
                    return tok[1]
                elif tok[0] == 'NUMBER':
                    self.next_token()
                    val = tok[1]
                    return float(val) if '.' in val else int(val)
                elif tok[0] == 'STRING':
                    self.next_token()
                    return tok[1][1:-1]
                elif tok[0] == 'IDENTIFIER':
                    self.next_token()
                    return tok[1]
                else:
                    self.next_token()
                    return None

            def parse_dict(self):
                self.expect('{')
                result = {}
                while True:
                    tok = self.peek()
                    if tok is None:
                        break
                    if tok[0] == '}':
                        self.next_token()
                        break
                    if tok[0] == 'IDENTIFIER':
                        key = tok[1]
                        self.next_token()
                    elif tok[0] == 'STRING':
                        key = tok[1][1:-1]
                        self.next_token()
                    else:
                        self.next_token()
                        continue
                    self.expect(':')
                    value = self.parse_value()
                    result[key] = value
                    if self.peek() and self.peek()[0] == ',':
                        self.next_token()
                return result

            def parse_list(self):
                self.expect('[')
                result = []
                while True:
                    tok = self.peek()
                    if tok is None:
                        break
                    if tok[0] == ']':
                        self.next_token()
                        break
                    value = self.parse_value()
                    result.append(value)
                    if self.peek() and self.peek()[0] == ',':
                        self.next_token()
                return result

        return _Parser(tokens).parse()

# =============================================================================
# RACE EDITOR GUI
# =============================================================================

class RaceEditorGUI:
    def __init__(self, root):
        self.root = root
        root.title("Songs of Syx Race Editor")
        root.geometry("1100x900")
        root.minsize(1000, 750)

        self.current_race = None
        self.main_path = None
        self.text_path = None
        self.main_data = {}
        self.text_data = {}
        self.race_list = []

        # Top frame
        top = ttk.Frame(root)
        top.pack(fill="x", padx=10, pady=5)

        ttk.Label(top, text="Race:").pack(side="left")
        self.race_combo = ttk.Combobox(top, state="readonly", width=45)
        self.race_combo.pack(side="left", padx=5)
        self.race_combo.bind("<<ComboboxSelected>>", self.load_race)

        ttk.Button(top, text="Refresh List", command=self.refresh_list).pack(side="left", padx=2)
        ttk.Button(top, text="Load from File...", command=self.load_from_file).pack(side="left", padx=2)
        ttk.Button(top, text="💾 Save", command=self.save_race).pack(side="left", padx=2)

        self.status = ttk.Label(root, text="Ready", relief="sunken", anchor="w")
        self.status.pack(fill="x", padx=10, pady=(0,5))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.build_tabs()
        self.refresh_list()

    # ---- Tab builders ----
    def build_tabs(self):
        # Identity
        self.tab_identity = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_identity, text="Identity")
        self._build_identity_tab()

        # Properties
        self.tab_props = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_props, text="Properties")
        self._build_props_tab()

        # Population
        self.tab_pop = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pop, text="Population")
        self._build_pop_tab()

        # Preferences
        self.tab_pref = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pref, text="Preferences")
        self._build_pref_tab()

        # Traits
        self.tab_traits = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_traits, text="Traits")
        self._build_traits_tab()

        # Resources & Stats
        self.tab_res = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_res, text="Resources & Stats")
        self._build_res_tab()

        # Boosts
        self.tab_boosts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_boosts, text="Boosts")
        self._build_boosts_tab()

        # Cultural
        self.tab_cultural = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_cultural, text="Cultural")
        self._build_cultural_tab()

        # Equipment
        self.tab_equip = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_equip, text="Equipment")
        self._build_equip_tab()

    def _build_identity_tab(self):
        parent = ttk.Frame(self.tab_identity)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        canvas = tk.Canvas(parent)
        scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.race_name_var = tk.StringVar()
        ttk.Label(inner, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(inner, textvariable=self.race_name_var, width=25).grid(row=0, column=1, sticky="w", padx=5, pady=2)

        self.race_names_var = tk.StringVar()
        ttk.Label(inner, text="Plural:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(inner, textvariable=self.race_names_var, width=25).grid(row=1, column=1, sticky="w", padx=5, pady=2)

        self.possessive_var = tk.StringVar()
        ttk.Label(inner, text="Possessive:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(inner, textvariable=self.possessive_var, width=25).grid(row=2, column=1, sticky="w", padx=5, pady=2)

        self.possessives_var = tk.StringVar()
        ttk.Label(inner, text="Possessive Plural:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(inner, textvariable=self.possessives_var, width=25).grid(row=3, column=1, sticky="w", padx=5, pady=2)

        self.pronoun_vars = {}
        pronoun_keys = ["HE", "HEC", "HIM", "HIMC", "HIS", "HISC", "HIMSELF", "HIMSELFC", "CHILD", "CHILDC"]
        for i, key in enumerate(pronoun_keys):
            row = 4 + i
            ttk.Label(inner, text=f"PRONOUN_{key}:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
            var = tk.StringVar()
            entry = ttk.Entry(inner, textvariable=var, width=40)
            entry.grid(row=row, column=1, sticky="w", padx=5, pady=2)
            self.pronoun_vars[key] = var

        self.challenge_var = tk.StringVar(value="Medium")
        ttk.Label(inner, text="Challenge:").grid(row=len(pronoun_keys)+4, column=0, sticky="w", padx=5, pady=2)
        ttk.Combobox(inner, textvariable=self.challenge_var, values=["Easy", "Medium", "Hard"], state="readonly", width=10).grid(row=len(pronoun_keys)+4, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(inner, text="Short Description:").grid(row=len(pronoun_keys)+5, column=0, sticky="nw", padx=5, pady=2)
        self.desc_text = scrolledtext.ScrolledText(inner, height=4, width=60)
        self.desc_text.grid(row=len(pronoun_keys)+5, column=1, padx=5, pady=2)

        ttk.Label(inner, text="Long Description:").grid(row=len(pronoun_keys)+6, column=0, sticky="nw", padx=5, pady=2)
        self.desc_long_text = scrolledtext.ScrolledText(inner, height=6, width=60)
        self.desc_long_text.grid(row=len(pronoun_keys)+6, column=1, padx=5, pady=2)

    def _build_props_tab(self):
        parent = ttk.Frame(self.tab_props)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        self.prop_vars = {}
        props = [
            ("Height", "HEIGHT", 6),
            ("Width", "WIDTH", 9),
            ("Baby Days", "BABY_DAYS", 12),
            ("Child Days", "CHILD_DAYS", 80),
            ("Corpse Decay", "CORPSE_DECAY", "true"),
            ("Sleeps", "SLEEPS", "true"),
            ("Slave Price", "SLAVE_PRICE", 11),
            ("Slave Price Recovery", "SLAVE_PRICE_RECOVERY", 0.5),
            ("Raid Mercinary", "RAID_MERCINARY", 1.0),
            ("Tourist Occurrence", "TOURIST_OCCURENCE", 1.0),
            ("Tourist Credits", "TOURIST_CREDITS", 0.75),
        ]
        for i, (label, key, default) in enumerate(props):
            ttk.Label(parent, text=label+":").grid(row=i, column=0, sticky="w", padx=5, pady=3)
            var = tk.StringVar(value=str(default))
            entry = ttk.Entry(parent, textvariable=var, width=15)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            self.prop_vars[key] = var

    def _build_pop_tab(self):
        parent = ttk.Frame(self.tab_pop)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        self.pop_vars = {}
        ttk.Label(parent, text="Population Max:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        var = tk.StringVar(value="1.0")
        entry = ttk.Entry(parent, textvariable=var, width=15)
        entry.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        self.pop_vars["MAX"] = var

        ttk.Label(parent, text="Growth:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        var = tk.StringVar(value="0.075")
        entry = ttk.Entry(parent, textvariable=var, width=15)
        entry.grid(row=1, column=1, sticky="w", padx=5, pady=3)
        self.pop_vars["GROWTH"] = var

        self.climate_vars = {}
        ttk.Label(parent, text="Climate:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        for i, climate in enumerate(["COLD", "TEMPERATE", "HOT"]):
            ttk.Label(parent, text=f"  {climate}:").grid(row=3+i, column=0, sticky="w", padx=15, pady=2)
            var = tk.StringVar(value="0.8" if climate != "TEMPERATE" else "1.0")
            entry = ttk.Entry(parent, textvariable=var, width=10)
            entry.grid(row=3+i, column=1, sticky="w", padx=5, pady=2)
            self.climate_vars[climate] = var

        self.terrain_vars = {}
        ttk.Label(parent, text="Terrain:").grid(row=6, column=0, sticky="w", padx=5, pady=3)
        for i, terrain in enumerate(["MOUNTAIN", "FOREST", "NONE"]):
            ttk.Label(parent, text=f"  {terrain}:").grid(row=7+i, column=0, sticky="w", padx=15, pady=2)
            var = tk.StringVar(value="0.2" if terrain != "NONE" else "1.5")
            entry = ttk.Entry(parent, textvariable=var, width=10)
            entry.grid(row=7+i, column=1, sticky="w", padx=5, pady=2)
            self.terrain_vars[terrain] = var

    def _build_pref_tab(self):
        parent = ttk.Frame(self.tab_pref)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        pref_notebook = ttk.Notebook(parent)
        pref_notebook.pack(fill="both", expand=True)

        # Food
        f = ttk.Frame(pref_notebook)
        pref_notebook.add(f, text="Food")
        ttk.Label(f, text="Food (comma-separated):").pack(anchor="w", padx=5, pady=5)
        self.food_text = scrolledtext.ScrolledText(f, height=4, width=60)
        self.food_text.pack(anchor="w", padx=5, fill="x")
        self.food_text.insert("1.0", "BREAD, MEAT, MUSHROOM, EGG")

        # Drink
        d = ttk.Frame(pref_notebook)
        pref_notebook.add(d, text="Drink")
        ttk.Label(d, text="Drink (comma-separated):").pack(anchor="w", padx=5, pady=5)
        self.drink_text = scrolledtext.ScrolledText(d, height=4, width=60)
        self.drink_text.pack(anchor="w", padx=5, fill="x")
        self.drink_text.insert("1.0", "*")

        # Road
        r = ttk.Frame(pref_notebook)
        pref_notebook.add(r, text="Road")
        ttk.Label(r, text="Road (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.road_text = scrolledtext.ScrolledText(r, height=5, width=60)
        self.road_text.pack(anchor="w", padx=5, fill="x")
        self.road_text.insert("1.0", "*:0.1\nSTONE1:0.5\nSTONE2:0.8\nDECOR1:1.0")

        # Structure
        s = ttk.Frame(pref_notebook)
        pref_notebook.add(s, text="Structure")
        ttk.Label(s, text="Structure (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.struct_text = scrolledtext.ScrolledText(s, height=5, width=60)
        self.struct_text.pack(anchor="w", padx=5, fill="x")
        self.struct_text.insert("1.0", "MOUNTAIN:0.2\nSTONE:0.7\nGRAND:1.0\nWOOD:0.5\nOUTDOORS:0.3")

        # Pool
        p = ttk.Frame(pref_notebook)
        pref_notebook.add(p, text="Pool")
        ttk.Label(p, text="Pool (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.pool_text = scrolledtext.ScrolledText(p, height=3, width=60)
        self.pool_text.pack(anchor="w", padx=5, fill="x")
        self.pool_text.insert("1.0", "POOL_STONE:1.0")

        # Work
        w = ttk.Frame(pref_notebook)
        pref_notebook.add(w, text="Work")
        ttk.Label(w, text="Work (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.work_text = scrolledtext.ScrolledText(w, height=12, width=60)
        self.work_text.pack(anchor="w", padx=5, fill="x")
        default_work = (
            "_ASYLUM:0.75\n_EMBASSY:1.0\n_EXPORT:0.25\n_INN:0.75\n_POLICE:0.5\n"
            "ADMIN_NORMAL:0.75\nBARBER_NORMAL:0.75\nGRAVEYARD_NORMAL:0.5\n"
            "LABORATORY_NORMAL:2.0\nLIBRARY_NORMAL:2.0\nMARKET_NORMAL:0.5\n"
            "MINE_GEM:-1.0\nPHYSICIAN_NORMAL:1.0\nREFINER_COALER:-0.75\n"
            "REFINER_SMELTER:-0.75\nREFINER_WEAVER:0.25\nSCHOOL_NORMAL:0.75\n"
            "SPEAKER_NORMAL:0.5\nSTAGE_NORMAL:1.0\nTAVERN_NORMAL:0.75\n"
            "TOMB_NORMAL:0.75\nUNIVERSITY_NORMAL:1.0\nWORKSHOP_BOWYER:0.75\n"
            "WORKSHOP_CARPENTER:0.75\nWORKSHOP_JEWELRY:0.75\nWORKSHOP_MECHANIC:0.75\n"
            "WORKSHOP_SMITHY:0.25\nWORKSHOP_TAILOR:0.75"
        )
        self.work_text.insert("1.0", default_work)

        # Other Races
        o = ttk.Frame(pref_notebook)
        pref_notebook.add(o, text="Other Races")
        ttk.Label(o, text="Other Races (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.other_races_text = scrolledtext.ScrolledText(o, height=8, width=60)
        self.other_races_text.pack(anchor="w", padx=5, fill="x")
        self.other_races_text.insert("1.0",
            "GARTHIMI:0.75\nCRETONIAN:0.75\nCANTOR:0.75\nQ_AMEVIA:0.75\n"
            "DONDORIAN:0.75\nARGONOSH:0.75\nTILAPI:0.2")

        # Building Override
        b = ttk.Frame(pref_notebook)
        pref_notebook.add(b, text="Building Override")
        ttk.Label(b, text="Building Override (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.building_override_text = scrolledtext.ScrolledText(b, height=3, width=60)
        self.building_override_text.pack(anchor="w", padx=5, fill="x")
        self.building_override_text.insert("1.0", "CIVIC_L_STANDS:1.5")

    def _build_traits_tab(self):
        parent = ttk.Frame(self.tab_traits)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(parent, text="Traits (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.traits_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        self.traits_text.pack(anchor="w", padx=5, fill="x")
        self.traits_text.insert("1.0", "FIGHTER:0.1\nGLUTTON:0.1\nSPRINTER:0.1")

    def _build_res_tab(self):
        parent = ttk.Frame(self.tab_res)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(parent, text="Resources (key:value, one per line):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.resources_text = scrolledtext.ScrolledText(parent, height=3, width=60)
        self.resources_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        self.resources_text.insert("1.0", "MEAT:30\nLEATHER:10")

        ttk.Label(parent, text="Stats (raw block, preserve formatting):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.stats_text = scrolledtext.ScrolledText(parent, height=12, width=80)
        self.stats_text.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        default_stats = '''\tACCESS_NOISE: {
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
        self.stats_text.insert("1.0", default_stats)

    def _build_boosts_tab(self):
        parent = ttk.Frame(self.tab_boosts)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(parent, text="Boosts (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.boosts_text = scrolledtext.ScrolledText(parent, height=15, width=80)
        self.boosts_text.pack(anchor="w", padx=5, fill="both", expand=True)
        default_boosts = (
            "PHYSICS_RESISTANCE_COLD>ADD:-0.15\nPHYSICS_RESISTANCE_HOT>ADD:-0.15\n"
            "PHYSICS_DEATH_AGE>MUL:0.8\nBATTLE_BLUNT_ATTACK>ADD:10\n"
            "CIVIC_IMMIGRATION>MUL:1.5\nROOM_UNIVERSITY*>MUL:1.5\n"
            "ROOM_SCHOOL*>MUL:1.5\nBEHAVIOUR_LAWFULNESS>MUL:0.75\n"
            "BEHAVIOUR_SANITY>MUL:0.8\nROOM_FARM*>MUL:1.1\n"
            "ROOM_ORCHARD*>MUL:1.1\nROOM_LIBRARY_NORMAL>MUL:1.25\n"
            "ROOM_ADMIN_NORMAL>MUL:1.25\nROOM_LABORATORY_NORMAL>MUL:1.25"
        )
        self.boosts_text.insert("1.0", default_boosts)

    def _build_cultural_tab(self):
        parent = ttk.Frame(self.tab_cultural)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        canvas = tk.Canvas(parent)
        scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.cultural_vars = {}
        cultural_fields = [
            ("HELLO", "Greetings, Salutations, Hail"),
            ("GOODBYE", "Farewell, Until next time, Safe travels"),
            ("CURSE", "By the great horn spoon!, Gods below!"),
            ("INSULT", "fool, idiot, imbecile"),
            ("INSULTING", "foolish, moronic, brain-drained"),
            ("LORD", "Lord, Master, Liege"),
            ("CITY", "city, metropolis, town"),
            ("OTHERS", "others, exotics"),
            ("SELVES", "fellows, subjects"),
            ("SELF", "fellow, subject"),
            ("CHILDREN", "children"),
        ]
        for i, (key, default) in enumerate(cultural_fields):
            ttk.Label(inner, text=f"{key}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            var = tk.StringVar(value=default)
            entry = ttk.Entry(inner, textvariable=var, width=60)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            self.cultural_vars[key] = var

        row = len(cultural_fields)
        ttk.Label(inner, text="Army Names (one per line):").grid(row=row, column=0, sticky="nw", padx=5, pady=5)
        self.army_names_text = scrolledtext.ScrolledText(inner, height=8, width=60)
        self.army_names_text.grid(row=row, column=1, padx=5, pady=5)
        self.army_names_text.insert("1.0",
            "Shields of Vengeance\nSwords of Tomorrow\nLegends of Lake Hoth\n"
            "The Inithil Rangers\nDarth's Opulent Oppressors\nThe Boys\n"
            "The Moster Hunters\nThe Unbreakables\nThe Immortals\n"
            "The Force of the Astarii\nThe Glimmering Blades\nThe Deathstalkers\n"
            "The Barbarians\nThe League of Extraordinary Gentlemen\n"
            "The Brotherhood of Ergoth\nThe Swordsmen of Naath")

        row += 1
        ttk.Label(inner, text="Pros (one per line):").grid(row=row, column=0, sticky="nw", padx=5, pady=5)
        self.pros_text = scrolledtext.ScrolledText(inner, height=5, width=60)
        self.pros_text.grid(row=row, column=1, padx=5, pady=5)
        self.pros_text.insert("1.0", "Excellent scientists and managers\nGood farmers\nGood learning rate")

        row += 1
        ttk.Label(inner, text="Cons (one per line):").grid(row=row, column=0, sticky="nw", padx=5, pady=5)
        self.cons_text = scrolledtext.ScrolledText(inner, height=5, width=60)
        self.cons_text.grid(row=row, column=1, padx=5, pady=5)
        self.cons_text.insert("1.0", "Unremarkable in battle\nCriminal and mentally unstable\nLimited natural skills\nDifficult to please")

    def _build_equip_tab(self):
        parent = ttk.Frame(self.tab_equip)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(parent, text="Enabled (comma-separated):").pack(anchor="w", padx=5, pady=5)
        self.equip_enabled_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.equip_enabled_var, width=80).pack(anchor="w", padx=5)
        ttk.Label(parent, text="Disabled (comma-separated):").pack(anchor="w", padx=5, pady=5)
        self.equip_disabled_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.equip_disabled_var, width=80).pack(anchor="w", padx=5)

    # -------------------------------------------------------------------------
    # Race discovery
    # -------------------------------------------------------------------------

    def refresh_list(self):
        races = []
        base_path = os.path.join(BASE_GAME_PATH, "assets", "init", "race")
        if os.path.exists(base_path):
            for f in os.listdir(base_path):
                if f.endswith('.txt'):
                    races.append(("Base Game", f[:-4], base_path))
        if os.path.exists(MODS_PATH):
            for mod in os.listdir(MODS_PATH):
                mod_dir = os.path.join(MODS_PATH, mod)
                if os.path.isdir(mod_dir):
                    for ver in os.listdir(mod_dir):
                        ver_dir = os.path.join(mod_dir, ver)
                        race_dir = os.path.join(ver_dir, "assets", "init", "race")
                        if os.path.exists(race_dir):
                            for f in os.listdir(race_dir):
                                if f.endswith('.txt'):
                                    races.append((f"{mod} ({ver})", f[:-4], race_dir))
        self.race_list = races
        self.race_combo['values'] = [f"{src}: {race}" for src, race, _ in races]
        if races:
            self.race_combo.current(0)
        self.status.config(text=f"Found {len(races)} races")

    # -------------------------------------------------------------------------
    # Load
    # -------------------------------------------------------------------------

    def load_race(self, event=None):
        selection = self.race_combo.get()
        if not selection:
            return
        parts = selection.split(": ", 1)
        if len(parts) != 2:
            return
        src_desc, race_name = parts
        for src, race, race_dir in self.race_list:
            if f"{src}: {race}" == selection:
                main_path = os.path.join(race_dir, f"{race}.txt")
                base = os.path.dirname(os.path.dirname(race_dir))
                text_path = os.path.join(base, "text", "race", f"{race}.txt")
                if os.path.exists(main_path) and os.path.exists(text_path):
                    self.load_files(main_path, text_path, race)
                    self.status.config(text=f"Loaded {race} from {src_desc}")
                else:
                    messagebox.showerror("Error", f"Files not found for {race}")
                break

    def load_from_file(self):
        filepath = filedialog.askopenfilename(
            title="Select main config file",
            filetypes=[("Race files", "*.txt")]
        )
        if not filepath:
            return
        base = os.path.dirname(os.path.dirname(filepath))
        text_path = os.path.join(base, "text", "race", os.path.basename(filepath))
        if not os.path.exists(text_path):
            text_path = filedialog.askopenfilename(
                title="Select cultural text file",
                filetypes=[("Race files", "*.txt")]
            )
            if not text_path:
                return
        race_name = os.path.splitext(os.path.basename(filepath))[0]
        self.load_files(filepath, text_path, race_name)

    def load_files(self, main_path, text_path, race_name):
        try:
            self.main_data = RaceParser.parse_main_file(main_path)
            self.text_data = RaceParser.parse_text_file(text_path)
            self.main_path = main_path
            self.text_path = text_path
            self.current_race = race_name
            self.populate_gui()
            self.status.config(text=f"Loaded {race_name}")
        except Exception as e:
            messagebox.showerror("Parse Error", f"Failed to parse:\n{str(e)}")

    # -------------------------------------------------------------------------
    # Populate GUI
    # -------------------------------------------------------------------------

    def populate_gui(self):
        # Identity
        self.race_name_var.set(self.text_data.get("NAME", ""))
        self.race_names_var.set(self.text_data.get("NAMES", ""))
        self.possessive_var.set(self.text_data.get("POSSESSIVE", ""))
        self.possessives_var.set(self.text_data.get("POSSESSIVES", ""))
        for key in self.pronoun_vars:
            val = self.text_data.get(f"PRONOUN_{key}", [])
            if val:
                self.pronoun_vars[key].set(", ".join(val))
        self.challenge_var.set(self.text_data.get("CHALLENGE", "Medium"))
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", self.text_data.get("DESC", ""))
        self.desc_long_text.delete("1.0", "end")
        self.desc_long_text.insert("1.0", self.text_data.get("DESC_LONG", ""))

        # Properties
        for key, var in self.prop_vars.items():
            val = self.main_data.get(key)
            if val is not None:
                var.set(str(val).lower() if isinstance(val, bool) else str(val))

        # Population
        pop = self.main_data.get("POPULATION", {})
        self.pop_vars["MAX"].set(str(pop.get("MAX", 1.0)))
        self.pop_vars["GROWTH"].set(str(pop.get("GROWTH", 0.075)))
        climate = pop.get("CLIMATE", {})
        for cl, var in self.climate_vars.items():
            var.set(str(climate.get(cl, 0.8)))
        terrain = pop.get("TERRAIN", {})
        for tr, var in self.terrain_vars.items():
            var.set(str(terrain.get(tr, 0.2)))

        # Preferences
        pref = self.main_data.get("PREFERRED", {})
        self._set_text_list(self.food_text, pref.get("FOOD", []))
        self._set_text_list(self.drink_text, pref.get("DRINK", []))
        self._set_text_dict(self.road_text, pref.get("ROAD", {}))
        self._set_text_dict(self.struct_text, pref.get("STRUCTURE", {}))
        self._set_text_dict(self.pool_text, pref.get("POOL", {}))
        self._set_text_dict(self.work_text, pref.get("WORK", {}))
        self._set_text_dict(self.other_races_text, pref.get("OTHER_RACES", {}))
        self._set_text_dict(self.building_override_text, pref.get("BUILDING_OVERRIDE", {}))

        # Traits
        self._set_text_dict(self.traits_text, self.main_data.get("TRAITS", {}))

        # Resources
        self._set_text_dict(self.resources_text, self.main_data.get("RESOURCE", {}))

        # Stats – we reconstruct from parsed data if possible, else leave placeholder
        stats = self.main_data.get("STATS", {})
        if stats:
            lines = []
            for key, val in stats.items():
                if isinstance(val, dict):
                    inner = "\n".join(f"\t\t{k}: {v}," if not isinstance(v, bool) else f"\t\t{k}: {str(v).lower()}," for k, v in val.items())
                    lines.append(f"\t{key}: {{\n{inner}\n\t}},")
                else:
                    lines.append(f"\t{key}: {val},")
            stats_raw = "\n".join(lines)
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", stats_raw)

        # Boosts
        self._set_text_dict(self.boosts_text, self.main_data.get("BOOST", {}))

        # Cultural lists
        for key, var in self.cultural_vars.items():
            vals = self.text_data.get(key, [])
            var.set(", ".join(vals))
        self.army_names_text.delete("1.0", "end")
        self.army_names_text.insert("1.0", "\n".join(self.text_data.get("ARMY_NAMES", [])))
        self.pros_text.delete("1.0", "end")
        self.pros_text.insert("1.0", "\n".join(self.text_data.get("PROS", [])))
        self.cons_text.delete("1.0", "end")
        self.cons_text.insert("1.0", "\n".join(self.text_data.get("CONS", [])))

        # Equipment
        self.equip_enabled_var.set(", ".join(self.main_data.get("EQUIPMENT_ENABLED", [])))
        self.equip_disabled_var.set(", ".join(self.main_data.get("EQUIPMENT_NOT_ENABLED", [])))

    def _set_text_list(self, widget, data):
        widget.delete("1.0", "end")
        if data:
            widget.insert("1.0", ", ".join(str(x) for x in data))

    def _set_text_dict(self, widget, data):
        widget.delete("1.0", "end")
        if data:
            lines = [f"{k}: {v}" for k, v in data.items()]
            widget.insert("1.0", "\n".join(lines))

    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------

    def save_race(self):
        if not self.current_race:
            messagebox.showinfo("Info", "No race loaded.")
            return
        choice = messagebox.askyesno("Save", "Save in place (overwrite original)?")
        if choice:
            target_main = self.main_path
            target_text = self.text_path
        else:
            target_dir = filedialog.askdirectory(title="Select target folder (must contain 'assets' subfolder)")
            if not target_dir:
                return
            race_name = self.current_race
            target_main = os.path.join(target_dir, "assets", "init", "race", f"{race_name}.txt")
            target_text = os.path.join(target_dir, "assets", "text", "race", f"{race_name}.txt")
            os.makedirs(os.path.dirname(target_main), exist_ok=True)
            os.makedirs(os.path.dirname(target_text), exist_ok=True)

        # Gather values
        overrides = self._gather_values()

        # Build main config
        race_name = self.current_race
        race_upper = race_name.upper()
        race_lower = race_name.lower()
        race_plural = self.race_names_var.get().strip() or (race_name + "s")

        subs_main = {}
        simple_keys = [
            "HEIGHT", "WIDTH", "BABY_DAYS", "CHILD_DAYS", "CORPSE_DECAY", "SLEEPS",
            "SLAVE_PRICE", "SLAVE_PRICE_RECOVERY", "RAID_MERCINARY",
            "TOURIST_OCCURENCE", "TOURIST_CREDITS", "POPULATION_MAX", "POPULATION_GROWTH"
        ]
        for k in simple_keys:
            val = overrides.get(k, "")
            if isinstance(val, bool):
                subs_main[k] = "true" if val else "false"
            else:
                subs_main[k] = str(val)
        subs_main["RACE_NAME"] = race_name
        subs_main["RACE_UPPER"] = race_upper

        climate = overrides.get("CLIMATE", {})
        subs_main["CLIMATE_COLD"] = str(climate.get("COLD", 0.8))
        subs_main["CLIMATE_TEMPERATE"] = str(climate.get("TEMPERATE", 1.0))
        subs_main["CLIMATE_HOT"] = str(climate.get("HOT", 0.8))

        terrain = overrides.get("TERRAIN", {})
        subs_main["TERRAIN_MOUNTAIN"] = str(terrain.get("MOUNTAIN", 0.2))
        subs_main["TERRAIN_FOREST"] = str(terrain.get("FOREST", 0.2))
        subs_main["TERRAIN_NONE"] = str(terrain.get("NONE", 1.5))

        subs_main["FOOD_LIST"] = format_list_tabs(overrides.get("FOOD", []), indent_tabs=2)
        subs_main["DRINK_LIST"] = format_list_tabs(overrides.get("DRINK", []), indent_tabs=2)
        subs_main["ROAD_DICT"] = format_dict_tabs(overrides.get("ROAD", {}), indent_tabs=2)
        subs_main["STRUCTURE_DICT"] = format_dict_tabs(overrides.get("STRUCTURE", {}), indent_tabs=2)
        subs_main["POOL_DICT"] = format_dict_tabs(overrides.get("POOL", {}), indent_tabs=2)
        subs_main["WORK_DICT"] = format_dict_tabs(overrides.get("WORK", {}), indent_tabs=2)
        subs_main["OTHER_RACES_DICT"] = format_dict_tabs(overrides.get("OTHER_RACES", {}), indent_tabs=2)
        subs_main["BUILDING_OVERRIDE_DICT"] = format_dict_tabs(overrides.get("BUILDING_OVERRIDE", {}), indent_tabs=2)

        subs_main["TRAITS_DICT"] = format_dict_tabs(overrides.get("TRAITS", {}), indent_tabs=1)
        subs_main["RESOURCE_DICT"] = format_dict_tabs(overrides.get("RESOURCE", {}), indent_tabs=1)
        subs_main["BOOST_DICT"] = format_dict_tabs(overrides.get("BOOST", {}), indent_tabs=1)

        equip_enabled = overrides.get("EQUIPMENT_ENABLED", [])
        equip_disabled = overrides.get("EQUIPMENT_NOT_ENABLED", [])
        subs_main["EQUIPMENT_ENABLED_LIST"] = format_equipment_list(equip_enabled)
        subs_main["EQUIPMENT_NOT_ENABLED_LIST"] = format_equipment_list(equip_disabled)

        stats_raw = self.stats_text.get("1.0", "end-1c").strip()
        subs_main["STATS_RAW"] = stats_raw

        main_content = MAIN_CONFIG_TEMPLATE.format(**subs_main)

        # Build cultural content
        subs_text = {}
        subs_text["RACE_NAME"] = race_name
        subs_text["RACE_NAMES"] = self.race_names_var.get().strip() or (race_name + "s")
        subs_text["RACE_UPPER"] = race_upper

        identity = overrides.get("IDENTITY", {})
        pronoun_keys = ["HE", "HEC", "HIM", "HIMC", "HIS", "HISC", "HIMSELF", "HIMSELFC", "CHILD", "CHILDC"]
        for key in pronoun_keys:
            items = identity.get(key, [])
            if items:
                subs_text[f"PRONOUN_{key}"] = ", ".join(f'"{w}"' for w in items) + ","
            else:
                subs_text[f"PRONOUN_{key}"] = ""

        cultural_fields = ["HELLO", "GOODBYE", "CURSE", "INSULT", "INSULTING",
                           "LORD", "CITY", "OTHERS", "SELVES", "SELF", "CHILDREN"]
        for field in cultural_fields:
            items = overrides.get(field, [])
            subs_text[f"{field}_LIST"] = format_cultural_list(items)

        army = overrides.get("ARMY_NAMES", [])
        subs_text["ARMY_NAMES_LIST"] = format_cultural_list(army)
        pros = overrides.get("PROS", [])
        subs_text["PROS_LIST"] = format_cultural_list(pros)
        cons = overrides.get("CONS", [])
        subs_text["CONS_LIST"] = format_cultural_list(cons)

        subs_text["DESC_TEXT"] = self.desc_text.get("1.0", "end-1c").strip()
        subs_text["DESC_LONG_TEXT"] = self.desc_long_text.get("1.0", "end-1c").strip()
        subs_text["CHALLENGE"] = overrides.get("CHALLENGE", "Medium")

        text_content = TEXT_RACE_TEMPLATE.format(**subs_text)

        # Write files
        try:
            with open(target_main, "w", encoding="utf-8") as f:
                f.write(main_content)
            with open(target_text, "w", encoding="utf-8") as f:
                f.write(text_content)
            messagebox.showinfo("Saved", f"Race saved to:\n{target_main}\n{target_text}")
            self.status.config(text=f"Saved {race_name}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save:\n{str(e)}")

    def _gather_values(self):
        overrides = {}

        for key, var in self.prop_vars.items():
            val = var.get().strip()
            if val.lower() == "true":
                overrides[key] = True
            elif val.lower() == "false":
                overrides[key] = False
            elif "." in val:
                overrides[key] = float(val)
            else:
                overrides[key] = int(val)

        overrides["CHALLENGE"] = self.challenge_var.get()

        overrides["MAX"] = float(self.pop_vars["MAX"].get())
        overrides["GROWTH"] = float(self.pop_vars["GROWTH"].get())
        overrides["CLIMATE"] = {cl: float(var.get()) for cl, var in self.climate_vars.items()}
        overrides["TERRAIN"] = {tr: float(var.get()) for tr, var in self.terrain_vars.items()}

        overrides["FOOD"] = self._parse_text_list(self.food_text)
        overrides["DRINK"] = self._parse_text_list(self.drink_text)
        overrides["ROAD"] = self._parse_text_dict(self.road_text)
        overrides["STRUCTURE"] = self._parse_text_dict(self.struct_text)
        overrides["POOL"] = self._parse_text_dict(self.pool_text)
        overrides["WORK"] = self._parse_text_dict(self.work_text)
        overrides["OTHER_RACES"] = self._parse_text_dict(self.other_races_text)
        overrides["BUILDING_OVERRIDE"] = self._parse_text_dict(self.building_override_text)

        overrides["TRAITS"] = self._parse_text_dict(self.traits_text)
        overrides["RESOURCE"] = self._parse_text_dict(self.resources_text)
        overrides["BOOST"] = self._parse_text_dict(self.boosts_text)

        overrides["EQUIPMENT_ENABLED"] = [x.strip() for x in self.equip_enabled_var.get().split(",") if x.strip()]
        overrides["EQUIPMENT_NOT_ENABLED"] = [x.strip() for x in self.equip_disabled_var.get().split(",") if x.strip()]

        identity = {}
        for key, var in self.pronoun_vars.items():
            identity[key] = [x.strip() for x in var.get().split(",") if x.strip()]
        identity["NAME"] = self.race_name_var.get()
        identity["NAMES"] = self.race_names_var.get()
        identity["POSSESSIVE"] = self.possessive_var.get()
        identity["POSSESSIVES"] = self.possessives_var.get()
        overrides["IDENTITY"] = identity

        for key, var in self.cultural_vars.items():
            overrides[key] = [x.strip() for x in var.get().split(",") if x.strip()]

        overrides["ARMY_NAMES"] = [x.strip() for x in self.army_names_text.get("1.0", "end-1c").split("\n") if x.strip()]
        overrides["PROS"] = [x.strip() for x in self.pros_text.get("1.0", "end-1c").split("\n") if x.strip()]
        overrides["CONS"] = [x.strip() for x in self.cons_text.get("1.0", "end-1c").split("\n") if x.strip()]

        return overrides

    def _parse_text_list(self, widget):
        content = widget.get("1.0", "end-1c").strip()
        if not content:
            return []
        return [x.strip() for x in content.replace("\n", ",").split(",") if x.strip()]

    def _parse_text_dict(self, widget):
        content = widget.get("1.0", "end-1c").strip()
        result = {}
        if not content:
            return result
        for line in content.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip()
                if v.lower() == "true":
                    result[k] = True
                elif v.lower() == "false":
                    result[k] = False
                elif "." in v:
                    result[k] = float(v)
                else:
                    try:
                        result[k] = int(v)
                    except ValueError:
                        result[k] = v
        return result

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = RaceEditorGUI(root)
    root.mainloop()