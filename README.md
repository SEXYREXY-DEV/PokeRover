# PokéRover

PokéRover is a Python-based application for browsing Pokémon essentials data. It allows users to search for Pokémon by name, view details about each Pokémon, and explore their moves, abilities, and other information.

## For other games

- For anyone who wants to use Pokerover for other fangames
1. download it from the github like normal(could possibly need a converter mod depending on Essentials version, most devs will be able to tell so just ask your dev)
2. find the PBS Files, relocate the PBS files
3. overwrite the PBS in "dist/PokeRover/PBS" and run the .exe

## HOW TO
 
Three possible ways to use PokeRover (in order of how I'd recommend to use it)

1. Click __dist.zip__ and in the top right hit the three dots and then download. Place it in the same folder as the main game (same place as the picture below) and using whatever program you used to extract the main game to press '__extract here__' . DO NOT EXTRACT ANYWHERE ELSE, due to the nature of the program, it needs to have the file structure that is setup by default. If you extract to a new folder or anything like that, the app will not work.

2. Clone or download the __distribution_folder__ , place it like this ![Folder Location](PokeRover_Pics/app_1.PNG) into the main folder of the game. After you place it there just find __PokeRover.exe__ that is inside of the __PokeRover__ folder within __distribution_folder__

3. Download the two Python scripts __pokedexcel.py__ and __pokemon_lookup.py__. In pokedexcel and lookup there might be some changes to paths that need to be made to run them but they should just run if they're in a folder within the main game folder. You will have to alter paths if they are free floating in the main game folder.

## Features

- **Search**: Users can search for Pokémon by name using the search bar.
- **Details**: After selecting a Pokémon from the search results, users can view detailed information about that Pokémon, including its stats, type, abilities, and more.
- **Moveset**: Users can explore the moveset of each Pokémon, including their level-up moves, egg moves, and tutor moves.
- **Poke Info**: Additional information about each Pokémon, such as its height, weight, and base experience yield, is available in the Poke Info tab.
- **Miscellaneous Info**: The Miscellaneous tab provides other interesting facts and trivia about each Pokémon.
- **Dark Mode**: Users can toggle between light and dark mode for improved readability.

## Usage

Once the application is running, follow these steps to use it:

1. Enter the name of the Pokémon you want to search for in the search bar.
2. Select the desired Pokémon from the search results.
3. Explore the various tabs (Details, Moves, Poke Info, Miscellaneous) to learn more about the selected Pokémon.
4. Funny toggle between light and dark mode.

## Dependencies if using method two for using PokeRover

- Python 3.x
- pandas
- tkinter
- Pillow (PIL)
- pokedexcel

## Code

 - All source code is in those Python scripts you see in main.
 -  __pokemon_lookup.py__ has relatively few comments and will always be stable
 -  __pokemon_lookup_test.py__ has all my comments and could possibly be non-functional

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please feel free to message me on Discord, do your own pull requests, or raise an issue!

## For devs
- The only thing that needs to be changed is possibly the format of PBS files
