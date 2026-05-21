import pickle
import numpy as np
from sklearn.preprocessing import PolynomialFeatures

poly = PolynomialFeatures(degree=1, include_bias=False)
poly.fit(np.zeros((1, 90)))

with open('poly.pkl', 'wb') as f:
    pickle.dump(poly, f)

print("poly.pkl saved with include_bias=False!")