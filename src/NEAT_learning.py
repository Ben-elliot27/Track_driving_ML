"""
A script that implements the NEAT learning algorithm using python-neat module
"""
import torch.nn as nn
import torch

from Gen_alg import Generic_Learning_Alg

import neat

INPUT_LEN = 12+3

class Default_Net(nn.Module):
    """
    Neural Network class
    """
    def __init__(self):
        super(Default_Net, self).__init__()
        self.linear_relu = nn.Sequential(
            nn.Linear(INPUT_LEN, 15, bias=False),
            nn.ReLU(),
            nn.Linear(15, 10, bias=False),
        )

    def forward(self, x):
        return self.linear_relu(x)


class NEAT(Generic_Learning_Alg):

    def __init__(self, game_window, update_freq=None):
        super.__init__(game_window, update_freq, Default_Net().linear_relu.double())

    def set_players_new_NN(self):
        """
        Set the players new neural network according to NEAT algorithm
        :return:
        """





 # --------------------------------------------------------------------------------
def eval_genomes(genomes, config):
    """
    Runs the genomes and sets genomes final fitness
    :return:
    """


def run(config_file):
    # Load configuration
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    winner = p.run(eval_genomes, 1)
