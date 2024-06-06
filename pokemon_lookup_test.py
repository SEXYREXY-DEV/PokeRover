import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import pandas as pd
import pokedexcel
import evos
from text_methods import TextWrapper
from colors import Styles

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
        self.shiny_folder = os.path.join(base_dir, 'Graphics', 'Pokemon', 'Front Shiny')


class PokemonApp(tk.Tk):
    def __init__(self, data):
        super().__init__()
        self.data = data

        self.title("PokéRover")
        self.geometry("1280x720")
        self.minsize(1280, 720)
        self.maxsize(1280, 720)

        self.selected_pokemon = None
        self.sort_criteria = 'Name'

        self.styles = Styles(self)
        self.toggle_button = tk.Button(self, text="Dark Mode", command=self.styles.toggle_mode, font=("Arial", 12))
        self.toggle_button.pack(pady=10)

        def toggle_mode(self):
            self.styles.toggle_mode()
            self.apply_color_scheme()

        def apply_color_scheme(self):
            # Main window
            self.configure(bg=self.styles.colors["bg"])

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
        self.image_type_menu = ttk.Combobox(self.details_frame, textvariable=self.image_type_var, font=("Arial", 12))
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
            self.data.df_pokemon_details.sort_values(by=sort_by, inplace=True, ascending=True)  # Set ascending to True for 'Name'
        else:
            self.data.df_pokemon_details.sort_values(by=sort_by, inplace=True, ascending=False)  # Set ascending to False for other criteria
        self.display_sorted_results()

    def display_sorted_results(self):
        self.result_listbox.delete(0, tk.END)
        unique_results = self.data.df_pokemon_details.drop_duplicates(subset=['Name'])
        for index, row in unique_results.iterrows():
            display_name = f"{row['Name']} ({row['InternalName']})"
            self.result_listbox.insert(tk.END, display_name)

    def search_pokemon(self):
        query = self.search_entry.get().strip().lower()
        results = self.data.df_pokemon_details[self.data.df_pokemon_details['Name'].str.lower().str.contains(query)]
        if results.empty:
            messagebox.showerror("Error", "No Pokemon found with that name.")
        else:
            sorted_results = results.sort_values(by='Name', ascending=True)  # Sort in descending order
            self.result_listbox.delete(0, tk.END)
            unique_results = sorted_results.drop_duplicates(subset=['Name'])
            for index, row in unique_results.iterrows():
                display_name = f"{row['Name']} ({row['InternalName']})"
                self.result_listbox.insert(tk.END, display_name)

    def show_details(self, event):
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
            details = "\n".join(f"{col}: {TextWrapper.wrap_text(str(val), 80)}" for col, val in self.selected_pokemon.items() if col not in ['RegularImagePath', 'ShinyImagePath', 'GrowthRate', 'BaseEXP', 'Rareness'])
            self.details_text.delete('1.0', tk.END)
            self.details_text.insert(tk.END, details)
            self.update_image_options()
            self.update_moveset()
            self.update_poke_info()
            self.update_misc_info()
            self.update_evos()  # Add this line to update the evolutions tab
            #self.notebook.select(self.evos_frame)  # Switch to the "Evos" tab

    def update_evos(self):
        # Clear the existing content in the evos_inner_frame
        for widget in self.evos_inner_frame.winfo_children():
            widget.destroy()

        if self.selected_pokemon is not None and self.selected_pokemon['Evolution Line']:
            evos = self.selected_pokemon['Evolution Line'].split(', ')
            col_count = 6
            for index, evo in enumerate(evos):
                row = index // col_count * 2
                col = index % col_count
                
                evo_name = evo.split('(')[0].strip()
                evo_image_path = os.path.join(self.data.regular_folder, f"{evo_name}.png")
                
                if os.path.exists(evo_image_path):
                    evo_image = Image.open(evo_image_path)
                    evo_image = evo_image.resize((100, 100), Image.LANCZOS)
                    evo_photo = ImageTk.PhotoImage(evo_image)
                    evo_label = tk.Label(self.evos_inner_frame, image=evo_photo, bg='white')
                    evo_label.image = evo_photo
                    evo_label.grid(row=row, column=col, padx=10, pady=5, sticky='n')

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
            image_options = ['Regular', 'Shiny']
            self.image_type_menu['values'] = image_options
            self.image_type_menu.current(0)
            self.update_image()

    def update_image(self, event=None):
        if self.selected_pokemon is not None:
            name = self.selected_pokemon['InternalName'] if self.selected_pokemon['InternalName'] is not None else self.selected_pokemon['Name'].lower()
            image_type = self.image_type_var.get()
            if image_type == 'Regular':
                image_path = os.path.join(self.data.regular_folder, f"{name}.png")
            elif image_type == 'Shiny':
                image_path = os.path.join(self.data.shiny_folder, f"{name}.png")
            else:
                if 'shiny' in image_type.lower():
                    image_path = os.path.join(self.data.shiny_folder, image_type)
                else:
                    image_path = os.path.join(self.data.regular_folder, image_type)
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize((200, 200), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo)
                self.image_label.image = photo
            else:
                self.image_label.config(image='', text='No Image Available')

    def update_moveset(self):
        if self.selected_pokemon is not None:
            internal_name = self.selected_pokemon['InternalName'] if self.selected_pokemon['InternalName'] is not None else None
            name = self.selected_pokemon['Name'] if internal_name is None else None
            
            if internal_name:
                moveset = self.data.df_moveset_details[self.data.df_moveset_details['InternalName'] == internal_name]
            else:
                moveset = self.data.df_moveset_details[self.data.df_moveset_details['Name'] == name]
                
            if not moveset.empty:
                moves = moveset.iloc[0]['Moves'].split(',')
                formatted_moves = "\n".join([f"{moves[i]} - {moves[i + 1]}" for i in range(0, len(moves), 2)])
                self.moves_text.delete('1.0', tk.END)
                self.moves_text.insert(tk.END, f"Moves:\n{formatted_moves}\n\n")
                tutor_moves = moveset.iloc[0]['TutorMoves'].split(',')
                formatted_tutor_moves = "\n".join(tutor_moves)
                self.moves_text.insert(tk.END, f"Tutor Moves:\n{formatted_tutor_moves}\n\n")
                egg_moves_data = moveset.iloc[0]['EggMoves']
                if isinstance(egg_moves_data, str) and egg_moves_data:  
                    egg_moves = egg_moves_data.split(',')
                    formatted_egg_moves = "\n".join(egg_moves)
                    self.moves_text.insert(tk.END, f"Egg Moves:\n{formatted_egg_moves}")
                else:
                    self.moves_text.insert(tk.END, "No Egg Moves Available")
            else:
                self.moves_text.delete('1.0', tk.END)
                self.moves_text.insert(tk.END, "No Moves Available")

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

def main():
    pokedexcel.main()
    
    # PROJECT PATH
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # pyinstaller
    #base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    styles = Styles
    # PokemonData!!
    data = PokemonData(base_dir)
    # Appdata finally (I forgot to put this in and had to troubleshoot with chatgpt :(   )
    app = PokemonApp(data)
    app.mainloop()

if __name__ == '__main__':
    main()
