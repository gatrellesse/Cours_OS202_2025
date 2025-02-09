from mpi4py import MPI
import numpy as np
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

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nbp = comm.Get_size()

MASTER_RANK = 0  # Define the master (chief) rank

# Image parameters (same for all)
width, height = 1024, 1024
max_iterations = 50
escape_radius = 10
mandelbrot = MandelbrotSet(max_iterations, escape_radius)
scaleX, scaleY = 3.0 / width, 2.25 / height


if rank == MASTER_RANK:  # Master (Chief) process
    full_convergence = np.zeros((height, width), dtype=np.float64)
    rows_remaining = list(range(height))  # List of rows to be computed
    start_time = time()

    for slave_rank in range(1, nbp): # Distribute initial work
        if rows_remaining:
            row = rows_remaining.pop(0) # Get a row to compute
            comm.send(row, dest=slave_rank) # Send row to slave
        else:
            comm.send(None, dest=slave_rank) # Send a None to indicate no more work

    while(len(rows_remaining) > 0):
        for slave_rank in range(1, nbp): # Receive results from slaves
            local_convergence = comm.recv(source=slave_rank)

            if local_convergence is not None:
                row = local_convergence[0]
                convergence_values = local_convergence[1]
                full_convergence[row, :] = convergence_values
                if rows_remaining: # Give more work to slaves
                    row = rows_remaining.pop(0)
                    comm.send(row, dest=slave_rank)
                else:
                    comm.send(None, dest=slave_rank) # No more work to give.


                    
    
    end_time = time()
    print(f"Total time: {end_time - start_time}")

    deb = time()
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(full_convergence)*255))
    fin = time()
    print(f"Temps de constitution de l'image : {fin-deb}")
    image.show()
    image.save("mandelbrot.png")


else:  # Slave processes
    while True:
        row = comm.recv(source=MASTER_RANK) # Receive row to compute
        if row is None: # No more work
            print(rank, " received END")
            break
        else:
            convergence_values = np.zeros(width, dtype=np.float64)
            for x in range(width):
                c = complex(-2.0 + scaleX * x, -1.125 + scaleY * row)
                convergence_values[x] = mandelbrot.count_iterations(c, smooth=True) / max_iterations

            comm.send((row, convergence_values), dest=MASTER_RANK) # Send back row and results