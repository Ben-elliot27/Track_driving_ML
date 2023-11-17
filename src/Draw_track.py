"""
Handles the drawing of the track
"""

import arcade
import pickle
import numpy as np

from Wall import Wall

WALL_SPRITE_IMG = '../images/wall_sprite.png'
WALL_SCALING = 0.3
DISTANCE_BETWEEN_WALLS = 5

class Draw_track(arcade.View):

    def __init__(self):

        super().__init__()
        self.wall_list = arcade.SpriteList()
        self.wall_sprite = None
        self.draw_walls = False

        arcade.set_background_color(arcade.color.AMAZON)

    def on_show_view(self):
        """
        called when view first shown
        :return:
        """
        self.wall_list = arcade.SpriteList()
        self.wall_sprite = None
        self.draw_walls = False

        arcade.set_background_color(arcade.color.AMAZON)



    def on_draw(self):
        """
        Renders items on screen
        :return:
        """
        self.clear()
        arcade.draw_text("""Draw track \n
        press d to start drawing, \n
        press e for eraser, \n
        press S to save track""", self.window.width - 30, self.window.height - 30,
                         arcade.color.WHITE, font_size=10, anchor_x="center")
        self.wall_list.draw()

    def on_key_press(self, key, modifiers: int):
        """
        Called whenever a key is pressed
        :param key: key that was pressed
        :param modifiers:
        :return:
        """

        match key:
            case arcade.key.D:
                self.draw_walls = True

    def on_key_release(self, key, _modifiers: int):
        """
        Called whenever a key is released
        :param key:
        :param _modifiers:
        :return:
        """

        match key:
            case arcade.key.D:
                self.draw_walls = False

    def on_update(self, delta_time: float):
        pass


    def spawn_wall(self, cursor_pos: list, d_cursor_pos: list):
        """
        spawns wall at current cursor position
        :param cursor_pos: [x_pos, y_pos] of cursor
        :param d_cursor_pos: [dx, dy] change in position of cursor
        :return:
        """
        self.wall_sprite = Wall(WALL_SPRITE_IMG, scale=WALL_SCALING)

        self.wall_sprite.center_x = cursor_pos[0]
        self.wall_sprite.center_y = cursor_pos[1]

        try:
            self.wall_sprite.angle = np.arctan(d_cursor_pos[0] / d_cursor_pos[1])
        except ZeroDivisionError:
            self.wall_sprite.angle = 0

        self.wall_list.append(self.wall_sprite)

    def is_far_enough_from_other_wall(self, cursor_pos: list):
        """
        Checks if cursor is far enough from last drawn wall
        :param cursor_pos: [x_pos, y_pos] of cursor
        :return: True/False
        """
        try:
            if arcade.get_distance(cursor_pos[0], cursor_pos[1],
                                   self.wall_list[-1].center_x, self.wall_list[-1].center_y) > DISTANCE_BETWEEN_WALLS:
                return True
            else:
                return False
        except IndexError:
            # first wall not yet drawn
            return True


    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, _buttons: int, _modifiers: int):
        """
        Called when mouse dragged

        :param int x: x position of mouse
        :param int y: y position of mouse
        :param int dx: Change in x since the last time this method was called
        :param int dy: Change in y since the last time this method was called
        :param int _buttons: Which button is pressed
        :param int _modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                              pressed during this event. See :ref:`keyboard_modifiers`.
        """

        mouse_pos = [x, y]
        d_mouse_pos = [dx, dy]
        if self.is_far_enough_from_other_wall(mouse_pos):
            self.spawn_wall(mouse_pos, d_mouse_pos)




def main():
    """ Main function """
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 750
    SCREEN_TITLE = "Track learning"
    FRAME_RATE = 1/25

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.set_update_rate(FRAME_RATE)  # sets fps to FRAME_RATE
    start_view = Draw_track()
    window.show_view(start_view)
    arcade.run()

main()