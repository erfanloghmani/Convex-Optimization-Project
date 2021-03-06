# -*- coding: utf-8 -*-
"""CVX project: Second order methods.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1b7PgpI-ZpczfCyPZtvCnqJHZoaKDjBUR
"""

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
# %matplotlib inline

import jax.numpy as np
import numpy as onp
from jax import grad, jit, vmap
from jax import jacfwd, jacrev
from jax import random
from sklearn.utils import shuffle

key = random.PRNGKey(0)

"""## Generate data"""

X0 = random.normal(key, (100, 2)) - 1
X1 = random.normal(key, (100, 2)) + 1
X = np.vstack([X0, X1])
t = np.vstack([np.zeros([100, 1]), np.ones([100, 1])])

X, t = shuffle(X, t)

X_train, X_test = X[:150], X[150:]
t_train, t_test = t[:150], t[150:]

sns.scatterplot(x=X[:, 0], y=X[:, 1], hue=t[:, 0])

"""## Logistic methods"""

def sigm(x):
    return 1/(1+np.exp(-x))

def NLL(y, t):
    return -np.mean(t*np.log(y) + (1-t)*np.log(1-y))

def loss(W):
    z = X_train @ W
    y = sigm(z)
    return NLL(y, t_train)

"""## Original logistic regression

## Plot loss landscape
"""

def plot_loss_surface(loss_fn=loss, lim=2, ax=None):
  x_line = onp.linspace(-lim, lim, 40)
  y_line = onp.linspace(-lim, lim, 40)

  X_surface, Y_surface = onp.meshgrid(x_line, y_line)

  L_surface = onp.zeros_like(X_surface)
  for i in range(X_surface.shape[0]):
    for j in range(X_surface.shape[1]):
      W = onp.array([[X_surface[i, j]], [Y_surface[i, j]]])
      L_surface[i, j] = float(loss_fn(W))
  g = plt.axes(ax, projection='3d')
  g.plot_surface(X_surface, Y_surface, L_surface, rstride=1, cstride=1,
                  cmap='viridis', edgecolor='none')
  g.set_title('surface')
  return g

plot_loss_surface()
plt.show()

"""### Gradient decent"""

EPOCH_COUNT = 10

def GD(lr=0.2, epochs=EPOCH_COUNT, loss_fn=loss):
  W = np.array([[0.], [0.]])
  loss_list = []
  for it in range(epochs):
    loss_list.append(float(loss_fn(W)))
    W_grad = grad(loss_fn, argnums=0)(W)
    W = W - lr * W_grad
  loss_list.append(float(loss_fn(W)))
  return loss_list

gd_loss_list_1 = GD()

sns.lineplot(x=range(len(gd_loss_list_1)), y=gd_loss_list_1)
plt.show()

"""### Newton method"""

def hessian(f):
    return jacfwd(jacrev(f))

def Newton(epochs=EPOCH_COUNT, loss_fn=loss):
  W = np.array([[0.], [0.]])
  loss_list = []
  for it in range(epochs):
    loss_list.append(float(loss_fn(W)))
    W_grad = grad(loss_fn, argnums=0)(W)
    W_hess = hessian(loss_fn)(W)[:, 0, :, 0]
    W = W - np.linalg.inv(W_hess) @ W_grad
  loss_list.append(float(loss_fn(W)))
  return loss_list

newton_loss_list_1 = Newton()

sns.lineplot(x=range(len(newton_loss_list_1)), y=newton_loss_list_1)
plt.show()

"""### Natural gradient"""

def Likelihood(W):
  z = X_train @ W
  y = sigm(z)
  return np.exp(t_train*np.log(y) + (1 - t_train)*np.log(1 - y))

def Natural(lr=0.2, epochs=EPOCH_COUNT, loss_fn=loss, likelihood_fn=Likelihood):
  W = np.array([[0.], [0.]])

  loss_list = []
  previous_likelihood = None

  for it in range(epochs):
    loss_list.append(float(loss_fn(W)))
    W_grad = grad(loss_fn, argnums=0)(W)
    likelihood = likelihood_fn(W)

    # Plot current and previous likelihood distributions
    if previous_likelihood is not None:
      sns.distplot(previous_likelihood, bins=np.arange(11) / 10)
    sns.distplot(likelihood, bins=np.arange(11) / 10)
    plt.show()
    previous_likelihood = likelihood.copy()

    W_grad_LL = jacfwd(lambda W: np.log(likelihood_fn(W)), argnums=0)(W)[:, 0, :, 0]
    F = np.expand_dims(W_grad_LL, 2) @ np.expand_dims(W_grad_LL, 1)
    F = np.mean(F, axis=0)
    W = W - lr * np.linalg.inv(F) @ W_grad
  loss_list.append(float(loss_fn(W)))
  return loss_list

natural_loss_list_1 = Natural()

sns.lineplot(x=range(len(natural_loss_list_1)), y=natural_loss_list_1)
plt.show()

"""## Altered logistic regression

## Plot loss surface
"""

def loss_2(W):
    z = 0.01 * X_train @ W
    y = sigm(z)
    return NLL(y, t_train)

g = plot_loss_surface()
plot_loss_surface(loss_fn=loss_2, lim=4, ax=g)
plt.show()

"""### Gradient decent"""

gd_loss_list_2 = GD(loss_fn=loss_2)

sns.lineplot(x=range(len(gd_loss_list_2)), y=gd_loss_list_2)
plt.show()

sns.lineplot(x=range(len(gd_loss_list_1)), y=gd_loss_list_1)
sns.lineplot(x=range(len(gd_loss_list_2)), y=gd_loss_list_2)
plt.show()

"""## Newton method"""

newton_loss_list_2 = Newton(loss_fn=loss_2)

sns.lineplot(x=range(len(newton_loss_list_2)), y=newton_loss_list_2)
plt.show()

sns.lineplot(x=range(len(newton_loss_list_1)), y=newton_loss_list_1)
sns.lineplot(x=range(len(newton_loss_list_2)), y=newton_loss_list_2)
plt.show()

"""### Natural gradient"""

def Likelihood_2(W):
  z = 0.01 * X_train @ W
  y = sigm(z)
  return np.exp(t_train*np.log(y) + (1 - t_train)*np.log(1 - y))

natural_loss_list_2 = Natural(loss_fn=loss_2, likelihood_fn=Likelihood_2)

sns.lineplot(x=range(len(natural_loss_list_2)), y=natural_loss_list_2)
plt.show()

sns.lineplot(x=range(len(natural_loss_list_1)), y=natural_loss_list_1)
sns.lineplot(x=range(len(natural_loss_list_2)), y=natural_loss_list_2)
plt.show()

def loss_3(W):
    Q = np.array([[0.5, -0.3], [-0.3, 0.5]])
    z = X_train @ Q @ W
    y = sigm(z)
    return NLL(y, t_train)

g = plot_loss_surface()
plot_loss_surface(loss_fn=loss_3, lim=2, ax=g)
plt.show()

gd_loss_list_3 = GD(loss_fn=loss_3)

sns.lineplot(x=range(len(gd_loss_list_1)), y=gd_loss_list_1)
sns.lineplot(x=range(len(gd_loss_list_2)), y=gd_loss_list_2)
sns.lineplot(x=range(len(gd_loss_list_3)), y=gd_loss_list_3)
plt.show()

newton_loss_list_3 = Newton(loss_fn=loss_3)

sns.lineplot(x=range(len(newton_loss_list_1)), y=newton_loss_list_1)
sns.lineplot(x=range(len(newton_loss_list_2)), y=newton_loss_list_2)
sns.lineplot(x=range(len(newton_loss_list_3)), y=newton_loss_list_3)
plt.show()
