"""
Handles the drawing of the track

Pyglet 2.0 dev 23
Arcade 2.6.17

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

ROTATION = 5
REWARD_IMG = '../images/reward_gate.png'
REWARD_INIT_SCALE = 0.2

class Draw_track(arcade.View):

    def __init__(self, Main_Menu, track=None):
        # Main_Menu: The main menu object
        # Track: [wall_list, reward_list, player_spawn_pos]
        # If wanted to edit a previously saved track, otherwise draw fresh track

        super().__init__()

        self.Main_menu = Main_Menu

        if track:
            self.wall_list = track[0]
            self.reward_list = track[1]
            self.player_spawn_pos = track[2]
        else:
            self.wall_list = arcade.SpriteList()
            self.reward_list = arcade.SpriteList()
            self.player_spawn_pos = ['x', 'y']

        self.wall_sprite = None



        self.setting = None  # Holds information about current selected mode
        # OPTIONS: draw_walls, erase_walls, place_rewards, place_player, save


        self.rubber_sprite = Wall(RUBBER_SPRITE_IMG, scale=RUBBER_INIT_SCALE)
        self.rubber_sprite.visible = False

        self.reward_sprite = Wall(REWARD_IMG, scale=REWARD_INIT_SCALE)

        # --------------------------------------------- GUI ------------------------------------------------------------

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.file_name_box = arcade.gui.UIInputText(
            x=self.window.width/2,
            y=self.window.height/2,
            width = 300,
            height = 50,
            text = "Enter File name",
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

        self.setting = None

        self.rubber_sprite.visible = False

        self.manager.enable()

        arcade.set_background_color(arcade.color.AMAZON)



    def on_draw(self):
        """
        Renders items on screen
        :return:
        """
        self.clear()

        arcade.draw_text("press d to start drawing walls", self.window.width - 110, self.window.height - 30,
                         arcade.color.WHITE, font_size=10, anchor_x="center")
        arcade.draw_text("press e for eraser,", self.window.width - 110, self.window.height - 50,
                         arcade.color.WHITE, font_size=10, anchor_x="center")
        arcade.draw_text("press S to save track", self.window.width - 110, self.window.height - 70,
                         arcade.color.WHITE, font_size=10, anchor_x="center")
        arcade.draw_text("press r to place reward gates", self.window.width - 110, self.window.height - 90,
                         arcade.color.WHITE, font_size=10, anchor_x="center")
        arcade.draw_text("press p to place player spawn point", self.window.width - 110, self.window.height - 110,
                         arcade.color.WHITE, font_size=10, anchor_x="center")
        arcade.draw_text("press ESC to return to main menu", self.window.width - 110, self.window.height - 130,
                         arcade.color.WHITE, font_size=10, anchor_x="center")

        if self.setting == 'draw_walls':
            arcade.draw_text(f"Mode: Drawing", 10, self.window.height - 30,
                             arcade.color.WHITE, font_size=10, anchor_x="left")
        elif self.setting == 'erase_walls':
            arcade.draw_text(f"Mode: Erasing", 10, self.window.height - 30,
                             arcade.color.WHITE, font_size=10, anchor_x="left")
            arcade.draw_text(f"Press UP/DOWN arrow keys to adjust eraser size", 10, self.window.height - 50,
                             arcade.color.WHITE, font_size=10, anchor_x="left")
        elif self.setting == 'place_rewards':
            arcade.draw_text(f"Mode: Reward placement", 10, self.window.height - 30,
                             arcade.color.WHITE, font_size=10, anchor_x="left")
            arcade.draw_text(f"Press RIGHT/LEFT arrow keys to rotate reward gate", 10, self.window.height - 50,
                             arcade.color.WHITE, font_size=10, anchor_x="left")
        elif self.setting == 'place_player':
            arcade.draw_text(f"Mode: Player spawn", 10, self.window.height - 30,
                             arcade.color.WHITE, font_size=10, anchor_x="left")
        if self.setting == 'save':
            self.manager.draw()
            arcade.draw_text(f"Press BACKSLASH to exit saving mode", 10, self.window.height - 30,
                             arcade.color.WHITE, font_size=10, anchor_x="left")



        self.wall_list.draw()
        self.rubber_sprite.draw()
        if self.setting == 'place_rewards':
            self.reward_sprite.draw()
        self.reward_list.draw()

    def on_key_press(self, key, modifiers: int):
        """
        Called whenever a key is pressed
        :param key: key that was pressed
        :param modifiers:
        :return:
        """
        if not self.setting == 'save':
            match key:
                case arcade.key.D:
                    # draw
                    self.setting = 'draw_walls'
                    self.rubber_sprite.visible = False
                case arcade.key.E:
                    # erase
                    self.setting = 'erase_walls'
                    self.rubber_sprite.visible = True
                case arcade.key.UP:
                    # make rubber bigger
                    self.rubber_sprite.scale += RUBBER_SCALING
                case arcade.key.DOWN:
                    # make rubber smaller
                    self.rubber_sprite.scale -= RUBBER_SCALING
                case arcade.key.RIGHT:
                    # Rotate reward gate
                    self.reward_sprite.angle -= ROTATION
                case arcade.key.LEFT:
                    self.reward_sprite.angle += ROTATION
                case arcade.key.S:
                    # save current track
                    self.rubber_sprite.visible = False
                    self.setting = 'save'
                case arcade.key.ESCAPE:
                    # Return to main menu
                    self.window.show_view(self.Main_menu)
                case arcade.key.P:
                    # Place player
                    self.rubber_sprite.visible = False
                    self.setting = 'place_player'
                case arcade.key.R:
                    # Place rewards
                    self.rubber_sprite.visible = False
                    self.setting = 'place_rewards'

        elif key == arcade.key.BACKSLASH:
            # Turn of saving mode
            self.rubber_sprite.visible = False
            self.setting = None
        elif key == arcade.key.ESCAPE:
            self.window.show_view(self.Main_menu)




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
            #  zero division or index error
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
        if self.setting == 'draw_walls':
            mouse_pos = [x, y]
            if self.is_far_enough_from_other_wall(mouse_pos):
                self.spawn_wall(mouse_pos)

        elif self.setting == 'erase_walls':
            self.eraser(mouse_pos=[x, y])


    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """
        Called every time mouse moves

        :param int x: x position of mouse
        :param int y: y position of mouse
        :param int dx: Change in x since the last time this method was called
        :param int dy: Change in y since the last time this method was called
        """

        if self.setting == 'erase_walls':
            self.rubber_sprite.position = (x, y)
        elif self.setting == 'place_rewards':
            self.reward_sprite.position = (x, y)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """
        Called whenever mouse is clicked
        :param x:
        :param y:
        :param button:
        :param modifiers:
        :return:
        """
        if self.setting == 'place_rewards':
            self.place_reward()
        elif self.setting == 'place_player':
            self.player_spawn_pos = [x, y]



    def save_track(self, name):
        """
        Saves the current track (by saving the positions of the walls, rewards and starting player position
         as a pickle dump
          [[wall_list_position, wall_position_angle], [reward_list_position, reward_list_angle], [x_player, y_player])
        Can't pickle the objects themselves as an arcade.spritelist() of sprite objects which is unpickle-able
        :param name: name of the file
        :return:
        """
        wall_dt = []
        for wall in self.wall_list:
            wall_dt.append([wall.position, wall.angle])

        reward_dt = []
        for reward in self.reward_list:
            reward_dt.append([reward.position, reward.angle])

        saved_dt = [wall_dt, reward_dt, self.player_spawn_pos]

        f = open(f'../Tracks/{name}', 'wb')
        pickle.dump(saved_dt, f)
        f.close()
        self.submit_file_button.text = "Saved"

        time.sleep(0.3)

        self.setting = None


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
        delete_list_2 = arcade.check_for_collision_with_list(self.rubber_sprite, self.reward_list)

        for wall in delete_list:
            self.wall_list.remove(wall)

        for reward in delete_list_2:
            self.reward_list.remove(reward)

    def submit_file_on_click(self, a):
        """
        Handles when the submit file name button is pressed
        :return:
        """
        name = self.file_name_box.text
        self.save_track(name)

    def place_reward(self):
        """
        Places a reward where the user clicked
        :return:
        """
        new_reward = Wall(REWARD_IMG, REWARD_INIT_SCALE)
        new_reward.position = self.reward_sprite.position
        new_reward.angle = self.reward_sprite.angle
        self.reward_list.append(new_reward)

    def on_hide_view(self):
        """
        Called when view is closed
        :return:
        """
        self.manager.disable()

    @staticmethod
    def load_track(file):
        """
        Loads a track given the file name
        :param: str file: directory of file to load track from
        :return: [wall_list, reward_list, player_spawn_pos]
        """
        wall_list = arcade.SpriteList()
        reward_list = arcade.SpriteList()

        f = open(file, 'rb')
        try:
            track_dt = pickle.load(f)

            f.close()

            for wall_dt in track_dt[0]:
                wall_sprite = Wall(WALL_SPRITE_IMG, scale=WALL_SCALING)
                wall_sprite.position = wall_dt[0]
                wall_sprite.angle = wall_dt[1]
                wall_list.append(wall_sprite)

            for reward_dt in track_dt[1]:
                reward_sprite = Wall(REWARD_IMG, REWARD_INIT_SCALE)
                reward_sprite.position = reward_dt[0]
                reward_sprite.angle = reward_dt[1]
                reward_list.append(reward_sprite)
        except EOFError:
            # Ran out of data or file empty
            return [wall_list, reward_list, [0, 0]]

        return [wall_list, reward_list, track_dt[2]]











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



