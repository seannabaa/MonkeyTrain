"""
MonkeyTrain - A Memory Training Game
Author: [Your Name]
Date: December 2024
Version: Beta 1.0

Description:
MonkeyTrain is a memory training game where players must memorize and click
a sequence of numbers in ascending order. The game features adaptive difficulty
that scales based on player performance.

How to Play:
1. Watch the grid as numbers appear briefly
2. Memorize the positions of the numbers
3. Click the tiles in ascending order (1, 2, 3, ...)
4. Complete sequences to increase your score and difficulty

Controls:
- Mouse Click: Select tiles / Navigate menus
- ESC: Pause game / Return to menu
- D: Toggle dark mode
"""

import pygame
import random
import time
import sys

# =============================================================================
# INITIALIZE PYGAME MODULES
# =============================================================================
pygame.init()
pygame.mixer.init()  # Initialize audio mixer for sound effects

# =============================================================================
# CONSTANTS - GAME CONFIGURATIONS
# =============================================================================

# Window Dimensions
WIDTH = 1280
HEIGHT = 720

# Color Definitions (RGB tuples)
# Light Mode Colors
LIGHT_MODE = {
    'bg': (40, 45, 60),
    'tile_revealed': (70, 80, 100),
    'tile_hidden': (110, 120, 140),
    'tile_clicked': (90, 100, 120),
    'text': (255, 255, 255),
    'success': (100, 200, 100),
    'failure': (200, 100, 100),
    'button': (60, 70, 90),
    'button_hover': (80, 90, 110),
    'subtitle': (200, 200, 200)
}

# Dark Mode Colors
DARK_MODE = {
    'bg': (15, 15, 20),
    'tile_revealed': (40, 45, 60),
    'tile_hidden': (60, 65, 80),
    'tile_clicked': (50, 55, 70),
    'text': (240, 240, 250),
    'success': (80, 180, 80),
    'failure': (180, 80, 80),
    'button': (35, 40, 55),
    'button_hover': (50, 55, 70),
    'subtitle': (180, 180, 190)
}

# Font Settings
font_title = pygame.font.SysFont("calibri", 48, bold=True)
font_large = pygame.font.SysFont("open-sans", 36)
font_medium = pygame.font.SysFont("open-sans", 28)
font_small = pygame.font.SysFont("open-sans", 24)
font_tiny = pygame.font.SysFont("open-sans", 18)

# Game Settings
BASE_DISPLAY_TIME = 10.0  # Seconds to show numbers
TILE_SIZE = 75
TILE_PADDING = 10
FADE_SPEED = 5  # Speed of fade animations (lower = slower)

# Animation Settings
CLICK_ANIMATION_DURATION = 300  # milliseconds

# Create the game window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MonkeyTrain - Memory Training Game")

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

# Current color scheme (starts with light mode)
current_colors = LIGHT_MODE.copy()
is_dark_mode = False

# Sound effects toggle
sounds_enabled = True

# Animation state
clicked_tiles = []  # List of (row, col, timestamp) tuples for click animations

# =============================================================================
# AUDIO SETUP
# =============================================================================

def create_sound_effect(frequency, duration, sound_type='click'):
    """
    Create simple sound effects programmatically since we can't load external files.
    
    Args:
        frequency: Sound frequency in Hz
        duration: Duration in seconds
        sound_type: Type of sound ('click', 'success', 'failure')
    
    Returns:
        pygame.mixer.Sound object or None if sound creation fails
    """
    try:
        sample_rate = 22050
        period = int(sample_rate / frequency)
        amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
        
        samples = []
        for i in range(int(duration * sample_rate)):
            sample_value = int(amplitude * ((i % period) / period - 0.5) * 2)
            samples.append([sample_value, sample_value])
        
        sound = pygame.mixer.Sound(buffer=bytes(samples))
        sound.set_volume(0.3)
        return sound
    except:
        return None

# Initialize sound effects
try:
    sound_click = create_sound_effect(800, 0.05, 'click')
    sound_success = create_sound_effect(600, 0.2, 'success')
    sound_failure = create_sound_effect(200, 0.3, 'failure')
except:
    sound_click = None
    sound_success = None
    sound_failure = None
    print("Warning: Sound effects could not be initialized")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def play_sound(sound):
    """Play a sound effect if sounds are enabled."""
    if sounds_enabled and sound is not None:
        try:
            sound.play()
        except:
            pass

def draw_text(surface, text, x, y, font, color):
    """
    Draw text at a specific position.
    
    Args:
        surface: Pygame surface to draw on
        text: Text string to render
        x, y: Position coordinates
        font: Pygame font object
        color: RGB color tuple
    """
    text_image = font.render(text, True, color)
    surface.blit(text_image, (x, y))

def draw_text_centered(surface, text, y, font, color):
    """
    Draw text centered horizontally at a specific y position.
    
    Args:
        surface: Pygame surface to draw on
        text: Text string to render
        y: Vertical position
        font: Pygame font object
        color: RGB color tuple
    """
    text_image = font.render(text, True, color)
    x = (WIDTH - text_image.get_width()) // 2
    surface.blit(text_image, (x, y))

def draw_button(surface, text, x, y, width, height, font, is_hovered=False):
    """
    Draw a button with hover effect.
    
    Args:
        surface: Pygame surface to draw on
        text: Button text
        x, y: Button position
        width, height: Button dimensions
        font: Pygame font object
        is_hovered: Whether mouse is over button
    
    Returns:
        pygame.Rect: Button rectangle for collision detection
    """
    color = current_colors['button_hover'] if is_hovered else current_colors['button']
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, color, button_rect, border_radius=10)
    pygame.draw.rect(surface, current_colors['text'], button_rect, 2, border_radius=10)
    
    text_surface = font.render(text, True, current_colors['text'])
    text_x = x + (width - text_surface.get_width()) // 2
    text_y = y + (height - text_surface.get_height()) // 2
    surface.blit(text_surface, (text_x, text_y))
    
    return button_rect

def generate_grid(grid_size):
    """
    Generate a randomized grid of sequential numbers.
    
    Args:
        grid_size: Size of the grid (e.g., 3 for 3x3)
    
    Returns:
        2D list representing the grid with shuffled numbers
    """
    numbers = list(range(1, grid_size * grid_size + 1))
    random.shuffle(numbers)
    
    # Build the 2D Grid
    grid = []
    index = 0
    
    for row in range(grid_size):
        current_row = []
        for col in range(grid_size):
            current_row.append(numbers[index])
            index += 1
        grid.append(current_row)
    
    return grid

def get_tile_positions(grid_size):
    """
    Calculate the screen positions for each tile in the grid.
    
    Args:
        grid_size: Size of the grid
    
    Returns:
        2D list of (x, y, size) tuples for each tile position
    """
    total_width = grid_size * TILE_SIZE + (grid_size - 1) * TILE_PADDING
    total_height = grid_size * TILE_SIZE + (grid_size - 1) * TILE_PADDING
    
    # Center the grid both horizontally and vertically
    start_x = (WIDTH - total_width) // 2
    start_y = (HEIGHT - total_height) // 2 + 40  # Offset slightly down for header space
    
    positions = []
    
    for row in range(grid_size):
        current_row = []
        for col in range(grid_size):
            x = start_x + col * (TILE_SIZE + TILE_PADDING)
            y = start_y + row * (TILE_SIZE + TILE_PADDING)
            current_row.append((x, y, TILE_SIZE))
        positions.append(current_row)
    
    return positions

def draw_grid(grid, positions, reveal, alpha=255):
    """
    Draw the game grid with tiles and numbers.
    
    Args:
        grid: 2D list of numbers
        positions: 2D list of tile positions
        reveal: Whether to show numbers or hide them
        alpha: Transparency value (0-255) for fade effects
    """
    global clicked_tiles
    current_time = pygame.time.get_ticks()
    
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            x, y, size = positions[row][col]
            
            # Check if this tile was recently clicked
            is_clicked = False
            for clicked_row, clicked_col, timestamp in clicked_tiles:
                if clicked_row == row and clicked_col == col:
                    if current_time - timestamp < CLICK_ANIMATION_DURATION:
                        is_clicked = True
                    else:
                        clicked_tiles.remove((clicked_row, clicked_col, timestamp))
                    break
            
            # Choose tile color based on state
            if is_clicked:
                tile_color = current_colors['tile_clicked']
            elif reveal:
                tile_color = current_colors['tile_revealed']
            else:
                tile_color = current_colors['tile_hidden']
            
            # Apply alpha for fade effects
            if alpha < 255:
                tile_surface = pygame.Surface((size, size))
                tile_surface.set_alpha(alpha)
                tile_surface.fill(tile_color)
                window.blit(tile_surface, (x, y))
            else:
                pygame.draw.rect(window, tile_color, (x, y, size, size), border_radius=8)
            
            # Draw number if revealed
            if reveal:
                number_text = str(grid[row][col])
                text_surface = font_large.render(number_text, True, current_colors['text'])
                
                if alpha < 255:
                    text_surface.set_alpha(alpha)
                
                text_x = x + (size - text_surface.get_width()) // 2
                text_y = y + (size - text_surface.get_height()) // 2
                window.blit(text_surface, (text_x, text_y))

def get_clicked_tile_value(mouse_pos, grid, positions):
    """
    Determine which tile was clicked and return its value.
    
    Args:
        mouse_pos: (x, y) tuple of mouse position
        grid: 2D list of numbers
        positions: 2D list of tile positions
    
    Returns:
        Tuple of (value, row, col) if a tile was clicked, else (None, None, None)
    """
    mouse_x, mouse_y = mouse_pos
    
    for row in range(len(positions)):
        for col in range(len(positions[row])):
            x, y, size = positions[row][col]
            # Check if click is within tile bounds
            if x <= mouse_x <= x + size and y <= mouse_y <= y + size:
                return grid[row][col], row, col
    
    return None, None, None

def calculate_difficulty(score):
    """
    Calculate grid size and display time based on current score.
    Implements adaptive difficulty scaling.
    
    Args:
        score: Current player score
    
    Returns:
        Tuple of (grid_size, display_time)
    """
    if score < 3:
        return 3, BASE_DISPLAY_TIME + 0.3
    elif score < 7:
        return 4, BASE_DISPLAY_TIME
    elif score < 12:
        return 5, BASE_DISPLAY_TIME - 0.2
    else:
        # Maximum difficulty
        return 5, max(BASE_DISPLAY_TIME - 0.5, 3.0)

def toggle_dark_mode():
    """Toggle between light and dark color modes."""
    global is_dark_mode, current_colors
    is_dark_mode = not is_dark_mode
    current_colors = DARK_MODE.copy() if is_dark_mode else LIGHT_MODE.copy()

# =============================================================================
# GAME STATE FUNCTIONS
# =============================================================================

def fade_transition(duration_ms=500):
    """
    Create a smooth fade to black transition.
    
    Args:
        duration_ms: Duration of fade in milliseconds
    """
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((0, 0, 0))
    
    for alpha in range(0, 255, FADE_SPEED):
        fade_surface.set_alpha(alpha)
        window.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)

def run_round(level_size, reveal_time):
    """
    Run a single game round.
    
    Args:
        level_size: Size of the grid (3, 4, or 5)
        reveal_time: Time in seconds to show numbers
    
    Returns:
        True if round completed successfully
        False if player made a mistake
        None if player quit
    """
    global clicked_tiles
    
    # Generate the game grid and get tile positions
    grid = generate_grid(level_size)
    positions = get_tile_positions(level_size)
    
    # Create the correct sequence (1, 2, 3, ... n)
    correct_sequence = list(range(1, level_size * level_size + 1))
    
    # Game state variables
    is_showing_numbers = True
    show_start_time = pygame.time.get_ticks()
    user_sequence = []
    clicked_tiles = []
    running = True
    
    # Fade in effect
    for alpha in range(0, 255, FADE_SPEED * 2):
        window.fill(current_colors['bg'])
        draw_text_centered(window, "MonkeyTrain", 30, font_title, current_colors['text'])
        draw_text_centered(window, "Memorize the positions, then click in order: 1, 2, 3...", 80, font_small, current_colors['subtitle'])
        draw_grid(grid, positions, reveal=True, alpha=alpha)
        pygame.display.update()
        pygame.time.delay(10)
    
    while running:
        # Clear the screen
        window.fill(current_colors['bg'])
        
        # Draw title and instructions at top
        draw_text_centered(window, "MonkeyTrain", 30, font_title, current_colors['text'])
        draw_text_centered(window, "Memorize the positions, then click in order: 1, 2, 3...", 80, font_small, current_colors['subtitle'])
        
        # Calculate elapsed time
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - show_start_time) / 1000
        
        # Handle reveal phase timing
        if is_showing_numbers:
            # Show countdown timer centered at top
            time_remaining = max(0, reveal_time - elapsed_seconds)
            timer_text = f"Memorize: {time_remaining:.1f}s"
            draw_text_centered(window, timer_text, 120, font_medium, current_colors['success'])
            draw_grid(grid, positions, reveal=True)
            
            if elapsed_seconds > reveal_time:
                is_showing_numbers = False
        else:
            # Show progress centered at top
            progress_text = f"Progress: {len(user_sequence)} / {len(correct_sequence)}"
            draw_text_centered(window, progress_text, 120, font_medium, current_colors['text'])
            draw_grid(grid, positions, reveal=False)
        
        # Draw controls hint at bottom center
        draw_text_centered(window, "ESC: Menu  |  D: Dark Mode", HEIGHT - 35, font_tiny, current_colors['subtitle'])
        
        # Update the display
        pygame.display.update()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            # Handle keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_d:
                    toggle_dark_mode()
            
            # Handle mouse clicks during play phase
            if event.type == pygame.MOUSEBUTTONDOWN and not is_showing_numbers:
                mouse_pos = pygame.mouse.get_pos()
                clicked_value, row, col = get_clicked_tile_value(mouse_pos, grid, positions)
                
                if clicked_value is not None:
                    # Add click animation
                    clicked_tiles.append((row, col, pygame.time.get_ticks()))
                    play_sound(sound_click)
                    
                    user_sequence.append(clicked_value)
                    current_index = len(user_sequence) - 1
                    
                    # Check if the clicked number is correct
                    if user_sequence[current_index] != correct_sequence[current_index]:
                        play_sound(sound_failure)
                        return False  # Wrong answer
                    
                    # Check if sequence is complete
                    if len(user_sequence) == len(correct_sequence):
                        play_sound(sound_success)
                        return True  # Round completed successfully
    
    return None

def show_start_screen():
    """
    Display the game's start screen with instructions and options.
    
    Returns:
        str: 'play' to start game, 'help' for instructions, None to quit
    """
    clock = pygame.time.Clock()
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        window.fill(current_colors['bg'])
        
        # Title section - centered
        draw_text_centered(window, "MonkeyTrain", 100, font_title, current_colors['text'])
        draw_text_centered(window, "A Memory Training Game", 165, font_medium, current_colors['subtitle'])
        
        # Instructions section - centered
        instructions = [
            "How to Play:",
            "",
            "1. Watch as numbers appear on the grid",
            "2. Memorize all number positions",
            "3. Click tiles in order: 1, 2, 3...",
            "4. Complete sequences to level up!"
        ]
        
        y_offset = 210
        for instruction in instructions:
            if instruction:
                draw_text_centered(window, instruction, y_offset, font_small, current_colors['text'])
            y_offset += 32
        
        # Buttons - centered
        button_width = 280
        button_height = 50
        button_x = (WIDTH - button_width) // 2
        
        play_button = draw_button(window, "Start Game", button_x, 420, button_width, button_height, font_medium,
                                  button_x <= mouse_pos[0] <= button_x + button_width and 
                                  420 <= mouse_pos[1] <= 470)
        
        help_button = draw_button(window, "Controls & Help", button_x, 485, button_width, button_height, font_medium,
                                 button_x <= mouse_pos[0] <= button_x + button_width and 
                                 485 <= mouse_pos[1] <= 535)
        
        dark_mode_button = draw_button(window, f"Dark Mode: {'ON' if is_dark_mode else 'OFF'}", 
                                      button_x, 550, button_width, button_height, font_medium,
                                      button_x <= mouse_pos[0] <= button_x + button_width and 
                                      550 <= mouse_pos[1] <= 600)
        
        # Footer - centered
        draw_text_centered(window, "Press ESC anytime to return to menu", HEIGHT - 30, font_tiny, current_colors['subtitle'])
        
        pygame.display.update()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(mouse_pos):
                    play_sound(sound_click)
                    return 'play'
                elif help_button.collidepoint(mouse_pos):
                    play_sound(sound_click)
                    return 'help'
                elif dark_mode_button.collidepoint(mouse_pos):
                    play_sound(sound_click)
                    toggle_dark_mode()

def show_help_screen():
    """Display detailed help and controls screen."""
    clock = pygame.time.Clock()
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        window.fill(current_colors['bg'])
        
        # Title - centered
        draw_text_centered(window, "Controls & Help", 60, font_title, current_colors['text'])
        
        # Help content - all centered
        help_text = [
            "",
            "Keyboard Controls:",
            "ESC - Return to menu / Pause game",
            "D - Toggle dark mode on/off",
            "",
            "",
            "Difficulty Progression:",
            "Score 0-2: 3×3 grid, 10.3 seconds",
            "Score 3-6: 4×4 grid, 10.0 seconds",
            "Score 7-11: 5×5 grid, 9.8 seconds",
            "Score 12+: 5×5 grid, 9.5 seconds",
            "",
            "",
            "Pro Tips:",
            "• Focus on spatial patterns, not just numbers",
            "• Group numbers mentally (corners, edges, center)",
            "• Take short breaks to maintain focus"
        ]
        
        y_offset = 130
        for line in help_text:
            if line.startswith("Keyboard") or line.startswith("Difficulty") or line.startswith("Pro"):
                draw_text_centered(window, line, y_offset, font_medium, current_colors['success'])
                y_offset += 35
            elif line:
                draw_text_centered(window, line, y_offset, font_small, current_colors['text'])
                y_offset += 28
            else:
                y_offset += 15
        
        # Back button - centered
        button_width = 280
        button_height = 50
        button_x = (WIDTH - button_width) // 2
        
        back_button = draw_button(window, "Back to Menu", button_x, HEIGHT - 90, button_width, button_height, font_medium,
                                 button_x <= mouse_pos[0] <= button_x + button_width and 
                                 HEIGHT - 90 <= mouse_pos[1] <= HEIGHT - 40)
        
        pygame.display.update()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(mouse_pos):
                    play_sound(sound_click)
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

def show_feedback_screen(is_correct, score, grid_size):
    """
    Display feedback after a round completes.
    
    Args:
        is_correct: Whether the player succeeded
        score: Current score
        grid_size: Size of grid that was just completed
    """
    window.fill(current_colors['bg'])
    
    # All feedback centered vertically and horizontally
    if is_correct:
        draw_text_centered(window, "Correct!", HEIGHT // 2 - 80, font_title, current_colors['success'])
        draw_text_centered(window, f"You completed the {grid_size}×{grid_size} grid!", 
                         HEIGHT // 2 - 20, font_medium, current_colors['text'])
    else:
        draw_text_centered(window, "Wrong!", HEIGHT // 2 - 80, font_title, current_colors['failure'])
        draw_text_centered(window, "Don't give up! Try again!", 
                         HEIGHT // 2 - 20, font_medium, current_colors['text'])
    
    # Score display - centered
    draw_text_centered(window, f"Current Score: {score}", HEIGHT // 2 + 30, font_large, current_colors['text'])
    
    # Next difficulty info - centered
    next_size, next_time = calculate_difficulty(score)
    draw_text_centered(window, f"Next Challenge: {next_size}×{next_size} grid, {next_time:.1f}s", 
                     HEIGHT // 2 + 80, font_small, current_colors['subtitle'])
    
    pygame.display.update()
    time.sleep(2.5)

def game_loop():
    """
    Main game loop that manages rounds and scoring.
    """
    score = 0
    running = True
    
    while running:
        # Get difficulty settings based on current score
        grid_size, display_time = calculate_difficulty(score)
        
        # Run a round and get the result
        result = run_round(grid_size, display_time)
        
        # Handle the result
        if result is None:
            # Player quit the game - return to menu
            running = False
        elif result is True:
            # Player completed the round successfully
            score += 1
            show_feedback_screen(True, score, grid_size)
        else:
            # Player made a mistake
            show_feedback_screen(False, score, grid_size)
            score = 0  # Reset score on failure

def main():
    """
    Main entry point for the game.
    Initializes the game and manages the main menu loop.
    """
    clock = pygame.time.Clock()
    
    while True:
        action = show_start_screen()
        
        if action is None:
            break
        elif action == 'play':
            game_loop()
        elif action == 'help':
            show_help_screen()
    
    pygame.quit()
    sys.exit()

# =============================================================================
# PROGRAM ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
