import streamlit as st
from sklearn import datasets
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_moons, make_circles, make_classification
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap

# frontend ui section
st.title('Visualizing make moons dataset')

st.write("""
### Checking the influence of noise on sample data points on the built-in make moons dataset from scikit-learn.
Make moons is an scikit-learns's generated dataset which creates two interleaving half circles.
Used to visualize clustering and classification algorithms.
""")

d_name = st.sidebar.selectbox("Select sklearn dataset", ("moons", "circles", "classification"))

# dataset parameters function
def add_params(d_name):
    params = dict()
    if d_name == "moons":
        noise = st.sidebar.slider("noise", 0.01, 1.00)
        n_samples = st.sidebar.slider("no. of samples", 1, 100)
        params["noise"] = noise
        params["n_samples"] = n_samples
    elif d_name == "circles":
        noise = st.sidebar.slider("noise", 0.01, 1.00)
        n_samples = st.sidebar.slider("no. of samples", 1, 100)
        factor = st.sidebar.slider("factor", 0.01, 1.00)
        params["noise"] = noise
        params["n_samples"] = n_samples
        params["factor"] = factor
    else:
        n_samples = st.sidebar.slider("no. of samples", 1, 100)
        n_features = st.sidebar.slider("no. of features", 2, 100)
        n_informative = st.sidebar.slider("no. of informative features", 2, 100)
        params["n_samples"] = n_samples
        params["n_features"] = n_features
        params["n_informative"] = n_informative
    return params

params = add_params(d_name)

def set_dataset(d_name, params):
    if d_name == "moons":
        X, y = make_moons(n_samples=params["n_samples"], noise=params["noise"], random_state=42)
    elif d_name == "circles":
        X, y = make_circles(n_samples=params["n_samples"], noise=params["noise"], random_state=42, factor=params["factor"])
    else:
        X, y = make_classification(n_samples=params["n_samples"], n_features=params["n_features"], n_informative=params["n_informative"], random_state=42, n_redundant=0)
    return X, y


X, y = set_dataset(d_name, params)

# plotting section
fig = plt.figure()
plt.plot(X[:, 0][y==0], X[:, 1][y==0], "bs")
plt.plot(X[:, 0][y==1], X[:, 1][y==1], "g^")
#plt.axis([-1.5, 2.5, -1, 1.5])
plt.grid(True, which='both')
plt.xlabel(r"$x_1$", fontsize=20)
plt.ylabel(r"$x_2$", fontsize=20, rotation=0)

st.pyplot(fig)