"""
Script to run a python arcade driving game with visible 'raycasts' and checkpoints for implementing a machine learning
model to train on. Currently cannot hold turn button to turn as thought this was a better setup for the NN model.

Because it uses arcade, a simple game library, it doesn't have many features such as proper raycasts so they are
implemented 'dodgily' as a series of individual objects.

Global variables saved from script:
ray_hit_list: list of rays colliding with a wall
ray_distance: distance along ray to collision with wall
game_window: the arcade game window object
DEAD: whether player has collided with wall
closest_reward: distance to closest reward to player
player_angle: current angle of the player
REWARD_INDEX: index in list of the reward
reward_count: total number of rewards
score_total: total number of rewards collected
"""

import math

import GLOBALS
import arcade
import numpy as np

import os
import pathlib

CAR_SPRITE_IMG = "../images/Car_sprite.png"
CIRCLE_SPRITE_IMG = '../images/Circle_sprite.png'
WALL_SPRITE_IMG = '../images/wall_sprite.png'


SPRITE_SCALING = 0.05

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
SCREEN_TITLE = "Track learning"

# Important constants

# Speed limit
MAX_SPEED = 3.0

# How fast we accelerate
ACCELERATION_RATE = 0.5

# How fast the car turns
TURNING_RATE = 3

# How fast to slow down after we let off the key
FRICTION = 0.07

# Initials for walls
WALL_COUNT = 8
WALL_SCALING = [5.7, 4.1, 5.6, 4.1,
                4.2, 2.9, 4.2, 2.9]
X_POS = [490, 995, 490, 10,
         490, 995 - 120, 485, 10 + 120]
Y_POS = [10, 365, 730, 365,
         10 + 120, 365, 740 - 120, 365]
WALL_ANGLES = [0, 90, 0, 90, 0, 90, 0, 90]

# Initials for rewards
REWARD_COUNT = 8
REWARD_SCALING = [.8, .8, .8, .8,
                  .8, .8, .8, .8]
REWARD_X_POS = [332, 683, 950, 950,
                770, 350, 64, 64]
REWARD_Y_POS = [50, 50, 220, 400,
                680, 680, 530, 250]
REWARD_ANGLES = [90, 90, 0, 0, 90, 90, 0, 0]

# Initials for rays
RAY_COUNT = 8
RAY_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
RAY_OFFSET = 25
RAY_DISTANCE = 10
RAY_GAP = 10
RAY_SCALING = 0.01

DEAD = False

global params

# Initialise global variables
GLOBALS.init()
GLOBALS.ray_hit_list = np.array([0 for a in range(RAY_COUNT * RAY_DISTANCE)])
GLOBALS.ray_distance = np.array([10 for a in range(RAY_COUNT)])


# -----------------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------------


class Player(arcade.Sprite):

    def initialise(self):
        self.current_vel = 0
        self.isDead = False
        self.change_vel = 0

    def update(self):

        self.current_vel += self.change_vel

        # Vcos(theta)
        self.center_x += self.current_vel * math.cos(math.radians(self.angle))
        self.center_y += self.current_vel * math.sin(math.radians(self.angle))

        # Check to see if we hit the screen edge
        if self.left < 0:
            self.left = 0
            self.change_x = 0  # Zero x speed
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1
            self.change_x = 0

        if self.bottom < 0:
            self.bottom = 0
            self.change_y = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1
            self.change_y = 0

        if (self.change_x != 0 and self.change_y != 0):
            self.angle = math.degrees(math.atan(self.change_y / self.change_x))

    def player_movement(self, direction):
        """ Handles player movement
         input: [UP, LEFT, RIGHT]"""
        input = direction
        self.change_vel = 0

        # Add some friction
        if self.current_vel > FRICTION:
            self.current_vel -= FRICTION
        elif self.current_vel < -FRICTION:
            self.current_vel += FRICTION
        else:
            self.current_vel = 0

        # Apply acceleration based on the keys pressed
        if input[0] == 1:
            self.change_vel += ACCELERATION_RATE
        if input[1] == 1 and input[2] != 1:
            self.angle += TURNING_RATE
        elif input[2] == 1 and input[1] != 1:
            self.angle += -TURNING_RATE

        if self.current_vel > MAX_SPEED:
            self.current_vel = MAX_SPEED
        elif self.current_vel < -MAX_SPEED:
            self.current_vel = -MAX_SPEED

    def collision_with_wall(self):
        # Generate a list of all walls that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                        self.wall_list)
        if len(hit_list) != 0:
            self.isDead = True
        else:
            self.isDead = False


# -----------------------------------------------------------------------------------------------------------------------
class Wall(arcade.Sprite):

    def update(self):
        pass


# -----------------------------------------------------------------------------------------------------------------------

class Ray(arcade.Sprite):

    def update(self):
        pass

    def rotate_point_func(self, point_x, point_y, deg):
        self.position = arcade.rotate_point(
            self.center_x, self.center_y,
            point_x, point_y, deg)


# -----------------------------------------------------------------------------------------------------------------------

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        """
        Initializer
        """

        # Call the parent class initializer
        super().__init__(width, height, title)

        # Variables that will hold sprite lists
        self.player_list = None
        self.wall_list = None
        self.reward_list = None
        self.ray_list = None

        # Set up the player info
        self.player_sprite = None

        # Set up wall info
        self.wall_sprite = None
        self.reward_sprite = None
        self.ray_sprite = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        # Jammy way of getting the individual rays to work
        self.RAY_DELTA_X = np.zeros((RAY_DISTANCE, RAY_COUNT))
        self.RAY_DELTA_Y = np.zeros((RAY_DISTANCE, RAY_COUNT))
        self.RAY_ANGLE_DELTA = np.zeros((RAY_DISTANCE, RAY_COUNT))

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.reward_list = arcade.SpriteList(use_spatial_hash=True)  # visible = False
        self.ray_list = arcade.SpriteList()  # visible = False

        # Set up the player
        self.player_sprite = Player(CAR_SPRITE_IMG,
                                    SPRITE_SCALING)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)
        self.player_sprite.initialise()

        for i in range(WALL_COUNT):
            # Set up the wall
            self.wall_sprite = Wall(WALL_SPRITE_IMG,
                                    WALL_SCALING[i])
            self.wall_sprite.center_x = X_POS[i]
            self.wall_sprite.center_y = Y_POS[i]
            self.wall_sprite.angle = WALL_ANGLES[i]
            self.wall_list.append(self.wall_sprite)

        # Set up the rewards
        self.reward_sprite = Wall(WALL_SPRITE_IMG,
                                  REWARD_SCALING[0])
        self.reward_sprite.center_x = REWARD_X_POS[0]
        self.reward_sprite.center_y = REWARD_Y_POS[0]
        self.reward_sprite.angle = REWARD_ANGLES[0]
        self.reward_list.append(self.reward_sprite)

        for i in range(RAY_DISTANCE):
            for a in range(RAY_COUNT):
                self.RAY_DELTA_X[i][a] = i * RAY_GAP * math.cos(np.radians(a * 45))
                self.RAY_DELTA_Y[i][a] = i * RAY_GAP * math.sin(np.radians(a * 45))
                self.RAY_ANGLE_DELTA[i][a] = RAY_ANGLES[a]
        self.RAY_DELTA_X = self.RAY_DELTA_X.flatten().tolist()
        self.RAY_DELTA_Y = self.RAY_DELTA_Y.flatten().tolist()
        self.RAY_ANGLE_DELTA = self.RAY_ANGLE_DELTA.flatten().tolist()

        for i in range(RAY_COUNT * RAY_DISTANCE):
            # Set up the rays
            self.ray_sprite = Ray(CIRCLE_SPRITE_IMG,
                                  RAY_SCALING)
            self.ray_sprite.center_x = 50
            self.ray_sprite.center_y = 50
            self.ray_sprite.angle = self.RAY_ANGLE_DELTA[i]
            self.ray_list.append(self.ray_sprite)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.player_list.draw()
        self.wall_list.draw()
        self.reward_list.draw()
        self.ray_list.draw()

        # Display text
        arcade.draw_text(f"Velocity: {GLOBALS.current_vel:6.3f}", 10, 50, arcade.color.BLACK)
        arcade.draw_text(f"Angle: {self.player_sprite.angle % 360:6.3f}", 10, 70, arcade.color.BLACK)
        arcade.draw_text(f"xPOS: {self.player_sprite.center_x:6.3f}", 10, 90, arcade.color.BLACK)
        arcade.draw_text(f"yPOS: {self.player_sprite.center_y:6.3f}", 10, 110, arcade.color.BLACK)
        # arcade.draw_text(f"yPOS: {GLOBALS.ray_distance}", 10, 110, arcade.color.BLACK)

    def on_update(self, delta_time):
        """ Movement and game logic """

        self.player_list.update()

        # Check which rays are touching a wall
        self.ray_detection()

        # Update Ray position to move with player
        for i in range(len(self.ray_list)):
            self.ray_list[i].center_x = self.player_list[0].center_x + self.RAY_DELTA_X[i]
            self.ray_list[i].center_y = self.player_list[0].center_y + self.RAY_DELTA_Y[i]
            self.ray_list[i].angle = self.player_list[0].angle + self.RAY_ANGLE_DELTA[i]
            self.ray_list[i].rotate_point_func(self.player_sprite.center_x, self.player_sprite.center_y,
                                               self.player_list[0].angle)

        # Get distance to nearest reward
        GLOBALS.closest_reward = arcade.get_distance_between_sprites(self.player_list[0], self.reward_sprite)

        # Check if reward is hit
        if arcade.check_for_collision(self.player_sprite, self.reward_sprite):
            GLOBALS.reward_count += 1
            GLOBALS.score_total += 1
            GLOBALS.REWARD_INDEX = (GLOBALS.REWARD_INDEX + 1) % 8
            self.reward_sprite.center_x = REWARD_X_POS[GLOBALS.REWARD_INDEX]
            self.reward_sprite.center_y = REWARD_Y_POS[GLOBALS.REWARD_INDEX]
            self.reward_sprite.angle = REWARD_ANGLES[GLOBALS.REWARD_INDEX]
            self.reward_sprite.scaling = REWARD_SCALING[GLOBALS.REWARD_INDEX]

        GLOBALS.ray_hit_list = [0 for a in range(RAY_COUNT * RAY_DISTANCE)]

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.player_sprite.player_movement([1, 0, 0])
        elif key == arcade.key.LEFT:
            self.player_sprite.player_movement([0, 1, 0])
        elif key == arcade.key.RIGHT:
            self.player_sprite.player_movement([0, 0, 1])

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.player_movement([0, 0, 0])

    def AI_setup(self):
        """ SET UP AND INSTANTIATE THE AI PART"""
        pass

    def ray_detection(self):
        """
        Check which parts of the ray are touching a wall and work out distances along each ray
        """
        for wall in self.wall_list:
            for i in range(len(self.ray_list)):
                if arcade.check_for_collision(wall, self.ray_list[i]):
                    GLOBALS.ray_hit_list[i] = 1

        ray_list = np.array(GLOBALS.ray_hit_list)
        ray_list = ray_list.reshape((RAY_DISTANCE, RAY_COUNT)).T
        for i, row in enumerate(ray_list):
            indicies = row.nonzero()
            try:
                GLOBALS.ray_distance[i] = indicies[0][0]
            except IndexError:
                GLOBALS.ray_distance[i] = 10


def main():
    """ Main function """
    GLOBALS.game_window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    GLOBALS.game_window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

# --------------------------------------------------------------------------------------
