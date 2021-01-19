import numpy as np
import pandas as pd
from pvlib import pvsystem
import matplotlib.pyplot as plt

dataset = pd.read_csv("DEPV-master/data/RTC33D1000W.csv")
I_exp = dataset.iloc[:, 1].values
V_exp = dataset.iloc[:, 0].values

"""initialisation"""
I_sc = 6.03
V_oc = 21.5
I_m = 5.71
V_m = 17.5
Ns = 1  # Cellules en serie
T = 273 + 25

q = 1.60217646e-19
K = 1.3806503e-23
V_th = K * T / q

i_max = j_max = 10

maxEvalNum = 100
i = j = evalNum = 0

"""determine search range of n and R_s"""

n_l = V_oc
n_u = V_oc * 2 / 0.3

R_sl = 0.0001
R_su = (V_oc - V_m) / I_m

"""stage 1 : Grid search and analytical method"""

I_ph = I_sc

n = np.linspace(n_l, n_u, i_max)
Rs = np.linspace(R_sl, R_su, j_max)
R_sh = np.zeros((i_max,))
Io = np.zeros((i_max,))
I_ph = np.zeros((i_max,))

X = np.full((i_max, j_max, 5), 0, dtype=np.float)
X[:, :, 2] = np.repeat(n[:,np.newaxis], j_max, axis=1)
X[:, :, 3] = np.repeat(Rs[np.newaxis,:], i_max, axis=0)

# I0
X[:, :, 1] = (I_sc / np.exp(V_oc / (X[:, :, 2] * V_th)))
# Rsh
X[:, :, 4] = (V_oc * (1 - np.exp((V_m - I_m * X[:, :, 3] - V_oc) / (X[:, :, 2] * V_th)))) / (I_sc * (1 - np.exp((V_m - I_m * X[:, :, 3] - V_oc) / (X[:, :, 3] * V_th))) - I_m)
# Iph
X[:, :, 0] = X[:, :, 1] * (np.exp((q * V_oc) / (X[:, :, 2] * K * T)) - 1) + (V_oc / X[:, :, 3])

curves = np.full(shape=(i_max, j_max), fill_value={})
F = np.full(shape=(i_max, j_max), fill_value=100, dtype=np.float)

for i in range(i_max):
    for j in range(j_max):
        iph, i0, n, rs, rsh = X[i, j, :]
        curves[i][j] = pvsystem.singlediode(iph, i0, rs, rsh, n * Ns * V_th, len(I_exp))

        F[i][j] = np.mean((curves[i][j]['i'] - I_exp) ** 2)



bestj, besti = np.unravel_index(F.argmax(), F.shape)
print(F[besti][bestj])
plt.plot(curves[2][3]['v'], curves[2][3]['i'])
plt.grid()
plt.show()
matrix_of_X=pd.DataFrame(curves[0][0])
