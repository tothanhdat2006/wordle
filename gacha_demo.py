"""
Standalone demo for the CSGO-style gacha box opening animation.
Run this file directly to test the animation without integrating it into the main game.
"""

from kivy.app import App
from kivy.core.window import Window
from gacha_animation import GachaAnimationDemo


class GachaAnimationDemoApp(App):
    def build(self):
        Window.size = (1080, 720)
        Window.clearcolor = (0.12, 0.12, 0.12, 1)
        return GachaAnimationDemo()


if __name__ == '__main__':
    GachaAnimationDemoApp().run()
