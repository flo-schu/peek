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



# replicated vs continuous

## replicated
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import itertools as it
from scipy.stats import norm, expon, binom

n = np.tile(np.repeat([10,10,10,7,3],[10,10,10,7,3]),2)
temp = np.repeat([20, 24], 40)
pest = np.tile(np.repeat([0.001, 0.01, 0.1,1,10],[10,10,10,7,3]),2)
ph = norm.rvs(7,1,80)
popd = norm.rvs(50,20,80)
# food = expon.rvs(0,.1,80)
rnoise = norm.rvs(0,10,80)

collapse = 0.2 * temp*pest + 0.1 * temp + 0.4 * pest + 0.05 * -ph + 0.1*popd + rnoise + 10
collapse = np.where(collapse < 0 , 0, collapse)

def loglog(x, a, b):
    return 1 / ( 1 + (x / a) ** -b)

cprob=loglog(collapse, 30, 3)
b = binom(1, p=cprob)
cosig = b.rvs() 

# TODO: perhaps, I need to implement a non probabilistic production
#       of the collapsed status (e.g. using a threshold value, beyond nanocosms collapse)                        
#       This threshold could of course vary slightly accross the nanocosms.

df = pd.DataFrame()
df['n'] = n
df['temp'] = temp
df['pest'] = pest
df['ph'] = ph
df['popd'] = popd
df['p'] = cprob
df['collapsed'] = cosig


dfs = df.groupby(['temp','pest'])['collapsed'].mean()

fig, (ax1, ax2) = plt.subplots(2,1)

ax1.plot(dfs[24], label=24)
ax1.plot(dfs[20], label=20)
ax1.set_xscale('log')
ax1.legend()

ax2.plot(dfs[:,10  ], label=10)
ax2.plot(dfs[:,1   ], label=1)
ax2.plot(dfs[:,.1  ], label=0.1)
ax2.plot(dfs[:,.01 ], label=0.01)
ax2.plot(dfs[:,.001], label= 0.001)
ax2.set_xlim(19,25)
ax2.legend()

plt.show()


from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

x = np.array((pest,temp)).T
model = LogisticRegression(solver='liblinear', random_state=0)
model.fit(x, cosig)
model.predict_proba(x)
model.predict(x)

model.score(x,cosig)
confusion_matrix(cosig, model.predict(x))
print(classification_report(cosig, model.predict(x)))

# non-linear logistic regression
# this is what I need to extract the correct coefficients from the model.
# A linear approach will clearly not be sufficient.
# https://towardsdatascience.com/logistic-regression-as-a-nonlinear-classifier-bdc6746db734

# assumptions of logistic regression - these should be met: 
# + independence
# + follow identical probability distribution.

# non-linear

import numpy as np
import pandas as pd
from scipy import optimize
from scipy.stats import norm, binom
import matplotlib.pyplot as plt
import itertools as it
from sklearn.preprocessing import StandardScaler, RobustScaler


def logistic(x):
    return 1 / ( 1 + np.exp( -x ) )

def loglog(x, a, b):
    return 1 / ( 1 + (x / a) ** -b)

scaler = RobustScaler()
temp = [0,5]
pest = [0.001, 0.01, 0.1,1,10]
r = 1
n = [10*r,10*r,10*r,7*r,3*r]*len(temp)

X = []
for i, ni in zip(it.product(temp, pest),n):
    d = np.tile(np.array(i), ni)
    X.append(d.reshape(int(len(d)/2),2))

X = np.concatenate(X)

N = len(X)
ph = norm.rvs(7,0,N)
popd = norm.rvs(50,0,N)
rnoise = norm.rvs(0,0,N)
X = np.column_stack((X,ph,popd,rnoise))

collapse = (6. * X[:,0]*X[:,1] +         # interaction temp, pest
            .0* X[:,0] + 3 * X[:,1] +     # temp + pest
            0.00 * X[:,2] + 0.00*X[:,3]  # ph + popdensity
            + X[:,4] + 10)               # random noise + intercept

collapse = np.where(collapse < 0 , 0, collapse)

# collapse_scaled=scaler.fit_transform(collapse.reshape((N,1)))
# cprob = logistic(collapse_scaled)
cprob=loglog(collapse, 6, 1.5)
b = binom(1, p=cprob)
y = b.rvs() 
X = np.column_stack((X, cprob, y))

def f(x, predictors):
    """
    function which links predictor variables to a probability value between 
    0 and 1
    """
    collapse = (x[0] * predictors[:, 0] * predictors[:, 1] + 
                x[1] * predictors[:, 0] + 
                x[2] * predictors[:, 1] + x[3] )
    collapse = loglog(collapse, x[4], x[5])
    return collapse

def ll_f(x, predictors, y):
    """
    this function evaluates the log likelihood of a non linear function f
    linked with log-odds ratio.
    A more generic form can be imagined by plugging in other link functions and
    using different probability disitrbutions than the bernoulli

    y: binary signal [0,1] from real data
    X: vector of predictor variables
    x: coefficients which are fit to f
    """
    p = f(x, predictors) # evaluate non-linear function
    # ll = np.dot(y, p) - np.sum (np.log(1.0 + np.exp(p)))
    ll = np.sum( y * np.log(p) + (1-y) * np.log( 1 - p) )
    return -ll

# x0 = np.array([.01, .01, .01])
x0 = np.array([1,1,1,1,4,2])
# predictors = scaler.fit_transform(X[:, 0:2])
predictors = X[:, 0:2]
y = X[:,6]
testp = f(x0, predictors)
ll_f(x0,predictors,y)


bnds=optimize.Bounds(lb=[0,0,0,0,1e-5,1e-5], ub=[100,100,100,100,100,100])
root = optimize.minimize(ll_f, x0, args=(predictors, y), bounds=bnds)

# the outcome of the model (linked by logit) is the log odds ratio
# i.e. the odds of collpase 
print(root)
print(np.round(root['x'],2))

# compute probabilites of collapse after recovery from optimizer :) works like a charm
pred_p = np.round(1/(1+np.exp(-f(root['x'], predictors))),2)
pred_p = f(root['x'], predictors)
X = np.column_stack((X,pred_p))


df = pd.DataFrame(X, columns=['temp','pest','pH','popdens','rnoise','p','collapse','pred_p'])
dfs = df.groupby(['temp','pest'])['collapse'].mean()


dfp = df.groupby(['temp','pest'])['p'].mean()
dfpp = df.groupby(['temp','pest'])['pred_p'].mean()

X20 = np.concatenate(np.split(X, np.where(X[:,0] == 0)[0][1:]))
X25 = np.concatenate(np.split(X, np.where(X[:,0] == 5)[0][1:]))

fig, (ax1, ax2) = plt.subplots(2,1)

ax1.plot(X20[:,1], X20[:,6], 'o', label='+0°C', alpha=.2)
ax1.plot(X25[:,1], X20[:,6], 'o', label='+5°C', alpha=.2)
ax1.plot(dfs[temp[1]], linestyle="solid" , color="orange", alpha=.5)
ax1.plot(dfs[temp[0]], linestyle="solid", color ="blue", alpha=.5)
ax1.plot(dfp[temp[1]], linestyle="dashed" , color="orange")
ax1.plot(dfp[temp[0]], linestyle="dashed", color ="blue")
ax1.plot(dfpp[temp[1]], linestyle="dotted" , color="orange")
ax1.plot(dfpp[temp[0]], linestyle="dotted", color ="blue")
ax1.set_xscale('log')
ax1.legend()

ax2.plot(dfs[:,10  ], label=10)
ax2.plot(dfs[:,1   ], label=1)
ax2.plot(dfs[:,.1  ], label=0.1)
ax2.plot(dfs[:,.01 ], label=0.01)
ax2.plot(dfs[:,.001], label= 0.001)
ax2.set_xlim(temp[0]-1,temp[1]+1)
ax2.legend()

plt.show()

# # recovery from data works - but until now it's linear

# # getting the logistic is the inverse of log-odds
# print(f(root['x'], predictors))

# # exponetiating the results give us a proportional increase of ... of collapsing by 
# # incrementing the variable by one unit.
# np.round(np.exp(root['x']),2)


