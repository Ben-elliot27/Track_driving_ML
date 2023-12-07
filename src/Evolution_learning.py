"""
A script that handles learning via Evolution and natural selection by running the code for a certain time period,
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

TODO make a better way of saving the best player & don't a;ways overwrite

"""

from threading import Timer

import arcade
import numpy as np
import torch
import torch.nn as nn

NUM_BEST_PLAYERS = 4
TOT_NUM_PLAYERS = NUM_BEST_PLAYERS + 20  # Best players also spawned

RNG = np.random.default_rng(seed=82) # Uses numpy random generator
SIGMA = 3

EPOCH_TIME = 10  # seconds // this is not currently based on the number of updates that happens, but could be in future

RATE = 1 / 8  # rate of increase of time simulated for
RATE_RAND = 1 / 30  # rate of decrease of random noise

INPUT_LEN = 12 + 3  # Num of rays + speed, angle, dist to nearest rewards


class Net(nn.Module):
    """
    Neural Network class
    """
    def __init__(self):
        super(Net, self).__init__()
        self.linear_relu = nn.Sequential(
            nn.Linear(INPUT_LEN, 25, bias=False),
            nn.ReLU(),
            nn.Linear(10, 10, bias=False),
            nn.ReLU(),
            nn.Linear(10, 4, bias=False)
        )

    def forward(self, x):
        return self.linear_relu(x)


class Evolution_learning():

    def __init__(self, game_window):
        self.game_window = game_window
        self.epochs = 0
        self.save = False
        self.NUM_BEST_PLAYERS = NUM_BEST_PLAYERS
        self.best_players_to_draw = arcade.SpriteList()

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
            model = Net().linear_relu.double()

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
            player.model = Net().linear_relu.double()

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

        if self.epochs % 30 == 0:
            self.game_window.save_best_player()

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

            if i >= NUM_BEST_PLAYERS:
                with torch.no_grad():
                    best_player = self.best_players[i % NUM_BEST_PLAYERS]
                    for a in range(len(best_player.model)):
                        if a % 2 == 0:
                            mult_arr = (SIGMA / (self.epochs ** RATE_RAND)) * RNG.standard_normal(
                                size=best_player.model[a].weight.shape)
                            player.model[a].weight = nn.Parameter(best_player.model[a].weight + mult_arr)
            else:
                with torch.no_grad():
                    best_player = self.best_players[i % NUM_BEST_PLAYERS]
                    for a in range(len(best_player.model)):
                        if a % 2 == 0:
                            player.model[a].weight = nn.Parameter(best_player.model[a].weight)
                    self.best_players_to_draw[i] = player



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


