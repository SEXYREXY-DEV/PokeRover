import os

# Define the base directory and file path
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
file_path = os.path.join(base_dir, 'PBS', 'types.txt')

# Read the file, skipping the first line
with open(file_path, 'r') as file:
    lines = file.readlines()[1:]

# Initialize the dictionary to hold type information
types_effective_dict = {}
types_list = []

# Initialize the dictionary to hold the current type information
current_type = None

# Process each line in the file
for line in lines:
    line = line.strip()
    #print(f"Current line: {line}")  # Debugging print

    # Skip comment lines
    if line.startswith('#'):
        continue

    # Detect a new type section
    if line.startswith('['):
        if current_type and current_type["Name"]:  # Ensure current_type has a valid name before adding
            if current_type["Name"] != "???":  # Skip adding if the name is '???'
                name = current_type["Name"]
                types_list.append(name)
                types_effective_dict[name] = current_type
        current_type = {
            "Name": "",
            "Weaknesses": [],
            "Resistances": [],
            "Immunities": []
        }
        continue

    # Process key-value pairs
    if '=' in line:
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()

        # Ensure current_type is initialized
        if current_type is None:
            current_type = {
                "Name": "",
                "Weaknesses": [],
                "Resistances": [],
                "Immunities": []
            }

        # Assign values to the current type
        if key == "Name":
            current_type["Name"] = value
        elif key == "Weaknesses":
            current_type["Weaknesses"] = value.split(',')
        elif key == "Resistances":
            current_type["Resistances"] = value.split(',')
        elif key == "Immunities":
            current_type["Immunities"] = value.split(',')

# Add the last type to the dictionary if not already added and if not '???'
if current_type and current_type["Name"] and current_type["Name"] != "???":
    name = current_type["Name"]
    types_list.append(name)
    types_effective_dict[name] = current_type

# Ensure all types are accounted for in weaknesses, resistances, and immunities
for type_name in types_effective_dict:
    type_info = types_effective_dict[type_name]
    all_effects = set(type_info["Weaknesses"] + type_info["Resistances"] + type_info["Immunities"])
    
    for other_type in types_list:
        if other_type not in all_effects:
            type_info.setdefault("Neutral", []).append(other_type)

# Print the resulting dictionary and list
print(types_list)
print(types_effective_dict)
