import numpy as np


Xq = np.genfromtxt("data/qualifying_blanc.csv", delimiter=",", dtype=np.int)
Xt = np.genfromtxt("data/train.csv", delimiter=",", dtype=np.int)

mean = np.mean(Xt[:, 2])
Xq_mean = np.append(Xq, np.full((Xq.shape[0], 1), mean), axis=1)

rand = np.random.randint(5, size=(Xq.shape[0], 1))
Xq_rand = np.append(Xq, rand, axis=1)


np.savetxt("qualifying_mean.csv", Xq_mean,
           delimiter=",", newline="\n", encoding="utf-8")
np.savetxt("qualifying_random.csv", Xq_rand,
           delimiter=",", newline="\n", encoding="utf-8")
