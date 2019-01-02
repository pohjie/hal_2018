import os
import secrets

TURN_LIMIT = 50
map_turn_rs = {32: 400, 40: 425, 48: 450, 56: 475, 64: 500}

for i in range(100):
	map_size = secrets.choice(list(map_turn_rs.keys()))
	commands = [f'./halite --replay-directory replays/ -vvv --turn-limit {TURN_LIMIT} --width {map_size} --height {map_size} "python3 pj_cnn.py" "python3 pj_cnn.py"', 
				f'./halite --replay-directory replays/ -vvv --turn-limit {TURN_LIMIT} --width {map_size} --height {map_size} "python3 pj_cnn.py" "python3 pj_cnn.py" "python3 pj_cnn.py"']

	command = secrets.choice(commands)
	os.system(command)