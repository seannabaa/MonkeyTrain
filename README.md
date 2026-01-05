# MonkeyTrain

a Cognitive Chimp Test game that trains short-term memory.

PLEASE GO TO INSTRUCTIONS.MD TO SHOW HOW TO LAUNCH THE GAME
---

## **About**

MonkeyTrain is a short memory game built in Python using Pygame. The game demonstrates a grid of numbered tiles for a given amount of time. The numbers then disappear after clicking the first number, and the player must click the tiles in the correct order. When the order is completed correctly, the number of tiles will increase by one and will be randomised into different parts of the grid. If the order is incorrect, then the grid will reset to the original value. The main concept is to strengthen short-term memory through repeated practice.
The goal is to help users improve short-term number recall through fast pattern recognition. The target audience for a variety of people, including middle-school and high school students, adults, and older people.

---
## **Video Demo (Update 1.0) **
https://youtu.be/l47QNu3MEYA 
--- 

## **Version History**

### *0.5 - Prototype (11/19)* 
- A rough outline of MonkeyTrain
- Includes a start game screen, 3x3 grid generation, and difficulty logic
- Rough Work of Visuals done, got a main idea down of the function and logic
- Click Detection is still bugged, and time is very short

### *1.0 - Beta Version Update (12/12)*
- Updated the User Interface to make it more aesthetically pleasing.
- created a "Controls and Help" feature that demonstrates the game's mechanics, controls, and difficulty progression.
- Controls & Help will also have Pro Tips and advice.
- Added 'Dark Mode' Feature that allows users to switch from normal UI colours to darker UI colours,
- Longer and adjusted time periods make it easier for the beginner stages to remember the n x m grid given.
- Overall revamped from the Prototype.

Your Criticism is needed! Please help me with this project. I plan to learn more every day while I build this cool project.

---


## **Software**
- Python
- Pygame Library

---

## **System Requirements**
- Windows 10/11
- macOS 10.13 +
- Linux (Ubuntu 20.04+ or equivalent)

---
## ** Project Structure + File Descriptions  **

*File Breakdown*
- main.py is the main application, containing the main game loop of game development: processing user events, such as mouse clicks, updating the game state, and creating frames to the screen. I structured this game at 60 frames per second (FPS) to ensure smooth transitions between the menu and the gameplay.

*Themes and Global configuration*
- In the main.py, all colours for light and dark mode and their colour palettes.
- I used a theme injection approach, where every rendering function references  ```current_theme['key']```, allowing for ga lobal dark mode toggle that updates the entire UI instantly without restarting the game loop. 
- I defined variables like  ```TILE_SIZE```, ```TILE_GAP```, and ```ANIMATION_SPEED``` at the global level, ensuring the game's "Feel" and difficulty can be tuned in one location.

*Program Sound Generation*
- One challenge I ran through was the ```generate_sound``` function. I wanted the game to be entirely self-contained without requiring external ```.wav``` or ```.mp3``` files.
- I utilized pygame.mixer to generate Square Waves Mathematically, calculating the ```wave_period``` based on a target frequency and fills a buffer with raw audio samples.

*Grid/Coordinate Logic*
- The logic for tile placement is handled by calculate_tile_positions:
  - I used mathematical alignment, which centred a dynamic grid (changing from 3x3 to 4x4 to 5x5), requiring precise maths. I used the formula, *GridWidth = (Size x TileSize) + ((Size - 1) x Gap)*, allowing the grid to remain perfectly centred on a 1280 x 720 canvas.
  - The ```get_tile_at_position``` function acts as a bridge between the user's mouse coordinates and the internal 2D list, iterating through the tile rectangles and returning the specific value clicked, enabling real-time validation.

*Difficulty Progression System*
- The ```get_difficulty_settings``` function acts as a game's balancer, using a tiered system:
  - Tier 1 (Easy, Start of game) 3x3 grid, 10 seconds of time
  - Tier 2 (Intermediate) 4x4 grid, -0.3 seconds of time
  - Tier 3 (Expert), 5x5 grid, less time than intermediate, ensuring the game remains challenging for advanced players.
---
## **Design Choices**

- I used a single file architecture for ```main.py``` to simplify the end-user experience. A user only needs to download one script to play, compensating for the lack of files using exenstive block comments and a functional programming style to keep the code readable.
- One challenge was "ghost clicks", where a single click from a mouse would wrongly register. I solved this using the ```pygame.event.get()``` queue instead to ensure that each click is processed exactly once per number frame.

---

## **Inspiration**
- Human Benchmark
- Lumosity
- "Chimp outperforms humans at memory task" By New Scientist on YouTube
- Wordle
- Connections
