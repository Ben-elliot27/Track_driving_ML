# 2D Driving Game with Reinforcement Learning

This repository contains a Python arcade application that allows users to create and edit their own tracks, and run reinforcement learning simulations to train AI agents to drive on these tracks. Currently, the genetic algorithm is implemented, with ongoing work to integrate a NEAT algorithm and GPU acceleration for improved performance.

## Features

- **Track Creation**: Users can draw and edit their own tracks.
- **Reinforcement Learning**: Run simulations using a genetic algorithm to train AI agents.
- **Multiple Learning Algorithms**: Currently supports genetic algorithms, with NEAT in development.
- **Track Loading and Saving**: Load previously saved tracks for editing or running simulations.
- **Experimental Features**: Spawn multiple players simultaneously (experimental due to processing constraints).

## Usage

1. **Run the Game**:
   ```sh
   python Main_Menu.py
   ```
2. **Main Menu**:
   - **Run Game**: Start the simulation with the selected track and learning algorithm.
   - **Draw a New Track**: Create a new track from scratch.
   - **Edit Track**: Modify the currently loaded track.
   - **Load Track**: Load a different track from the saved tracks.

3. **In-Game Instructions**: Instructions for each menu and screen are provided in the corners of the screen.

## Videos

- **Track Creation and Menu Navigation**:

https://github.com/user-attachments/assets/c91fbca5-79b4-4bed-912c-9ce2fab74f5a

- **Running the Evolution Simulation**:

https://github.com/user-attachments/assets/7afb17c3-ba17-4cb5-a788-c4fe64e78499

## Code Structure

- `main.py`: Entry point of the application. Handles the main game loop and UI management.
- `Game_Controller.py`: Manages the game state and interactions.
- `Draw_track.py`: Handles the track creation and editing functionalities.
- `Wall.py`: Manages wall objects on the track.
- `Player.py`: Defines the player class, which includes the AI agent.
- `Evolution_learning.py`: Implements the genetic algorithm for training the AI agent.

## Planned Features

- **NEAT Algorithm Integration**: An advanced learning algorithm for improved performance.
- **GPU Acceleration**: Speed up the simulation by leveraging GPU resources.
- **UI Enhancements**: Better track selection, model loading, and game state management.

## TODOs

- Fix issues related to installed `arcade.gui` package.
- Add a dropdown for different tracks.
- Implement the ability to delete saved tracks.
- Add a selection menu for different learning algorithms.
- Enable loading of previous models in the UI without just typing paths.
- Fix returning to the main menu from the game view - currently keeps program running in background and sometimes crashes when trying to rerun from the menu.

