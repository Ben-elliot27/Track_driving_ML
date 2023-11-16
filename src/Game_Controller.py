"""
Main game class - handles running of arcade and window as well as setting up sprite_lists

Because it uses arcade, a simple game library, it doesn't have many features such as proper ray-casts, so they are
implemented 'dodgily' as a series of individual objects.
"""

import arcade

from Evolution_learning import Evolution_learning
from Player import Player
from Wall import Wall

# Options: "Evolution"
LEARNING_METHOD = "Evolution"  # Method by which the AI will be trained

FRAME_RATE = 1 / 20  # 20 fps

UPDATE_FREQ = 3  # Frames per NN ran to get new movement


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):

        # Call the parent class initializer
        super().__init__(width, height, title)

        # Variables that will hold sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        # Set up the player, wall, ray info
        self.player_sprite = None
        self.wall_sprite = None

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        self.update_freq_count = 0  # Counter

        # image initialization
        self.CAR_SPRITE_IMG = "../images/Car_sprite.png"
        self.CIRCLE_SPRITE_IMG = '../images/Circle_sprite.png'
        self.WALL_SPRITE_IMG = '../images/wall_sprite.png'
        self.PLAYER_SCALING = 0.05

        # Initials for walls
        self.WALL_COUNT = 8
        self.WALL_SCALING = [5.7, 4.1, 5.6, 4.1,
                             4.2, 2.9, 4.2, 2.9]
        self.WALL_X_POS = [490, 995, 490, 10,
                           490, 995 - 120, 485, 10 + 120]
        self.WALL_Y_POS = [10, 365, 730, 365,
                           10 + 120, 365, 740 - 120, 365]
        self.WALL_ANGLES = [0, 90, 0, 90, 0, 90, 0, 90]

        self.player_spawn_pos = [50, 50]

    def setup(self):
        """ Set up the game and initialize the variables. """

        self.set_update_rate(FRAME_RATE)  # sets fps to FRAME_RATE

        # Sprite lists setup
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        self.spawn_walls()

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
        self.player_sprite.initialise()

    def spawn_walls(self):
        """
        Spawns all walls and adds them to the wall_list attached to this object
        Does draw walls

        REQUIRES attributes:
        WALL_SPRITE_IMG: image file directory link :str
        WALL_COUNT: :int
        WALL_X_POS: [:floats]
        WALL_Y_POS: [:floats]
        WALL_ANGLES: [:floats]
        :return:
        """
        for i in range(self.WALL_COUNT):
            # Set up the wall
            self.wall_sprite = Wall(self.WALL_SPRITE_IMG,
                                    self.WALL_SCALING[i])
            self.wall_sprite.center_x = self.WALL_X_POS[i]
            self.wall_sprite.center_y = self.WALL_Y_POS[i]
            self.wall_sprite.angle = self.WALL_ANGLES[i]
            self.wall_list.append(self.wall_sprite)

        # Draw walls
        self.wall_list.draw()

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before start drawing
        self.clear()

        self.wall_list.draw()  # Draw the walls

        # Draw the best players if there are any yet
        try:
            for player in self.learning_alg.best_players:
                player.draw()
                player.ray_list.draw()
                player.reward_list.draw()
        except:
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
