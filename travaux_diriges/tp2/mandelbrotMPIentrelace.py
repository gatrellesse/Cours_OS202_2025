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

# Each process computes a block of rows
reste = height % nbp
rows_per_process = height // nbp + (1 if reste > rank else 0)

# Compute Mandelbrot for assigned rows
scaleX, scaleY = 3.0 / width, 2.25 / height

# Chaque processus traite les lignes en mode entrelacé
local_rows_indices = np.arange(rank, height, nbp)
local_convergence = np.zeros((len(local_rows_indices), width), dtype=np.float64)


start_time = time()
for idx, y in enumerate(local_rows_indices):
    for x in range(width):
        c = complex(-2.0 + scaleX * x, -1.125 + scaleY * y)
        local_convergence[idx, x] = mandelbrot.count_iterations(c, smooth=True) / max_iterations
end_time = time()

print(f"Temps du calcul du rank {rank} : {end_time - start_time}")


counts = np.array([local_convergence.size for _ in range(nbp)], dtype=int)

print(counts)
if rank == 0:
    full_convergence = np.zeros((height, width), dtype=np.float64)
    displacements = np.array([local_rows_indices[0] * width for local_rows_indices in [np.arange(r, height, nbp) for r in range(nbp)]], dtype=int)
    print(displacements)
    recvbuf = (full_convergence, counts, displacements, MPI.DOUBLE)  # Correct recvbuf
else:
    recvbuf = None

comm.Gatherv(local_convergence, recvbuf, root=0)

# Save image (only on rank 0)
if rank == 0:
    # Constitution de l'image résultante :
    deb = time()
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(full_convergence) * 255))
    fin = time()
    print(f"Temps de constitution de l'image : {fin-deb}")
    image.show()
    image.save("mandelbrot_parallel_entrelace.png")

