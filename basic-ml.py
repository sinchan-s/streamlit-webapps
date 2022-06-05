import streamlit as st
from sklearn import datasets
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.decomposition import PCA
from matplotlib import pyplot as plt

# frontend ui section
st.title('Basic ML Visualizer')

st.write("""
## Exploring different classifiers
""")

d_name = st.sidebar.selectbox("Select dataset", ("iris", "breast cancer", "wine"))
c_name = st.sidebar.selectbox("Select classifer", ("KNN", "SVM", "RF"))

# classifier building section
def get_dataset(d_name):
    if d_name == "iris":
        data = datasets.load_iris()
    elif d_name == "breast cancer":
        data = datasets.load_breast_cancer()
    else:
        data = datasets.load_wine()
    X = data.data
    y = data.target
    return X,y

X,y = get_dataset(d_name)
st.write("dataset shape: ", X.shape)
st.write("no. of classes: ", len(np.unique(y)))

def add_parameters_ui(c_name):
    params = dict()
    if c_name == "KNN":
        K = st.sidebar.slider("K", 1, 15)
        params["K"] = K
    elif c_name == "SVM":
        C = st.sidebar.slider("C", 0.01, 10.0)
        params["C"] = C
    else:
        max_depth = st.sidebar.slider("max_depth", 2, 15)
        n_estimators = st.sidebar.slider("n_estimators", 1, 100)
        params["max_depth"] = max_depth
        params["n_estimators"] = n_estimators
    return params

params = add_parameters_ui(c_name)

def get_classifier(c_name, params):
    if c_name == "KNN":
        clf = KNeighborsClassifier(n_neighbors=params["K"])
    elif c_name == "SVM":
        clf = SVC(C=params["C"])
    else:
        clf = RandomForestClassifier(n_estimators=params["n_estimators"], max_depth=params["max_depth"], random_state=42)
    return clf

clf = get_classifier(c_name, params)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

acc = accuracy_score(y_test, y_pred)
st.write(f"Classifier = {c_name}")
st.write(f"Accuracy = {acc}")

# adding 2 PCA components
pca = PCA(2)
X_projected = pca.fit_transform(X)

x1 = X_projected[:, 0]
x2 = X_projected[:, 1]

# plotting section
fig = plt.figure()
plt.scatter(x1, x2, c=y, alpha=0.7, cmap="viridis")
plt.xlabel("Principle component 1")
plt.ylabel("Principle component 2")
plt.colorbar()

st.pyplot(fig)