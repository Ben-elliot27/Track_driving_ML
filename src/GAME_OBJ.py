"""
Edited version of the Game script st the variables and methods are attached to the player rather than the screen.

Script to run a python arcade driving game with visible 'raycasts' and checkpoints for implementing a machine learning
model to train on.

Because it uses arcade, a simple game library, it doesn't have many features such as proper raycasts so they are
implemented 'dodgily' as a series of individual objects.


"""

import math
import arcade
import numpy as np




# -----------------------------------------------------------------------------------------------------------------------


class Player(arcade.Sprite):

    def initialise(self):
        self.current_vel = 0
        self.isDead = False
        self.change_vel = 0

        # Speed limit
        self.MAX_SPEED = 3.0

        # How fast we accelerate
        self.ACCELERATION_RATE = 0.5

        # How fast the car turns
        self.TURNING_RATE = 3

        # How fast to slow down after we let off the key
        self.FRICTION = 0.07

        # Initials for rays
        self.RAY_COUNT = 8
        self.RAY_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
        self.RAY_OFFSET = 25
        self.RAY_DISTANCE = 10
        self.RAY_GAP = 10
        self.RAY_SCALING = 0.01

        #image initialsiation
        self.CAR_SPRITE_IMG = "../images/Car_sprite.png"
        self.CIRCLE_SPRITE_IMG = '../images/Circle_sprite.png'
        self.WALL_SPRITE_IMG = '../images/wall_sprite.png'
        self.SPRITE_SCALING = 0.05

        # Initials for rewards
        self.REWARD_COUNT = 8
        self.REWARD_SCALING = [.8, .8, .8, .8,
                          .8, .8, .8, .8]
        self.REWARD_X_POS = [332, 683, 950, 950,
                        770, 350, 64, 64]
        self.REWARD_Y_POS = [50, 50, 220, 400,
                        680, 680, 530, 250]
        self.REWARD_ANGLES = [90, 90, 0, 0, 90, 90, 0, 0]

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.reward_list = arcade.SpriteList(use_spatial_hash=True)  # visible = False

        # Jammy way of getting the individual rays to work
        self.RAY_DELTA_X = np.zeros((self.RAY_DISTANCE, self.RAY_COUNT))
        self.RAY_DELTA_Y = np.zeros((self.RAY_DISTANCE, self.RAY_COUNT))
        self.RAY_ANGLE_DELTA = np.zeros((self.RAY_DISTANCE, self.RAY_COUNT))

        self.ray_list = arcade.SpriteList(use_spatial_hash=True)

        self.ray_hit_list = np.array([0 for a in range(self.RAY_COUNT * self.RAY_DISTANCE)])
        self.ray_distance = np.array([10 for a in range(self.RAY_COUNT)]) #USED IN NN

        self.spawn_rewards() #Set up the first reward

        self.reward_distance = 10000 #USED IN NN

        self.reward_count = 0

        self.reward_index = 0

        self.spawn_rays()

    def spawn_rays(self):
        for i in range(self.RAY_DISTANCE):
            for a in range(self.RAY_COUNT):
                self.RAY_DELTA_X[i][a] = i * self.RAY_GAP * math.cos(np.radians(a * 45))
                self.RAY_DELTA_Y[i][a] = i * self.RAY_GAP * math.sin(np.radians(a * 45))
                self.RAY_ANGLE_DELTA[i][a] = self.RAY_ANGLES[a]
        self.RAY_DELTA_X = self.RAY_DELTA_X.flatten().tolist()
        self.RAY_DELTA_Y = self.RAY_DELTA_Y.flatten().tolist()
        self.RAY_ANGLE_DELTA = self.RAY_ANGLE_DELTA.flatten().tolist()

        for i in range(self.RAY_COUNT * self.RAY_DISTANCE):
            # Set up the rays
            self.ray_sprite = Ray(self.CIRCLE_SPRITE_IMG,
                                  self.RAY_SCALING)
            self.ray_sprite.center_x = 50
            self.ray_sprite.center_y = 50
            self.ray_sprite.angle = self.RAY_ANGLE_DELTA[i]
            self.ray_list.append(self.ray_sprite)

        self.ray_list.draw()

    def spawn_rewards(self):
        # Set up the rewards
        self.reward_sprite = Wall(self.WALL_SPRITE_IMG,
                                  self.REWARD_SCALING[0])
        self.reward_sprite.center_x = self.REWARD_X_POS[0]
        self.reward_sprite.center_y = self.REWARD_Y_POS[0]
        self.reward_sprite.angle = self.REWARD_ANGLES[0]
        self.reward_list.append(self.reward_sprite)

        self.reward_list.draw()

    def update(self):
        """
        :param wall_list: list of wall arcade objects
        :return:
        """
        #Update speed
        if self.current_vel < self.MAX_SPEED:
            self.current_vel += self.change_vel
        elif self.current_vel >= self.MAX_SPEED:
            self.current_vel = self.MAX_SPEED

        # Add some friction
        if self.current_vel > self.FRICTION:
            self.current_vel -= self.FRICTION
        elif self.current_vel < -self.FRICTION:
            self.current_vel += self.FRICTION
        else:
            self.current_vel = 0

        self.center_x += self.current_vel * math.cos(math.radians(self.angle))
        self.center_y += self.current_vel * math.sin(math.radians(self.angle))

        self.update_angle()

        self.update_ray_positions()

        self.update_rewards()


    def update_ray_positions(self):
        # Update Ray position to move with player
        for i in range(len(self.ray_list)):
            self.ray_list[i].center_x = self.center_x + self.RAY_DELTA_X[i]
            self.ray_list[i].center_y = self.center_y + self.RAY_DELTA_Y[i]
            self.ray_list[i].angle = self.angle + self.RAY_ANGLE_DELTA[i]
            self.ray_list[i].rotate_point_func(self.center_x, self.center_y,
                                               self.angle)

    def update_angle(self):
        if (self.change_x != 0 and self.change_y != 0):
            self.angle = math.degrees(math.atan(self.change_y / self.change_x))

    def update_ray_hit_list(self, wall_list):
        """
        Check which parts of the ray are touching a wall and work out distances along each ray
        """

        for wall in wall_list:
            for i in range(len(self.ray_list)):
                if arcade.check_for_collision(wall, self.ray_list[i]):
                    self.ray_hit_list[i] = 1

        ray_list = np.array(self.ray_hit_list)
        ray_list = ray_list.reshape((self.RAY_DISTANCE, self.RAY_COUNT)).T
        for i, row in enumerate(ray_list):
            indicies = row.nonzero()
            try:
                self.ray_distance[i] = indicies[0][0]
            except IndexError:
                self.ray_distance[i] = 10


    def player_movement(self, direction):
        """ Handles player movement
         input: [UP, LEFT, RIGHT]
         ie [1, 0, 0] is UP"""

        input = direction
        self.change_vel = 0

        # Apply acceleration based on the keys pressed
        if input[0] == 1:
            self.change_vel += self.ACCELERATION_RATE
        if input[1] == 1 and input[2] != 1:
            self.angle += self.TURNING_RATE
        elif input[2] == 1 and input[1] != 1:
            self.angle += -self.TURNING_RATE

    def collision_with_wall(self, wall_list):
        # Generate a list of all walls that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self,
                                                        wall_list)
        if len(hit_list) != 0:
            self.isDead = True
            self.death_sequence()
        else:
            self.isDead = False

    def death_sequence(self):
        #Function to control what happens when the player touches a wall and 'dies'
        print("isDead")

    def update_rewards(self):
        # A funcion to update the reward count of the player

        #self.reward_sprite might not be defined in right scope
        #Gets distance to the closest reward
        self.reward_distance = arcade.get_distance_between_sprites(self, self.reward_sprite)

        if arcade.check_for_collision(self, self.reward_sprite):
            self.reward_count += 1
            self.reward_index = (self.reward_index + 1) % 8
            self.reward_sprite.center_x = self.REWARD_X_POS[self.reward_index]
            self.reward_sprite.center_y =self. REWARD_Y_POS[self.reward_index]
            self.reward_sprite.angle = self.REWARD_ANGLES[self.reward_index]
            self.reward_sprite.scaling = self.REWARD_SCALING[self.reward_index]

    def add_AI(self):
        pass



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


        # Set up the player info
        self.player_sprite = None

        # Set up wall info
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
        self.spawn_player()


    def spawn_player(self):
        # Set up the player
        self.player_sprite = Player(self.CAR_SPRITE_IMG,
                                    self.SPRITE_SCALING)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)
        self.player_sprite.initialise()

        #Draw Player
        self.player_list.draw()

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
        self.player_list.draw()
        self.wall_list.draw()
        self.reward_list.draw()
        self.ray_list.draw()


        # Display text
        for player_sprite in self.player_list:
            arcade.draw_text(f"Velocity: {player_sprite.current_vel:6.3f}", 10, 50, arcade.color.BLACK)
            arcade.draw_text(f"Angle: {player_sprite.angle % 360:6.3f}", 10, 70, arcade.color.BLACK)
            arcade.draw_text(f"xPOS: {player_sprite.center_x:6.3f}", 10, 90, arcade.color.BLACK)
            arcade.draw_text(f"yPOS: {player_sprite.center_y:6.3f}", 10, 110, arcade.color.BLACK)

    def on_update(self, delta_time):
        """ Movement and game logic """

        self.player_list.update()
        for player in self.player_list:
            player.update_ray_hit_list(self.wall_list)
            player.collision_with_wall(self.wall_list)

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


