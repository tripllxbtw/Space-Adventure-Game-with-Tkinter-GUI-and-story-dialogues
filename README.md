# Space-Adventure-Game-with-Tkinter-GUI-and-story-dialogues
# Space Adventure Game

A text-and-GUI based space exploration game built with Python and Tkinter.

## Features
- User registration and login system
- Save/load progress with JSON
- Interactive missions on different planets
- Typing text effect and dialogues
- Beautiful background and icons

## Requirements

- Python 3.10+
- Pillow
- Tkinter (usually preinstalled)

## How to run

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Run the game: `python src/main.py`

## Build executable (Windows)

```bash
pyinstaller --onefile --windowed --icon=dist/icon.ico src/main.py
