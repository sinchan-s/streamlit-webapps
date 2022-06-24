import streamlit as st
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.datasets import make_moons
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import StandardScaler

# frontend ui section
st.title('Polyomial SVM classifier in action')

st.write("""
#### Checking real-time implementation of SVM classifier on the sklearn generated dataset: `make_moons`.""")
np.meshgrid()
d_name = st.sidebar.selectbox("Select sklearn dataset", ("moons", "circles", "classification"))

x0s = np.linspace(-1.5, 2.5, 100)

# dataset parameters function
def add_params(d_name):
    params = dict()
    if d_name == "moons":
        n_samples = st.sidebar.slider("no. of samples", 2, 100)
        noise = st.sidebar.slider("noise", 0.01, 1.00)
        params["n_samples"] = n_samples
        params["noise"] = noise
    elif d_name == "circles":
        n_samples = st.sidebar.slider("no. of samples", 2, 100)
        noise = st.sidebar.slider("noise", 0.01, 1.00)
        factor = st.sidebar.slider("factor", 0.01, 1.00)
        params["n_samples"] = n_samples
        params["noise"] = noise
        params["factor"] = factor
    else:
        n_samples = st.sidebar.slider("no. of samples", 2, 100)
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

polynomial_svm_clf = Pipeline([
        ("poly_features", PolynomialFeatures(degree=3)),
        ("scaler", StandardScaler()),
        ("svm_clf", LinearSVC(C=10, loss="hinge", random_state=42))
    ])

polynomial_svm_clf.fit(X, y)

# plotting section
fig = plt.figure()
plt.plot(X[:, 0][y==0], X[:, 1][y==0], "ko")
plt.plot(X[:, 0][y==1], X[:, 1][y==1], "rs")
plt.axis([-1.5, 2.5, -1, 1.5])
plt.grid(True, which='both')
plt.xlabel(r"$x_1$", fontsize=20)
plt.ylabel(r"$x_2$", fontsize=20, rotation=0)

# initialization section
x0s = np.linspace(-1.5, 2.5, 100)
x1s = np.linspace(-1.0, 1.5, 100)
x0, x1 = np.meshgrid(x0s, x1s)
X = np.c_[x0.ravel(), x1.ravel()]
y_pred = polynomial_svm_clf.predict(X).reshape(x0.shape)
y_deci = polynomial_svm_clf.decision_function(X).reshape(x0.shape)
plt.contourf(x0, x1, y_pred, cmap=plt.cm.brg, alpha=0.2)
plt.contourf(x0, x1, y_deci, cmap=plt.cm.brg, alpha=0.1)

st.pyplot(fig)