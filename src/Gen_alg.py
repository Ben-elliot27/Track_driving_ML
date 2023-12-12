"""
Contains class for generic evolution algorithm
"""

import arcade
from threading import Timer
import torch
import torch.nn as nn
import numpy as np

NUM_BEST_PLAYERS = 4
TOT_NUM_PLAYERS = NUM_BEST_PLAYERS + 20  # Best players also spawned

RNG = np.random.default_rng(seed=82)  # Uses numpy random generator
SIGMA = 3

EPOCH_TIME = 10  # seconds // this is not currently based on the number of updates that happens, but could be in future

RATE = 1 / 8  # rate of increase of time simulated for

class Generic_Learning_Alg:

    def __init__(self, game_window, update_freq, net):
        self.game_window = game_window
        self.epochs = 0
        self.save = False
        self.NUM_BEST_PLAYERS = NUM_BEST_PLAYERS
        self.best_players_to_draw = arcade.SpriteList()
        self.epochs_to_save = update_freq
        self.net = net

    def on_startup_init(self):
        """
        FOR WHEN THE SAVED NN IS NOT USED
        Set up the players, their NNs and their weights
        Also start timer on how long it should run for (separate thread)
        :return:
        """
        for i in range(TOT_NUM_PLAYERS):
            self.game_window.spawn_player()

        for a, player in enumerate(self.game_window.player_list):
            # Create the NN
            model = self.net

            with torch.no_grad():
                for i in range(len(model)):
                    if i % 2 == 0:
                        multiplier_arr = SIGMA * RNG.standard_normal(size=model[i].weight.shape)
                        model[i].weight = nn.Parameter(model[i].weight + multiplier_arr)

                player.model = model
            if a < NUM_BEST_PLAYERS:
                self.best_players_to_draw.append(player)

        for player in self.game_window.player_list:
            player.isActive = True
        t = Timer(EPOCH_TIME, self.on_cycle_end)
        t.start()

    def on_startup_with_model(self, NN_dir):
        """
        FOR WHEN THE SAVED NN IS USED
        Set up the players, their NNs (based on saved model) and their weights
        Also start timer on how long it should run for (separate thread)
        :param NN_dir :str: directory for the NN to be loaded
        :return:
        """

        for i in range(TOT_NUM_PLAYERS):
            self.game_window.spawn_player()

        loaded_model = torch.load(NN_dir).double()

        for i, player in enumerate(self.game_window.player_list):
            player.model = self.net

            if i >= NUM_BEST_PLAYERS:
                with torch.no_grad():
                    for a in range(len(loaded_model)):
                        if a % 2 == 0:
                            mult_arr = SIGMA * RNG.standard_normal(
                                size=loaded_model[a].weight.shape)
                            player.model[a].weight = nn.Parameter(loaded_model[a].weight + mult_arr)
            else:
                player.model = loaded_model
                self.best_players_to_draw.append(player)

        for player in self.game_window.player_list:
            player.isActive = True
        if self.game_window.menu_setting is None:
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
        self.set_players_new_NN()
        self.reset_player()

        if self.epochs_to_save:
            if self.epochs % self.epochs_to_save == 0:
                self.game_window.save_best_player(epochs=self.epochs_to_save)

        t = Timer(EPOCH_TIME * (self.epochs ** RATE), self.on_cycle_end)
        t.start()

    def pick_best_players(self):
        """
        Picks the highest 3 scoring players from the last run and print their information
        Also deactivates all players, so they don't carry on moving
        :return: best_players: list of player arcade objects
        """
        costs = []
        for player in self.game_window.player_list:
            player.isActive = False
            costs.append(player.cost)

        best_list = sorted(self.game_window.player_list, key=lambda player: player.cost, reverse=True)[
                         0:self.NUM_BEST_PLAYERS]

        print(f"""Costs of players: {sorted(costs, reverse=True)}
        Players: {best_list}
        Epoch: {self.epochs}
        """)

        return best_list

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
            player.reset_reward_list()

        for player in self.game_window.player_list:
            player.isActive = True  # re-active player

    def set_players_new_NN(self):
        """
        Set the players new neural network according to the learning algorithm chosen
        :return:
        """
        pass
