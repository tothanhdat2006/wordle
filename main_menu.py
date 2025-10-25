from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

"""
Main menu for the game
Most of its UI is written in wordle.kv
"""
class MainMenuManager(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def show_instruction(self):
        instruction_text = (
            "[b][size=24sp][color=6ac764]Welcome to Gacha Wordle![/color][/size][/b]\n\n"
            "[b][size=20sp]How to Play:[/size][/b]\n"
            "• Guess the hidden 5-letter word within 6 tries\n"
            "• Each guess must be a valid word\n"
            "• After each guess, tiles change color:\n"
            "  [b][color=6aaa64]GREEN[/color][/b] - Letter is correct and in the right position\n"
            "  [b][color=c9b458]YELLOW[/color][/b] - Letter is in the word but wrong position\n"
            "  [b][color=787c7e]GRAY[/color][/b] - Letter is not in the word\n\n"
            "[b][size=20sp]Gacha System:[/size][/b]\n"
            "Use gacha items during gameplay for advantages or surprises!\n\n"
            "[b][size=18sp]Gacha Item Chances:[/size][/b]\n"
            "  [color=ff6b6b]Remove Tries: 17%[/color] - Lose one attempt (one row will be filled with random letters and cannot be guessed)\n"
            "  [color=9b59b6]Add Curse: 30%[/color] - Random box becomes cursed, filled with a random letter and cannot be guessed\n"
            "  [color=e74c3c]Instant Lose: 3%[/color] - Game over immediately\n"
            "  [color=2ecc71]Add Tries: 12%[/color] - Regain one attempt (unlock the row that was previously filled by Remove Tries curse)\n"
            "  [color=3498db]Remove Curse: 25%[/color] - Remove the curse effect from a cursed box\n"
            "  [color=f39c12]Hint One Letter: 10%[/color] - Reveal a letter in the hidden word\n"
            "  [color=27ae60]Instant Win: 3%[/color] - Win immediately\n\n"
            "[i]Good luck and have fun![/i]"
        )
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        scroll_view = ScrollView(size_hint=(1, 0.9))
        instruction_label = Label(
            text=instruction_text,
            markup=True,
            size_hint_y=None,
            text_size=(500, None),
            halign='left',
            valign='top',
            font_size='16sp',
            color=(1, 1, 1, 1)
        )
        instruction_label.bind(
            texture_size=instruction_label.setter('size')
        )
        scroll_view.add_widget(instruction_label)
        
        close_btn = Button(
            text='Got it!',
            size_hint=(1, 0.1),
            font_size='18sp',
            bold=True,
            background_normal='',
            background_color=(0.3, 0.7, 0.3, 1)
        )
        content.add_widget(scroll_view)
        content.add_widget(close_btn)
        
        popup = Popup(
            title='How to Play',
            title_size='22sp',
            title_color=(0.42, 0.78, 0.39, 1),
            content=content,
            size_hint=(0.85, 0.85),
            auto_dismiss=False,
            separator_color=(0.3, 0.7, 0.3, 1)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def enter_game(self):
        self.manager.current = 'game_screen'
