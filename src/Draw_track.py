"""
Handles the drawing of the track

TODO: Add ability to edit a previously saved track
"""
import time

import arcade
import arcade.gui
import pickle
import numpy as np



from Wall import Wall

WALL_SPRITE_IMG = '../images/wall_2.png'
WALL_SCALING = 0.1
WALL_WIDTH = 0.5
DISTANCE_BETWEEN_WALLS = 10

RUBBER_SPRITE_IMG = '../images/rubber_sprite.png'
RUBBER_INIT_SCALE = 0.05
RUBBER_SCALING = 0.005

class Draw_track(arcade.View):

    def __init__(self):

        super().__init__()

        self.wall_list = arcade.SpriteList()
        self.wall_sprite = None
        self.draw_walls = False
        self.erase_walls = False
        self.save = False

        self.rubber_sprite = Wall(RUBBER_SPRITE_IMG, scale=RUBBER_INIT_SCALE)
        self.rubber_sprite.visible = False

        # --------------------------------------------- GUI ------------------------------------------------------------

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.file_name_box = arcade.gui.UIInputText(
            x=self.window.width/2,
            y=self.window.height/2,
            width = 300,
            height = 50,
            text = "Enter File name",
            font_name = ('Arial',),
            font_size = 18,
            text_color = arcade.color.WHITE)

        # Create a button
        self.submit_file_button = arcade.gui.UIFlatButton(
          color=arcade.color.DARK_BLUE_GRAY,
          text='Submit',
          width=90,
          height=40,
          x=self.window.height/2 + 100,
          y=self.window.height/2)
        self.submit_file_button.on_click = self.submit_file_on_click

        self.v_box = arcade.gui.UIBoxLayout()
        self.v_box.add(self.file_name_box)
        self.v_box.add(self.submit_file_button)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

        arcade.set_background_color(arcade.color.AMAZON)

    def on_show_view(self):
        """
        called when view first shown
        :return:
        """
        self.wall_list = arcade.SpriteList()
        self.wall_sprite = None
        self.draw_walls = False

        self.rubber_sprite.visible = False

        arcade.set_background_color(arcade.color.AMAZON)



    def on_draw(self):
        """
        Renders items on screen
        :return:
        """
        self.clear()

        arcade.draw_text("press d to start drawing", self.window.width - 90, self.window.height - 30,
                         arcade.color.WHITE, font_size=10, anchor_x="center")
        arcade.draw_text("press e for eraser,", self.window.width - 90, self.window.height - 50,
                         arcade.color.WHITE, font_size=10, anchor_x="center")
        arcade.draw_text("press S to save track", self.window.width - 90, self.window.height - 70,
                         arcade.color.WHITE, font_size=10, anchor_x="center")

        if self.draw_walls:
            arcade.draw_text(f"Mode: Drawing", 10, self.window.height - 30,
                             arcade.color.WHITE, font_size=10, anchor_x="left")
        elif self.erase_walls:
            arcade.draw_text(f"Mode: Erasing", 10, self.window.height - 30,
                             arcade.color.WHITE, font_size=10, anchor_x="left")
            arcade.draw_text(f"Press UP/DOWN arrow keys to adjust eraser size", 10, self.window.height - 50,
                             arcade.color.WHITE, font_size=10, anchor_x="left")
        if self.save:
            self.manager.draw()
            arcade.draw_text(f"Press BACKSLASH to exit saving mode", 10, self.window.height - 30,
                             arcade.color.WHITE, font_size=10, anchor_x="left")



        self.wall_list.draw()
        self.rubber_sprite.draw()

    def on_key_press(self, key, modifiers: int):
        """
        Called whenever a key is pressed
        :param key: key that was pressed
        :param modifiers:
        :return:
        """
        if not self.save:
            match key:
                case arcade.key.D:
                    # draw
                    self.erase_walls = False
                    self.rubber_sprite.visible = False
                    self.draw_walls = not self.draw_walls
                case arcade.key.E:
                    # erase
                    self.draw_walls = False
                    self.rubber_sprite.visible = not self.rubber_sprite.visible
                    self.erase_walls = not self.erase_walls
                case arcade.key.UP:
                    # make rubber bigger
                    self.rubber_sprite.scale += RUBBER_SCALING
                case arcade.key.DOWN:
                    # make rubber smaller
                    self.rubber_sprite.scale -= RUBBER_SCALING
                case arcade.key.S:
                    # save current track
                    self.erase_walls = False
                    self.draw_walls = False
                    self.save = True

        elif key == arcade.key.BACKSLASH:
            # Turn of saving mode
            self.save = False




    def on_update(self, delta_time: float):
        pass


    def spawn_wall(self, cursor_pos: list):
        """
        spawns wall at current cursor position
        :param cursor_pos: [x_pos, y_pos] of cursor
        :return:
        """
        self.wall_sprite = Wall(WALL_SPRITE_IMG, scale=WALL_SCALING)

        self.wall_sprite.center_x = cursor_pos[0]
        self.wall_sprite.center_y = cursor_pos[1]

        try:
            last_wall = self.wall_list[-1]
            last_end_x = last_wall.center_x + np.cos(np.degrees(last_wall.angle)) * WALL_WIDTH
            last_end_y = last_wall.center_y + np.sin(np.degrees(last_wall.angle)) * WALL_WIDTH

            del_x = np.array(self.wall_sprite.center_x - last_end_x)
            del_y = np.array(self.wall_sprite.center_y - last_end_y)

            self.wall_sprite.angle = np.arctan2(del_y, del_x) * 180/np.pi
        except IndexError:

            #zero division or index error
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




    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, _modifiers: int):
        """
        Called when mouse dragged

        :param int x: x position of mouse
        :param int y: y position of mouse
        :param int dx: Change in x since the last time this method was called
        :param int dy: Change in y since the last time this method was called
        :param int buttons: Which button is pressed
        :param int _modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                              pressed during this event. See :ref:`keyboard_modifiers`.
        """
        if self.draw_walls:
            mouse_pos = [x, y]
            if self.is_far_enough_from_other_wall(mouse_pos):
                self.spawn_wall(mouse_pos)

        elif self.erase_walls:
            self.eraser(mouse_pos=[x, y])

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """
        Called every time mouse moves

        :param int x: x position of mouse
        :param int y: y position of mouse
        :param int dx: Change in x since the last time this method was called
        :param int dy: Change in y since the last time this method was called
        """

        if self.erase_walls:
            self.rubber_sprite.position = (x, y)


    def save_track(self, name):
        """
        Saves the current track (by saving the positions of the walls as a pickle dump)
        SAVES IT IN FORM [[(x1, y1), (x2, y2), ...], [36, 45, ...]]
        :param name: name of the file
        :return:
        """


        wall_positions = []  # list of tuples of position
        wall_angles = []  # list of wall angles
        for wall in self.wall_list:
            wall_positions.append(wall.position)
            wall_angles.append(wall.angle)
        f = open(f'../Tracks/{name}', 'wb')
        pickle.dump([wall_positions, wall_angles], f)
        f.close()
        self.submit_file_button.text = "Saved"

        time.sleep(0.3)

        self.save = False


    def eraser(self, mouse_pos):
        """
        An eraser to erase current pieces of placed track
        Spawns a rubber sprite
        any wall colliding with the rubber sprite is deleted
        can make rubber bigger or lower with certain keys
        :return:
        """

        self.rubber_sprite.position = tuple(mouse_pos)

        delete_list = arcade.check_for_collision_with_list(self.rubber_sprite, self.wall_list)
        for wall in delete_list:
            self.wall_list.remove(wall)

    def submit_file_on_click(self, a):
        """
        Handles when the submit file name button is pressed
        :return:
        """
        print(a)
        name = self.file_name_box.text
        self.save_track(name)










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