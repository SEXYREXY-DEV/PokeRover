import re
import pandas as pd
import os

class MoveParser:
    def __init__(self, filename):
        self.filename = filename
        self.moves = self.parse_moves()
    
    def parse_moves(self):
        with open(self.filename, 'r') as file:
            content = file.read()

        moves = {}
        move_blocks = content.split('#-------------------------------')
        move_pattern = re.compile(r"\[(.*?)\](.*?)Name = (.*?)\nType = (.*?)\n.*?Power = (.*?)\nAccuracy = (.*?)\n", re.S)

        for block in move_blocks:
            match = move_pattern.search(block)
            if match:
                move_code, _, name, move_type, power, accuracy = match.groups()
                moves[move_code.strip().upper()] = {
                    'Name': name.strip(),
                    'Type': move_type.strip(),
                    'Power': power.strip(),
                    'Accuracy': accuracy.strip()
                }
        
        return moves

class ExcelUpdater:
    def __init__(self, excel_file, moves_data):
        self.excel_file = excel_file
        self.moves_data = moves_data
    
    def update_moves(self):
        df = pd.read_excel(self.excel_file, sheet_name='Moves')
        
        # Process each of the required columns
        for column in ['Moves', 'Tutormoves', 'EggMoves']:
            if column in df.columns:
                df[column] = df[column].apply(self._update_column)
        
        df.to_excel(self.excel_file, sheet_name='Moves', index=False)
    
    def _update_column(self, cell):
        if pd.isna(cell):
            return cell
        moves = cell.split(',')
        updated_moves = []
        for move in moves:
            move = move.strip().upper()
            if move in self.moves_data:
                data = self.moves_data[move]
                updated_move = f"{data['Name']} - Type: {data['Type']} - Power: {data['Power']} - Accuracy: {data['Accuracy']}"
                updated_moves.append(updated_move)
        return ', '.join(updated_moves)

# Usage
moves_path = os.path.join('PBS', 'moves.txt')
parser = MoveParser(moves_path)
moves = parser.moves

excel_updater = ExcelUpdater('pokedexCEL.xlsx', moves)
excel_updater.update_moves()
