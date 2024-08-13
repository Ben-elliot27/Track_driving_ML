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
TODO: threading + CUDA
"""

from threading import Timer

from Gen_alg import Generic_Learning_Alg
import arcade
import numpy as np
import torch
import torch.nn as nn

NUM_BEST_PLAYERS = 4
TOT_NUM_PLAYERS = NUM_BEST_PLAYERS + 20  # Best players also spawned

RNG = np.random.default_rng(seed=82)  # Uses numpy random generator
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
            nn.Linear(25, 10, bias=False),
            nn.ReLU(),
            nn.Linear(10, 4, bias=False)
        )

    def forward(self, x):
        return self.linear_relu(x)


class Evolution_learning(Generic_Learning_Alg):

    def __init__(self, game_window, update_freq=None):
        super().__init__(game_window, update_freq, Net().linear_relu.double())

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
                            player.model[a].weight = nn.Parameter(best_player.model[a].weight.cpu() + mult_arr)
            else:
                with torch.no_grad():
                    best_player = self.best_players[i % NUM_BEST_PLAYERS]
                    for a in range(len(best_player.model)):
                        if a % 2 == 0:
                            player.model[a].weight = nn.Parameter(best_player.model[a].weight)
                    self.best_players_to_draw[i] = player




