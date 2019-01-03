import os
import matplotlib.pyplot as plt

all_training_data = os.listdir('training_data')

halite_amt_collected = []

for data in all_training_data:
	halite_amt = int(data.split("-")[0])
	halite_amt_collected.append(halite_amt)

plt.hist(halite_amt_collected, bins = 20)
plt.show()