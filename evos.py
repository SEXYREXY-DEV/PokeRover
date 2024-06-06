import pandas as pd
import os

class Evolution:
    def __init__(self, workbook_path):
        self.workbook_path = workbook_path
        self.dfs = pd.read_excel(self.workbook_path, sheet_name=None, engine='openpyxl')
        self.dfs_cleaned = {name: df.where(pd.notnull(df), None) for name, df in self.dfs.items()}
        self.df_pokemon_details = self.dfs_cleaned['Main']
        self.evos_dict = {}
        self.method_dict = {}

    def find_evolution(self, base_pokemon):
        base_pokemon = base_pokemon.upper()
        pokemon_row = self.df_pokemon_details[self.df_pokemon_details['InternalName'] == base_pokemon]
        if not pokemon_row.empty and not pokemon_row['Evolutions'].isnull().values[0]:
            evolution = pokemon_row['Evolutions'].values[0]
            evolutions = evolution.split(',')
            evolution_names = [e.strip() for e in evolutions]
            # Extract the first evolution name
            evolution_name = evolution_names[0]
            evolution_method = evolution_names[2] if len(evolution_names) > 2 else None
            if evolution_method:
                self.method_dict[evolution_name] = evolution_method
            if len(evolutions) > 1:
                # Extract subsequent evolution names and methods every 3rd word after the first one
                for i in range(3, len(evolutions), 3):
                    if i < len(evolutions):
                        evolution_name += f", {evolution_names[i]}"
                        if i + 2 < len(evolution_names):
                            evolution_method = evolution_names[i + 2]
                            self.method_dict[evolution_names[i]] = evolution_method
            return evolution_name
        else:
            return None

    def find_more_evolutions(self, pokemon):
        evo_list = []
        evo_list.append(pokemon)
        pokemon2 = self.find_evolution(pokemon)
        if pokemon2 is not None:
            evo_list.append(pokemon2)
            pokemon3 = self.find_evolution(pokemon2)
            if pokemon3 is not None:
                evo_list.append(pokemon3)
        if len(evo_list) > 1:
            return evo_list

    def search(self, values, searchFor):
        for k, v_list in values.items():
            if v_list is not None and searchFor in v_list:
                return k
        return None

    def update_evolution_lines(self, dictionary):
        for key, value in list(dictionary.items()):
            if value is None:
                dictionary[key] = []
            result_key = self.search(dictionary, key)
            if result_key:
                dictionary[key] = dictionary[result_key]
            else:
                if key not in dictionary[key]:
                    dictionary[key].append(key)

    def generate_evolution_dict(self):
        for index, row in self.df_pokemon_details.iterrows():
            evolution_list = self.find_more_evolutions(row['InternalName'])
            self.evos_dict.update({row['InternalName']: evolution_list})
        self.update_evolution_lines(self.evos_dict)
        return self.evos_dict

    def update_spreadsheet(self, evolution_dict):
        # Add 'Evolution Line' column if not already present
        if 'Evolution Line' not in self.df_pokemon_details.columns:
            self.df_pokemon_details['Evolution Line'] = None
        
        # Update 'Evolution Line' column based on 'InternalName'
        for index, row in self.df_pokemon_details.iterrows():
            internal_name = row['InternalName']
            evolution_line = evolution_dict.get(internal_name)
            if evolution_line and len(evolution_line) > 1:
                evolution_line_str = ', '.join(evolution_line)
                for pokemon in evolution_line:
                    if pokemon in self.method_dict:
                        evolution_line_str = evolution_line_str.replace(pokemon, f"{pokemon}({self.method_dict[pokemon]})")
                self.df_pokemon_details.at[index, 'Evolution Line'] = evolution_line_str
        
        # Write updated dataframe back to the spreadsheet
        with pd.ExcelWriter(self.workbook_path, engine='openpyxl') as writer:
            for sheet_name, df in self.dfs.items():
                if sheet_name == 'Main':
                    self.df_pokemon_details.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

# Example usage:
#workbook_path = os.path.join('pokedexCEL.xlsx')
#pokedex = Evolution(workbook_path)
#evos_dict = pokedex.generate_evolution_dict()
#pokedex.update_spreadsheet(evos_dict)
