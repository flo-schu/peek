
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
temp = np.linspace(1,5,8)
pest = np.logspace(-1,1,num=10)
r = 1
n = [1]*80

X = []
for i, ni in zip(it.product(temp, pest),n):
    d = np.tile(np.array(i), ni)
    X.append(d.reshape(int(len(d)/2),2))

X = np.concatenate(X)

N = len(X)
ph = norm.rvs(7,0,N)
popd = norm.rvs(50,10,N)
rnoise = norm.rvs(0,5,N)
X = np.column_stack((X,ph,popd,rnoise))

collapse = (8 * X[:,0]*X[:,1] +         # interaction temp, pest
            .2* X[:,0] + 3 * X[:,1] +     # temp + pest
            0.00 * X[:,2] + .05*X[:,3]  # ph + popdensity
            + X[:,4] + 10)               # random noise + intercept

collapse = np.where(collapse < 0 , 0, collapse)

# collapse_scaled=scaler.fit_transform(collapse.reshape((N,1)))
# cprob = logistic(collapse_scaled)
cprob=loglog(collapse, 30, 5)
np.random.seed()
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
x0 = np.array([.1,.1,.1,.1,3,2])
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

print( 'everythin scales with', root['x'][4])

#TODO: I can extract the paramters after scrambling them. The paramters from the linear combination
#      scale well with the 'a' parameter of the loglogistic function. Parameter b has probably some+
#      logarithmic or exponential relation to the paramter. Find that out!! 
#      Hence, if I rescale the paramters with 'a', I should end up with the paramters from
#      my input. This is good in so far, that I don't have to know starting values in advance. 
#      Now I can proceed with non-replicated designs and see which works better-
#      scaling may work with np.log(b)*a


# compute probabilites of collapse after recovery from optimizer :) works like a charm
pred_p = np.round(1/(1+np.exp(-f(root['x'], predictors))),2)
pred_p = f(root['x'], predictors)
X = np.column_stack((X,pred_p))


df = pd.DataFrame(X, columns=['temp','pest','pH','popdens','rnoise','p','collapse','pred_p'])
dfs = df.groupby(['temp','pest'])['collapse'].mean()


dfp = df.groupby(['temp','pest'])['p'].mean()
dfpp = df.groupby(['temp','pest'])['pred_p'].mean()
dfpp
fig, (ax1, ax2) = plt.subplots(2,1)

# ax1.plot(X20[:,1], X20[:,6], 'o', label='+0°C', alpha=.2)
# ax1.plot(X25[:,1], X20[:,6], 'o', label='+5°C', alpha=.2)
# ax1.plot(dfs[temp[1]], linestyle="solid" , color="orange", alpha=.5)
# ax1.plot(dfs[temp[0]], linestyle="solid", color ="blue", alpha=.5)
ax1.plot( dfp[temp[0]], linestyle="dashed", color ="blue", label=np.round(temp[0],1)  )
ax1.plot(dfpp[temp[0]], linestyle="dotted", color ="blue"   )
ax1.plot( dfp[temp[3]], linestyle="dashed", color ="green", label=np.round(temp[3],1) )
ax1.plot(dfpp[temp[3]], linestyle="dotted", color ="green"  )
ax1.plot( dfp[temp[5]], linestyle="dashed", color ="red",   label=np.round(temp[5],1) )
ax1.plot(dfpp[temp[5]], linestyle="dotted", color ="red"    )
ax1.plot( dfp[temp[7]], linestyle="dashed" , color="orange", label=np.round(temp[7],1))
ax1.plot(dfpp[temp[7]], linestyle="dotted" , color="orange" )
ax1.set_xscale('log')
ax1.legend()
ax1.set_xlabel('pesticides')
ax1.set_ylabel("collapse")

ax2.plot( dfp[:,pest[0]], linestyle="dashed", color ="blue",label=np.round(pest[0],1))
ax2.plot(dfpp[:,pest[0]], linestyle="dotted", color ="blue")
ax2.plot( dfp[:,pest[3]], linestyle="dashed", color ="green",label=np.round(pest[3],1))
ax2.plot(dfpp[:,pest[3]], linestyle="dotted", color ="green")
ax2.plot( dfp[:,pest[6]], linestyle="dashed", color ="red",label=np.round(pest[6],1))
ax2.plot(dfpp[:,pest[6]], linestyle="dotted", color ="red")
ax2.plot( dfp[:,pest[9]], linestyle="dashed" , color="orange",label=np.round(pest[9],1))
ax2.plot(dfpp[:,pest[9]], linestyle="dotted" , color="orange")
ax2.legend()
ax2.set_xlabel('temperature rise')
ax2.set_ylabel("collapse")

plt.show()

# # recovery from data works - but until now it's linear

# # getting the logistic is the inverse of log-odds
print(f(root['x'], predictors))

# # exponetiating the results give us a proportional increase of ... of collapsing by 
# # incrementing the variable by one unit.
# np.round(np.exp(root['x']),2)


