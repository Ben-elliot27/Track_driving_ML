"""
A script that will handle learning via Evolution and natural selection by running the code for e certain time period,
finding which players performed best and using their 'genetics' (NN weights) to train the next generation.
"""
from tensorflow import keras
import numpy as np
NUM_BEST_PLAYERS = 3
TOT_NUM_PLAYERS = 10

RNG = np.random.default_rng(seed=82)
SIGMA = 3
class Evolution_learning():

    def __init__(self, game_window):
        self.game_window = game_window
        self.best_players = []
        self.epochs = 0


    def on_startup(self):
        #set up the players NNs and their weights
        #Also start timer on how long it should run for
        for i in range(TOT_NUM_PLAYERS):
            self.game_window.spawn_player()

        for player in self.game_window.player_list:

            inputs = keras.Input(shape=(11,))
            dense = keras.layers.Dense(64, activation='relu')(inputs)
            outputs = keras.layers.Dense(4)(dense)
            model = keras.Model(inputs=inputs, outputs=outputs)
            model.compile(optimizer='Adam')

            new_weights = []

            #Give each NN a random deviation at the start
            for weights in model.get_weights():
                new_weights.append(
                    weights + SIGMA*RNG.standard_normal(size=weights.shape)
                )
            model.set_weights(new_weights)

            player.isActive = True



    def timers(self):
        self.epochs += 1


    def on_cycle_end(self):
        #When current cycle ends

        #self.game_window.clear() #clear the screen (now just moving players rather than respawning)
        #maybe want to pause game so players don't carry on moving
        self.best_players = self.pick_best_players()
        self.set_players_new_NN()



    def pick_best_players(self):
        """
        picks the highest 3 scoring players from the last run
        also deactivates the player so they don't carry on moving
        :return: best_players: list of player arcade objects
        """
        player_costs = []
        best_players = []
        for player in self.game_window.player_list:
            player.isActive = False
            player_costs.append(player.cost)
        player_costs_sorted = sorted(player_costs)
        for i in range(NUM_BEST_PLAYERS - 1):
            a = player_costs.index(player_costs_sorted[i])
            best_players.append(self.game_window.player_list[a])
            print(f"""Costs of players: {a}
            Players: {best_players}
            """)

        #Would be nice to save the NNs of the best performers or only show them
        return best_players


    def set_players_new_NN(self):
        """
        Sets the new NNs based on the highest performers from the previous run
        Rather than using NEAT and actually mutating parents, this just uses randomness
        :return:
        """

        for i, player in enumerate(self.game_window.player_list):


            new_weights = []
            for weights in self.best_players[i % NUM_BEST_PLAYERS].model.get_weights():
                new_weights.append(
                    weights + (SIGMA/(self.epochs)**1/4) * RNG.standard_normal(size=weights.shape)
                )
            player.model.set_weights(new_weights)

            #move player back to start
            player.center_x = self.game_window.player_spawn_pos[0]
            player.center_y = self.game_window.player_spawn_pos[1]

            player.isActive = True #re-active player








