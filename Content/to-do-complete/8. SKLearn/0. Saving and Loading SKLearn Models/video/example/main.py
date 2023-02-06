import joblib
from sklearn.linear_model import LinearRegression
from sklearn.datasets import load_boston

X, y = load_boston(return_X_y=True)
model = LinearRegression()
model.fit(X, y)
print(X[0])

joblib.dump(model, 'mymodel.joblib')  # SAVE THE MODEL
