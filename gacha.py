import random
import string

class Gacha:
    def __init__(self):
        pass

    def remove_curse(self, gamebox_layout, current_row):
        for row in range(current_row + 1):
            for col in range(gamebox_layout.max_word_length):
                index = row * gamebox_layout.max_word_length + col
                if gamebox_layout.box_state[index] == 0:
                    gamebox_layout.set_box_state(row, col, 1)  # unlock box using the method
                    print(f"Remove a curse from box at row {row}, col {col}")
                    return gamebox_layout
        print(f"Tried to remove a curse from box at row {current_row}, but it was not cursed.")
        return gamebox_layout

    def add_tries(self, gamebox_layout, current_row):
        if current_row > 0:
            # delete all letters in the random row [0, current_row-1]
            random_row = random.randint(current_row, gamebox_layout.num_tries - 1)
            print(f"Add tries by clearing row {random_row}")
            for i in range(gamebox_layout.max_word_length):
                gamebox_layout.delete_letter_at(random_row, i)
                gamebox_layout.set_box_state(random_row, i, 1)  # unlock using the method
        else:
            print("Tried to add tries, but no previous rows exist.")
        return gamebox_layout
    
    def win_game(self, gamebox_layout, current_row):
        print("Caused the player to win the game instantly!")
        return None

    def add_curse(self, gamebox_layout, current_row):
        random_row = random.randint(current_row, gamebox_layout.num_tries - 1)
        random_col = random.randint(0, gamebox_layout.max_word_length - 1)
        index = random_row * gamebox_layout.max_word_length + random_col
        if gamebox_layout.box_state[index] == 1:
            gamebox_layout.add_letter_at(random_row, random_col, random.choice(string.ascii_uppercase))
            gamebox_layout.set_box_state(random_row, random_col, 0)  # curse box using the method
            print(f"Added a curse to box at row {random_row}, col {random_col}")
        else:
            print(f"Tried to add a curse to box at row {random_row}, col {random_col}, but it was already cursed.")
        return gamebox_layout

    def remove_tries(self, gamebox_layout, current_row):
        if current_row < gamebox_layout.num_tries - 1:
            random_row = random.randint(current_row + 1, gamebox_layout.num_tries - 1)
            print(f"Remove tries by adding random word to row {random_row}")
            for i in range(gamebox_layout.max_word_length):
                gamebox_layout.add_letter_at(random_row, i, random.choice(string.ascii_uppercase))
                gamebox_layout.set_box_state(random_row, i, 0)  # lock using the method
        else:
            print("Tried to remove tries, but this is the last row.")
        return gamebox_layout

    def lose_game(self, gamebox_layout, current_row):
        print("Caused the player to lose the game instantly!")
        return None

    def random_event(self, gamebox_layout, current_row):
        events = [self.remove_tries, self.add_curse, self.lose_game, 
                  self.add_tries, self.remove_curse, self.win_game]
        event = random.choices(events, weights=[0.19, 0.4, 0.01, 0.19, 0.4, 0.01], k=1)[0]
        return event(gamebox_layout, current_row)
