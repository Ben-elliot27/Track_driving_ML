"""
Edited version of the Game script st the variables and methods are attached to the player rather than the screen.

Script to run a python arcade driving game with visible 'raycasts' and checkpoints for implementing a machine learning
model to train on.

Because it uses arcade, a simple game library, it doesn't have many features such as proper raycasts so they are
implemented 'dodgily' as a series of individual objects.


"""


import arcade

from Player import Player
from Wall import Wall
from Ray import Ray

import time

from Evolution_learning import Evolution_learning

#Options: "Evolution"
LEARNING_METHOD = "Evolution" #Method by which the AI will be trained


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):

        # Call the parent class initializer
        super().__init__(width, height, title)

        # Variables that will hold sprite lists
        self.player_list = None
        self.wall_list = None

        # Set up the player, wall, ray info
        self.player_sprite = None
        self.wall_sprite = None
        self.ray_sprite = None

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        #image initialsiation
        self.CAR_SPRITE_IMG = "../images/Car_sprite.png"
        self.CIRCLE_SPRITE_IMG = '../images/Circle_sprite.png'
        self.WALL_SPRITE_IMG = '../images/wall_sprite.png'
        self.SPRITE_SCALING = 0.05



        # Initials for walls
        self.WALL_COUNT = 8
        self.WALL_SCALING = [5.7, 4.1, 5.6, 4.1,
                        4.2, 2.9, 4.2, 2.9]
        self.X_POS = [490, 995, 490, 10,
                 490, 995 - 120, 485, 10 + 120]
        self.Y_POS = [10, 365, 730, 365,
                 10 + 120, 365, 740 - 120, 365]
        self.WALL_ANGLES = [0, 90, 0, 90, 0, 90, 0, 90]

        self.player_spawn_pos = [50, 50]





    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.reward_list = arcade.SpriteList(use_spatial_hash=True)  # visible = False
        self.ray_list = arcade.SpriteList()  # visible = False

        # Spawn and draw all the sprites.
        #Spawn objects
        self.spawn_walls()
        #self.spawn_player()

        if LEARNING_METHOD == "Evolution":

            inp = input("Load from previously saved model (y/n)? ")
            if inp == 'y':
                self.learning_alg = Evolution_learning(self)
                self.learning_alg.on_startup_withmodel()
            else:
                self.learning_alg = Evolution_learning(self)
                self.learning_alg.on_startup_init()





    def spawn_player(self):
        # Set up the player
        self.player_sprite = Player(self.CAR_SPRITE_IMG,
                                    self.SPRITE_SCALING)
        self.player_sprite.center_x = self.player_spawn_pos[0]
        self.player_sprite.center_y = self.player_spawn_pos[1]
        self.player_list.append(self.player_sprite)
        self.player_sprite.initialise()

        #Draw Player
        #self.player_list.draw()


    def spawn_walls(self):
        for i in range(self.WALL_COUNT):
            # Set up the wall
            self.wall_sprite = Wall(self.WALL_SPRITE_IMG,
                                    self.WALL_SCALING[i])
            self.wall_sprite.center_x = self.X_POS[i]
            self.wall_sprite.center_y = self.Y_POS[i]
            self.wall_sprite.angle = self.WALL_ANGLES[i]
            self.wall_list.append(self.wall_sprite)

        #Draw walls
        self.wall_list.draw()

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before start drawing
        self.clear()

        # Draw all the sprites.
        #self.player_list.draw()
        self.wall_list.draw()
        #self.reward_list.draw()
        #self.ray_list.draw()
        try:
            for player in self.learning_alg.best_players:
                player.draw()
                player.ray_list.draw()
                player.reward_list.draw()
        except:
            print("No best_player list yet")
            for player in self.player_list[0:2]:
                player.draw()




        """
        # Display text
        for player_sprite in self.player_list:
            arcade.draw_text(f"Velocity: {player_sprite.current_vel:6.3f}", 10, 50, arcade.color.BLACK)
            arcade.draw_text(f"Angle: {player_sprite.angle % 360:6.3f}", 10, 70, arcade.color.BLACK)
            arcade.draw_text(f"xPOS: {player_sprite.center_x:6.3f}", 10, 90, arcade.color.BLACK)
            arcade.draw_text(f"yPOS: {player_sprite.center_y:6.3f}", 10, 110, arcade.color.BLACK)
            """

    def on_update(self, delta_time):
        """ Movement and game logic """

        t0 = time.time()
        self.player_list.update()
        for player in self.player_list:
            player.update_ray_hit_list(self.wall_list)
            player.collision_with_wall(self.wall_list)
        t1 = time.time()
        print("total update time:", t1 - t0)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        """
        if key == arcade.key.UP:
            self.player_sprite.player_movement([1, 0, 0, 0])
        elif key == arcade.key.LEFT:
            self.player_sprite.player_movement([0, 1, 0, 0])
        elif key == arcade.key.RIGHT:
            self.player_sprite.player_movement([0, 0, 1, 0])
        elif key == arcade.key.DOWN:
            self.player_sprite.player_movement([0, 0, 0, 1])
            """
        if key == arcade.key.S:
            self.learning_alg.save = True


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.player_movement([0, 0, 0])







def main():
    """ Main function """
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 750
    SCREEN_TITLE = "Track learning"
    game_window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game_window.setup()
    arcade.run()



# --------------------------------------------------------------------------------------


main()


