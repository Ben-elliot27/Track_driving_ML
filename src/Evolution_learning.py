"""
A script that will handle learning via Evolution and natural selection by running the code for e certain time period,
finding which players performed best and using their 'genetics' (NN weights) to train the next generation.
"""
import numpy as np
class Evolution_learning():

    def __init__(self, game_window):
        self.game_window = game_window


    def on_cycle_end(self):
        #When current cycle ends

        self.game_window.clear() #clear the screen

        self.pick_best_players()
        self.set_players_new_NN()
        self.run_again()

    def pick_best_players(self):
        player_costs = []
        for player in self.game_window.player_list:
            player_costs.append(player.cost)
        player_costs.index(max(player_costs))





