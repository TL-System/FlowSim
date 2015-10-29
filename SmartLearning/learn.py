import random
import nn
import numpy as np

class Learn:
    def __init__(self, number_actions, number_sources, number_destinations, number_state_features, number_hidden_nodes_per_layer, activation_function_type, exploration_type, epsilon, alpha, gamma, beta, learning_rate):
        np.seterr(all='raise')
        activation_functions = {0: logistic, 1: tanh, 2: softplus, 3: rectified_linear, 4: identity}
        activation_function_primes = {0: logistic_prime, 1: tanh_prime, 2: softplus_prime, 3: rectified_linear_prime, 4: identity_prime}
        hidden_info = ()
        for i in range(0, len(number_hidden_nodes_per_layer)):
            hidden_info = hidden_info + ((number_hidden_nodes_per_layer[i], activation_functions[activation_function_type], activation_function_primes[activation_function_type]),)
        param = ((number_state_features + number_sources + number_destinations + number_actions, 0, 0),) + hidden_info + ((1, identity, identity_prime),)

        self.NN = nn.NeuralNetwork(param, learning_rate)
        self.rho = random.gauss(0, 1)
        self.exploration_type = exploration_type
        if exploration_type == 0:
            self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.number_actions = number_actions
        self.number_sources = number_sources
        self.number_destinations = number_destinations
        self.beta = beta
        self.K = 1

    def get_NN_Value(self, state, source, destination, action):
        x = np.array(state + source + destination + action)
        return self.NN.feedforward(x)

    def learn_NN(self, state, source, destination, action, new_value):
        x = np.array(state + source + destination + action)
        old_value = self.get_NN_Value(state, source, destination, action)
        target = old_value + self.alpha * (new_value - old_value)
        self.NN.update_weights(x, target)

    def choose_action(self, state, source, destination):
        if self.exploration_type == 1:
            if self.K < 1000000:
                #self.epsilon = -(0.95/99999)*self.K + 999.95/99999
                self.epsilon = -(1.0/1111110)*self.K + 1111111/1111110.0
                self.K += 1
            else:
                self.epsilon = 0.10
        if state == [] or random.random() < self.epsilon:
            action = random.choice(range(self.number_actions))
            self.action = action
        else:
            source_list = [0 for i in range(0, self.number_sources)]
            source_list[source] = 1
            destination_list = [0 for i in range(0, self.number_destinations)]
            destination_list[destination] = 1
            l = [0 for i in range(1, self.number_actions)]
            l = [1] + l
            possible_actions = [l[-i:] + l[:-i] for i in range(self.number_actions)]
            q = [self.get_NN_Value(state, source_list, destination_list, a) for a in possible_actions]
            maxQ = max(q)
            count = q.count(maxQ)
            if count > 1:
                best = [i for i in range(self.number_actions) if q[i] == maxQ]
                i = random.choice(best)
            else:
                i = q.index(maxQ)

            action = i
        #return [0 for i in range(action)] + [1] + [0 for i in range(action + 1, self.number_actions)]
        return action

    def Q_learn(self, state1, source, destination, action1, reward, state2):
        source_list = [0 for i in range(0, self.number_sources)]
        source_list[source] = 1
        destination_list = [0 for i in range(0, self.number_destinations)]
        destination_list[destination] = 1
        l = [0 for i in range(1, self.number_actions)]
        l = [1] + l
        possible_actions = [l[i:] + l[:i] for i in range(self.number_actions)]
        maxqnew = max([self.get_NN_Value(state2, source_list, destination_list, a) for a in possible_actions])
        self.learn_NN(state1, source_list, destination_list, action1, reward + self.gamma*maxqnew)

    def R_learn(self, state1, source, destination, action1, reward, state2):
        source_list = [0 for i in range(0, self.number_sources)]
        source_list[source] = 1
        destination_list = [0 for i in range(0, self.number_destinations)]
        destination_list[destination] = 1
        l = [0 for i in range(1, self.number_actions)]
        l = [1] + l
        update_rho = False
        possible_actions = [l[-i:] + l[:-i] for i in range(self.number_actions)]
        maxqprevious = max([self.get_NN_Value(state1, source_list, destination_list, a) for a in possible_actions])
        maxqnew = max([self.get_NN_Value(state2, a) for a in possible_actions])
        if abs(self.get_NN_Value(state1, source_list, destination_list, action1) - maxqprevious) < 0.000000000000001:
            update_rho = True
        self.learn_NN(state1, source_list, destination_list, action1, reward - self.rho + maxqnew)
        if update_rho:
            self.rho += self.beta * (reward - self.rho + maxqnew - maxqprevious)

def logistic(x):
    try:
        ex = 1.0/(1 + np.exp(-x))
    except Exception,e:
        print e
        print x
    return ex

def logistic_prime(x):
    try:
        ex = 1.0/(1 + np.exp(-x))
    except:
        print x
        print ex
    return ex * (1 - ex)

def identity(x):
    return x

def identity_prime(x):
    return 1

def softplus(x):
    return np.log(1 + np.exp(x))

def softplus_prime(x):
    return logistic(x)

def rectified_linear(x):
    return max(0, x)

def rectified_linear_prime(x):
    if x > 0:
        return 1
    else:
        return 0

def tanh(x):
    return np.tanh(x)

def tanh_prime(x):
    return 1 - (np.tanh(x))**2