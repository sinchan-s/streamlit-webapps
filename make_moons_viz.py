import streamlit as st
from sklearn import datasets
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_moons
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap

# frontend ui section
st.title('Visualizing make moons dataset')

st.write("""
#### Checking the influence of noise on sample data points on the built-in make moons dataset from scikit-learn
""")

def add_parameters():
    params = dict()
    noise = st.sidebar.slider("noise", 0.01, 1.00)
    n_samples = st.sidebar.slider("no. of samples", 1, 100)
    params["noise"] = noise
    params["n_samples"] = n_samples
    return params

params = add_parameters()

def set_dataset(params):
    X, y = make_moons(n_samples=params["n_samples"], noise=params["noise"], random_state=42)
    return X, y

X, y = set_dataset(params)

# plotting section
fig = plt.figure()
plt.plot(X[:, 0][y==0], X[:, 1][y==0], "bs")
plt.plot(X[:, 0][y==1], X[:, 1][y==1], "g^")
plt.axis([-1.5, 2.5, -1, 1.5])
plt.grid(True, which='both')
plt.xlabel(r"$x_1$", fontsize=20)
plt.ylabel(r"$x_2$", fontsize=20, rotation=0)

st.pyplot(fig)