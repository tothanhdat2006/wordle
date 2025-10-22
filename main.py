from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.lang import Builder


import random

"""
Main menu for the game
Most of its UI is written in wordle.kv
"""
class MainMenuManager(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def enter_game(self):
        self.manager.current = 'game_screen'

"""
Game board layout
"""
class GameBoxLayout(StackLayout):
    def __init__(self, hidden_text, **kwargs):
        super().__init__(**kwargs)
        box_size = 60
        spacing = 10
        self.size_hint = (None, None)

        self.num_tries = 6
        self.hidden_text = hidden_text.upper()
        self.max_word_length = len(self.hidden_text)
        self.width = self.max_word_length * box_size + (self.max_word_length-1) * spacing + 2 * spacing 
        self.height = self.num_tries * box_size + (self.num_tries-1) * spacing + 2 * spacing

        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1) # Dark gray background

        for _ in range(self.num_tries * self.max_word_length):
            word_box = Label(text='', size_hint=(None, None), size=(box_size, box_size), font_size=32, color=(0, 0, 0, 1))
            with word_box.canvas.before:
                Color(1, 1, 1, 1) # White background
                word_box.rect = Rectangle(size=word_box.size, pos=word_box.pos)
            word_box.bind(size=self._update_rect, pos=self._update_rect)
            self.add_widget(word_box)

    def _update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
    
    def update_hidden_text(self, new_hidden_text):
        self.hidden_text = new_hidden_text.upper()
        self.max_word_length = len(self.hidden_text)

    def reset(self):
        for word_box in self.children:
            word_box.text = ''
            word_box.canvas.before.clear()
            with word_box.canvas.before:
                Color(1, 1, 1, 1) # White background
                word_box.rect = Rectangle(size=word_box.size, pos=word_box.pos)

    def check_current_row(self, cur_row):
        """
        Check the words in the current row and color them 

        Args:
            row (int): Current row index
        Return:
            Number of correct letters in correct position
        """
        num_corrects = 0
        for c in range(self.max_word_length):
            index = cur_row * self.max_word_length + c
            word_box = self.children[len(self.children) - 1 - index]
            
            word_box.canvas.before.clear() #important!!!!!!!!!!!!!
            
            if word_box.text == self.hidden_text[c]:
                with word_box.canvas.before:
                    Color(0, 1, 0, 1)  # Green (for correct letters in correct position)
                    word_box.rect = Rectangle(size=word_box.size, pos=word_box.pos)
                num_corrects += 1
            elif word_box.text in self.hidden_text:
                with word_box.canvas.before:
                    Color(1, 1, 0, 1)  # Yellow (for correct letters in wrong position)
                    word_box.rect = Rectangle(size=word_box.size, pos=word_box.pos)
            else:
                with word_box.canvas.before:
                    Color(0.5, 0.5, 0.5, 1)  # Gray (for incorrect letters)
                    word_box.rect = Rectangle(size=word_box.size, pos=word_box.pos)
        return num_corrects

    def add_letter_at(self, row, col, letter):
        index = row * self.max_word_length + col
        if 0 <= index < len(self.children):
            self.children[len(self.children) - 1 - index].text = letter

    def delete_letter_at(self, row, col):
        index = row * self.max_word_length + col
        if 0 <= index < len(self.children):
            self.children[len(self.children) - 1 - index].text = ''


"""
Main game screen
Most of the game logic is handled here
"""
class GameScreenManager(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.winning_streak = 0  # Track winning streak
        self.total_games = 0
        self.total_wins = 0
        self.current_row = 0
        self.current_col = 0

        self.word_list = [
            "apple", "grape", "mango", "pearl", "stone",
            "chair", "table", "plant", "light", "sound",
            "crane", "flame", "brick", "sword", "cloud",
            "coder", "debug", "array", "stack", "queue",
            "globe", "flock", "brave", "charm", "dwarf",
            "lunar", "comet", "popup", "pixel", "vivid"
        ]
        self.num_tries = 6
        self.hidden_text = self.keyword_generator()
        self.max_word_length = len(self.hidden_text)
        
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        
        main_container = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Stats
        stats_layout = BoxLayout(size_hint_y=0.1, spacing=20)
        self.streak_label = Label(
            text=f'[b]Streak: [color=6ac764]{self.winning_streak}[/color][/b]',
            markup=True,
            font_size='20sp',
            size_hint_x=0.3
        )
        self.games_label = Label(
            text=f'[b]Games: {self.total_games}[/b]',
            markup=True,
            font_size='18sp',
            size_hint_x=0.3
        )
        self.wins_label = Label(
            text=f'[b]Wins: [color=6ac764]{self.total_wins}[/color][/b]',
            markup=True,
            font_size='18sp',
            size_hint_x=0.3
        )
        stats_layout.add_widget(self.streak_label)
        stats_layout.add_widget(self.games_label)
        stats_layout.add_widget(self.wins_label)
        
        # Game board
        self.game_main_layout = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=0.7)
        self.gamebox_layout = GameBoxLayout(hidden_text=self.hidden_text)
        self.game_main_layout.add_widget(self.gamebox_layout)
        
        button_layout = BoxLayout(size_hint_y=0.1, spacing=20, size_hint_x=0.5, pos_hint={'center_x': 0.5})
        
        self.surrender_btn = Button(
            text='SURRENDER',
            background_color=(0.8, 0.3, 0.3, 1),
            bold=True,
            font_size='18sp'
        )
        self.surrender_btn.bind(on_press=self.surrender_game)
        
        self.menu_btn = Button(
            text='MENU',
            background_color=(0.5, 0.5, 0.5, 1),
            bold=True,
            font_size='18sp'
        )
        self.menu_btn.bind(on_press=lambda x: self.confirm_menu())
        
        button_layout.add_widget(self.surrender_btn)
        button_layout.add_widget(self.menu_btn)
        
        main_container.add_widget(stats_layout)
        main_container.add_widget(self.game_main_layout)
        main_container.add_widget(button_layout)
        self.add_widget(main_container)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """
        Handle keyboard input. Process:
        1. Backspace: delete last letter
        2. a-z: add letter to current position
        3. Enter: submit current row
        4. Ignore other keys
        """
        if keycode[1] == 'backspace':
            self.current_col = max(0, self.current_col - 1)
            self.gamebox_layout.delete_letter_at(self.current_row, self.current_col)
        elif 'a' <= keycode[1] <= 'z' and len(keycode[1]) == 1:
            if self.current_col < self.max_word_length:
                self.gamebox_layout.add_letter_at(self.current_row, self.current_col, keycode[1].upper())
                self.current_col += 1
        elif keycode[1] == 'enter':
            if self.current_col < self.max_word_length:
                print("Not enough letters entered.")
                return True
            num_correct = self.gamebox_layout.check_current_row(self.current_row)
            self.current_row += 1
            self.current_col = 0
            
            # Winning state
            if num_correct == self.max_word_length:
                self.total_games += 1
                self.total_wins += 1
                self.winning_streak += 1
                self.update_stats_display()
                
                winning_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
                
                # labels
                congrats_label = Label(
                    text=f'[b][size=32sp][color=6ac764]CONGRATULATIONS![/color][/size][/b]',
                    markup=True,
                    size_hint_y=0.25
                )
                tries_text = f'[size=20sp]You found the word in [b][color=6ac764]{self.current_row}[/color][/b] {"try" if self.current_row == 1 else "tries"}![/size]'
                tries_label = Label(text=tries_text, markup=True, size_hint_y=0.15)
                # show streak info
                streak_text = f'[size=22sp]Winning Streak: [b][color=ff9500]{self.winning_streak}[/color][/b][/size]'
                streak_info_label = Label(text=streak_text, markup=True, size_hint_y=0.15)
                answer_label = Label(
                    text=f'[size=28sp]The word was: [b][color=6ac764]{self.gamebox_layout.hidden_text}[/color][/b][/size]',
                    markup=True,
                    size_hint_y=0.25
                )
                
                
                button_layout = BoxLayout(size_hint_y=0.2, spacing=10)
                play_again_btn = Button(text='PLAY AGAIN', background_color=(0.3, 0.7, 0.3, 1), bold=True)
                menu_btn = Button(text='MAIN MENU', background_color=(0.5, 0.5, 0.5, 1), bold=True)
                button_layout.add_widget(play_again_btn)
                button_layout.add_widget(menu_btn)
                
                win_popup = Popup(
                    title='Victory!',
                    content=winning_layout,
                    size_hint=(0.7, 0.5),
                    separator_color=(0.4, 0.8, 0.4, 1)
                )
                
                play_again_btn.bind(on_release=lambda x: self.restart_game(win_popup))
                menu_btn.bind(on_release=lambda x: self.back_to_menu_with_reset(win_popup))
                winning_layout.add_widget(congrats_label)
                winning_layout.add_widget(tries_label)
                winning_layout.add_widget(streak_info_label)
                winning_layout.add_widget(answer_label)
                winning_layout.add_widget(button_layout)
                win_popup.open()
                
            # Game over state
            if self.current_row >= self.num_tries:
                self.total_games += 1
                self.winning_streak = 0  # reset streak when loss
                self.update_stats_display()
                
                gameover_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
                
                # labels
                gameover_label = Label(
                    text='[b][size=32sp][color=c9b458]GAME OVER[/color][/size][/b]',
                    markup=True,
                    size_hint_y=0.3
                )
                fail_label = Label(
                    text='[size=18sp]Better luck next time![/size]',
                    markup=True,
                    size_hint_y=0.2
                )
                answer_label = Label(
                    text=f'[size=24sp]The word was: [b][color=ff6b6b]{self.gamebox_layout.hidden_text}[/color][/b][/size]',
                    markup=True,
                    size_hint_y=0.3
                )
                
                button_layout = BoxLayout(size_hint_y=0.2, spacing=10)
                try_again_btn = Button(text='TRY AGAIN', background_color=(0.3, 0.7, 0.3, 1), bold=True)
                menu_btn = Button(text='MAIN MENU', background_color=(0.5, 0.5, 0.5, 1), bold=True)
                button_layout.add_widget(try_again_btn)
                button_layout.add_widget(menu_btn)
                
                gameover_popup = Popup(
                    title='Game Over',
                    content=gameover_layout,
                    size_hint=(0.7, 0.5),
                    separator_color=(0.8, 0.4, 0.4, 1)
                )
                try_again_btn.bind(on_release=lambda x: self.restart_game(gameover_popup))
                menu_btn.bind(on_release=lambda x: self.back_to_menu_with_reset(gameover_popup))
                gameover_layout.add_widget(gameover_label)
                gameover_layout.add_widget(fail_label)
                gameover_layout.add_widget(answer_label)
                gameover_layout.add_widget(button_layout)
                gameover_popup.open()
        else:
            pass
        return True
    
    def keyword_generator(self):
        """
        Pick a random 5 letters keyword for the game
        """
        return random.choice(self.word_list).upper()
    
    def update_stats_display(self):
        """
        Update the statistics display
        """
        self.streak_label.text = f'[b]Streak: [color=6ac764]{self.winning_streak}[/color][/b]'
        self.games_label.text = f'[b]Games: {self.total_games}[/b]'
        self.wins_label.text = f'[b]Wins: [color=6ac764]{self.total_wins}[/color][/b]'
    
    def surrender_game(self, instance):
        """
        Handle surrender button press
        """
        # Update stats
        self.total_games += 1
        self.winning_streak = 0
        self.update_stats_display()

        surrender_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # labels
        surrender_label = Label(
            text='[b][size=28sp][color=ff6b6b]YOU SURRENDERED[/color][/size][/b]',
            markup=True,
            size_hint_y=0.3
        )
        message_label = Label(
            text='[size=18sp]Don\'t give up so easily next time![/size]',
            markup=True,
            size_hint_y=0.2
        )
        answer_label = Label(
            text=f'[size=24sp]The word was: [b][color=c9b458]{self.gamebox_layout.hidden_text}[/color][/b][/size]',
            markup=True,
            size_hint_y=0.3
        )
        
        button_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        try_again_btn = Button(text='TRY AGAIN', background_color=(0.3, 0.7, 0.3, 1), bold=True)
        menu_btn = Button(text='MAIN MENU', background_color=(0.5, 0.5, 0.5, 1), bold=True)
        button_layout.add_widget(try_again_btn)
        button_layout.add_widget(menu_btn)
        
        surrender_popup = Popup(
            title='Surrendered',
            content=surrender_layout,
            size_hint=(0.7, 0.5),
            separator_color=(0.8, 0.4, 0.4, 1)
        )
        try_again_btn.bind(on_release=lambda x: self.restart_game(surrender_popup))
        menu_btn.bind(on_release=lambda x: self.back_to_menu_with_reset(surrender_popup))
        surrender_layout.add_widget(surrender_label)
        surrender_layout.add_widget(message_label)
        surrender_layout.add_widget(answer_label)
        surrender_layout.add_widget(button_layout)
        surrender_popup.open()
    
    def confirm_menu(self):
        """
        Confirm before going back to menu
        """
        if self.current_row > 0:  # Only confirm if game in progress
            confirm_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
            
            # labels
            warning_label = Label(
                text='[b][size=24sp]Leave Game?[/size][/b]',
                markup=True,
                size_hint_y=0.4
            )
            message_label = Label(
                text='[size=18sp]Your current progress will be lost.[/size]',
                markup=True,
                size_hint_y=0.3
            )
            
            button_layout = BoxLayout(size_hint_y=0.3, spacing=10)
            stay_btn = Button(text='STAY', background_color=(0.3, 0.7, 0.3, 1), bold=True)
            leave_btn = Button(text='LEAVE', background_color=(0.8, 0.3, 0.3, 1), bold=True)
            button_layout.add_widget(stay_btn)
            button_layout.add_widget(leave_btn)
            
            confirm_popup = Popup(
                title='Confirm',
                content=confirm_layout,
                size_hint=(0.6, 0.4)
            )
            
            stay_btn.bind(on_release=confirm_popup.dismiss)
            leave_btn.bind(on_release=lambda x: self.force_menu(confirm_popup))
            confirm_layout.add_widget(warning_label)
            confirm_layout.add_widget(message_label)
            confirm_layout.add_widget(button_layout)
            confirm_popup.open()
        else:
            self.back_to_menu()
    
    def restart_game(self, popup):
        """
        Restart the game without going back to menu
        """
        popup.dismiss()
        self.current_row = 0
        self.current_col = 0
        self.hidden_text = self.keyword_generator()
        self.gamebox_layout.update_hidden_text(self.hidden_text)
        self.gamebox_layout.reset()
    
    def back_to_menu(self):
        self.manager.current = 'main_menu'

    def back_to_menu_with_reset(self, popup):
        """
        Go back to menu and reset game state
        """
        if popup:
            popup.dismiss()
        self.current_row = 0
        self.current_col = 0
        self.gamebox_layout.reset()
        self.back_to_menu()
    
    def force_menu(self, popup):
        """
        Force return to menu and reset streak
        """
        popup.dismiss()
        self.winning_streak = 0
        self.update_stats_display()
        self.back_to_menu_with_reset(None)


"""
Wordle game main application
"""
class WordleApp(App):
    def build(self):
        Window.size = (1080, 720)
        sm = ScreenManager()
        sm.add_widget(MainMenuManager(name='main_menu'))
        sm.add_widget(GameScreenManager(name='game_screen'))
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
    WordleApp().run()