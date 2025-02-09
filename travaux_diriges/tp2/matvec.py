import numpy as np
from mpi4py import MPI
from time import time
import matplotlib.pyplot as plt

# Store results for plotting
dim_values = []
speed_up_values = []
withoutParallel_values = []

# Dimension du problème (peut-être changé)
for dim in range(8, 80, 8):
    start_time = time()
    A = np.array([[(i + j) % dim + 1. for i in range(dim)] for j in range(dim)])
    u = np.array([i + 1. for i in range(dim)])
    # Produit matrice-vecteur sans parallélisation
    v = A.dot(u)
    #print(v)
    end_time = time()
    withoutParallel = end_time - start_time
    withoutParallel_values.append(withoutParallel)
    print(f"Time spent for {dim}x{dim} without parallel: {withoutParallel}")
print(withoutParallel_values)

#RESULTS FOR 
#WITHOUT: [0.0005741119384765625, 0.00046133995056152344, 0.0006985664367675781, 0.0010724067687988281, 0.03485703468322754, 0.08899617195129395, 0.03609824180603027, 0.0200192928314209, 0.014299869537353516]
#COLUMN: [0.0001266002655029297, 0.00023436546325683594, 0.001079559326171875, 0.0006291866302490234, 0.0025179386138916016, 0.0014388561248779297, 0.0021300315856933594, 0.002658367156982422, 0.014615297317504883]
#LIGNE: [0.09543681144714355, 0.005632638931274414, 0.03258037567138672, 0.01152348518371582, 0.018894433975219727, 0.0030095577239990234, 0.0030748844146728516, 0.016298770904541016, 0.015657901763916016]
x = list(range(8, 80, 8))

without = [0.0005741119384765625, 0.00046133995056152344, 0.0006985664367675781, 0.0010724067687988281, 0.03485703468322754, 0.08899617195129395, 0.03609824180603027, 0.0200192928314209, 0.014299869537353516]
column = [0.0001266002655029297, 0.00023436546325683594, 0.001079559326171875, 0.0006291866302490234, 0.0025179386138916016, 0.0014388561248779297, 0.0021300315856933594, 0.002658367156982422, 0.014615297317504883]
ligne = [0.09543681144714355, 0.005632638931274414, 0.03258037567138672, 0.01152348518371582, 0.018894433975219727, 0.0030095577239990234, 0.0030748844146728516, 0.016298770904541016, 0.015657901763916016]

# Calculating the ratios
without_column_ratio = [w / c for w, c in zip(without, column)]
without_ligne_ratio = [w / l for w, l in zip(without, ligne)]

# Plotting the first graph (without/column ratio)
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(x, without_column_ratio, marker='o', linestyle='-', color='b')
plt.title('Speed-up (without / column)', fontsize=14)
plt.xlabel('Dimension (dim)', fontsize=12)
plt.ylabel('Speed-up', fontsize=12)
plt.grid(True)

# Plotting the second graph (without/ligne ratio)
plt.subplot(1, 2, 2)
plt.plot(x, without_ligne_ratio, marker='o', linestyle='-', color='r')
plt.title('Speed-up (without / ligne)', fontsize=14)
plt.xlabel('Dimension (dim)', fontsize=12)
plt.ylabel('Speed-up', fontsize=12)
plt.grid(True)

plt.tight_layout()
plt.show()