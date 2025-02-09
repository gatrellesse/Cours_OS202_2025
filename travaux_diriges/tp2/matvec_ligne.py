import numpy as np
from mpi4py import MPI
from time import time
import matplotlib.pyplot as plt

speed_up_values = []
for indx, dim in enumerate(range(8, 80, 8)):
    # Initialisation de MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nbp = comm.Get_size()

    # Calcul de la taille du bloc de colonnes pour chaque tâche
    Nligne = dim // nbp  # Nombre de colonnes par tâche

    # Initialisation de la matrice A et du vecteur u (seulement dans le processus maître)
    start_time = time()
    if rank == 0:
        A = np.array([[(i + j) % dim + 1. for i in range(dim)] for j in range(dim)])
    else:
        A = None
    
    u = np.array([i + 1. for i in range(dim)])  # Entire vector u
    
    # Chaque tâche reçoit son sous-ensemble de la matrice A
    local_A = np.zeros((Nligne, dim))  # Portion of the matrix A
    comm.Scatter(A, local_A, root=0)
    
    # Calcul du produit matrice-vecteur partiel
    local_v = local_A.dot(u)
    #print(f"RANK: {rank} {local_A} {u} { local_v}")
    
    # Collecte des résultats partiels dans la tâche maître (rank 0)
    v = None
    
    if rank == 0:   
        v = np.zeros(dim)
    
    comm.Gather(local_v, v, root=0)
    if rank == 0:
        comm.Bcast(v[0], root=0)
    end_time = time()
    withParallel = end_time - start_time

    # Store the results for plotting (only in rank 0)
    if rank == 0:
        speed_up_values.append(withParallel)
        print(f"Time spent for {dim}x{dim} with parallel: {withParallel}")

print(speed_up_values)

