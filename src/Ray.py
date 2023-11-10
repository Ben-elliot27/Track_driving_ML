"""
Ray class for the game
"""
import arcade
class Ray(arcade.Sprite):

    def update(self):
        pass

    def rotate_point_func(self, point_x, point_y, deg):
        self.position = arcade.rotate_point(
            self.center_x, self.center_y,
            point_x, point_y, deg)

