"""
A script that will handle learning via Evolution and natural selection by running the code for e certain time period,
finding which players performed best and using their 'genetics' (NN weights) to train the next generation.
https://medium.com/@evertongomede/neuroevolution-of-augmenting-topologies-neat-innovating-neural-network-architecture-evolution-bc5508527252
"""
from tensorflow import keras
from threading import Timer
import numpy as np
import arcade
NUM_BEST_PLAYERS = 2
TOT_NUM_PLAYERS = NUM_BEST_PLAYERS + 20  #Best players also spawned

RNG = np.random.default_rng(seed=82)
SIGMA = 3

EPOCH_TIME = 10 #seconds

RATE = 1/30
RATE_RAND = 1/50
class Evolution_learning():

    def __init__(self, game_window):
        self.game_window = game_window
        self.epochs = 0
        self.save = False
        self.NUM_BEST_PLAYERS = NUM_BEST_PLAYERS
        self.best_list = []




    def on_startup_init(self):
        #set up the players NNs and their weights
        #Also start timer on how long it should run for
        for i in range(TOT_NUM_PLAYERS):
            self.game_window.spawn_player()


        for player in self.game_window.player_list:

            inputs = keras.Input(shape=(11,))
            dense = keras.layers.Dense(50, activation='relu')(inputs)
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
            player.model = model

        for player in self.game_window.player_list:
            player.isActive = True
        t = Timer(EPOCH_TIME, self.on_cycle_end)
        t.start()

    def on_startup_withmodel(self):
        #set up the players NNs aand weights from previously saved NN
        #Also start timer on how long it should run for
        for i in range(TOT_NUM_PLAYERS):
            self.game_window.spawn_player()


        for player in self.game_window.player_list:

            model = keras.models.load_model('../models_evolution/current_best.keras')

            new_weights = []

            #Give each NN a random deviation at the start
            for weights in model.get_weights():
                new_weights.append(
                    weights + SIGMA*RNG.standard_normal(size=weights.shape)
                )
            model.set_weights(new_weights)
            player.model = model

        for player in self.game_window.player_list:
            player.isActive = True
        t = Timer(EPOCH_TIME, self.on_cycle_end)
        t.start()





    def on_cycle_end(self):
        #When current cycle ends

        #self.game_window.clear() #clear the screen (now just moving players rather than respawning)
        #maybe want to pause game so players don't carry on moving
        self.epochs += 1
        self.best_players = self.pick_best_players()
        self.save_best_player()
        self.set_players_new_NN()

        t = Timer(EPOCH_TIME * (self.epochs)**(RATE), self.on_cycle_end)
        t.start()



    def pick_best_players(self):
        """
        picks the highest 3 scoring players from the last run
        also deactivates the player so they don't carry on moving
        :return: best_players: list of player arcade objects
        """
        costs = []
        for player in self.game_window.player_list:
            player.isActive = False
            costs.append(player.cost)


        self.best_list = sorted(self.game_window.player_list, key=lambda player: player.cost, reverse=True)[0:NUM_BEST_PLAYERS]


        print(f"""Costs of players: {sorted(costs, reverse=True)}
        Players: {self.best_list}
        Epoch: {self.epochs}
        """)

        #Would be nice to save the NNs of the best performers or only show them
        return self.game_window.player_list[0:NUM_BEST_PLAYERS]


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
                    weights + (SIGMA/(self.epochs)**RATE_RAND) * RNG.standard_normal(size=weights.shape)
                )
            player.model.set_weights(new_weights)

            #move player back to start
            player.center_x = self.game_window.player_spawn_pos[0]
            player.center_y = self.game_window.player_spawn_pos[1]
            player.angle = 0

        for player in self.game_window.player_list:
            player.isActive = True #re-active player


    def save_best_player(self):
        """
        function to save the model of the best player from the current run
        :return:
        """
        if self.save:
            self.best_players[0].model.save('../models_evolution/current_best.keras')
            print("Model saved")
            self.save = False










