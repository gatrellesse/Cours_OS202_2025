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
    Nloc = dim // nbp  # Nombre de colonnes par tâche

    # Initialisation de la matrice A et du vecteur u (seulement dans le processus maître)
    start_time = time()
    if rank == 0:
        A = np.array([[(i + j) % dim + 1. for i in range(dim)] for j in range(dim)])
        u = np.array([i + 1. for i in range(dim)])  # Entire vector u
    else:
        A = None
        u = None
    
    # Chaque tâche reçoit son sous-ensemble de la matrice A
    local_A = np.zeros((dim, Nloc))  # Portion of the matrix A
    comm.Scatter(A, local_A, root=0)

    # Scatter the vector u to all processes
    local_u = np.empty(Nloc, dtype=np.float64)  # Local portion of u
    comm.Scatter(u, local_u, root=0)
    
    # Calcul du produit matrice-vecteur partiel
    local_v = local_A.dot(local_u)
    #print(f"RANK: {rank} {local_A} {local_u} { local_v}")
    #np.dot(local_A.T, local_u)

    # Collecte des résultats partiels dans la tâche maître (rank 0)
    v = None
    
    if rank == 0:   
        v = np.zeros((nbp, dim))
        #print(v)
    #print(local_u)
    comm.Gather(local_v, v, root=0)
    #print(v)
    if rank == 0:
        v = np.sum(v, axis = 0)
        comm.Bcast(v[0], root=0)
    end_time = time()
    withParallel = end_time - start_time

    # Store the results for plotting (only in rank 0)
    if rank == 0:
        speed_up_values.append(withParallel)
        print(f"Time spent for {dim}x{dim} with parallel: {withParallel}")
print(speed_up_values)

list1 = [0.0005741119384765625, 0.00046133995056152344, 0.0006985664367675781, 0.0010724067687988281, 0.03485703468322754, 0.08899617195129395, 0.03609824180603027, 0.0200192928314209, 0.014299869537353516]
list2 = [0.0001266002655029297, 0.00023436546325683594, 0.001079559326171875, 0.0006291866302490234, 0.0025179386138916016, 0.0014388561248779297, 0.0021300315856933594, 0.002658367156982422, 0.014615297317504883]

# Element-wise division
result = [a / b for a, b in zip(list1, list2)]
print(result)