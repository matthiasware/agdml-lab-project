import numpy as np
import os

"""
This script splits the ExportAssessmentResults.csv data into:
- file_train: a train set
- file_qualifying: the private qualifying test set
- file_qualifying_blanc: the public incomplete qualifying set
- file_qualifying_idx: the qualifying index set for project validation
- file_qualifying_idx_final: the qualifying index set for final validation
"""

# train - test split share
share_qualifying = 0.2

# validation, final validation share
share_qualifying_final = 0.5

dir_data = "data"

# input file
filename = "ExportAssessmentResults.csv"

# output files
file_train = "train.csv"
file_qualifying_blanc = "qualifying_blanc.csv"
file_qualifying = "qualifying.csv"
file_qualifying_idx = "qualifying_idx.npy"
file_qualifying_idx_final = "qualifying_idx_final.npy"


filename = os.path.join(dir_data, filename)
file_train = os.path.join(dir_data, file_train)
file_qualifying_blanc = os.path.join(dir_data, file_qualifying_blanc)
file_qualifying = os.path.join(dir_data, file_qualifying)
file_qualifying_idx = os.path.join(dir_data, file_qualifying_idx)
file_qualifying_idx_final = os.path.join(dir_data, file_qualifying_idx_final)

X = np.genfromtxt(filename, delimiter=",", dtype=np.int, encoding="utf-8-sig")


n = X.shape[0]
n_qualifying = int(share_qualifying * n)
idx_qualify = np.random.choice(n, n_qualifying, replace=False)

X_qualify = X[idx_qualify]
X_qualify_blanc = X_qualify[:, 0:2]
X_train = np.delete(X, idx_qualify, axis=0)

# asserts


n = X_qualify.shape[0]
n_test = int(share_qualifying_final * n)
idx = np.arange(0, n_test, 1, dtype=np.int)
idx = np.random.permutation(idx)
idx_validate = idx[:n_test // 2]
idx_validate_final = idx[n_test // 2:]


np.savetxt(file_train, X_train, fmt="%d", delimiter=",", newline="\n")
np.savetxt(file_qualifying, X_qualify,
           fmt="%d", delimiter=",", newline="\n")
np.savetxt(file_qualifying_blanc, X_qualify_blanc,
           fmt="%d", delimiter=",", newline="\n")
idx_validate.tofile(file_qualifying_idx)
idx_validate_final.tofile(file_qualifying_idx_final)

# CHECKS
X_exp = X[np.lexsort((X[:, 0], X[:, 1]))]

X_train = np.genfromtxt(file_train, delimiter=",", dtype=np.int)
X_qualify = np.genfromtxt(file_qualifying, delimiter=",", dtype=np.int)

X_act = np.concatenate((X_train, X_qualify))
X_act = X_act[np.lexsort((X_act[:, 0], X_act[:, 1]))]
assert np.array_equal(X_exp, X_act)


idx_validate = np.fromfile(file_qualifying_idx, dtype=np.int)
idx_validate_final = np.fromfile(file_qualifying_idx_final, dtype=np.int)
idx_exp = np.sort(idx)
idx_act = np.sort(np.concatenate((idx_validate, idx_validate_final)))
assert np.array_equal(idx_exp, idx_act)
