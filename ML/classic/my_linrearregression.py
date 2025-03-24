import numpy as np


class MyLinearRegression:
    def __init__(self, reg_coefficient = 0.0) -> None:
        self.lambda_ = reg_coefficient
        self.weights = None


    def fit(self, X_train: np.array, y_train: np.array) -> None:
        X_train = np.hstack((np.ones((X_train.shape[0], 1)), X_train))
        n_features = X_train.shape[1]
        I = np.eye(n_features)
        XT_X_inv = np.linalg.inv(X_train.T @ X_train + self.lambda_ * I)
        self.weights = XT_X_inv @ X_train.T @ y_train


    def predict(self, X_test: np.array) -> np.array:
        X_test = np.hstack((np.ones((X_test.shape[0], 1)), X_test))
        pred = X_test @ self.weights
        return pred
