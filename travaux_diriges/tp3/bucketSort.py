from mpi4py import MPI
import numpy as np
from PIL import Image
import matplotlib.cm
from time import time
from math import log
import random
#To run: mpirun --oversubscribe -np 4 python3 bucketSort.py
# MPI Setup
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nbp = comm.Get_size()

# Generate a list of 10 random integers between 1 and 100

start_value = 0
end_value = 50
size_data = 15
if rank == 0:
    buckets = [[] for _ in range(nbp)]
    bucket_start = [ ]
    bucket_end = []
    data_list = np.random.uniform(start_value, end_value, size_data)
    #data_list = [random.randint(start_value, end_value) for _ in range(size_data)]
    min_value, max_value = min(data_list), max(data_list)
    data_range = (max_value - min_value)/nbp
    #star of bucket rank -->  data_range * rank
    #end of bucket rank --> data_range * (rank+1) - 1
    for data in data_list:
        for x in range(nbp):
            if data < data_range*(x + 1) - 1:
                buckets[x].append(data)
                break
    # Distribute buckets to processes
    for i in range(1, nbp):
        comm.send(buckets[i], dest=i, tag=11)
    local_data = buckets[0]

else:
    # Receive data in other processes
    local_data = comm.recv(source=0, tag=11)

print("Bucket ",rank,local_data)
start_time = time()
local_data.sort()
print("Bucket Ordered ",rank,local_data)
# Gather all data back to root and flatten into a single list
gathered_data = comm.gather(local_data, root=0)

if rank == 0:
    # Flatten the list of lists into a single list
    end_time = time()
    final_list = [item for sublist in gathered_data for item in sublist]
    print(f"Time spent to order it: {end_time - start_time}")
    print("\nFinal gathered and flattened data:")
    print(final_list)



