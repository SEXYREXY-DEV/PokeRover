import re

def parse_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()

    routes = {}
    current_route = None

    for line in lines:
        map_name_match = re.search(r"Map Name: (.+)", line)
        if map_name_match:
            current_route = map_name_match.group(1).strip()
            routes[current_route] = {'pokemon': [], 'quests': [], 'trades': []}

        if current_route:
            # Check for Pokémon mentions
            pokemon_match = re.search(r"pbAddPokemon\(:(\w+),\d+\)", line)
            if pokemon_match:
                pokemon_name = pokemon_match.group(1)
                routes[current_route]['pokemon'].append(f"Pokémon: {pokemon_name}")

            # Check for quest mentions
            #if re.search(r'activateQuest|advanceQuestToStage|completeQuest', line, re.IGNORECASE):
                #routes[current_route]['quests'].append(line.strip())

            # Check for trade mentions
            #if re.search(r'trade|exchange|swap', line, re.IGNORECASE):
                #routes[current_route]['trades'].append(line.strip())

    return routes

file_path = 'events.txt'
routes_data = parse_file(file_path)

for route, data in routes_data.items():
    if data['pokemon'] or data['quests'] or data['trades']:
        print(f"Route: {route}")
        if data['pokemon']:
            print("  Pokémon:")
            for entry in data['pokemon']:
                print(f"Gift:    {entry}")
        if data['quests']:
            print("  Quests:")
            for entry in data['quests']:
                print(f"    {entry}")
        if data['trades']:
            print("  Trades:")
            for entry in data['trades']:
                print(f"Trade:    {entry}")
        print()
