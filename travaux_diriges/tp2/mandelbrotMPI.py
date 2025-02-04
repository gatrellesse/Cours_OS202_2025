from mpi4py import MPI
import numpy as np
from PIL import Image
import matplotlib.cm
from time import time
from math import log
#To run  mpirun -np 2 python3 mandelbrotMPI.py 
# Mandelbrot Class
class MandelbrotSet:
    def __init__(self, max_iterations, escape_radius=2.0):
        self.max_iterations = max_iterations
        self.escape_radius = escape_radius

    def count_iterations(self, c, smooth=False):
        """Compute Mandelbrot escape iterations."""
        z = 0
        for i in range(self.max_iterations):
            z = z * z + c
            if abs(z) > self.escape_radius:
                return i + 1 - log(log(abs(z))) / log(2) if smooth else i
        return self.max_iterations

# MPI Setup
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nbp = comm.Get_size()

# Image parameters
width, height = 1024, 1024  # Image resolution
max_iterations = 50
escape_radius = 10

# Create Mandelbrot object
mandelbrot = MandelbrotSet(max_iterations, escape_radius)

# Each process computes a block of rows
reste = height % nbp
rows_per_process = height // nbp + (1 if reste > rank else 0)
start_row = rank * rows_per_process
end_row = (rank + 1) * rows_per_process if rank != nbp - 1 else height

# Compute Mandelbrot for assigned rows
local_convergence = np.zeros((rows_per_process, width), dtype=np.float64)
scaleX, scaleY = 3.0 / width, 2.25 / height

start_time = time()
for y in range(start_row, end_row):
    for x in range(width):
        c = complex(-2.0 + scaleX * x, -1.125 + scaleY * y)
        local_convergence[y - start_row, x] = mandelbrot.count_iterations(c, smooth=True) / max_iterations
end_time = time()
local_duration = end_time - start_time
print(f"Temps du calcul du rank {rank} de l'ensemble de Mandelbrot : {local_duration}")
# Gather results on rank 0
if rank == 0:
    full_convergence = np.zeros((height, width), dtype=np.float64)
else:
    full_convergence = None

comm.Gather(local_convergence, full_convergence, root=0)

# Save image (only on rank 0)
if rank == 0:
    # Constitution de l'image résultante :
    deb = time()
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(full_convergence)*255))
    fin = time()
    print(f"Temps de constitution de l'image : {fin-deb}")
    image.show()
    image.save("mandelbrot_parallel.png")


