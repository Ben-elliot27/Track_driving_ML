"""
MAIN QLearning AI script -- based off Torch NN
NOT WORKING
"""


import os
#import pygame
import argparse
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from DQL import DQNAgent
from random import randint
import random
import statistics
import torch.optim as optim
import torch
#from GPyOpt.methods import BayesianOptimization
import datetime
import distutils.util
import arcade
import GLOBALS

#################################
#   Define parameters manually  #
#################################
def define_parameters():
    params = dict()
    # Neural Network
    params['epsilon_decay_linear'] = 1 / 100
    params['learning_rate'] = 0.00013629
    params['first_layer_size'] = 200  # neurons in the first layer
    params['second_layer_size'] = 20  # neurons in the second layer
    params['third_layer_size'] = 50  # neurons in the third layer
    params['episodes'] = 250
    params['memory_size'] = 2500
    params['batch_size'] = 1000
    # Settings
    params['weights_path'] = 'weights/weights.h5'
    params['train'] = False
    params["test"] = True
    params['plot_score'] = True
    params['log_path'] = 'logs/scores_' + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + '.txt'
    return params

def get_record(score, record):
    if score >= record:
        return score
    else:
        return record

def initialize_game(player, game, food, agent, batch_size):
    state_init1 = agent.get_state()  # [0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0]
    action = [1, 0, 0]
    GLOBALS.game_window.AI_player_move(action)
    state_init2 = agent.get_state()
    reward1 = agent.set_reward()
    agent.remember(state_init1, action, reward1, state_init2, False)
    agent.replay_new(agent.memory, batch_size)
