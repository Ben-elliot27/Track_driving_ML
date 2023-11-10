"""
A script that will handle learning via Evolution and natural selection by running the code for e certain time period,
finding which players performed best and using their 'genetics' (NN weights) to train the next generation.
"""
import numpy as np
NUM_BEST_PLAYERS = 3
class Evolution_learning():

    def __init__(self, game_window):
        self.game_window = game_window
        self.best_players


    def on_startup(self):
        #set up the players NNs and their weights
        #Also start timer on how long it should run for

        for player in self.game_window.player_list:
            player.model.set_weights() #need something in here
            player.model.set_biases() #and again

        pass


    def on_cycle_end(self):
        #When current cycle ends

        self.game_window.clear() #clear the screen
        #maybe want to pause game so players don't carry on moving
        self.best_players = self.pick_best_players()
        self.set_players_new_NN()
        self.run_again()

    def pick_best_players(self):
        """
        picks the highest 3 scoring players from the last run
        :return: best_players: list of player arcade objects
        """
        player_costs = []
        best_players = []
        for player in self.game_window.player_list:
            player_costs.append(player.cost)
        player_costs_sorted = sorted(player_costs)
        for i in range(NUM_BEST_PLAYERS - 1):
            a = player_costs.index(player_costs_sorted[i])
            best_players.append(self.game_window.player_list[a])

        #Would be nice to save the NNs of the best performers or only show them
        return best_players


    def set_players_new_NN(self):
        """
        Sets the new NNs based on the highest performers from the previous run
        :return:
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x)
                        for x, y in zip(sizes[:-1], sizes[1:])]
        """

        for i, player in enumerate(self.game_window.player_list):

            weights = self.best_players[i % NUM_BEST_PLAYERS].model.get_weights()
            weights += np.random.normal(loc=0.0, scale=0.5, size=weights.shape) #adds the weights based on normal distribution

            biases = self.best_players[i % NUM_BEST_PLAYERS].model.get_biases()
            biases += np.random.normal(loc=0.0, scale=0.5,
                                        size= biases.shape)  # adds the weights based on normal distribution
            player.model.set_biases(biases)

            #move player back to start
            player.center_x = self.game_window.player_spawn_pos[0]
            player.center_y = self.game_window.player_spawn_pos[1]








