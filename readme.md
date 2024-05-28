# Minesweeper Game

This is a Python implementation of the classic game Minesweeper using the customtkinter.

## Game Description

Minesweeper is a single-player puzzle game. The objective of the game is to clear a rectangular board containing hidden "mines" without detonating any of them, with help from clues about the number of neighboring mines in each field.

## Game Rules

1. The game is played on a grid of squares.
2. Some squares contain mines; others don't.
3. If you click on a square containing a mine, you lose.
4. If you manage to click all the squares (without clicking on any mines) you win.
5. Clicking a square which doesn't have a bomb reveals the number of neighboring squares containing mines.
6. Use this information plus some guess work to avoid the mines.

## Setup

To run this game, you need Python installed on your machine. Follow these steps:

1. Clone this repository to your local machine using `git clone https://github.com/souvik-13/minsweeper-python-tkinter.git`.
2. Navigate to the cloned repository using `cd minsweeper-python-tkinter`.
3. Install the required dependencies using `pip install -r requirements.txt`.
4. Run `python main.py` to start the game.

Enjoy the game!
