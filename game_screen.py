from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.widget import Widget

import random
from gacha import Gacha
"""
Virtual keyboard widget for the Wordle game
"""
class VirtualKeyboard(BoxLayout):
    def __init__(self, handle_key_input, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 3
        self.padding = 5
        self.size_hint_y = None
        self.height = 140
        
        self.handle_key_input = handle_key_input
        self.key_buttons = {}
        
        keyboard_rows = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'BACKSPACE']
        ]
        
        for row in keyboard_rows:
            row_layout = BoxLayout(spacing=3, size_hint_y=1)
            
            # add spacing left
            if len(row) == 9:
                row_layout.add_widget(Widget(size_hint_x=0.5))
            
            for key in row:
                if key == 'ENTER' or key == 'BACKSPACE':
                    btn = Button(
                        text=key,
                        font_size='11sp',
                        bold=True,
                        size_hint_x=1,
                        background_normal='',
                        background_color=(0.5, 0.5, 0.5, 1)
                    )
                else:
                    btn = Button(
                        text=key,
                        font_size='13sp',
                        bold=True,
                        size_hint_x=0.5,
                        background_normal='',
                        background_color=(0.5, 0.5, 0.5, 1)
                    )
                
                btn.bind(on_press=self.on_button_press)
                row_layout.add_widget(btn)
                
                if key not in ['ENTER', 'BACKSPACE']:
                    self.key_buttons[key] = btn
            
            # add spacing right
            if len(row) == 9:
                row_layout.add_widget(Widget(size_hint_x=0.5))
            
            self.add_widget(row_layout)
    
    def on_button_press(self, button):
        """
        Handle virtual keyboard button press
        """
        key = button.text
        if key == 'BACKSPACE':
            self.handle_key_input('backspace')
        elif key == 'ENTER':
            self.handle_key_input('enter')
        else:
            self.handle_key_input(key.lower())
    
    def update_key_color(self, letter, state):
        """
        Update the color of a key based on its state
        state: 'correct' (green), 'present' (yellow), 'absent' (gray)
        """
        letter = letter.upper()
        if letter in self.key_buttons:
            button = self.key_buttons[letter]
            current_color = button.background_color
            
            # correct > present > absent
            if state == 'correct':
                button.background_color = (0.4, 0.7, 0.4, 1)  # Green
            elif state == 'present':
                if current_color != (0.4, 0.7, 0.4, 1):
                    button.background_color = (0.8, 0.7, 0.2, 1)  # Yellow
            elif state == 'absent':
                if current_color == (0.5, 0.5, 0.5, 1):
                    button.background_color = (0.3, 0.3, 0.3, 1)  # Dark gray
    
    def reset_keyboard(self):
        """Reset all key colors to default"""
        for button in self.key_buttons.values():
            button.background_color = (0.5, 0.5, 0.5, 1)


"""
Game board layout
"""
class GameBoxLayout(StackLayout):
    def __init__(self, hidden_text, word_list, **kwargs):
        super().__init__(**kwargs)
        box_size = 60
        spacing = 10
        self.size_hint = (None, None)

        self.word_list = word_list
        self.num_tries = 6
        self.hidden_text = hidden_text.upper()
        self.max_word_length = len(self.hidden_text)
        self.is_letter_revealed = [False] * self.max_word_length
        self.width = self.max_word_length * box_size + (self.max_word_length-1) * spacing + 2 * spacing 
        self.height = self.num_tries * box_size + (self.num_tries-1) * spacing + 2 * spacing
        self.box_state = {}
        for i in range(self.num_tries * self.max_word_length):
            self.box_state[i] = 1  # possible states:  0 (locked), 1 (changable), 2 (revealed)

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

    def reveal_letter(self, index):
        """
        Reveal the letter at the given index on the board
        Args:
            index (int): Index of the letter in the hidden text
        """
        self.is_letter_revealed[index] = True
        for row in range(self.num_tries):
            for col in range(self.max_word_length):
                if col == index:
                    self.add_letter_at(row, col, self.hidden_text[index])
                    self.set_box_state(row, col, 2)  # set to revealed

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
            tuple: (Number of correct letters in correct position, dict of letter states)
        """
        num_corrects = 0
        letter_states = {}
        guessed_letter = []
        # precheck
        for c in range(self.max_word_length):
            index = cur_row * self.max_word_length + c
            word_box = self.children[len(self.children) - 1 - index]
            letter = word_box.text
            if not letter:
                return 0, {}  # incomplete row
            guessed_letter.append(letter)
        guessed_letter = "".join(guessed_letter) 
        if guessed_letter not in self.word_list:
            return 0, {}  # invalid word
        
        for c in range(self.max_word_length):
            index = cur_row * self.max_word_length + c
            word_box = self.children[len(self.children) - 1 - index]
            letter = word_box.text
            
            word_box.canvas.before.clear() #important!!!!!!!!!!!!!
            word_box.color = (1, 1, 1, 1)  # Set text color to white for visibility
            
            if word_box.text == self.hidden_text[c]:
                num_corrects += 1
                letter_states[letter] = 'correct'
                with word_box.canvas.before:
                    Color(0, 1, 0, 1)  # Green (for correct letters in correct position)
                    word_box.rect = Rectangle(size=word_box.size, pos=word_box.pos)

            elif word_box.text in self.hidden_text:
                if letter not in letter_states or letter_states[letter] != 'correct':
                    letter_states[letter] = 'present'
                with word_box.canvas.before:
                    Color(1, 1, 0, 1)  # Yellow (for correct letters in wrong position)
                    word_box.rect = Rectangle(size=word_box.size, pos=word_box.pos)

            else:
                if letter not in letter_states:
                    letter_states[letter] = 'absent'

                with word_box.canvas.before:
                    Color(0.5, 0.5, 0.5, 1)  # Gray (for incorrect letters)
                    word_box.rect = Rectangle(size=word_box.size, pos=word_box.pos)

        return num_corrects, letter_states

    def add_letter_at(self, row, col, letter):
        index = row * self.max_word_length + col
        if 0 <= index < len(self.children):
            if self.box_state.get(index) == 1:
                self.children[len(self.children) - 1 - index].text = letter.upper()
                return 1
            else:
                return 0

    def delete_letter_at(self, row, col):
        index = row * self.max_word_length + col
        if 0 <= index < len(self.children):
            if self.box_state.get(index) == 1:
                self.children[len(self.children) - 1 - index].text = ''
                return 1
            else:
                return 0


    def set_box_state(self, row, col, state: int): # force state to be an int
        """
        Set the state of a box

        Args:
            row (int): Row index
            col (int): Column index
            state (int): State to set (0 for locked, 1 for changable, 2 for revealed)
        """
        index = row * self.max_word_length + col
        self.box_state[index] = state
        child_index = len(self.children) - 1 - index
        word_box = self.children[child_index]
        
        word_box.canvas.before.clear()
        with word_box.canvas.before:
            if state == 0:
                Color(0.8, 0.8, 0.8, 1)  # Light gray for locked boxes
            elif state == 1:
                Color(1, 1, 1, 1)  # White for changable boxes
            elif state == 2:
                Color(0.6, 1, 0.6, 1)  # Light green for revealed boxes
            word_box.rect = Rectangle(size=word_box.size, pos=word_box.pos)
        
        word_box.rect.pos = word_box.pos
        word_box.rect.size = word_box.size
        

"""
Main game screen
Most of the game logic is handled here
"""
class GameScreenManager(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gacha_system = Gacha()
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
            "lunar", "comet", "popup", "pixel", "vivid",
            "frost", "blaze", "lemon", "candy", "baker",
            "burst", "quest", "dream", "tiger", "zebra",
            "nerdy", "grant", "juice", "stove", "scale",
            "cigar", "movie", "focus", "piano", "robot",
            "evade", "watch", "erode", "refer", "awake",
            "serve"
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

        # roll dice button
        self.gacha_btn = Button(
            text='ROLL DICE',
            size_hint_x=0.5,
            background_color=(0.3, 0.5, 0.8, 1),
            bold=True,
            font_size='18sp'
        )
        self.gacha_btn.bind(on_press=lambda x: self.gacha())
        
        # Game board
        self.game_main_layout = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=0.6)
        self.gamebox_layout = GameBoxLayout(hidden_text=self.hidden_text, word_list=self.word_list)
        self.game_main_layout.add_widget(self.gamebox_layout)
        
        # Virtual keyboard
        self.virtual_keyboard = VirtualKeyboard(handle_key_input=self.handle_key_input, size_hint_y=None)
        self.virtual_keyboard.height = 140
        
        button_layout = BoxLayout(size_hint_y=0.08, spacing=20, size_hint_x=0.5, pos_hint={'center_x': 0.5})
        
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
        button_layout.add_widget(self.gacha_btn)
        main_container.add_widget(stats_layout)
        main_container.add_widget(self.game_main_layout)
        main_container.add_widget(self.virtual_keyboard)
        main_container.add_widget(button_layout)
        self.add_widget(main_container)

    def handle_key_input(self, key):
        """
        Handle keyboard input for physical and virtual keyboards
        
        Args:
            key (str): The key pressed ('backspace', 'enter', or a letter)
        """
        if key == 'backspace':
            print(f"Trying to delete letter at row {self.current_row}, col {self.current_col}")
            if self.current_col > 0:
                is_delete = self.gamebox_layout.delete_letter_at(self.current_row, self.current_col-1)
                if is_delete:
                    self.current_col = max(0, self.current_col - 1)
                else:
                    while self.current_col - 1 >= 0:
                        self.current_col -= 1
                        is_delete = self.gamebox_layout.delete_letter_at(self.current_row, self.current_col - 1)
                        if is_delete:
                            self.current_col = max(0, self.current_col - 1)
                            return True
        elif len(key) == 1 and 'a' <= key <= 'z':
            print(f"Trying to add letter '{key.upper()}' at row {self.current_row}, col {self.current_col}")
            if self.current_col < self.max_word_length:
                is_add = self.gamebox_layout.add_letter_at(self.current_row, self.current_col, key.upper())
                if is_add:
                    self.current_col += 1
                else:
                    while self.current_col + 1 < self.max_word_length:
                        self.current_col += 1  # skip locked box
                        is_add = self.gamebox_layout.add_letter_at(self.current_row, self.current_col, key.upper())
                        if is_add:
                            self.current_col += 1
                            return True
        elif key == 'enter':
            num_correct, letter_states = self.gamebox_layout.check_current_row(self.current_row)
            if letter_states == {}:
                print("Incomplete row, cannot submit.")
                return True
            
            # Update virtual keyboard color
            for letter, state in letter_states.items():
                self.virtual_keyboard.update_key_color(letter, state)
            
            self.current_row += 1
            self.current_col = 0
            
            # Winning state
            if num_correct == self.max_word_length:
                self.handle_win()
                
            # Game over state
            elif self.current_row >= self.num_tries:
                self.handle_game_over()

        return True

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
            self.handle_key_input('backspace')
        elif 'a' <= keycode[1] <= 'z' and len(keycode[1]) == 1:
            self.handle_key_input(keycode[1])
        elif keycode[1] == 'enter':
            self.handle_key_input('enter')
        else:
            pass
        return True
    
    def gacha(self):
        self.manager.current = 'gacha_animation'
    
    def apply_gacha_result(self, result_func):
        """
        Apply the gacha result function to the game board
        
        Args:
            result_func: The gacha function to apply (from Gacha class)
        """
        gamebox_layout = result_func(self.gamebox_layout, self.current_row)
        
        if gamebox_layout is None:
            if 'win' in result_func.__name__: # instant win
                self.handle_win()
            elif 'lose' in result_func.__name__: # instant lose
                self.handle_game_over()
        else:
            self.gamebox_layout = gamebox_layout

    def handle_win(self):
        """
        Handle winning state
        """
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
            separator_color=(0.4, 0.8, 0.4, 1),
            auto_dismiss=False
        )
        
        play_again_btn.bind(on_release=lambda x: self.restart_game(win_popup))
        menu_btn.bind(on_release=lambda x: self.back_to_menu_with_reset(win_popup))
        winning_layout.add_widget(congrats_label)
        winning_layout.add_widget(tries_label)
        winning_layout.add_widget(streak_info_label)
        winning_layout.add_widget(answer_label)
        winning_layout.add_widget(button_layout)
        win_popup.open()
    
    def handle_game_over(self):
        """
        Handle game over state
        """
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
            separator_color=(0.8, 0.4, 0.4, 1),
            auto_dismiss=False
        )
        try_again_btn.bind(on_release=lambda x: self.restart_game(gameover_popup))
        menu_btn.bind(on_release=lambda x: self.back_to_menu_with_reset(gameover_popup))
        gameover_layout.add_widget(gameover_label)
        gameover_layout.add_widget(fail_label)
        gameover_layout.add_widget(answer_label)
        gameover_layout.add_widget(button_layout)
        gameover_popup.open()
    
    def keyword_generator(self):
        """
        Pick a random 5 letters keyword for the game
        """
        keyword = random.choice(self.word_list).upper()
        print(keyword)
        return keyword
    
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
            separator_color=(0.8, 0.4, 0.4, 1),
            auto_dismiss=False
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
                size_hint=(0.6, 0.4),
                auto_dismiss=False
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
        self.virtual_keyboard.reset_keyboard()
    
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
        self.virtual_keyboard.reset_keyboard()
        self.back_to_menu()
    
    def force_menu(self, popup):
        """
        Force return to menu and reset streak
        """
        popup.dismiss()
        self.winning_streak = 0
        self.update_stats_display()
        self.virtual_keyboard.reset_keyboard()
        self.back_to_menu_with_reset(None)
