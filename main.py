from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.lang import Builder

from main_menu import MainMenuManager
from game_screen import GameScreenManager
from gacha_animation import GachaAnimationScreen

"""
Wordle game main application
"""
class GachaWordleApp(App):
    def build(self):
        Window.size = (1080, 720)
        sm = ScreenManager()
        self.GachaAnimationScreen = GachaAnimationScreen(name='gacha_animation')
        sm.add_widget(MainMenuManager(name='main_menu'))
        sm.add_widget(GameScreenManager(name='game_screen'))
        sm.add_widget(self.GachaAnimationScreen)
        Window.bind(on_request_close=self.on_exit)
        return sm

    def on_exit(self, *args):
        self.show_exit_popup()
        return True

    def show_exit_popup(self):
        layout = BoxLayout(orientation='vertical')
        cancel_button = Button(text="Cancel", size_hint=(1, 0.3))
        close_button = Button(text="Exit", size_hint=(1, 0.3))

        layout.add_widget(Label(text="Are you sure you want to exit?"))
        layout.add_widget(cancel_button)
        layout.add_widget(close_button)

        popup = Popup(title="Exit Confirmation", content=layout, size_hint=(0.6, 0.4))
        close_button.bind(on_release=lambda x: self.stop()) # Stop the app on confirmation
        cancel_button.bind(on_release=popup.dismiss) # Dismiss the popup on cancel
        popup.open()
    
    

if __name__ == '__main__':
    Builder.load_file('./wordle.kv')
    GachaWordleApp().run()