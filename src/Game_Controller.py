"""
Main game class - handles running of arcade and window as well as setting up sprite_lists

Because it uses arcade, a simple game library, it doesn't have many features such as proper ray-casts, so they are
implemented 'dodgily' as a series of individual objects.

TODO: add loading of a previous model to a UI element + loading of track
TODO: make it so you can leave the game view and go back to main menu

"""

import arcade

from Evolution_learning import Evolution_learning
from Player import Player
from Wall import Wall
import pickle
from Draw_track import Draw_track



# Options: "Evolution"
LEARNING_METHOD = "Evolution"  # Method by which the AI will be trained

FRAME_RATE = 1 / 20  # 20 fps

UPDATE_FREQ = 3  # Frames per NN ran to get new movement






class MyGame(arcade.View):
    """
    Main application class.
    """

    def __init__(self, MainMenu, track=None):
        #  In future also need to add rewards list

        # Call the parent class initializer
        super().__init__()

        self.Main_Menu = MainMenu

        if track:
            self.wall_list = track[0]
            self.reward_list = track[1]
            self.player_spawn_pos = track[2]

        else:
            self.window.show_view(self.Main_Menu)

        # Variables that will hold sprite lists
        self.player_list = arcade.SpriteList()

        # Set up the player, wall, ray info
        self.player_sprite = None

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        self.update_freq_count = 0  # Counter

        # image initialization
        self.CAR_SPRITE_IMG = "../images/Car_sprite.png"
        self.CIRCLE_SPRITE_IMG = '../images/Circle_sprite.png'
        self.WALL_SPRITE_IMG = '../images/wall_sprite.png'
        self.PLAYER_SCALING = 0.05





    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists setup
        self.player_list = arcade.SpriteList()


        if LEARNING_METHOD == "Evolution":

            inp = input("Load from previously saved model (y/n)? ")
            if inp == 'y':
                self.learning_alg = Evolution_learning(self)
                self.learning_alg.on_startup_withmodel()
            else:
                self.learning_alg = Evolution_learning(self)
                self.learning_alg.on_startup_init()

    def spawn_player(self):
        """
        Spawns a player and adds it to the player_list attached to this object
        Does not draw player

        REQUIRES attributes:
        CAR_SPRITE_IMG: image file directory link
        SPRITE_SCALING: float
        PLAYER_SPAWN_POS: [x: float, y: float]
        :return:
        """
        self.player_sprite = Player(self.CAR_SPRITE_IMG,
                                    self.PLAYER_SCALING)
        self.player_sprite.center_x = self.player_spawn_pos[0]
        self.player_sprite.center_y = self.player_spawn_pos[1]
        self.player_list.append(self.player_sprite)
        self.player_sprite.initialise(reward_list=self.reward_list)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before start drawing
        self.clear()

        arcade.draw_text("press ESC to access menu", self.window.width - 90, self.window.height - 30,
                         arcade.color.WHITE, font_size=10, anchor_x="center")

        self.wall_list.draw()  # Draw the walls

        # Draw the best players if there are any yet
        try:
            for player in self.learning_alg.best_players:
                player.draw()
                player.ray_list.draw()
                player.reward_list.draw()
        except:
            print("No best players yet")
            # No best_player list yet
            for player in self.player_list[0:2]:
                player.draw()

    def on_update(self, delta_time):
        """
        Movement and game logic, called every FRAME_RATE s
        :param delta_time: time since function last called
        :return:
        """

        self.player_list.update()  # Updates player movement

        # Updates player movement via NN every UDPATE_FREQ frames
        if self.update_freq_count >= UPDATE_FREQ:
            for player in self.player_list:
                player.update_ray_hit_list(self.wall_list)
                player.collision_with_wall(self.wall_list)
                player.AI_movement()
                self.update_freq_count = 0
        else:
            self.update_freq_count += 1

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        # Save the current model
        if key == arcade.key.S:
            self.learning_alg.save = True

        if key == arcade.key.ESCAPE:
            self.window.show_view(self.Main_Menu)  # TODO: make it so that you can go to/from main menu without losing progress


# --------------------------------------------------------------------------------------
