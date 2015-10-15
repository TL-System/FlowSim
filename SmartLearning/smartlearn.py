import learn as l
import random

#General information for Q-Learning.
#A state is a list, where each entry in the list corresponds to a state feature.
#For instance, if we use as state features the number of active flows in 3 links, the return value could be [32, 45, 75]
#Be careful to use a fixed ordering for the state features.
#An action is again a list, where only one entry is 1 and the rest are 0.
#For instance, if we have 4 actions, the action [0, 1, 0, 0] means that we take the second action (can only take one)

class LearnSDN:

    def __init__(self, number_actions, number_sources, number_destinations, number_states, number_hidden_nodes_per_layer, activation_function_type, exploration_type, epsilon, alpha, gamma, beta, learning_rate, learning_method):
        #Create an instance of the Q_Learning class.
        self.learn = l.Learn(number_actions, number_sources, number_destinations, number_states, number_hidden_nodes_per_layer, activation_function_type, exploration_type, epsilon, alpha, gamma, beta, learning_rate)
        self.learning_method = learning_method
        self.number_actions = number_actions

    def select_action(self, current_state, source, destination):
        return self.learn.choose_action(current_state, source, destination)

    def update(self, previous_state, source, destination, previous_action, current_state, reward):
        previous_action_list = self.get_action_list(previous_action)
        if self.learning_method == 0:
            self.Q(previous_state, source, destination, previous_action_list, current_state, reward)
        elif self.learning_method == 1:
            self.R(previous_state, source, destination, previous_action_list, current_state, reward)

    def Q(self, previous_state, source, destination, previous_action, current_state, reward):
            if previous_state != [] and previous_action != []:
                self.learn.Q_learn(previous_state, source, destination, previous_action, reward, current_state)

    def R(self, previous_state, source, destination, previous_action, current_state, reward):
        if previous_state != [] and previous_action != []:
            self.learn.R_learn(previous_state, source, destination, previous_action, reward, current_state)

    def get_action_list(self, action):
        return [0 for i in range(action)] + [1] + [0 for i in range(action + 1, self.number_actions)]