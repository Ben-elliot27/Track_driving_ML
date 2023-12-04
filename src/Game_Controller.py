"""
Main game class - handles running of arcade and window as well as setting up sprite_lists

Because it uses arcade, a simple game library, it doesn't have many features such as proper ray-casts, so they are
implemented 'dodgily' as a series of individual objects.

TODO: add loading of a previous model to a UI element + loading of track
TODO: make it so you can leave the game view and go back to main menu

"""

import arcade

from Evolution_learning import Evolution_learning
from Player import Player
from Wall import Wall
import pickle
from Draw_track import Draw_track
import arcade.gui
import glob


LEARNING_METHOD_Options = ["evolution"]
FRAME_RATE = 1 / 20  # 20 fps

UPDATE_FREQ = 3  # Frames per NN ran to get new movement



MENUS = ['main_menu', 'alg_selector', 'NN_selector']


class MyGame(arcade.View):
    """
    Main application class.
    """

    def __init__(self, MainMenu, track=None):

        # Call the parent class initializer
        super().__init__()

        self.Main_Menu = MainMenu
        self.LEARNING_METHOD = None  # Method by which the AI will be trained

        self.NN_to_use = 'NONE'  # The NN to be used in simulation

        if track:
            self.wall_list = track[0]
            self.reward_list = track[1]
            self.player_spawn_pos = track[2]

        else:
            self.window.show_view(self.Main_Menu)

        # Variables that will hold sprite lists
        self.player_list = arcade.SpriteList()

        # Set up the player, wall, ray info
        self.player_sprite = None

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        self.update_freq_count = 0  # Counter

        # image initialization
        self.CAR_SPRITE_IMG = "../images/Car_sprite.png"
        self.CIRCLE_SPRITE_IMG = '../images/Circle_sprite.png'
        self.WALL_SPRITE_IMG = '../images/wall_sprite.png'
        self.PLAYER_SCALING = 0.05

        # --------------------------------------------- GUI ------------------------------------------------------------

        # SCREEN 1
        self.manager_1 = arcade.gui.UIManager()
        self.manager_1.enable()
        self.menu_setting = MENUS[0]

        self.select_learn_alg_button = arcade.gui.UIFlatButton(
          color=arcade.color.DARK_BLUE_GRAY,
          text='Select learning algorithm',
          width=400,
          height=200,
          x=self.window.width/2,
          y=self.window.height/2)
        self.select_learn_alg_button.on_click = self.select_learning_algorithm

        self.select_NN_button = arcade.gui.UIFlatButton(
          color=arcade.color.DARK_BLUE_GRAY,
          text='Select NN',
          width=400,
          height=200,
          x=self.window.width/2,
          y=self.window.height/2)
        self.select_NN_button.on_click = self.select_new_NN_model

        self.run_game_button = arcade.gui.UIFlatButton(
            color=arcade.color.DARK_BLUE_GRAY,
            text='Run game with current selected options',
            width=400,
            height=200,
            x=self.window.width / 2,
            y=self.window.height / 2)
        self.run_game_button.on_click = self.run_game

        self.current_selected_options_text = arcade.gui.UITextArea(
            text=f"""
            Current selected learning algorithm: {self.LEARNING_METHOD}
            Current selected NN: {self.NN_to_use}
            """,
            font_size=12,
            height=60
        )

        self.v_box = arcade.gui.UIBoxLayout(space_between=5)
        self.v_box.add(self.current_selected_options_text)
        self.v_box.add(self.select_learn_alg_button)
        self.v_box.add(self.select_NN_button)
        self.v_box.add(self.run_game_button)

        self.manager_1.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

        # SCREEN 2
        self.manager_learning_alg = arcade.gui.UIManager()
        self.manager_learning_alg.disable()

        self.v_box_learning_alg = arcade.gui.UIBoxLayout(space_between=5)

        self.manager_learning_alg.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box_learning_alg)
        )

        # SCREEN 3
        self.manager_NN = arcade.gui.UIManager()
        self.manager_NN.disable()

        self.v_box_NN = arcade.gui.UIBoxLayout(space_between=5)

        self.manager_NN.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box_NN)
        )

    def on_show_view(self):
        """
        Called whenever view is first shown
        :return:
        """

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists setup
        self.player_list = arcade.SpriteList()

        if self.LEARNING_METHOD == "evolution":
            if self.NN_to_use != 'NONE':
                self.learning_alg = Evolution_learning(self)
                self.learning_alg.on_startup_with_model(NN_dir=self.NN_to_use)
            else:
                self.learning_alg = Evolution_learning(self)
                self.learning_alg.on_startup_init()
        else:
            print("No valid learning method selected")

    def select_learning_algorithm(self, event):
        """
        Called when select learning algorithm button pressed
        Shows screen for selecting the learning algorithm
        :return:
        """
        self.menu_setting = MENUS[1]
        self.manager_1.disable()
        self.manager_NN.disable()
        self.manager_learning_alg.enable()

        buttons = []
        self.v_box_learning_alg.clear()
        for i, l_alg in enumerate(LEARNING_METHOD_Options):
            buttons.append(arcade.gui.UIFlatButton(
                color=arcade.color.GRAPE,
                text=f'{l_alg}',
                x=self.window.width / 2,
                y=self.window.height / 2,
                width=400,
                height=self.window.height / len(LEARNING_METHOD_Options) - 40))
            buttons[i].on_click = self.l_alg_change

            self.v_box_learning_alg.add(buttons[i])

    def l_alg_change(self, event):
        """
        Called whenever a learning algorithm option button is clicked
        :return:
        """
        self.LEARNING_METHOD = event.source.text
        self.current_selected_options_text.text = f"""
            Current selected learning algorithm: {self.LEARNING_METHOD}
            Current selected NN: {self.NN_to_use}
            """
        self.menu_setting = MENUS[0]
        self.manager_learning_alg.disable()
        self.manager_1.enable()

    def select_new_NN_model(self, event):
        """
        Called when select new NN button clicked
        Shows screen for selecting the new NN
        :return:
        """
        self.menu_setting = MENUS[2]
        self.manager_1.disable()
        self.manager_NN.enable()
        self.manager_learning_alg.disable()

        trained_nets = self.get_trained_nets()

        self.NN_option_text = arcade.gui.UITextArea(
            text=f"""OPTIONS FOR NN for current selected learning method:
            NONE, {trained_nets}""",
            font_size=20,
            width=self.window.width - 30,
            height=200
        )
        NN_selection = arcade.gui.UIInputText(
            text='Enter directory of NN',
            font_size=14,
            width=self.window.height - 30
        )
        submit_button = arcade.gui.UIFlatButton(
            color=arcade.color.GRAPE,
            text='SUBMIT',
            x=self.window.width / 2,
            y=self.window.width / 2,
            width=70,
            height=50
        )
        submit_button.on_click = self.submit_NN_name

        print(trained_nets)

        self.v_box_NN.clear()
        self.v_box_NN.add(self.NN_option_text)
        self.v_box_NN.add(NN_selection)
        self.v_box_NN.add(submit_button)

    def get_trained_nets(self):
        """
        Gets the list of saved neural networs
        :return: saved_nets: list of directories of saved NNs
        """
        saved_nets = glob.glob(f'../models_{self.LEARNING_METHOD}/*')

        return saved_nets

    def submit_NN_name(self, event):
        """
        Called when submit button pressed to submit NN file name
        :return:
        """
        self.NN_to_use = f"{self.NN_option_text.text}"
        self.menu_setting = MENUS[0]
        self.manager_NN.disable()
        self.manager_1.enable()


    def run_game(self, event):
        """
        Called when run_game button pressed
        Runs the game with current selected learning algorithm and NN
        :return:
        """
        self.menu_setting = None
        self.manager_1.disable()
        self.setup()


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
        self.player_sprite.initialise(reward_list=self.reward_list)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before start drawing
        self.clear()

        self.wall_list.draw()  # Draw the walls

        arcade.draw_text("press ESC to access menu", self.window.width - 110, self.window.height - 30,
                         arcade.color.WHITE, font_size=10, anchor_x="center")
        arcade.draw_text("press \ to select new learning algorithm or NN", self.window.width - 110,
                         self.window.height - 50, arcade.color.WHITE, font_size=10, anchor_x="center")

        # Draw the UI managers
        if self.menu_setting == MENUS[0]:
            self.manager_1.draw()
        elif self.menu_setting == MENUS[1]:
            self.manager_learning_alg.draw()
        elif self.menu_setting == MENUS[2]:
            self.manager_NN.draw()

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

        if key == arcade.key.ESCAPE:
            self.window.show_view(self.Main_Menu)  # TODO: make it so that you can go to/from main menu without losing progress

        if key == arcade.key.BACKSLASH:
            # Select new learning algorithm or NN
            self.menu_setting = MENUS[0]
            self.manager_1.enable()


# --------------------------------------------------------------------------------------
