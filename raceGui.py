import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

# Try to import the generator
try:
    import raceGen
    print("✅ generate_race imported successfully")
except ImportError as e:
    print(f"❌ Failed to import generate_race: {e}")
    sys.exit(1)

class FullRaceGeneratorGUI:
    def __init__(self, root):
        self.root = root
        root.title("Songs of Syx Race Generator - Full Customization")
        root.geometry("1050x850")
        root.minsize(1000, 750)

        # Main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # --- Tab 1: Identity ---
        self.tab_identity = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_identity, text="Identity")
        self.build_identity_tab()

        # --- Tab 2: Properties ---
        self.tab_props = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_props, text="Properties")
        self.build_properties_tab()

        # --- Tab 3: Population ---
        self.tab_pop = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pop, text="Population")
        self.build_population_tab()

        # --- Tab 4: Preferences ---
        self.tab_pref = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pref, text="Preferences")
        self.build_preferences_tab()

        # --- Tab 5: Traits ---
        self.tab_traits = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_traits, text="Traits")
        self.build_traits_tab()

        # --- Tab 6: Resources & Stats ---
        self.tab_res = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_res, text="Resources & Stats")
        self.build_resources_stats_tab()

        # --- Tab 7: Boosts ---
        self.tab_boosts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_boosts, text="Boosts")
        self.build_boosts_tab()

        # --- Tab 8: Cultural ---
        self.tab_cultural = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_cultural, text="Cultural")
        self.build_cultural_tab()

        # --- Tab 9: Equipment ---
        self.tab_equip = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_equip, text="Equipment")
        self.build_equipment_tab()

        # --- Bottom controls ---
        bottom_frame = ttk.Frame(root)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(bottom_frame, text="Output Directory:").pack(side="left", padx=(0,5))
        self.output_dir_var = tk.StringVar(value="assets")
        out_entry = ttk.Entry(bottom_frame, textvariable=self.output_dir_var, width=30)
        out_entry.pack(side="left", padx=(0,5))
        ttk.Button(bottom_frame, text="Browse", command=self.browse_output).pack(side="left", padx=(0,10))

        self.copy_sprites_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bottom_frame, text="Copy sprites", variable=self.copy_sprites_var).pack(side="left", padx=(0,5))
        ttk.Label(bottom_frame, text="Template:").pack(side="left", padx=(5,0))
        self.template_var = tk.StringVar(value="HUMAN")
        ttk.Entry(bottom_frame, textvariable=self.template_var, width=10).pack(side="left", padx=(5,10))

        self.generate_btn = ttk.Button(bottom_frame, text="🚀 Generate Race!", command=self.generate)
        self.generate_btn.pack(side="right")

        # Status bar
        self.status = ttk.Label(root, text="Ready", relief="sunken", anchor="w")
        self.status.pack(fill="x", padx=10, pady=(0,5))

    # ---------- Helper: add a labeled entry ----------
    def add_entry(self, parent, label, row, col, default="", width=20, **kwargs):
        ttk.Label(parent, text=label + ":").grid(row=row, column=col, sticky="w", padx=5, pady=3)
        var = tk.StringVar(value=str(default))
        entry = ttk.Entry(parent, textvariable=var, width=width, **kwargs)
        entry.grid(row=row, column=col+1, sticky="w", padx=5, pady=3)
        return var

    # ---------- Helper: add a scrolled text area ----------
    def add_textarea(self, parent, label, row, col, default="", height=4, width=50):
        ttk.Label(parent, text=label + ":").grid(row=row, column=col, sticky="nw", padx=5, pady=3)
        text_widget = scrolledtext.ScrolledText(parent, height=height, width=width)
        text_widget.grid(row=row, column=col+1, sticky="w", padx=5, pady=3)
        if default:
            text_widget.insert("1.0", default)
        return text_widget

    # ---------- Tab Builders ----------
    def build_identity_tab(self):
        parent = self.tab_identity
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.race_name_var = self.add_entry(scroll_frame, "Name", 0, 0, "Elf", width=25)
        self.race_names_var = self.add_entry(scroll_frame, "Names (plural)", 1, 0, "Elves", width=25)
        self.race_possessive_var = self.add_entry(scroll_frame, "Possessive", 2, 0, "Elf", width=25)
        self.race_possessives_var = self.add_entry(scroll_frame, "Possessives (plural)", 3, 0, "Elf", width=25)

        pronoun_labels = ["HE", "HEC", "HIM", "HIMC", "HIS", "HISC", "HIMSELF", "HIMSELFC", "CHILD", "CHILDC"]
        self.pronoun_vars = {}
        for i, label in enumerate(pronoun_labels):
            row = 4 + i//2
            col = (i%2)*2
            ttk.Label(scroll_frame, text=f"PRONOUN_{label} (comma-separated):").grid(row=row, column=col, sticky="w", padx=5, pady=2)
            var = tk.StringVar(value="he, she" if "HE" in label else "him, her")
            entry = ttk.Entry(scroll_frame, textvariable=var, width=30)
            entry.grid(row=row, column=col+1, sticky="w", padx=5, pady=2)
            self.pronoun_vars[label] = var

        self.challenge_var = tk.StringVar(value="Medium")
        ttk.Label(scroll_frame, text="Challenge:").grid(row=14, column=0, sticky="w", padx=5, pady=3)
        ttk.Combobox(scroll_frame, textvariable=self.challenge_var, values=["Easy", "Medium", "Hard"], state="readonly", width=10).grid(row=14, column=1, sticky="w", padx=5, pady=3)

        # Short Description
        ttk.Label(scroll_frame, text="Short Description (DESC):").grid(row=15, column=0, sticky="nw", padx=5, pady=3)
        self.desc_text = scrolledtext.ScrolledText(scroll_frame, height=4, width=70)
        self.desc_text.grid(row=15, column=1, columnspan=3, sticky="w", padx=5, pady=3)
        self.desc_text.insert("1.0", "Elves, said to be the last creation of the gods. Excel at intelligent jobs and are decent farmers. They can be a constant headache with insanity, criminal behavior, and demands for lavish surroundings.")

        # Long Description
        ttk.Label(scroll_frame, text="Long Description (DESC_LONG):").grid(row=16, column=0, sticky="nw", padx=5, pady=3)
        self.desc_long_text = scrolledtext.ScrolledText(scroll_frame, height=6, width=70)
        self.desc_long_text.grid(row=16, column=1, columnspan=3, sticky="w", padx=5, pady=3)
        self.desc_long_text.insert("1.0", "Elves are regarded as the final creation of the Astarii, possessing free will and a flexible mind. Ancient elves were immortal, but when they sided with Aminion in the second war of the gods, they were punished with mortality.\nElves make excellent researchers and administrators. They are also fairly good at farming.\n\nBread, Meat, Mushrooms, and Eggs are their favorite foods.")

    def build_properties_tab(self):
        parent = ttk.Frame(self.tab_props)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        props = [
            ("Height", "HEIGHT", 6),
            ("Width", "WIDTH", 9),
            ("Baby Days", "BABY_DAYS", 12),
            ("Child Days", "CHILD_DAYS", 80),
            ("Corpse Decay", "CORPSE_DECAY", "true"),   # lowercase
            ("Sleeps", "SLEEPS", "true"),               # lowercase
            ("Slave Price", "SLAVE_PRICE", 11),
            ("Slave Price Recovery", "SLAVE_PRICE_RECOVERY", 0.5),
            ("Raid Mercinary", "RAID_MERCINARY", 1.0),
            ("Tourist Occurrence", "TOURIST_OCCURENCE", 1.0),
            ("Tourist Credits", "TOURIST_CREDITS", 0.75),
        ]
        self.prop_vars = {}
        for i, (label, key, default) in enumerate(props):
            ttk.Label(parent, text=label + ":").grid(row=i, column=0, sticky="w", padx=5, pady=3)
            var = tk.StringVar(value=str(default))
            entry = ttk.Entry(parent, textvariable=var, width=15)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            self.prop_vars[key] = var

    def build_population_tab(self):
        parent = ttk.Frame(self.tab_pop)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        self.pop_vars = {}
        ttk.Label(parent, text="Population Max:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        var = tk.StringVar(value="1.0")
        entry = ttk.Entry(parent, textvariable=var, width=15)
        entry.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        self.pop_vars["MAX"] = var

        ttk.Label(parent, text="Population Growth:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        var = tk.StringVar(value="0.075")
        entry = ttk.Entry(parent, textvariable=var, width=15)
        entry.grid(row=1, column=1, sticky="w", padx=5, pady=3)
        self.pop_vars["GROWTH"] = var

        ttk.Label(parent, text="Climate Modifiers (cold, temperate, hot):").grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=(10,5))
        self.climate_vars = {}
        for i, climate in enumerate(["COLD", "TEMPERATE", "HOT"]):
            ttk.Label(parent, text=f"  {climate}:").grid(row=3+i, column=0, sticky="w", padx=15, pady=2)
            var = tk.StringVar(value="0.8" if climate != "TEMPERATE" else "1.0")
            entry = ttk.Entry(parent, textvariable=var, width=10)
            entry.grid(row=3+i, column=1, sticky="w", padx=5, pady=2)
            self.climate_vars[climate] = var

        ttk.Label(parent, text="Terrain Modifiers (mountain, forest, none):").grid(row=6, column=0, columnspan=2, sticky="w", padx=5, pady=(10,5))
        self.terrain_vars = {}
        for i, terrain in enumerate(["MOUNTAIN", "FOREST", "NONE"]):
            ttk.Label(parent, text=f"  {terrain}:").grid(row=7+i, column=0, sticky="w", padx=15, pady=2)
            var = tk.StringVar(value="0.2" if terrain != "NONE" else "1.5")
            entry = ttk.Entry(parent, textvariable=var, width=10)
            entry.grid(row=7+i, column=1, sticky="w", padx=5, pady=2)
            self.terrain_vars[terrain] = var

    def build_preferences_tab(self):
        parent = ttk.Frame(self.tab_pref)
        parent.pack(fill="both", expand=True, padx=10, pady=10)

        pref_notebook = ttk.Notebook(parent)
        pref_notebook.pack(fill="both", expand=True)

        # Food
        food_frame = ttk.Frame(pref_notebook)
        pref_notebook.add(food_frame, text="Food")
        ttk.Label(food_frame, text="Preferred Foods (comma-separated or one per line):").pack(anchor="w", padx=5, pady=5)
        self.food_text = scrolledtext.ScrolledText(food_frame, height=4, width=60)
        self.food_text.pack(anchor="w", padx=5, fill="x")
        self.food_text.insert("1.0", "BREAD, MEAT, MUSHROOM, EGG")

        # Drink
        drink_frame = ttk.Frame(pref_notebook)
        pref_notebook.add(drink_frame, text="Drink")
        ttk.Label(drink_frame, text="Preferred Drinks (comma-separated or one per line):").pack(anchor="w", padx=5, pady=5)
        self.drink_text = scrolledtext.ScrolledText(drink_frame, height=4, width=60)
        self.drink_text.pack(anchor="w", padx=5, fill="x")
        self.drink_text.insert("1.0", "*")

        # Road
        road_frame = ttk.Frame(pref_notebook)
        pref_notebook.add(road_frame, text="Road")
        ttk.Label(road_frame, text="Road preferences (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.road_text = scrolledtext.ScrolledText(road_frame, height=5, width=60)
        self.road_text.pack(anchor="w", padx=5, fill="x")
        self.road_text.insert("1.0", "*:0.1\nSTONE1:0.5\nSTONE2:0.8\nDECOR1:1.0")

        # Structure
        struct_frame = ttk.Frame(pref_notebook)
        pref_notebook.add(struct_frame, text="Structure")
        ttk.Label(struct_frame, text="Structure preferences (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.struct_text = scrolledtext.ScrolledText(struct_frame, height=5, width=60)
        self.struct_text.pack(anchor="w", padx=5, fill="x")
        self.struct_text.insert("1.0", "MOUNTAIN:0.2\nSTONE:0.7\nGRAND:1.0\nWOOD:0.5\nOUTDOORS:0.3")

        # Pool
        pool_frame = ttk.Frame(pref_notebook)
        pref_notebook.add(pool_frame, text="Pool")
        ttk.Label(pool_frame, text="Pool preferences (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.pool_text = scrolledtext.ScrolledText(pool_frame, height=3, width=60)
        self.pool_text.pack(anchor="w", padx=5, fill="x")
        self.pool_text.insert("1.0", "POOL_STONE:1.0")

        # Work
        work_frame = ttk.Frame(pref_notebook)
        pref_notebook.add(work_frame, text="Work")
        ttk.Label(work_frame, text="Work preferences (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.work_text = scrolledtext.ScrolledText(work_frame, height=12, width=60)
        self.work_text.pack(anchor="w", padx=5, fill="x")
        self.work_text.insert("1.0", 
            "_ASYLUM:0.75\n_EMBASSY:1.0\n_EXPORT:0.25\n_INN:0.75\n_POLICE:0.5\n"
            "ADMIN_NORMAL:0.75\nBARBER_NORMAL:0.75\nGRAVEYARD_NORMAL:0.5\n"
            "LABORATORY_NORMAL:2.0\nLIBRARY_NORMAL:2.0\nMARKET_NORMAL:0.5\n"
            "MINE_GEM:-1.0\nPHYSICIAN_NORMAL:1.0\nREFINER_COALER:-0.75\n"
            "REFINER_SMELTER:-0.75\nREFINER_WEAVER:0.25\nSCHOOL_NORMAL:0.75\n"
            "SPEAKER_NORMAL:0.5\nSTAGE_NORMAL:1.0\nTAVERN_NORMAL:0.75\n"
            "TOMB_NORMAL:0.75\nUNIVERSITY_NORMAL:1.0\nWORKSHOP_BOWYER:0.75\n"
            "WORKSHOP_CARPENTER:0.75\nWORKSHOP_JEWELRY:0.75\nWORKSHOP_MECHANIC:0.75\n"
            "WORKSHOP_SMITHY:0.25\nWORKSHOP_TAILOR:0.75")

        # Other Races
        other_frame = ttk.Frame(pref_notebook)
        pref_notebook.add(other_frame, text="Other Races")
        ttk.Label(other_frame, text="Other races preferences (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.other_races_text = scrolledtext.ScrolledText(other_frame, height=8, width=60)
        self.other_races_text.pack(anchor="w", padx=5, fill="x")
        self.other_races_text.insert("1.0", 
            "GARTHIMI:0.75\nCRETONIAN:0.75\nCANTOR:0.75\nQ_AMEVIA:0.75\n"
            "DONDORIAN:0.75\nARGONOSH:0.75\nTILAPI:0.2")

        # World Building
        world_build_frame = ttk.Frame(pref_notebook)
        pref_notebook.add(world_build_frame, text="World Building")
        ttk.Label(world_build_frame, text="World Building preferences (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.world_build_text = scrolledtext.ScrolledText(world_build_frame, height=3, width=60)
        self.world_build_text.pack(anchor="w", padx=5, fill="x")
        self.world_build_text.insert("1.0", "CIVIC_L_STANDS:1.5")

    def build_traits_tab(self):
        parent = ttk.Frame(self.tab_traits)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(parent, text="Traits (key:value, one per line):").pack(anchor="w", padx=5, pady=5)
        self.traits_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        self.traits_text.pack(anchor="w", padx=5, fill="x")
        self.traits_text.insert("1.0", "FIGHTER:0.1\nGLUTTON:0.1\nSPRINTER:0.1")

    def build_resources_stats_tab(self):
        parent = ttk.Frame(self.tab_res)
        parent.pack(fill="both", expand=True, padx=10, pady=10)

        # Resources
        ttk.Label(parent, text="Starting Resources (key:value, one per line):").grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.resources_text = scrolledtext.ScrolledText(parent, height=3, width=60)
        self.resources_text.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.resources_text.insert("1.0", "MEAT:30\nLEATHER:10")

        # Stats - raw block, no parsing
        ttk.Label(parent, text="Stats (raw block – copy from HUMAN.txt and modify):").grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=(10,5))
        ttk.Label(parent, text="Format: KEY: { subkey: value, subkey2: value, },", font=("", 9), foreground="gray").grid(row=3, column=0, columnspan=2, sticky="w", padx=5)
        
        self.stats_text = scrolledtext.ScrolledText(parent, height=12, width=80)
        self.stats_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
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

    def build_boosts_tab(self):
        parent = ttk.Frame(self.tab_boosts)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(parent, text="Boosts (key:value, one per line, use >ADD or >MUL):").pack(anchor="w", padx=5, pady=5)
        self.boosts_text = scrolledtext.ScrolledText(parent, height=15, width=80)
        self.boosts_text.pack(anchor="w", padx=5, fill="both", expand=True)
        self.boosts_text.insert("1.0", 
            "PHYSICS_RESISTANCE_COLD>ADD:-0.15\nPHYSICS_RESISTANCE_HOT>ADD:-0.15\n"
            "PHYSICS_DEATH_AGE>MUL:0.8\nBATTLE_BLUNT_ATTACK>ADD:10\n"
            "CIVIC_IMMIGRATION>MUL:1.5\nROOM_UNIVERSITY*>MUL:1.5\n"
            "ROOM_SCHOOL*>MUL:1.5\nBEHAVIOUR_LAWFULNESS>MUL:0.75\n"
            "BEHAVIOUR_SANITY>MUL:0.8\nROOM_FARM*>MUL:1.1\n"
            "ROOM_ORCHARD*>MUL:1.1\nROOM_LIBRARY_NORMAL>MUL:1.25\n"
            "ROOM_ADMIN_NORMAL>MUL:1.25\nROOM_LABORATORY_NORMAL>MUL:1.25")

    def build_cultural_tab(self):
        parent = ttk.Frame(self.tab_cultural)
        parent.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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
        self.cultural_vars = {}
        for i, (key, default) in enumerate(cultural_fields):
            ttk.Label(scroll_frame, text=f"{key} (comma-separated):").grid(row=i, column=0, sticky="w", padx=5, pady=3)
            var = tk.StringVar(value=default)
            entry = ttk.Entry(scroll_frame, textvariable=var, width=60)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            self.cultural_vars[key] = var

        row = len(cultural_fields)
        ttk.Label(scroll_frame, text="Army Names (one per line):").grid(row=row, column=0, sticky="nw", padx=5, pady=5)
        self.army_names_text = scrolledtext.ScrolledText(scroll_frame, height=8, width=60)
        self.army_names_text.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        default_army = """Shields of Vengeance
Swords of Tomorrow
Legends of Lake Hoth
The Inithil Rangers
Darth's Opulent Oppressors
The Boys
The Moster Hunters
The Unbreakables
The Immortals
The Force of the Astarii
The Glimmering Blades
The Deathstalkers
The Barbarians
The League of Extraordinary Gentlemen
The Brotherhood of Ergoth
The Swordsmen of Naath"""
        self.army_names_text.insert("1.0", default_army)

        row += 1
        ttk.Label(scroll_frame, text="Pros (one per line):").grid(row=row, column=0, sticky="nw", padx=5, pady=5)
        self.pros_text = scrolledtext.ScrolledText(scroll_frame, height=5, width=60)
        self.pros_text.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        default_pros = """Excellent scientists and managers
Good farmers
Good learning rate"""
        self.pros_text.insert("1.0", default_pros)

        row += 1
        ttk.Label(scroll_frame, text="Cons (one per line):").grid(row=row, column=0, sticky="nw", padx=5, pady=5)
        self.cons_text = scrolledtext.ScrolledText(scroll_frame, height=5, width=60)
        self.cons_text.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        default_cons = """Unremarkable in battle
Criminal and mentally unstable
Limited natural skills
Difficult to please"""
        self.cons_text.insert("1.0", default_cons)

    def build_equipment_tab(self):
        parent = ttk.Frame(self.tab_equip)
        parent.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(parent, text="Equipment Enabled (comma-separated):").pack(anchor="w", padx=5, pady=5)
        self.equip_enabled_var = tk.StringVar(value="")
        ttk.Entry(parent, textvariable=self.equip_enabled_var, width=80).pack(anchor="w", padx=5)

        ttk.Label(parent, text="Equipment Not Enabled (comma-separated):").pack(anchor="w", padx=5, pady=5)
        self.equip_disabled_var = tk.StringVar(value="")
        ttk.Entry(parent, textvariable=self.equip_disabled_var, width=80).pack(anchor="w", padx=5)

    # ---------- Output browsing ----------
    def browse_output(self):
        dirname = filedialog.askdirectory(title="Select output directory")
        if dirname:
            self.output_dir_var.set(dirname)

    # ---------- Utility: get text from ScrolledText or Entry ----------
    def get_text_content(self, widget):
        if isinstance(widget, scrolledtext.ScrolledText):
            return widget.get("1.0", "end-1c").strip()
        else:
            return widget.get().strip()

    def parse_list_from_widget(self, widget):
        """Return list of strings, splitting by commas and newlines."""
        content = self.get_text_content(widget)
        if not content:
            return []
        items = []
        for part in content.replace('\n', ',').split(','):
            item = part.strip()
            if item:
                items.append(item)
        return items

    def parse_dict_from_text(self, widget):
        """Return dict from key:value pairs, one per line or comma-separated."""
        content = self.get_text_content(widget)
        result = {}
        if not content:
            return result
        for part in content.replace('\n', ',').split(','):
            part = part.strip()
            if not part:
                continue
            if ':' in part:
                k, v = part.split(':', 1)
                k = k.strip()
                v = v.strip()
                # Handle booleans
                if v.lower() == "true":
                    result[k] = True
                elif v.lower() == "false":
                    result[k] = False
                else:
                    try:
                        if '.' in v or v[0].isdigit() or v[0] == '-':
                            result[k] = float(v) if '.' in v else int(v)
                        else:
                            result[k] = v
                    except ValueError:
                        result[k] = v
        return result

    # ---------- Generate ----------
    def generate(self):
        print("\n" + "="*60)
        print("GENERATE BUTTON CLICKED")
        print("="*60)
        
        try:
            race_name = self.race_name_var.get().strip()
            print(f"  Race name: {race_name}")
            
            if not race_name:
                messagebox.showerror("Error", "Race name cannot be empty.")
                return
            if not race_name.replace("_", "").isalpha():
                messagebox.showerror("Error", "Race name must contain only letters and underscores.")
                return

            # Build overrides dictionary
            overrides = {}
            print("\n  📋 Values collected from GUI:")

            # Properties
            print("  📋 Properties:")
            for key, var in self.prop_vars.items():
                val = var.get().strip()
                try:
                    if val.lower() in ("true", "false"):
                        overrides[key] = val.lower() == "true"
                    elif '.' in val:
                        overrides[key] = float(val)
                    else:
                        overrides[key] = int(val)
                    print(f"     {key}: {overrides[key]}")
                except ValueError:
                    messagebox.showerror("Error", f"Invalid value for {key}: {val}")
                    return

            # Challenge
            overrides["CHALLENGE"] = self.challenge_var.get()
            print(f"     CHALLENGE: {overrides['CHALLENGE']}")

            # Population
            print("\n  📋 Population:")
            for key, var in self.pop_vars.items():
                try:
                    overrides[key] = float(var.get().strip())
                    print(f"     {key}: {overrides[key]}")
                except ValueError:
                    messagebox.showerror("Error", f"Invalid population value for {key}: {var.get()}")
                    return

            # Climate
            overrides["CLIMATE"] = {}
            print("\n  📋 Climate:")
            for climate, var in self.climate_vars.items():
                try:
                    overrides["CLIMATE"][climate] = float(var.get().strip())
                    print(f"     {climate}: {overrides['CLIMATE'][climate]}")
                except ValueError:
                    messagebox.showerror("Error", f"Invalid climate value for {climate}: {var.get()}")
                    return

            # Terrain
            overrides["TERRAIN"] = {}
            print("\n  📋 Terrain:")
            for terrain, var in self.terrain_vars.items():
                try:
                    overrides["TERRAIN"][terrain] = float(var.get().strip())
                    print(f"     {terrain}: {overrides['TERRAIN'][terrain]}")
                except ValueError:
                    messagebox.showerror("Error", f"Invalid terrain value for {terrain}: {var.get()}")
                    return

            # Preferences
            print("\n  📋 Preferences:")
            overrides["FOOD"] = self.parse_list_from_widget(self.food_text)
            print(f"     FOOD: {overrides['FOOD']}")
            overrides["DRINK"] = self.parse_list_from_widget(self.drink_text)
            print(f"     DRINK: {overrides['DRINK']}")
            overrides["ROAD"] = self.parse_dict_from_text(self.road_text)
            print(f"     ROAD: {overrides['ROAD']}")
            overrides["STRUCTURE"] = self.parse_dict_from_text(self.struct_text)
            print(f"     STRUCTURE: {overrides['STRUCTURE']}")
            overrides["POOL"] = self.parse_dict_from_text(self.pool_text)
            print(f"     POOL: {overrides['POOL']}")
            overrides["WORK"] = self.parse_dict_from_text(self.work_text)
            print(f"     WORK: {len(overrides['WORK'])} items")
            overrides["OTHER_RACES"] = self.parse_dict_from_text(self.other_races_text)
            print(f"     OTHER_RACES: {overrides['OTHER_RACES']}")
            overrides["BUILDING_OVERRIDE"] = self.parse_dict_from_text(self.world_build_text)
            print(f"     BUILDING_OVERRIDE: {overrides['BUILDING_OVERRIDE']}")

            # Traits
            overrides["TRAITS"] = self.parse_dict_from_text(self.traits_text)
            print(f"\n  📋 Traits: {overrides['TRAITS']}")

            # Resources
            overrides["RESOURCE"] = self.parse_dict_from_text(self.resources_text)
            print(f"\n  📋 Resources: {overrides['RESOURCE']}")

            # Stats - raw text, no parsing
            stats_raw = self.stats_text.get("1.0", "end-1c").strip()
            overrides["STATS_RAW"] = stats_raw
            print(f"\n  📋 Stats length: {len(stats_raw)} characters")

            # Boosts
            overrides["BOOST"] = self.parse_dict_from_text(self.boosts_text)
            print(f"\n  📋 Boosts: {len(overrides['BOOST'])} items")

            # Cultural identity
            overrides["IDENTITY"] = {}
            for key, var in self.pronoun_vars.items():
                overrides["IDENTITY"][key] = [x.strip() for x in var.get().split(',') if x.strip()]
            overrides["IDENTITY"]["NAME"] = race_name
            overrides["IDENTITY"]["NAMES"] = self.race_names_var.get().strip()
            overrides["IDENTITY"]["POSSESSIVE"] = self.race_possessive_var.get().strip()
            overrides["IDENTITY"]["POSSESSIVES"] = self.race_possessives_var.get().strip()
            print(f"\n  📋 Identity: {overrides['IDENTITY']['NAME']}, {overrides['IDENTITY']['NAMES']}")

            # Cultural lists
            for key, var in self.cultural_vars.items():
                overrides[key] = [x.strip() for x in var.get().split(',') if x.strip()]
            print(f"\n  📋 Cultural fields: {len(self.cultural_vars)} fields")

            # Army, pros, cons
            overrides["ARMY_NAMES"] = [x.strip() for x in self.army_names_text.get("1.0", "end-1c").split('\n') if x.strip()]
            overrides["PROS"] = [x.strip() for x in self.pros_text.get("1.0", "end-1c").split('\n') if x.strip()]
            overrides["CONS"] = [x.strip() for x in self.cons_text.get("1.0", "end-1c").split('\n') if x.strip()]
            print(f"  📋 Army names: {len(overrides['ARMY_NAMES'])} items")
            print(f"  📋 Pros: {len(overrides['PROS'])} items")
            print(f"  📋 Cons: {len(overrides['CONS'])} items")

            # Equipment
            overrides["EQUIPMENT_ENABLED"] = [x.strip() for x in self.equip_enabled_var.get().split(',') if x.strip()]
            overrides["EQUIPMENT_NOT_ENABLED"] = [x.strip() for x in self.equip_disabled_var.get().split(',') if x.strip()]
            print(f"  📋 Equipment enabled: {overrides['EQUIPMENT_ENABLED']}")
            print(f"  📋 Equipment disabled: {overrides['EQUIPMENT_NOT_ENABLED']}")

            # Output settings
            output_dir = self.output_dir_var.get().strip() or "assets"
            copy_sprites = self.copy_sprites_var.get()
            template_race = self.template_var.get().strip() or "HUMAN"
            print(f"\n  📁 Output dir: {output_dir}")
            print(f"  📁 Copy sprites: {copy_sprites}")
            print(f"  📁 Template race: {template_race}")

            # Descriptions
            desc_short = self.desc_text.get("1.0", "end-1c").strip()
            desc_long = self.desc_long_text.get("1.0", "end-1c").strip()
            print(f"\n  📋 Description length: {len(desc_short)} chars")
            print(f"  📋 Long description length: {len(desc_long)} chars")

            # --- Patch the generate_race module ---
            print("\n  🔧 Patching generate_race.DEFAULTS...")
            original_defaults = raceGen.DEFAULTS.copy()
            for key, value in overrides.items():
                raceGen.DEFAULTS[key] = value
            raceGen.DEFAULTS["DESC_TEXT"] = desc_short
            raceGen.DEFAULTS["DESC_LONG_TEXT"] = desc_long

            # --- Call the generator ---
            print("\n  🚀 Calling generate_race.generate_race()...")
            print("-" * 60)
            
            raceGen.generate_race(race_name, output_dir, copy_sprites, template_race)
            
            print("-" * 60)
            print("\n  ✅ Race generation complete!")
            messagebox.showinfo("Success", f"Race '{race_name}' generated successfully!\n\nOutput folder: {output_dir}")
            self.status.config(text="Generation complete.")
            
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print(f"\n  ❌ ERROR: {e}")
            print(error_msg)
            messagebox.showerror("Error", f"Generation failed:\n\n{str(e)}\n\nCheck the console for details.")
            self.status.config(text="Error occurred.")
        finally:
            # Restore original defaults
            if 'original_defaults' in locals():
                raceGen.DEFAULTS.clear()
                raceGen.DEFAULTS.update(original_defaults)
                print("\n  🔧 Restored original defaults.")


if __name__ == "__main__":
    print("="*60)
    print("STARTING RACE GENERATOR GUI")
    print("="*60)
    root = tk.Tk()
    app = FullRaceGeneratorGUI(root)
    root.mainloop()