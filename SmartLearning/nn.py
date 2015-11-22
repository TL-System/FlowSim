import numpy as np

class NeuralNetwork(object):
    def __init__(self, parameters, learning_rate):
        #Expect parameters to be a tuple of the form:
        #    ((n_input,0,0), (n_hidden_layer_1, f_1, f_1'), ...,
        #     (n_hidden_layer_k, f_k, f_k'), (n_output, f_o, f_o'))
        self.n_layers = len(parameters)
        #Counts number of neurons without bias neurons in each layer.
        self.sizes = [layer[0] for layer in parameters]
        #Activation functions for each layer.
        self.fs =[layer[1] for layer in parameters]
        #Derivatives of activation functions for each layer.
        self.fprimes = [layer[2] for layer in parameters]
        #Learning rate of backpropagation algorithm.
        self.learning_rate = learning_rate
        self.build_network()
 
    def build_network(self):
        #List of weight matrices taking the output of one layer to the input of the next.
        self.weights = []
        #Bias vector for each layer.
        self.biases = []
        #Input vector for each layer.
        self.inputs = []
        #Output vector for each layer.
        self.outputs = []
        #Vector of errors at each layer.
        self.errors = []
        #We initialise the weights randomly, and fill the other vectors with 1s.
        for layer in range(self.n_layers - 1):
            n = self.sizes[layer]
            m = self.sizes[layer + 1]
            self.weights.append(np.random.normal(0, 1, (m, n))/50.0)
            self.biases.append(np.random.normal(0, 1, (m, 1))/50.0)
            self.inputs.append(np.zeros((n, 1)))
            self.outputs.append(np.zeros((n, 1)))
            self.errors.append(np.zeros((n, 1)))
        #There are only n-1 weight matrices, so we do the last case separately.
        n = self.sizes[-1]
        self.inputs.append(np.zeros((n, 1)))
        self.outputs.append(np.zeros((n, 1)))
        self.errors.append(np.zeros((n, 1)))
 
    def feedforward(self, x):
        #Propagates the input from the input layer to the output layer.
        k = len(x)
        x.shape = (k, 1)
        self.inputs[0] = x
        self.outputs[0] = x
        for i in range(1, self.n_layers):
            self.inputs[i] = self.weights[i-1].dot(self.outputs[i-1]) + self.biases[i-1]
            self.outputs[i] = self.fs[i](self.inputs[i])
        return self.outputs[-1]
 
    def update_weights(self, x, y):
        #Update the weight matrices for each layer based on a single input x and target y.
        output = self.feedforward(x)
        self.errors[-1] = self.fprimes[-1](self.outputs[-1])*(output-y)
        n = self.n_layers-2
        for i in xrange(n, 0, -1):
            self.errors[i] = self.fprimes[i](self.inputs[i])*self.weights[i].T.dot(self.errors[i+1])
            self.weights[i] = self.weights[i] - self.learning_rate*np.outer(self.errors[i+1],self.outputs[i])
            self.biases[i] = self.biases[i] - self.learning_rate*self.errors[i+1]
        self.weights[0] = self.weights[0] - self.learning_rate*np.outer(self.errors[1],self.outputs[0])
        self.biases[0] = self.biases[0] - self.learning_rate*self.errors[1]