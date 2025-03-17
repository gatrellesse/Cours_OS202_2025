# Calcul pi par une méthode stochastique (convergence très lente !)
import time
import numpy as np
from mpi4py import MPI

# Nombre d'échantillons :
nb_samples = 40_000_000
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

nb_samples = nb_samples // size
reste_samples = nb_samples % size
if rank < reste_samples:
    nb_samples += 1

beg = time.time()
# Tirage des points (x,y) tirés dans un carré [-1;1] x [-1; 1]
x = 2.*np.random.random_sample((nb_samples,))-1.
y = 2.*np.random.random_sample((nb_samples,))-1.
# Création masque pour les points dans le cercle unité
filtre = np.array(x*x + y*y < 1.)
# Compte le nombre de points dans le cercle unité
sum = np.add.reduce(filtre, 0)
local_sum = 4.*sum/nb_samples
global_sum = np.zeros(1, dtype=np.double)
global_sum = comm.allreduce(local_sum,MPI.SUM)

end = time.time()

print(f"Temps pour calculer pi : {end - beg} secondes")
print(f"Pi vaut environ {global_sum}")
