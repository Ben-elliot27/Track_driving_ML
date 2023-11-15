"""
A script that will handle learning via Evolution and natural selection by running the code for a certain time period,
finding which players performed best and using their 'genetics' (NN weights) to train the next generation.

Uses a simple algorithm where the best players' NNs are given some random noise each cycle/epoch rather than doing a
NEAT algorithm and combining genes from good parents which would accelerate learning.

The random noise initially is given by:
SIGMA * normal(mu=0, sigma=0.5) // a normal distribution centred around 0
However this does change as the number of cycles increases as:
(SIGMA/(number of cycles)**RATE_RAND)

The length of each cycle also changes with the number of cycles as:
EPOCH_TIME * (number of cycles)**(RATE)


FUTURE ALG
https://medium.com/@evertongomede/neuroevolution-of-augmenting-topologies-neat-innovating-neural-network-architecture-evolution-bc5508527252
TODO FORMATIING
TODO check reseeting of rewards worked
"""

from threading import Timer

import numpy as np
from tensorflow import keras

NUM_BEST_PLAYERS = 2
TOT_NUM_PLAYERS = NUM_BEST_PLAYERS + 20  # Best players also spawned

RNG = np.random.default_rng(seed=82) # Uses numpy random generator
SIGMA = 3

EPOCH_TIME = 10  # seconds // this is not currently based on the number of updates that happens, but could be in future

RATE = 1 / 30  # rate of increase of time simulated for
RATE_RAND = 1 / 50  # rate of decrease of random noise


class Evolution_learning():

    def __init__(self, game_window):
        self.game_window = game_window
        self.epochs = 0
        self.save = False
        self.NUM_BEST_PLAYERS = NUM_BEST_PLAYERS

    def on_startup_init(self):
        """
        FOR WHEN THE SAVED NN IS NOT USED
        Set up the players, their NNs and their weights
        Also start timer on how long it should run for (separate thread)
        :return:
        """
        for i in range(TOT_NUM_PLAYERS):
            self.game_window.spawn_player()

        for player in self.game_window.player_list:
            # Create the NN
            inputs = keras.Input(shape=(11,))
            dense = keras.layers.Dense(50, activation='relu')(inputs)
            outputs = keras.layers.Dense(4)(dense)
            model = keras.Model(inputs=inputs, outputs=outputs)
            model.compile(optimizer='Adam')

            new_weights = []

            # Give each NN a random deviation at the start
            for weights in model.get_weights():
                new_weights.append(
                    weights + SIGMA * RNG.standard_normal(size=weights.shape)
                )
            model.set_weights(new_weights)
            player.model = model

        for player in self.game_window.player_list:
            player.isActive = True
        t = Timer(EPOCH_TIME, self.on_cycle_end)
        t.start()

    def on_startup_withmodel(self):
        """
        FOR WHEN THE SAVED NN IS USED
        Set up the players, their NNs (based on saved model) and their weights
        Also start timer on how long it should run for (separate thread)
        :return:
        """

        for i in range(TOT_NUM_PLAYERS):
            self.game_window.spawn_player()

        for player in self.game_window.player_list:

            model = keras.models.load_model('../models_evolution/current_best.keras')

            new_weights = []

            # Give each NN a random deviation at the start
            for weights in model.get_weights():
                new_weights.append(
                    weights + SIGMA * RNG.standard_normal(size=weights.shape)
                )
            model.set_weights(new_weights)
            player.model = model

        for player in self.game_window.player_list:
            player.isActive = True
        t = Timer(EPOCH_TIME, self.on_cycle_end)
        t.start()

    def on_cycle_end(self):
        """
        Called when current cycle/epoch ends
        Handles the selection of best players and giving the players their new NNs
        :return:
        """
        self.epochs += 1
        self.best_players = self.pick_best_players()
        self.save_best_player()
        self.set_players_new_NN()
        self.reset_player()

        t = Timer(EPOCH_TIME * (self.epochs ** RATE), self.on_cycle_end)
        t.start()

    def pick_best_players(self):
        """
        Picks the highest 3 scoring players from the last run and print their informaton
        Also deactivates all players, so they don't carry on moving
        :return: best_players: list of player arcade objects
        """
        costs = []
        for player in self.game_window.player_list:
            player.isActive = False
            costs.append(player.cost)

        best_list = sorted(self.game_window.player_list, key=lambda player: player.cost, reverse=True)[
                         0:NUM_BEST_PLAYERS]

        print(f"""Costs of players: {sorted(costs, reverse=True)}
        Players: {best_list}
        Epoch: {self.epochs}
        """)

        return best_list

    def set_players_new_NN(self):
        """
        Sets the new NNs based on the highest performers from the previous run
        Rather than using NEAT and actually mutating parents, this just uses randomness
        :return:
        """

        for i, player in enumerate(self.game_window.player_list):

            new_weights = []
            for weights in self.best_players[i % NUM_BEST_PLAYERS].model.get_weights():
                if i < NUM_BEST_PLAYERS:
                    new_weights.append(weights)
                else:
                    new_weights.append(
                        weights + (SIGMA / (self.epochs ** RATE_RAND)) * RNG.standard_normal(size=weights.shape)
                    )

            player.model.set_weights(new_weights)

    def reset_player(self):
        """
        Resets the players to their original just spawned state
        :return:
        """
        for player in self.game_window.player_list:
            # move player back to start
            player.center_x = self.game_window.player_spawn_pos[0]
            player.center_y = self.game_window.player_spawn_pos[1]
            player.angle = 0

            # reset reward positions
            player.reward_list.clear()
            player.spawn_rewards()

        for player in self.game_window.player_list:
            player.isActive = True  # re-active player

    def save_best_player(self):
        """
        Saves the model of the best player from the current run
        :return:
        """
        if self.save:
            self.best_players[0].model.save('../models_evolution/current_best.keras')
            print("Model saved")
            self.save = False
