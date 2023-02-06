
import joblib
model = joblib.load('mymodel.joblib')

example_input = [[6.320e-03, 1.800e+01, 2.310e+00, 0.000e+00, 5.380e-01, 6.575e+00, 6.520e+01,
                 4.090e+00, 1.000e+00, 2.960e+02, 1.530e+01, 3.969e+02, 4.980e+00]]
prediction = model.predict(example_input)

print('prediction:', prediction)
