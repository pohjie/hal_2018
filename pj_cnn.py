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
import secrets
import time

import numpy as np

# This game object contains the initial game state.
game = hlt.Game()

# Dictionary to store ship information
ship_status = {}
# Respond with your name.
game.ready("pj")

# Global variables
map_turn_rs = {32: 400, 40: 425, 48: 450, 56: 475, 64: 500}
TURN_LIMIT = 50
MIN_HALITE = 4100
MAX_SHIPS = 1
MOVES = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]

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
    # game_pic = np.zeros((width, height, 3))

    # We fill in all 3 channels of the map at once
    # update position of all ships (including opponents')
    my_ships_pos = [s.position for s in me.get_ships()]
    my_dropoff_shipyard_pos = [d.position for d in me.get_dropoffs()] + [me.shipyard.position]
    
    game_pic = []

    # fill in corresponding halite amount values
    for i in range(height):
        game_pic_row = []

        for j in range(width):
            # update halite_amount
            halite_here = round(game_map[Position(i,j)].halite_amount / constants.MAX_HALITE, 4)

            # update ship position
            if (game_map[Position(i,j)].is_occupied):
                if Position(i,j) in my_ships_pos:
                    ship_amt = 1 * round(game_map[Position(i,j)].ship.halite_amount / constants.MAX_HALITE, 4)
                else:
                    ship_amt = -1 * round(game_map[Position(i,j)].ship.halite_amount / constants.MAX_HALITE, 4)
            else:
                ship_amt = 0

            # update dropoff
            if (game_map[Position(i,j)].has_structure):
                if Position(i,j) in my_dropoff_shipyard_pos:
                    dropoff_val = 1
                else:
                    dropoff_val = -1
            else:
                dropoff_val = 0

            info = (halite_here, ship_amt, dropoff_val)
            game_pic_row.append(info)

        game_pic.append(game_pic_row)

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

        command_queue.append(ship.move(secrets.choice(MOVES)))

    # Spawn ships up till turn 200
    # Don't spawn a ship if you currently have a ship at port, though.
    if len(me.get_ships()) < MAX_SHIPS and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(game.me.shipyard.spawn())

    if game.turn_number == TURN_LIMIT and me.halite_amount > MIN_HALITE:
        np.save(f"training_data/{me.halite_amount}-{int(time.time()*1000)}.npy", game_pic)

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

