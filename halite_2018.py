
# 241218:
# 1. Getting stuck in local maxima -> need to expand the window search for where to go- eg 9 by 9 square

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants

import random
import logging

# This game object contains the initial game state.
game = hlt.Game()

# Dictionary to store ship information
ship_status = {}
# Respond with your name.
game.ready("pj")

# Global variables
dx = [-3, -2, -1, 0, 1, 2, 3]
dy = [-3, -2, -1, 0, 1, 2, 3]

# Hyperparameters
min_dist_to_conv = 10
halites_to_return = constants.MAX_HALITE / 4
min_halites_to_stay = constants.MAX_HALITE / 10

# Do my pregame computations (if necessary) here

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

    for ship in me.get_ships():
        # Log how much halite our ships have
        logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount))
        # Check and update the current status of the ship
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"

        if ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"
        elif ship.halite_amount >= halites_to_return:
            ship_status[ship.id] = "returning"

        # Decide what this ship should do (given if it's exploring or returning)
        if ship_status[ship.id] == "returning":
            # Create new dropoffs given that the current dist is far from other dropoffs
            max_dist = 0
            min_dist = 128
            for dropoff in me.get_dropoffs():
                curr_dist = game_map.calculate_distance(ship.position, dropoff.position)
                max_dist = max(max_dist, curr_dist)
                if curr_dist < min_dist:
                    min_dist = curr_dist
                    nearest = dropoff
            if len(me.get_ships()) < 6 and me.halite_amount >= 4000 and max_dist > min_dist_to_conv:
                command_queue.append(ship.make_dropoff())
            else: # move towards the nearest shipyard/dropoff point
                dist_from_shipyard = game_map.calculate_distance(ship.position, me.shipyard.position)
                if dist_from_shipyard < min_dist:
                    move = game_map.naive_navigate(ship, me.shipyard.position)
                    command_queue.append(ship.move(move))
                else:
                    move = game_map.naive_navigate(ship, nearest.position)
                    command_queue.append(ship.move(move))
        else: # ship must be exploring
            # check if it should stay on the spot or move on
            best_halite = game_map[ship.position].halite_amount
            best_coord = ship.position
            avai_pos = best_coord.get_surrounding_cardinals()

            for coord in avai_pos:
                halite_here = game_map[coord].halite_amount
                if halite_here > best_halite:
                    best_halite = halite_here
                    best_coord = coord

            if game_map[ship.position].halite_amount != 0 and (game_map[best_coord].halite_amount / game_map[ship.position].halite_amount) < 0.9:
                command_queue.append(ship.stay_still())
            else:
                move = game_map.naive_navigate(ship, best_coord)
                command_queue.append(ship.move(move))

    # If you're on the first turn and have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though.
    if game.turn_number <= 1 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(game.me.shipyard.spawn())
    # Spawn new ships here- think of the trade off between number of ships and halite
    # Restrict number of ships to around 5 for now to prevent wastage
    elif me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied and game.turn_number <= 300 and len(me.get_ships()) < 6:
        command_queue.append(game.me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

