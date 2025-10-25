from kivy.uix.screenmanager import Screen

"""
Main menu for the game
Most of its UI is written in wordle.kv
"""
class MainMenuManager(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def enter_game(self):
        self.manager.current = 'game_screen'
