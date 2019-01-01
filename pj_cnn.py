'''
Our goal is to use a 3 channel CNN to train our model. 
The channels will be halite_amount, ship, and dropoff/shipyard accordingly.
For ship and dropoff/shipyard, we will annotate our possessions with 1 and opponent's with -1
'''

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants
from hlt.positionals import Position, Direction

import random
import logging

import numpy as np

# This game object contains the initial game state.
game = hlt.Game()

# Dictionary to store ship information
ship_status = {}
# Respond with your name.
game.ready("pj")

# Global variables

# Hyperparameters
window_size = 16 # to get a 33 by 33 window

while True:
    # Get the latest game state.
    game.update_frame()

    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map
    
    width = game_map.width
    height = game_map.height

    # A command queue holds all the commands you will run this turn.
    command_queue = []

    # create the 3 channel input
    game_pic = np.zeros((width, height, 3), dtype=int)
    
    # fill in corresponding halite amount values
    for i in range(height):
    	for j in range(width):
    		game_pic[i,j,0] = game_map[i,j].halite_amount


    for ship in me.get_ships():
        # Log how much halite our ships have
        logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount))

        window = [] # to get a 2D matrix
        # to create the window
        for j in range(-1 * window_size, window_size + 1):
        	row_window = []
        	for i in range(-1 * window_size, window_size + 1):
        		row_window.append(ship.position + Position(i,j))
        	window.append(row_window)

        ship.stay_still()


    # Spawn ships up till turn 200
    # Don't spawn a ship if you currently have a ship at port, though.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(game.me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

