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
"""
import arcade
import arcade.gui
import pickle
import glob




from Game_Controller import MyGame
from Draw_track import Draw_track

from Wall import Wall



WALL_SPRITE_IMG = '../images/wall_2.png'
WALL_SCALING = 0.1

class Main_menu(arcade.View):
    """
    The main menu screen giving button options to go to all other screens
    """
    def __init__(self):

        super().__init__()

        self.wall_list = arcade.SpriteList()

        self.manager_1 = arcade.gui.UIManager()
        self.manager_1.enable()



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

        # Automatically load all tracks
        self.tracks = self.get_saved_tracks()

        if len(self.tracks) == 0:
            self.tracks = ["NO SAVED TRACKS"]


        self.v_box = arcade.gui.UIBoxLayout()
        self.v_box.add(self.run_game_button)
        self.v_box.add(self.draw_track_button)

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

    def on_draw(self):
        """
        Render the screen
        :return:
        """
        self.clear()

        self.manager_1.draw()

        self.wall_list.draw()


    def draw_track(self, a):
        """
        Handles what happens when the draw track button is pressed
        :return:
        """
        print("draw_track")
        self.window.show_view(Draw_track(self))

    def run_game(self, a):
        """
        Handles what happens when the run game button is pressed
        :return:
        """
        print("run game")

    def load_track(self, file):
        """
        loads the track behind the UI
        :param file: str relative directory of file
        :return:
        """
        if file == 'NO SAVED TRACKS':
            return
        f = open(file, 'rb')
        wall_dt = pickle.load(f)

        positions = []

        for wall_position in wall_dt[0]:
            positions.append(wall_position)
        for i, wall_angle in enumerate(wall_dt[1]):
            self.spawn_wall(positions[i], wall_angle)


    def spawn_wall(self, position, angle):

            self.wall_sprite = Wall(WALL_SPRITE_IMG,
                                    WALL_SCALING)
            self.wall_sprite.position = position
            self.wall_sprite.angle = angle
            self.wall_list.append(self.wall_sprite)

    def get_saved_tracks(self):
        """
        A function to get a list of the saved tracks
        :return: [str] track_list: list of directory of tracks
        """
        track_list = glob.glob('../Tracks/*')

        return track_list







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