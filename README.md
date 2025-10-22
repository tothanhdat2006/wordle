# Wordle Game

A desktop implementation of the popular Wordle game built with Python and Kivy, allowing unlimited times with no daily restrictions

## Features

- **Unlimited Plays** - Play as many games as you want
- **Statistics Tracking** - Track your wins, games played, and winning streak
- **Modern UI** - Clean, polished interface with smooth interactions

## How to Play

1. **Guess the word** - Type a 5-letter word using your keyboard and press Enter to submit your guess
3. **Check feedback**:
   - **Green** - Correct letter in correct position
   - **Yellow** - Correct letter in wrong position
   - **Gray** - Letter not in the word
4. **Win** - Guess the word within 6 tries

## Installation

1. Clone this repository:
```bash
git clone https://github.com/tothanhdat2006/wordle.git
cd wordle
```

2. Install dependencies using `uv`:
```bash
uv sync
```

3. Run the game:
```bash
python main.py
```

## Game Controls

- **A-Z Keys** - Type letters
- **Backspace** - Delete last letter
- **Enter** - Submit your guess
- **Surrender Button** - Give up and see the answer
- **Menu Button** - Return to main menu

## Requirements

- Python 3.8+
- Kivy 2.3.1+
- See `pyproject.toml` for full dependency list