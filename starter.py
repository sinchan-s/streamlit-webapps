import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="starter test file",
    page_icon="B",
    initial_sidebar_state="expanded",
)

st.title('Matplotlib random graph with `numpy.random.randn()`')

n = st.sidebar.slider("Random points", 1, 10000)

x = np.random.randn(n)
y = np.random.randn(n)

fig = plt.figure()
plt.plot(x, y, "cx")

st.pyplot(fig)
