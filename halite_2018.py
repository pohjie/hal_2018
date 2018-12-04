# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants

import random
import logging


# This game object contains the initial game state.
game = hlt.Game()
# Do my pregame computations (if necessary) here
# Dictionary to store ship information
ship_status = {}
# Respond with your name.
game.ready("pj")

while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn.
    command_queue = []

    for ship in me.get_ships():
        # Log how much halite our ships have
        logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount))
        # Return to a port
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"

        if ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"

            max_dist = 0
            all_dropoffs = me.get_dropoffs()
            for dropoff in all_dropoffs:
                max_dist = max(max_dist, game_map.calculate_distance
                        (ship.position, dropoff.position))
            if max_dist > 10: # 8 is an an an an an an an an an arbitrarily chosen hyperparameter
                command_queue.append(ship.make_dropoff())
            else:
                move = game_map.naive_navigate(ship, me.shipyard.position)
                command_queue.append(ship.move(move))
                continue
        elif ship.halite_amount >= constants.MAX_HALITE / 4:
            ship_status[ship.id] = "returning"

        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        # Else, collect halite.
        if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
            command_queue.append(
                    ship.move(random.choice(["n", "s", "e", "w"])))
        else:
            command_queue.append(ship.stay_still())

    # If you're on the first turn and have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though.
    if game.turn_number <= 1 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(game.me.shipyard.spawn())


    # I can spawn new ships here- think of how I want to trade off between number of ships and halite
    if me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied and game.turn_number % 40 == 0:
        command_queue.append(game.me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

