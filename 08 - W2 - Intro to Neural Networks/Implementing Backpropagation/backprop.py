import numpy as np
from data_prep import features, targets, features_test, targets_test

np.random.seed(42)

def sigmoid(x):
    """
    Calculate sigmoid
    """
    return 1 / (1 + np.exp(-x))


# Hyperparameters
n_hidden = 3  # number of hidden units
epochs = 500
learnrate = 0.05

n_records, n_features = features.shape
last_loss = None
# Initialize weights
weights_input_hidden = np.random.normal(scale=1 / n_features ** .5,
                                        size=(n_features, n_hidden))
weights_hidden_output = np.random.normal(scale=1 / n_features ** .5,
                                         size=n_hidden)

for e in range(epochs):
    del_w_input_hidden = np.zeros(weights_input_hidden.shape)
    del_w_hidden_output = np.zeros(weights_hidden_output.shape)
    for x, y in zip(features.values, targets):
        ## Forward pass ##
        # TODO: Calculate the output
        hidden_input = x
        hidden_activations = np.dot(hidden_input, weights_input_hidden)
        hidden_layer_output = sigmoid(hidden_activations)
        output_layer_in = np.dot(hidden_layer_output, weights_hidden_output)
        output = sigmoid(output_layer_in)

        ## Backward pass ##
        # TODO: Calculate the error
        error = y - output

        # TODO: Calculate error gradient in output unit
        sigmoid_prime = output * ( 1 - output )
        output_error = error * sigmoid_prime

        # TODO: propagate errors to hidden layer
        hidden_error = weights_hidden_output * output_error * hidden_layer_output * ( 1 - hidden_layer_output )

        # TODO: Update the change in weights
        del_w_hidden_output += learnrate * output_error * hidden_layer_output
        del_w_input_hidden += learnrate * hidden_error * hidden_input[:,None]

    # TODO: Update weights
    weights_input_hidden  += del_w_input_hidden
    weights_hidden_output += del_w_hidden_output

    # Printing out the mean square error on the training set
    if e % (epochs / 10) == 0:
        hidden_activations = sigmoid(np.dot(x, weights_input_hidden))
        out = sigmoid(np.dot(hidden_activations,
                             weights_hidden_output))
        loss = np.mean((out - targets) ** 2)

        if last_loss and last_loss < loss:
            print("Train loss: ", loss, "  WARNING - Loss Increasing")
        else:
            print("Train loss: ", loss)
        last_loss = loss

# Calculate accuracy on test data
hidden = sigmoid(np.dot(features_test, weights_input_hidden))
out = sigmoid(np.dot(hidden, weights_hidden_output))
predictions = out > 0.5
accuracy = np.mean(predictions == targets_test)
print("Prediction accuracy: {:.3f}".format(accuracy))
