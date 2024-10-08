"""
The player class for the game

"""

import arcade
import math
import numpy as np
import torch

from Ray import Ray
from Wall import Wall


MAX_ACCELERATION = 1.2
MAX_SPEED = 8.0

class Player(arcade.Sprite):

    def initialise(self, reward_list=None):
        """
        Initialises the player (needs to be called when first spawned
        Sets contants used by player as well
        :return:
        """

        # How fast the car turns
        self.TURNING_RATE = 3

        # How fast to slow down after we let off the key
        self.FRICTION = 0.08

        # Initials for rays
        self.RAY_COUNT = 12
        self.RAY_ANGLES = []
        for i in range(self.RAY_COUNT):
            self.RAY_ANGLES.append(360/self.RAY_COUNT * i)
        self.RAY_OFFSET = 25
        self.RAY_DISTANCE = 10
        self.RAY_GAP = 10
        self.RAY_SCALING = 0.01

        # image initialsiation
        self.CAR_SPRITE_IMG = "../images/Car_sprite.png"
        self.CIRCLE_SPRITE_IMG = '../images/Circle_sprite.png'
        self.WALL_SPRITE_IMG = '../images/wall_sprite.png'
        self.SPRITE_SCALING = 0.05

        # Initials for rewards
        self.reward_list = reward_list
        self.num_rewards = len(self.reward_list)
        self.current_reward_sprite = self.reward_list[0]
        self.reward_distance = 10000
        self.reward_index = 0
        self.reward_count = 0

        self.current_vel = 0
        self.isDead = False
        self.change_vel = 0

        self.isActive = False

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        # Jammy way of getting the individual rays to work
        self.RAY_DELTA_X = np.zeros((self.RAY_DISTANCE, self.RAY_COUNT))
        self.RAY_DELTA_Y = np.zeros((self.RAY_DISTANCE, self.RAY_COUNT))
        self.RAY_ANGLE_DELTA = np.zeros((self.RAY_DISTANCE, self.RAY_COUNT))

        self.ray_list = arcade.SpriteList(use_spatial_hash=True)

        self.ray_hit_list = np.array([0 for a in range(self.RAY_COUNT * self.RAY_DISTANCE)])
        self.ray_distance = np.array([10 for a in range(self.RAY_COUNT)])  # USED IN NN

        self.spawn_rays()

        self.model = None  # Attribute to set the tf model to

        # Set up cost
        self.cost = 0

        self.NN_inputs = np.array([self.current_vel / MAX_SPEED, self.angle / 360,
                                   self.reward_distance / 100].append(np.array(self.ray_distance) / 10))
        # ray distance normalising needs working on

    def spawn_rays(self):
        for i in range(self.RAY_DISTANCE):
            for a in range(self.RAY_COUNT):
                self.RAY_DELTA_X[i][a] = i * self.RAY_GAP * math.cos(np.radians(a * 360/self.RAY_COUNT))
                self.RAY_DELTA_Y[i][a] = i * self.RAY_GAP * math.sin(np.radians(a * 360/self.RAY_COUNT))
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

    def update(self):
        """
        :return:
        """
        if self.isActive:
            if self.current_vel < MAX_SPEED:
                self.current_vel += self.change_vel
            elif self.current_vel >= MAX_SPEED:
                self.current_vel = MAX_SPEED

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

            self.cost = self.update_cost()
        else:
            self.current_vel = 0

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

    def AI_movement(self):

        nn_list = [self.current_vel / MAX_SPEED, self.angle / 360, self.reward_distance / 1000]
        for dist in self.ray_distance:
            nn_list.append(dist / 10)
        self.NN_inputs = nn_list
        pred = self.model(torch.tensor(self.NN_inputs, dtype=torch.float64, device='cpu'))
        move = torch.softmax(pred, dim=0)
        move = move.detach().cpu().numpy()

        self.change_vel = move[0] * MAX_ACCELERATION
        self.change_vel = move[3] * MAX_ACCELERATION

        self.angle += move[1] * self.TURNING_RATE
        self.angle -= move[2] * self.TURNING_RATE

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
        # Function to control what happens when the player touches a wall and 'dies'
        # For now this just deatviates the player
        self.isActive = False

    def update_rewards(self):
        # A funcion to update the reward count of the player

        # self.reward_sprite might not be defined in right scope
        # Gets distance to the closest reward

        if arcade.check_for_collision(self, self.current_reward_sprite):
            self.reward_count += 1
            self.reward_index = (self.reward_index + 1) % self.num_rewards
            self.current_reward_sprite = self.reward_list[self.reward_index]

        self.reward_distance = arcade.get_distance_between_sprites(self, self.current_reward_sprite)

    def update_cost(self):
        # function to update the cost (positive good)
        # For non evolution approach - add in ray data and distance to walls into cost data
        if self.isDead:
            return -100000
        else:
            return (self.reward_count * 1000) + (1 / self.reward_distance * 100)

    def reset_reward_list(self):
        # Set up the rewards
        self.reward_index = 0
        self.current_reward_sprite = self.reward_list[0]
        self.reward_count = 0
