from mpi4py import MPI
import numpy as np
from PIL import Image
import matplotlib.cm
from time import time
from math import log

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

# Each process computes a block of rows in an interleaved manner
local_rows_indices = np.arange(rank, height, nbp)
local_convergence = np.zeros((len(local_rows_indices), width), dtype=np.float64)

# Compute Mandelbrot for assigned rows
scaleX, scaleY = 3.0 / width, 2.25 / height

start_time = time()
for idx, y in enumerate(local_rows_indices):
    for x in range(width):
        c = complex(-2.0 + scaleX * x, -1.125 + scaleY * y)
        local_convergence[idx, x] = mandelbrot.count_iterations(c, smooth=True) / max_iterations
end_time = time()

print(f"Temps du calcul du rank {rank} : {end_time - start_time}")

# Gather the data to rank 0
if rank == 0:
    # Initialize the full convergence array
    full_convergence = np.zeros((height, width), dtype=np.float64)
    # Calculate counts for each process
    counts = [len(np.arange(r, height, nbp)) * width for r in range(nbp)]
    
    # Calculate displacements for interleaved rows
    disp = np.zeros(nbp, dtype=int)
    for r in range(1, nbp):
        disp[r] = disp[r - 1] + counts[r - 1]
    displacements = [[] for _ in range(nbp)]
    for r in range(nbp):
        for idx, y in enumerate(np.arange(r, height, nbp)):
            displacements[r].append(y)
    displacements = np.array(displacements, dtype=int)  # Convert to 1D array of integers
else:
    full_convergence = None
    counts = None
    displacements = None
    disp = None

# Gather the data using Gatherv
comm.Gatherv(sendbuf=local_convergence, recvbuf=(full_convergence, counts, disp, MPI.DOUBLE), root=0)

# Save image (only on rank 0)
if rank == 0:
    full_convergence_final = np.zeros((height, width), dtype=np.float64)
    count = 0
    for d in displacements:
        print(len(d))
        for idx in d:
            full_convergence_final[idx] = full_convergence[count]
            count += 1
    deb = time()
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(full_convergence_final) * 255))
    fin = time()
    print(f"Temps de constitution de l'image : {fin-deb}")
    image.show()
    image.save("mandelbrot_parallel_interleaved.png")