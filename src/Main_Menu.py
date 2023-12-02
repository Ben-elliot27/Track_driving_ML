"""
Run Game
Load track
Select learning type
Draw track

Shows currently selected track

Want to be able to display currently selected track
and have ability to change loaded track

TODO: Add functionality for when run game button pressed
TODO: Add dropdown for different tracks
TODO: Need to make it so that when a new track is selected it actually drawns the new track in background
TODO: Add ability to delete a saved track
TODO: Add selection for learning alg

"""
import arcade
import arcade.gui
import glob
import numpy as np




from Game_Controller import MyGame
from Draw_track import Draw_track

from Wall import Wall



WALL_SPRITE_IMG = '../images/wall_2.png'
WALL_SCALING = 0.1

TRACK_DIRECTORY = "../Tracks/"

class Main_menu(arcade.View):
    """
    The main menu screen giving button options to go to all other screens
    """
    def __init__(self):

        super().__init__()

        self.wall_list = arcade.SpriteList()

        # Automatically load all tracks
        self.tracks = self.get_saved_tracks()

        if len(self.tracks) == 0:
            self.tracks = ["NO SAVED TRACKS"]

        self.current_selected_track = self.tracks[0]

        self.track_select = False


        self.reward_list = arcade.SpriteList()
        self.player_spawn_pos = ['x', 'y']

        self.track_dt = [self.wall_list, self.reward_list, self.player_spawn_pos]

        # --------------------------------------------- GUI ------------------------------------------------------------

        self.manager_1 = arcade.gui.UIManager()
        self.manager_1.enable()

        self.manager_2 = arcade.gui.UIManager()
        self.manager_2.disable()

        self.run_game_button = arcade.gui.UIFlatButton(
          color=arcade.color.DARK_BLUE_GRAY,
          text='Run Game',
          width=400,
          height=200,
          x=self.window.width/2,
          y=self.window.height/2)
        self.run_game_button.on_click = self.run_game

        self.draw_track_button = arcade.gui.UIFlatButton(
          color=arcade.color.DARK_BLUE_GRAY,
          text='Draw a new track',
          width=400,
          height=200,
          x=self.window.width/2,
          y=self.window.height/2)
        self.draw_track_button.on_click = self.draw_track

        self.edit_track_button = arcade.gui.UIFlatButton(
          color=arcade.color.DARK_BLUE_GRAY,
          text='Edit currently loaded track',
          width=400,
          height=200,
          x=self.window.width/2,
          y=self.window.height/2)
        self.edit_track_button.on_click = self.edit_track

        self.load_new_track_button = arcade.gui.UIFlatButton(
          color=arcade.color.DARK_YELLOW,
          text='LOAD A DIFFERENT TRACK',
          width=200,
          height=100,
          x=self.window.width/2,
          y=self.window.height/2)
        self.load_new_track_button.on_click = self.load_diff_track



        self.v_box = arcade.gui.UIBoxLayout()
        self.v_box.add(self.run_game_button)
        self.v_box.add(self.draw_track_button)
        self.v_box.add(self.edit_track_button)
        self.v_box.add(self.load_new_track_button)



        self.manager_1.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

        arcade.set_background_color(arcade.color.ASH_GREY)

    def on_show_view(self):
        """
        When view is first shown
        :return:
        """
        # Automatically load all tracks
        self.tracks = self.get_saved_tracks()
        if len(self.tracks) == 0:
            self.tracks = ["NO SAVED TRACKS"]
        # When view first shown, load the first track in background
        self.load_track(self.tracks[0])
        self.track_dt = [self.wall_list, self.reward_list, self.player_spawn_pos]

        # Enable UI manager
        self.manager_1.enable()

        arcade.set_background_color(arcade.color.ASH_GREY)

    def on_draw(self):
        """
        Render the screen
        :return:
        """
        self.clear()

        self.wall_list.draw()
        self.reward_list.draw()

        arcade.draw_text(f"Current selected track {self.current_selected_track[len(TRACK_DIRECTORY):]}",
                         self.window.width - 100, self.window.height - 30,
                         arcade.color.WHITE, font_size=10, anchor_x="center")

        if self.track_select:
            self.manager_2.draw()
        else:
            self.manager_1.draw()



    def draw_track(self, a):
        """
        Handles what happens when the draw track button is pressed
        :param a:
        :return:
        """
        self.window.show_view(Draw_track(self))
    def edit_track(self, a):
        """
        Handles what happens when the edit track button is pressed
        :param a:
        :return:
        """
        self.window.show_view(Draw_track(self, self.track_dt))

    def run_game(self, a):
        """
        Handles what happens when the run game button is pressed
        :return:
        """
        self.window.show_view(MyGame(self, self.track_dt))

    def load_track(self, file):
        """
        loads the track behind the UI
        :param file: str relative directory of file
        :return:
        """
        if file == 'NO SAVED TRACKS':
            return
        self.wall_list, self.reward_list, self.player_spawn_pos = Draw_track.load_track(file)


    def get_saved_tracks(self):
        """
        A function to get a list of the saved tracks
        :return: [str] track_list: list of directory of tracks
        """
        track_list = glob.glob(f'{TRACK_DIRECTORY}/*')

        return track_list

    def load_diff_track(self, a):
        """
        Load a different track when button clicked -----------------------------------------------------------------
        :return:
        """
        self.manager_1.disable()
        self.track_select = True
        self.manager_2.enable()

        self.tracks = self.get_saved_tracks()

        buttons = []  # list of buttons
        self.v_box2 = arcade.gui.UIBoxLayout()

        if len(self.tracks) == 0:
            # No saved tracks
            print('No saved tracks')  # TODO: Add a proper feature for this rather than just printing to console
        else:
            for i, track in enumerate(self.tracks):
                buttons.append(arcade.gui.UIFlatButton(
                    color=arcade.color.GRAPE,
                    text=f'{track[len(TRACK_DIRECTORY):]}',
                    x=self.window.width / 2,
                    y=self.window.height / 2,
                    width=400,
                    height=self.window.height / len(self.tracks) - 40))
                buttons[i].on_click = self.on_change_track

                self.v_box2.add(buttons[i])

            self.manager_2.add(
                arcade.gui.UIAnchorWidget(
                    child=self.v_box2)
            )

    def on_change_track(self, event):
        """
        Handles what happens when a track button is pressed
        :param event: The onclick event
        :return:
        """
        track = (f"{TRACK_DIRECTORY}{event.source.text}")
        self.manager_1.enable()
        self.track_select = False
        self.manager_2.disable()
        self.load_track(track)
        self.current_selected_track = track
        self.track_dt = [self.wall_list, self.reward_list, self.player_spawn_pos]









    def on_hide_view(self):
        """
        Called when view is hidden
        :return:
        """
        self.manager_1.disable()
        self.manager_2.disable()











def main():
    """ Main function """
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 750
    SCREEN_TITLE = "Track learning"
    FRAME_RATE = 1/25

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.set_update_rate(FRAME_RATE)  # sets fps to FRAME_RATE
    menu_view = Main_menu()
    window.show_view(menu_view)
    arcade.run()


main()