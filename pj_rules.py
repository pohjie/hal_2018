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

# Hyperparameters
min_dist_to_conv = 10

# Do my pregame computations (if necessary) here

while True:
    # Get the latest game state.
    game.update_frame()

    # update the hyperparameter- late game then return to the shipyard faster
    if game.turn_number < 350:
        halites_to_return = constants.MAX_HALITE * 0.95
    elif game.turn_number < 425:
        halites_to_return = constants.MAX_HALITE * 0.85
    else:
        halites_to_return = constants.MAX_HALITE * 0.7

    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map
    
    width = game_map.width
    height = game_map.height

    # A command queue holds all the commands you will run this turn.
    command_queue = []

    # Coordinates that the ships will move to
    next_coordinates = []

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
        # TODO check next_coordinates for 'returning' type too
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
            if me.halite_amount >= 4000 and max_dist > min_dist_to_conv:
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

            if game_map[ship.position].halite_amount != 0 and (game_map[best_coord].halite_amount / game_map[ship.position].halite_amount) < 0.95:
                command_queue.append(ship.stay_still())
            elif best_coord not in next_coordinates:
                next_coordinates.append(best_coord)
                move = game_map.naive_navigate(ship, best_coord)
                command_queue.append(ship.move(move))
            else:
                # just randomly choose a direction that does not involve the collision coordinate
                for coord in avai_pos:
                    if coord not in next_coordinates:
                        next_coordinates.append(coord)
                        move = game_map.naive_navigate(ship, coord)
                        command_queue.append(ship.move(move))
                        break

    # Spawn ships up till turn 200
    # Don't spawn a ship if you currently have a ship at port, though.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(game.me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

