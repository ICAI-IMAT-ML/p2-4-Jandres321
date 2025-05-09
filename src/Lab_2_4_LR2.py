import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import seaborn as sns


class LinearRegressor:
    """
    Extended Linear Regression model with support for categorical variables and gradient descent fitting.
    """

    def __init__(self):
        self.coefficients = None
        self.intercept = None

    """
    This next "fit" function is a general function that either calls the *fit_multiple* code that
    you wrote last week, or calls a new method, called *fit_gradient_descent*, not implemented (yet)
    """

    def fit(self, X, y, method="least_squares", learning_rate=0.01, iterations=1000):
        """
        Fit the model using either normal equation or gradient descent.

        Args:
            X (np.ndarray): Independent variable data (2D array).
            y (np.ndarray): Dependent variable data (1D array).
            method (str): method to train linear regression coefficients.
                        It may be "least_squares" or "gradient_descent".
            learning_rate (float): Learning rate for gradient descent.
            iterations (int): Number of iterations for gradient descent.

        Returns:
            None: Modifies the model's coefficients and intercept in-place.
        """
        if method not in ["least_squares", "gradient_descent"]:
            raise ValueError(
                f"Method {method} not available for training linear regression."
            )
        if np.ndim(X) == 1:
            X = X.reshape(-1, 1)

        if method == "least_squares":
            self.fit_multiple(X, y)
        elif method == "gradient_descent":
            self.fit_gradient_descent(X, y, learning_rate, iterations)

    def fit_multiple(self, X, y):
        """
        Fit the model using multiple linear regression (more than one independent variable).

        This method applies the matrix approach to calculate the coefficients for
        multiple linear regression.

        Args:
            X (np.ndarray): Independent variable data (2D array).
            y (np.ndarray): Dependent variable data (1D array).

        Returns:
            None: Modifies the model's coefficients and intercept in-place.
        """
        # Add a column of ones to X to account for the intercept
        X_b = np.c_[np.ones((X.shape[0], 1)), X]

        # Calculate the best fit line using the normal equation
        theta_best = np.linalg.pinv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)

        self.intercept = theta_best[0]
        self.coefficients = theta_best[1:]

    def fit_gradient_descent(self, X, y, learning_rate=0.01, iterations=1000):
        """
        Fit the model using gradient descent.

        Args:
            X (np.ndarray): Independent variable data (2D array), with bias.
            y (np.ndarray): Dependent variable data (1D array).
            learning_rate (float): Learning rate for gradient descent.
            iterations (int): Number of iterations for gradient descent.

        Returns:
            None: Modifies the model's coefficients and intercept in-place.
        """

        # Initialize the parameters to very small values (close to 0)
        m, n = X.shape
        self.coefficients = np.random.rand(n) * 0.01  # Small random numbers
        self.intercept = np.random.rand() * 0.01

        # Store the history of coefficients and intercept
        history = {"intercept": [], "coefficients": []}

        # Implement gradient descent
        for epoch in range(iterations):
            predictions = self.predict(X)
            error = predictions - y

            gradient_coefficients = (2 * learning_rate / m) * X.T.dot(error)
            gradient_intercept = (2 * learning_rate / m) * np.sum(error)

            self.intercept -= gradient_intercept
            self.coefficients -= gradient_coefficients

            # Store the current state of the parameters
            history["intercept"].append(self.intercept)
            history["coefficients"].append(self.coefficients.copy())

            # Calculate and print the loss every 10 epochs
            if epoch % 10 == 0:
                mse = np.mean(error**2)
                print(f"Epoch {epoch}: MSE = {mse}")
                if epoch == 0:
                    training_history = {"epoch": [], "mse": []}
                training_history["epoch"].append(epoch)
                training_history["mse"].append(mse)


        # Plot training history
        plt.figure(figsize=(10, 6))
        plt.plot(training_history["epoch"], training_history["mse"], label="MSE", color='purple')
        plt.xlabel("Epoch")
        plt.ylabel("Mean Squared Error")
        plt.title("Training History")
        plt.legend()
        plt.show()

        # Plot the parameter updates with better separation
        num_coefficients = len(history["coefficients"][0])

        # Plot intercept updates
        plt.figure(figsize=(10, 6))
        plt.plot(history["intercept"], label="Intercept", color='blue')
        plt.xlabel("Iteration")
        plt.ylabel("Value")
        plt.title("Intercept Updates")
        plt.legend()

        # Plot each coefficient in separate plots
        colors = plt.cm.viridis(np.linspace(0, 1, num_coefficients))
        for i in range(num_coefficients):
            plt.figure(figsize=(10, 6))
            plt.plot([coef[i] for coef in history["coefficients"]], label=f"Coefficient {i+1}", color=colors[i])
            plt.xlabel("Iteration")
            plt.ylabel("Value")
            plt.title(f"Coefficient {i+1} Updates")
            plt.legend()
            plt.show()

    def predict(self, X):
        """
        Predict the dependent variable values using the fitted model.

        Args:
            X (np.ndarray): Independent variable data (1D or 2D array).

        Returns:
            np.ndarray: Predicted values of the dependent variable.

        Raises:
            ValueError: If the model is not yet fitted.
        """
        if self.coefficients is None or self.intercept is None:
            raise ValueError("Model is not yet fitted")

        if np.ndim(X) == 1:
            # Predict when X is only one variable
            predictions = self.intercept + self.coefficients[0] * X
        else:
            # Predict when X is more than one variable
            X_b = np.c_[np.ones((X.shape[0], 1)), X]
            predictions = X_b.dot(np.r_[self.intercept, self.coefficients])

        return predictions


def evaluate_regression(y_true, y_pred):
    """
    Evaluates the performance of a regression model by calculating R^2, RMSE, and MAE.

    Args:
        y_true (np.ndarray): True values of the dependent variable.
        y_pred (np.ndarray): Predicted values by the regression model.

    Returns:
        dict: A dictionary containing the R^2, RMSE, and MAE values.
    """

    # R^2 Score
    ss_res = np.sum((y_true - y_pred) * (y_true - y_pred))
    ss_tot = np.sum((y_true - np.mean(y_true)) * (y_true - np.mean(y_true)))
    r_squared = 1 - (ss_res / ss_tot)

    # Root Mean Squared Error
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))

    # Mean Absolute Error
    mae = np.mean(np.abs(y_true - y_pred))

    return {"R2": r_squared, "RMSE": rmse, "MAE": mae}


def one_hot_encode(X, categorical_indices, drop_first=False):
    """
    One-hot encode the categorical columns specified in categorical_indices. This function
    shall support string variables.

    Args:
        X (np.ndarray): 2D data array.
        categorical_indices (list of int): Indices of columns to be one-hot encoded.
        drop_first (bool): Whether to drop the first level of one-hot encoding to avoid multicollinearity.

    Returns:
        np.ndarray: Transformed array with one-hot encoded columns.
    """
    X_transformed = []
    for i in range(X.shape[1]):
        if i in categorical_indices:
            # Get unique categories
            categories = np.unique(X[:, i])
            if drop_first:
                categories = categories[
                    1:
                ]  # Drop the first category to avoid multicollinearity
            # Create one-hot encoded columns
            for category in categories:
                one_hot_column = (X[:, i] == category).astype(float)
                X_transformed.append(one_hot_column)
        else:
            X_transformed.append(X[:, i].astype(float))

    return np.column_stack(X_transformed)
