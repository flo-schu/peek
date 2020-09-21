from random import randint
from sklearn.linear_model import LinearRegression


train_set_limit = 1000
train_n = 100

train_input = list()
train_output = list()
for i in range(train_n):
    a = randint(0, train_set_limit)
    b = randint(0, train_set_limit)
    c = randint(0, train_set_limit)
    op = a + (2*b) + (3*c)
    train_input.append([a, b, c])
    train_output.append(op)



predictor = LinearRegression(n_jobs=-1)
predictor.fit(X=train_input, y=train_output)

x_test = [[10, 20, 30]]
outcome = predictor.predict(X=x_test)
coefficients = predictor.coef_

print('Outcome : {}\nCoefficients : {}'.format(outcome, coefficients))