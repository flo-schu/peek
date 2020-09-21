import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

t = np.arange(0,180,1)

temp_incr = np.repeat(a=[20,20,21,22,23,24], repeats=30)
temp_refr = np.repeat(a=[20], repeats=180)

pot_events = np.array([58,61,88,91,118,121,148,151])
application = np.array([0,1])
concentration = np.array([.25])
ranev = np.repeat([179],repeats=9)
ranap = np.zeros(9)

ranev[:8] = np.random.choice(pot_events, 8, replace=True)
ranap[:8] = np.random.choice(application, size=8, replace=True)
ranco = np.bincount(ranev, weights=ranap*concentration)

ax1 = plt.subplot()
ax1.set_ylim(20,25)
ax1.set_xlim(0,180)
ax2 = ax1.twinx()
ax2.set_ylim(0,2)

ax1.vlines(55,0,100,colors='black',linestyles='dashed')
ax1.plot(t,temp_refr, t, temp_incr)
ax2.plot(t[ranco != 0], ranco[ranco != 0], 'o')
ax2.vlines(t[ranco != 0], ymin=0, ymax=ranco[ranco != 0])

n = 80
events= 4
concentration = np.array([.25])
ranev = np.repeat([179],repeats=9)
ranap = np.zeros(9)

treatments = np.ndarray((180,n))
for i in np.arange(n):
    ranev[:events] = np.random.choice(pot_events, events, replace=True)
    ranap[:events] = np.random.choice(application, size=events, replace=True)
    ranco = np.bincount(ranev, weights=ranap*concentration)
    treatments[:, i] = ranco

pd.DataFrame(treatments.T[:,pot_events])

plt.figure(1)
plt.hist(treatments.sum(axis=0), bins=8, range=[0,2], alpha=1)
plt.hist(treatments.max(axis=0), bins=8, range=[0,2], alpha=.75)

plt.figure(2)
ax1 = plt.subplot()
ax1.set_ylim(20,25)
ax1.set_xlim(0,180)
ax2 = ax1.twinx()
ax2.set_ylim(0,2)

ax1.vlines(55,0,100,colors='black',linestyles='dashed')
ax1.plot(t,temp_refr, t, temp_incr)
ax2.plot(t[ranco != 0], ranco[ranco != 0], 'o')
ax2.vlines(t[ranco != 0], ymin=0, ymax=ranco[ranco != 0])
