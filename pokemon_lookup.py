import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import pandas as pd
import pokedexcel
import evos
from text_methods import TextWrapper

# Data class because apparently globals are bad practice :(
class PokemonData:
    def __init__(self, base_dir):
        self.workbook_path = os.path.join('pokedexCEL.xlsx')
        pokedex = evos.Evolution(self.workbook_path)
        evos_dict = pokedex.generate_evolution_dict()
        pokedex.update_spreadsheet(evos_dict)
        # Dataframes but CLASSy
        dfs = pd.read_excel(self.workbook_path, sheet_name=None)
        self.dfs_cleaned = {name: df.where(pd.notnull(df), None) for name, df in dfs.items()}
        self.df_pokemon_details = self.dfs_cleaned['Main']
        self.df_moveset_details = self.dfs_cleaned['Moves']
        self.df_poke_info = self.dfs_cleaned['Poke Info']
        self.df_misc = self.dfs_cleaned['Misc']

        self.regular_folder = os.path.join(base_dir, 'Graphics', 'Pokemon', 'Front')
        self.shiny_folder = os.path.join(base_dir, 'Graphics', 'Pokemon', 'Front shiny')
        self.back_folder = os.path.join(base_dir, 'Graphics', 'Pokemon', 'Back')
        self.back_shiny_folder = os.path.join(base_dir, 'Graphics', 'Pokemon', 'Back shiny')
        self.icons_folder = os.path.join(base_dir, 'Graphics', 'Pokemon', 'Icons')
        self.icons_shiny_folder = os.path.join(base_dir, 'Graphics', 'Pokemon', 'Icons shiny')

class PokemonApp(tk.Tk):
    def __init__(self, data):
        super().__init__()
        self.data = data

        self.title("PokéRover")
        self.geometry("1280x720")
        self.minsize(1280, 720)
        self.maxsize(1280, 720)

        self.current_mode = "light"
        self.colors = light_mode_colors
        self.configure(bg=self.colors["bg"])
        self.selected_pokemon = None
        self.sort_criteria = 'Name'

        self.toggle_button = tk.Button(self, text="Dark Mode", command=self.toggle_mode, font=("Arial", 12))
        self.toggle_button.pack(pady=10)

        # Left pane
        self.left_pane = tk.Frame(self, width=240, bg='white')
        self.left_pane.pack(side='left', fill='y', padx=10, pady=10)
        self.search_label = tk.Label(self.left_pane, text="Search Pokemon:", font=("Arial", 12), bg='white')
        self.search_label.pack(pady=10)
        self.search_entry = tk.Entry(self.left_pane, width=20, font=("Arial", 12))
        self.search_entry.pack(pady=10)
        self.search_entry.bind('<Return>', lambda event: self.search_pokemon())
        self.search_button = tk.Button(self.left_pane, text="Search", command=self.search_pokemon, font=("Arial", 12))
        self.search_button.pack(pady=10)
        self.result_listbox = tk.Listbox(self.left_pane, width=30, height=30, font=("Arial", 12))
        self.result_listbox.pack(pady=20)
        self.result_listbox.bind('<<ListboxSelect>>', self.show_details)

        # Right pane
        self.right_pane = tk.Frame(self, bg='white')
        self.right_pane.pack(side='right', fill='both', expand=True)

        # Notebook
        self.notebook = ttk.Notebook(self.right_pane)
        self.notebook.pack(fill='both', expand=True)

        # Details Frame
        self.details_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.details_frame, text='Details')
        self.details_text = scrolledtext.ScrolledText(self.details_frame, wrap=tk.WORD, font=("Arial", 12), bg='white', height=15, width=70)
        self.details_text.pack(pady=10, padx=10, fill='both', expand=True)
        self.image_label = tk.Label(self.details_frame, bg='white')
        self.image_label.pack(pady=10, padx=10)
        self.image_type_var = tk.StringVar(value='Regular')
        self.image_type_menu = ttk.Combobox(self.details_frame, textvariable=self.image_type_var, font=("Arial", 12), values=['Regular', 'Shiny', 'Back', 'Back Shiny', 'Icon'])
        self.image_type_menu.pack(pady=10, padx=10, anchor='w')
        self.image_type_menu.bind('<<ComboboxSelected>>', self.update_image)

        # Moves Frame
        self.moves_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.moves_frame, text='Moves')
        self.moves_text = scrolledtext.ScrolledText(self.moves_frame, wrap=tk.WORD, font=("Arial", 12), bg='white')
        self.moves_text.pack(side='left', pady=10, padx=10, fill='both', expand=True)

        # Poke Info Frame
        self.poke_info_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.poke_info_frame, text='Poke Info')
        self.poke_info_label = tk.Label(self.poke_info_frame, text="", justify='left', anchor='nw', bg='white', font=("Arial", 12))
        self.poke_info_label.pack(pady=10, padx=10, fill='both', expand=True)

        # Misc Frame
        self.misc_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.misc_frame, text='Misc')
        self.misc_label = tk.Label(self.misc_frame, text="", justify='left', anchor='nw', bg='white', font=("Arial", 12))
        self.misc_label.pack(pady=10, padx=10, fill='both', expand=True)

        # Evos Frame
        self.evos_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.evos_frame, text='Evos')
        self.evos_canvas = tk.Canvas(self.evos_frame, bg='white')
        self.evos_canvas.pack(side='left', fill='both', expand=True)
        self.evos_scrollbar = tk.Scrollbar(self.evos_frame, orient='vertical', command=self.evos_canvas.yview)
        self.evos_scrollbar.pack(side='right', fill='y')
        self.evos_canvas.configure(yscrollcommand=self.evos_scrollbar.set)
        self.evos_inner_frame = tk.Frame(self.evos_canvas, bg='white')
        self.evos_canvas.create_window((0, 0), window=self.evos_inner_frame, anchor='nw')
        self.evos_inner_frame.bind('<Configure>', lambda event, canvas=self.evos_canvas: self.on_frame_configure(canvas))
        self.evos_image_type_var = tk.StringVar(value='Regular')
        self.evos_image_type_menu = ttk.Combobox(self.evos_frame, textvariable=self.evos_image_type_var, font=("Arial", 12), values=['Regular', 'Shiny'])
        self.evos_image_type_menu.pack(pady=10, padx=10, anchor='w')
        self.evos_image_type_menu.bind('<<ComboboxSelected>>', self.update_evos)



        # Creator Frame
        self.creator_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.creator_frame, text='Credits')
        self.creator_label = tk.Label(self.creator_frame, text="https://github.com/SEXYREXY-DEV   //////   sexyrexy1212 on discord", justify='left', anchor='nw', bg='white', font=("Arial", 12))
        self.creator_label.pack(pady=10, padx=10, fill='both', expand=True)
        self.add_tyrantrum_image()

        # Sorting dropdown menu
        self.sort_criteria_label = tk.Label(self, text="Sort by:", font=("Arial", 12), bg='white')
        self.sort_criteria_label.place(x=10, y=10)
        self.sort_criteria = ttk.Combobox(self, values=["Name", "HP", "Attack", "Defense", "SpAtk", "SpDef", "Spd"], font=("Arial", 12))
        self.sort_criteria.place(x=10, y=40)
        self.sort_criteria.current(0)  # Set default sorting criterion
        self.sort_criteria.bind('<<ComboboxSelected>>', self.sort_pokemon)

    def sort_pokemon(self, event=None):
        sort_by = self.sort_criteria.get()
        if sort_by == "Name":
            self.data.df_pokemon_details.sort_values(by=sort_by, inplace=True, ascending=True)
        else:
            self.data.df_pokemon_details.sort_values(by=sort_by, inplace=True, ascending=False)
        self.display_sorted_results()

    def display_sorted_results(self):
        self.result_listbox.delete(0, tk.END)
        unique_results = self.data.df_pokemon_details.drop_duplicates(subset=['InternalName'])
        for index, row in unique_results.iterrows():
            display_name = f"{row['Name']} ({row['InternalName']})"
            self.result_listbox.insert(tk.END, display_name)

    def search_pokemon(self):
        query = self.search_entry.get().strip().lower()
        results = self.data.df_pokemon_details[self.data.df_pokemon_details['Name'].str.lower().str.contains(query)]
        if results.empty:
            messagebox.showerror("Error", "No Pokemon found with that name.")
        else:
            sorted_results = results.sort_values(by='Name', ascending=True)
            self.result_listbox.delete(0, tk.END)
            for index, row in sorted_results.iterrows():
                display_name = f"{row['Name']} ({row['InternalName']})"
                self.result_listbox.insert(tk.END, display_name)

    def show_details(self, event=None):
        selected_index = self.result_listbox.curselection()
        if selected_index:
            selected_text = self.result_listbox.get(selected_index)
            name_part = selected_text.split(' (')[0]
            internal_name_part = selected_text.split(' (')[1].strip(')')
            if internal_name_part == 'None':
                self.selected_pokemon = self.data.df_pokemon_details[self.data.df_pokemon_details['Name'] == name_part].iloc[0]
            else:
                self.selected_pokemon = self.data.df_pokemon_details[
                    (self.data.df_pokemon_details['Name'] == name_part) & 
                    (self.data.df_pokemon_details['InternalName'] == internal_name_part)
                ].iloc[0]
            details = "\n".join(f"{col}: {TextWrapper.wrap_text(str(val), 80)}" for col, val in self.selected_pokemon.items() if col not in ['UniqueID','RegularImagePath', 'ShinyImagePath', 'GrowthRate', 'BaseEXP', 'Rareness'])
            self.details_text.delete('1.0', tk.END)
            self.details_text.insert(tk.END, details)
            self.update_image_options()
            self.update_moveset()
            self.update_poke_info()
            self.update_misc_info()
            self.update_evos()
            
            if event:
                print('printed from details')

            
    def update_evos(self, event=None):
        # Clear the existing content in the evos_inner_frame
        for widget in self.evos_inner_frame.winfo_children():
            widget.destroy()

        if self.selected_pokemon is not None and self.selected_pokemon['Evolution Line']:
            evos = self.selected_pokemon['Evolution Line'].split(', ')
            col_count = 6
            image_type = self.evos_image_type_var.get()

            for index, evo in enumerate(evos):
                row = index // col_count * 2
                col = index % col_count

                evo_name = evo.split('(')[0].strip()
                if image_type == 'Regular':
                    evo_image_path = os.path.join(self.data.regular_folder, f"{evo_name}.png")
                elif image_type == 'Shiny':
                    evo_image_path = os.path.join(self.data.shiny_folder, f"{evo_name}.png")

                if os.path.exists(evo_image_path):
                    evo_image = Image.open(evo_image_path)
                    evo_image = evo_image.resize((100, 100), Image.LANCZOS)
                    evo_photo = ImageTk.PhotoImage(evo_image)
                    evo_label = tk.Label(self.evos_inner_frame, image=evo_photo, bg='white')
                    evo_label.image = evo_photo
                    evo_label.grid(row=row, column=col, padx=10, pady=5, sticky='n')
                    evo_label.bind("<Enter>", lambda event, label=evo_label: label.config(bg="lightgray"))
                    evo_label.bind("<Leave>", lambda event, label=evo_label: label.config(bg="white"))

                    # Bind click event to the image label
                    evo_label.bind('<Button-1>', lambda event, name=evo_name: self.on_image_click(name))
                    #self.result_listbox.bind('<<ListboxSelect>>', self.show_details)

                    evo_name_label = tk.Label(self.evos_inner_frame, text=evo, bg='white', font=("Arial", 12))
                    evo_name_label.grid(row=row+1, column=col, padx=10, pady=5, sticky='n')
                else:
                    evo_name_label = tk.Label(self.evos_inner_frame, text=evo, bg='white', font=("Arial", 12))
                    evo_name_label.grid(row=row, column=col, padx=10, pady=5, sticky='n')

            # Configure grid columns to expand evenly
            for col in range(col_count):
                self.evos_inner_frame.columnconfigure(col, weight=1)
        else:
            no_evos_label = tk.Label(self.evos_inner_frame, text="No Evolution Information Available", bg='white', font=("Arial", 12))
            no_evos_label.pack(padx=10, pady=5, side='top', anchor='w')
    
    def on_image_click(self, pokemon_name):
        
        if pokemon_name:
            self.selected_pokemon = self.data.df_pokemon_details[
                    (self.data.df_pokemon_details['InternalName'] == pokemon_name)
                ].iloc[0]
            details = "\n".join(f"{col}: {TextWrapper.wrap_text(str(val), 80)}" for col, val in self.selected_pokemon.items() if col not in ['UniqueID','RegularImagePath', 'ShinyImagePath', 'GrowthRate', 'BaseEXP', 'Rareness'])
            self.details_text.delete('1.0', tk.END)
            self.details_text.insert(tk.END, details)
            self.update_image_options()
            self.update_moveset()
            self.update_poke_info()
            self.update_misc_info()
            self.notebook.select(self.details_frame)
            #self.update_evos()


    
    def on_frame_configure(self, canvas):
        canvas.configure(scrollregion=canvas.bbox('all'))

    def update_poke_info(self):
        if self.selected_pokemon is not None:
            poke_info = ""
            if self.selected_pokemon['InternalName'] is None:
                poke_info_data = self.data.df_poke_info[self.data.df_poke_info['Name'] == self.selected_pokemon['Name']]
            else:
                poke_info_data = self.data.df_poke_info[self.data.df_poke_info['InternalName'] == self.selected_pokemon['InternalName']]
            
            if not poke_info_data.empty:
                for col, val in poke_info_data.iloc[0].items():
                    wrapped_val = TextWrapper.wrap_text(str(val), 100)  # Adjust the width as needed
                    poke_info += f"{col}: {wrapped_val}\n"
            else:
                poke_info = "No Poke Info Available"
            self.poke_info_label.config(text=poke_info)

    def update_misc_info(self):
        if self.selected_pokemon is not None:
            misc_info = "" 
            if self.selected_pokemon['InternalName'] is None:
                misc_info_data = self.data.df_misc[self.data.df_misc['Name'] == self.selected_pokemon['Name']]
            else:
                misc_info_data = self.data.df_misc[self.data.df_misc['InternalName'] == self.selected_pokemon['InternalName']]
            
            if not misc_info_data.empty:
                for col, val in misc_info_data.iloc[0].items():
                    wrapped_val = TextWrapper.wrap_text(str(val), 100)  # Adjust the width as needed
                    misc_info += f"{col}: {wrapped_val}\n"
            else:
                misc_info = "No Misc Info Available"
            self.misc_label.config(text=misc_info)

    def update_image_options(self):
        if self.selected_pokemon is not None:
            image_options = ['Regular', 'Shiny', 'Back', 'Back Shiny', 'Icon']
            self.image_type_menu['values'] = image_options
            self.image_type_menu.current(0)
            self.update_image()

    def update_image(self, event=None):
        if self.selected_pokemon is None:
            return
        internal_name = self.selected_pokemon['InternalName'].lower()
        image_type = self.image_type_var.get()
        folder_map = {
            'Regular': self.data.regular_folder,
            'Shiny': self.data.shiny_folder,
            'Back': self.data.back_folder,
            'Back Shiny': self.data.back_shiny_folder,
            'Icon': self.data.icons_folder
        }
        folder = folder_map.get(image_type, self.data.regular_folder)
        try:
            if image_type != 'Icon':
                image_path = os.path.join(folder, f'{internal_name}.png')
                image = Image.open(image_path)
                image = image.resize((192, 192), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo)
                self.image_label.image = photo
            else:
                image_path = os.path.join(folder, f'{internal_name}.png')
                image = Image.open(image_path)
                image = image.resize((128, 64), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo)
                self.image_label.image = photo
        except Exception as e:
            messagebox.showerror("Image Error", f"Error loading image: {e}")

    def update_moveset(self):
        if self.selected_pokemon is not None:
            internal_name = self.selected_pokemon.get('InternalName', None)
            name = self.selected_pokemon.get('Name', None)
            
            if internal_name:
                moveset = self.data.df_moveset_details[self.data.df_moveset_details['InternalName'] == internal_name]
            else:
                moveset = self.data.df_moveset_details[self.data.df_moveset_details['Name'] == name]
            
            if not moveset.empty:
                moves = moveset.iloc[0].get('Moves', '')
                if moves:
                    moves = moves.split(',')
                    formatted_moves = []
                    for move in moves:
                        move = move.strip().upper()
                        if move == '':
                            continue  # Skip empty moves
                        
                        formatted_moves.append(move)
                    formatted_moves_text = "\n".join(formatted_moves)
                else:
                    formatted_moves_text = "No Moves Available"
                
                self.moves_text.delete('1.0', tk.END)
                self.moves_text.insert(tk.END, f"Moves:\n{formatted_moves_text}\n\n")
                
                tutor_moves = moveset.iloc[0].get('TutorMoves', '')
                if tutor_moves:
                    formatted_tutor_moves = "\n".join(tutor_moves.split(','))
                else:
                    formatted_tutor_moves = "No Tutor Moves Available"
                
                self.moves_text.insert(tk.END, f"Tutor Moves:\n{formatted_tutor_moves}\n\n")
                
                egg_moves = moveset.iloc[0].get('EggMoves', '')
                if egg_moves:
                    formatted_egg_moves = "\n".join(egg_moves.split(','))
                else:
                    formatted_egg_moves = "No Egg Moves Available"
                
                self.moves_text.insert(tk.END, f"Egg Moves:\n{formatted_egg_moves}")
            else:
                self.moves_text.delete('1.0', tk.END)
                self.moves_text.insert(tk.END, "No Moves Available")



    def toggle_mode(self):
        if self.current_mode == "light":
            self.colors = dark_mode_colors
            self.current_mode = "dark"
        else:
            self.colors = light_mode_colors
            self.current_mode = "light"
        
        self.apply_color_scheme()

    def apply_color_scheme(self):
        self.configure(bg=self.colors["bg"])
        self.left_pane.configure(bg=self.colors["bg"])
        self.search_label.configure(bg=self.colors["bg"], fg=self.colors["fg"])
        self.search_entry.configure(bg=self.colors["entry_bg"], fg=self.colors["entry_fg"])
        self.search_button.configure(bg=self.colors["button_bg"], fg=self.colors["button_fg"])
        self.result_listbox.configure(bg=self.colors["listbox_bg"], fg=self.colors["listbox_fg"])
        self.right_pane.configure(bg=self.colors["bg"])
        self.details_frame.configure(bg=self.colors["bg"])
        self.details_text.configure(bg=self.colors["text_bg"], fg=self.colors["text_fg"])  # Updated line
        self.image_label.configure(bg=self.colors["bg"])
        self.moves_frame.configure(bg=self.colors["bg"])
        self.moves_text.configure(bg=self.colors["text_bg"], fg=self.colors["text_fg"])
        self.poke_info_frame.configure(bg=self.colors["bg"])
        self.poke_info_label.configure(bg=self.colors["bg"], fg=self.colors["fg"])
        self.misc_frame.configure(bg=self.colors["bg"])
        self.misc_label.configure(bg=self.colors["bg"], fg=self.colors["fg"])
        self.evos_frame.configure(bg=self.colors["bg"])
        self.evos_canvas.configure(bg=self.colors["bg"])
        self.evos_inner_frame.configure(bg=self.colors["bg"])

    def add_tyrantrum_image(self):
        try:
            # Load the image from the shiny folder
            image_path = os.path.join(self.data.shiny_folder, 'TYRANTRUM.png')
            image = Image.open(image_path)
            image = image.resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            # Create a label to display the image and pack it into the creator_frame
            self.tyrantrum_label = tk.Label(self.creator_frame, image=photo, bg='white')
            self.tyrantrum_label.image = photo  # Keep a reference to avoid garbage collection
            self.tyrantrum_label.pack(pady=10)
        except Exception as e:
            print(f"Error loading Tyrantrum image: {e}")

light_mode_colors = {
    "bg": "white",
    "fg": "black",
    "entry_bg": "white",
    "entry_fg": "black",
    "button_bg": "lightgray",
    "button_fg": "black",
    "listbox_bg": "white",
    "listbox_fg": "black",
    "text_bg": "white",
    "text_fg": "black"
}

dark_mode_colors = {
    "bg": "#2e2e2e",
    "fg": "white",
    "entry_bg": "#4e4e4e",
    "entry_fg": "white",
    "button_bg": "#4e4e4e",
    "button_fg": "white",
    "listbox_bg": "#4e4e4e",
    "listbox_fg": "white",
    "text_bg": "#4e4e4e",
    "text_fg": "white"
}

def main():
    pokedexcel.main()
    
    # PROJECT PATH
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # pyinstaller
    #base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # PokemonData!!
    data = PokemonData(base_dir)
    # Appdata finally (I forgot to put this in and had to troubleshoot with chatgpt :(   )
    app = PokemonApp(data)
    app.mainloop()

if __name__ == '__main__':
    main()
