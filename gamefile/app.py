import pygame
import random
import time
import sys


# PYGAME INITIALIZATION
pygame.init() # Initialize all pygame modules (display, fonts, events, etc.)
pygame.mixer.init() # Initialize the mixer module for sound effects


# GLOBAL CONSTANTS

# Display Configuration
WINDOW_WIDTH = 1280   # Main window width in pixels
WINDOW_HEIGHT = 720   # Main window height in pixels


# Color Theme Dictionaries
# Three theme options for accessibility and user preference
# Each theme contains all color values used throughout the game

LIGHT_THEME = {
    'background': (40, 45, 60), # Main window background
    'tile_revealed': (70, 80, 100), # Tiles showing numbers (memorization phase)
    'tile_hidden': (110, 120, 140), # Tiles with hidden numbers (testing phase)
    'tile_clicked': (90, 100, 120), # Tile color immediately after click
    'text_primary': (255, 255, 255), # Main text (headings, numbers)
    'text_secondary': (200, 200, 200), # Secondary text (instructions, hints)
    'success': (100, 200, 100), # Success indicators (correct answers)
    'failure': (200, 100, 100), # Failure indicators (wrong answers)
    'button': (60, 70, 90), # Default button color
    'button_hover': (80, 90, 110) # Button color when mouse hovers
}

DARK_THEME = {
    'background': (15, 15, 20), # Darker background for reduced eye strain
    'tile_revealed': (40, 45, 60), # Darker revealed tiles
    'tile_hidden': (60, 65, 80), # Darker hidden tiles
    'tile_clicked': (50, 55, 70), # Darker clicked tiles
    'text_primary': (240, 240, 250), # Slightly off-white for less contrast
    'text_secondary': (180, 180, 190), # Dimmer secondary text
    'success': (80, 180, 80), # Darker success green
    'failure': (180, 80, 80), # Darker failure red
    'button': (35, 40, 55), # Darker buttons
    'button_hover': (50, 55, 70) # Darker button hover state
}

HIGH_CONTRAST_THEME = {
    'background': (0, 0, 0), # Pure black background for maximum contrast
    'tile_revealed': (160, 160, 160), # Light gray tiles (numbers visible)
    'tile_hidden': (160, 160, 160), # Light gray tiles (numbers hidden)
    'tile_clicked': (255, 200, 0), # Orange-yellow click feedback
    'text_primary': (255, 255, 255), # Pure white text
    'text_secondary': (255, 255, 255), # White secondary text
    'success': (0, 255, 0), # Bright green for success
    'failure': (255, 0, 0), # Bright red for failure
    'button': (128, 128, 128), # Gray buttons
    'button_hover': (200, 200, 200) # Light gray hover
}


# Game Configuration Constants
MEMORIZATION_TIME = 10.0  # Base seconds to memorize grid (adjusted by difficulty)
TILE_SIZE_STANDARD = 75 # Standard tile width and height in pixels
TILE_SIZE_LARGE = 110 # Large tile size for accessibility
TILE_SIZE_EXTRA_LARGE = 150 # Extra large tile size for accessibility
TILE_GAP = 10 # Space between tiles in pixels
ANIMATION_SPEED = 6 # Transparency change per frame for fade effects
CLICK_DURATION = 300 # Milliseconds to show click feedback on tiles
FADE_DURATION = 800 # Milliseconds for fade transitions between rounds


# Font Initialization
FONT_TITLE = pygame.font.SysFont("calibri", 72, bold=True)  # Game title, bolded
FONT_LARGE = pygame.font.SysFont("opensans", 36) # Tile numbers
FONT_MEDIUM = pygame.font.SysFont("opensans", 28) # Section headers
FONT_SMALL = pygame.font.SysFont("opensans", 24) # Instructions
FONT_TINY = pygame.font.SysFont("opensans", 18) # Footer text


# Display Window Creation
# Create the main game window with specified dimensions
display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Set the window title shown in the title bar
pygame.display.set_caption("MonkeyTrain - Memory Training Game")


# Variables that track the current game state and persist across functions

# Active color theme (starts with light theme, can be toggled)
current_theme = LIGHT_THEME.copy()
# Theme mode tracking: 0=Light, 1=Dark, 2=High Contrast
theme_mode = 0

# Accessibility settings
use_large_tiles = False  # True = large tiles, False = standard tiles
current_tile_size = TILE_SIZE_STANDARD  # Current active tile size

# Sound effects enabled/disabled
sound_effects_enabled = True

# List storing recent tile clicks for visual feedback
# Each entry is a tuple: (row_index, col_index, timestamp_ms)
# Used to temporarily highlight clicked tiles
click_animations = []


# SOUND MANAGEMENT FUNCTIONS
def generate_sound(frequency, duration):
    """
    Generate a simple square wave sound effect programmatically.
    
    This function creates sound effects without requiring audio files by
    generating raw audio samples mathematically.
    
    Functions:
        frequency (int): Sound frequency in Hz (higher = higher pitch)
        duration (float): Sound duration in seconds
        
    Returns:
        pygame.mixer.Sound: Sound object ready to play, or None if generation fails
        
    Technical Details:
        - Uses square wave for simple, retro-style sound effects
        - Sample rate of 22050 Hz (half of CD quality, sufficient for game sounds)
        - Generates stereo sound (2 channels)
        - Volume is set to 30% to avoid being too loud
    """
    try:
        sample_rate = 22050  # Samples per second (standard for game audio)
        
        # Calculate how many samples make up one complete wave cycle
        wave_period = int(sample_rate / frequency)
        
        # Maximum amplitude for 16-bit signed integers
        max_amplitude = 32767
        
        # Generate square wave samples as bytes
        num_samples = int(duration * sample_rate)
        audio_bytes = bytearray()
        
        for i in range(num_samples):
            # Square wave formula: alternates between high and low values
            sample_value = int(max_amplitude * 0.3 * ((i % wave_period) / wave_period - 0.5) * 2)
            
            # Convert to 16-bit signed integer (little-endian) for both channels
            audio_bytes.extend(sample_value.to_bytes(2, byteorder='little', signed=True))
            audio_bytes.extend(sample_value.to_bytes(2, byteorder='little', signed=True))
        
        # Create pygame Sound object from raw bytes
        sound = pygame.mixer.Sound(buffer=bytes(audio_bytes))
        sound.set_volume(0.3)
        
        return sound
        
    except Exception as e:
        # If sound generation fails, print error but don't crash the game
        print(f"Sound generation error: {e}")
        return None


# Pre-generate Sound Effects
# Create all sound effects at startup for better performance
# Click sound: high-pitched, short beep (800 Hz, 50ms)
sound_click = generate_sound(800, 0.05)

# Success sound: medium-pitched, pleasant tone (600 Hz, 200ms)
sound_success = generate_sound(600, 0.2)

# Failure sound: low-pitched, longer tone (200 Hz, 300ms)
sound_failure = generate_sound(200, 0.3)

def play_sound_effect(sound):
    """
    Safely play a sound effect with error handling.
    
    This wrapper function checks if sound effects are enabled and if the
    sound object is valid before playing.
    
    Functions:
        sound (pygame.mixer.Sound): The sound effect to play
        
    Returns:
        None
        
    Note:
        - Respects the sound_effects_enabled global setting
        - Gracefully handles cases where sound is None
        - Catches and ignores any playback errors to prevent crashes
    """
    if sound_effects_enabled and sound is not None:
        try:
            sound.play()
        except Exception:
            pass

# =============================================================================
# DISPLAY HELPER FUNCTIONS
# =============================================================================
# Utility functions for rendering text and UI elements

def render_text(surface, text, x, y, font, color):
    """
    Render text at a specific position on a surface.
    
    Functions:
        surface (pygame.Surface): The surface to draw on (usually the main display)
        text (str): The text content to render
        x (int): X-coordinate of text top-left corner
        y (int): Y-coordinate of text top-left corner
        font (pygame.font.Font): Font object to use for rendering
        color (tuple): RGB color tuple (r, g, b)
        
    Returns:
        None
        
    Note:
        This is a basic text rendering function. For centered text,
        use render_text_centered() instead.
    """
    # Convert text string to a drawable surface with anti-aliasing
    text_surface = font.render(text, True, color)
    
    # Draw the text surface onto the target surface
    surface.blit(text_surface, (x, y))

def render_text_centered(surface, text, y_position, font, color):
    """
    Render text horizontally centered on the screen.
    
    This is commonly used for titles, instructions, and other centered UI elements.
    
    Functions:
        surface (pygame.Surface): The surface to draw on
        text (str): The text content to render
        y_position (int): Y-coordinate (horizontal centering is automatic)
        font (pygame.font.Font): Font object to use
        color (tuple): RGB color tuple
        
    Returns:
        None
        
    Technical Details:
        Calculates the X position by subtracting half the text width from
        half the window width, effectively centering the text.
    """
    # Render text to get its dimensions
    text_surface = font.render(text, True, color)
    
    # Calculate X position to center horizontally
    x_position = (WINDOW_WIDTH - text_surface.get_width()) // 2
    
    # Draw the text
    surface.blit(text_surface, (x_position, y_position))

def draw_button(surface, text, x, y, width, height, font, is_hovered):
    """
    Draw an interactive button with hover effects.
    
    Creates a rounded rectangle button with border and centered text.
    Color changes based on hover state for visual feedback.
    
    Functions:
        surface (pygame.Surface): The surface to draw on
        text (str): Button label text
        x (int): X-coordinate of button top-left corner
        y (int): Y-coordinate of button top-left corner
        width (int): Button width in pixels
        height (int): Button height in pixels
        font (pygame.font.Font): Font for button text
        is_hovered (bool): True if mouse is currently over button
        
    Returns:
        pygame.Rect: The button's rectangle (for collision detection)
        
    Visual Design:
        - Rounded corners (8px radius) for modern look
        - 2px border in text_primary color
        - Background color changes on hover
        - Text is automatically centered within button
    """
    # Select button color based on hover state
    button_color = current_theme['button_hover'] if is_hovered else current_theme['button']
    
    # Create rectangle representing button area
    button_rect = pygame.Rect(x, y, width, height)
    
    # Draw filled button background with rounded corners
    pygame.draw.rect(surface, button_color, button_rect, border_radius=8)
    
    # Draw button border (width=2 means outline only)
    pygame.draw.rect(surface, current_theme['text_primary'], button_rect, 2, border_radius=8)
    
    # Render button text
    text_surface = font.render(text, True, current_theme['text_primary'])
    
    # Calculate position to center text within button
    text_x = x + (width - text_surface.get_width()) // 2
    text_y = y + (height - text_surface.get_height()) // 2
    
    # Draw centered text
    surface.blit(text_surface, (text_x, text_y))
    
    # Return rectangle for click detection
    return button_rect

# GRID GENERATION AND MANAGEMENT
# Functions for creating, positioning, and rendering the game grid

def create_number_grid(size):
    """
    Generate a grid with randomly shuffled sequential numbers.
    
    This is the core of each game round - it creates a grid where numbers
    1 through N² are placed in random positions.
    
    Functions:
        size (int): Grid dimensions (creates size × size grid)
        
    Returns:
        list[list[int]]: 2D list representing the grid
                        Example for size=3:
                        [[7, 2, 4],
                         [1, 9, 3],
                         [6, 5, 8]]
                         
    Algorithm:
        1. Create sequential list [1, 2, 3, ..., size²]
        2. Shuffle to randomize positions
        3. Distribute into 2D grid structure
        
    Note:
        Each call generates a completely new random layout
    """
    # Generate sequential numbers from 1 to size²
    # For a 3×3 grid: [1, 2, 3, 4, 5, 6, 7, 8, 9]
    numbers = list(range(1, size * size + 1))
    
    # Randomize the order in-place
    random.shuffle(numbers)
    
    # Build 2D grid structure row by row
    grid = []
    for row_index in range(size):
        row = []
        for col_index in range(size):
            # Calculate flat index in the shuffled numbers list
            number_index = row_index * size + col_index
            row.append(numbers[number_index])
        grid.append(row)
    
    return grid

def calculate_tile_positions(grid_size):
    """
    Calculate the screen position and size of each tile in the grid.
    
    This function centers the entire grid on screen and calculates the
    exact pixel coordinates where each tile should be drawn.
    
    Functions:
        grid_size (int): Number of tiles per row/column
        
    Returns:
        list[list[tuple]]: 2D list where each element is (x, y, size)
                          - x: Left edge of tile in pixels
                          - y: Top edge of tile in pixels
                          - size: Width/height of tile (uses current_tile_size)
                          
    Layout Algorithm:
        1. Calculate total grid dimensions including gaps
        2. Center the grid horizontally
        3. Center vertically with 40px downward offset for header
        4. Calculate each tile position accounting for gaps
    """
    # Calculate total dimensions including gaps between tiles
    # Formula: (tiles × size) + (gaps × gap_size)
    # For 3 tiles: need 2 gaps between them
    total_grid_width = grid_size * current_tile_size + (grid_size - 1) * TILE_GAP
    total_grid_height = grid_size * current_tile_size + (grid_size - 1) * TILE_GAP
    
    # Center grid horizontally
    grid_start_x = (WINDOW_WIDTH - total_grid_width) // 2
    
    # Center vertically with slight downward offset for header space
    grid_start_y = (WINDOW_HEIGHT - total_grid_height) // 2 + 40
    
    # Calculate position for each tile
    positions = []
    for row in range(grid_size):
        row_positions = []
        for col in range(grid_size):
            # Position = start + (tile_index × (tile_size + gap))
            tile_x = grid_start_x + col * (current_tile_size + TILE_GAP)
            tile_y = grid_start_y + row * (current_tile_size + TILE_GAP)
            
            # Store as tuple: (x, y, size)
            row_positions.append((tile_x, tile_y, current_tile_size))
        positions.append(row_positions)
    
    return positions

def render_grid(grid, positions, show_numbers, transparency=255):
    """
    Draw the game grid with numbers and visual effects.
    
    This is the main rendering function for the grid. It handles:
    - Different tile colors based on game state
    - Showing/hiding numbers during different phases
    - Click feedback animations
    - Fade in/out transparency effects
    
    Functions:
        grid (list[list[int]]): The number grid to render
        positions (list[list[tuple]]): Tile positions from calculate_tile_positions()
        show_numbers (bool): True during memorization, False during testing
        transparency (int): Alpha value 0-255 for fade effects (default: 255 = fully opaque)
        
    Returns:
        None
        
    Visual States:
        - Recently clicked: Uses tile_clicked color
        - Numbers shown: Uses tile_revealed color
        - Numbers hidden: Uses tile_hidden color
        
    Performance Note:
        Cleans up expired click animations at the start of each call
    """
    global click_animations
    
    current_time = pygame.time.get_ticks()
    
    # Remove expired click animations (older than CLICK_DURATION)
    # List comprehension: keep only animations that are still within duration
    click_animations = [(r, c, t) for r, c, t in click_animations 
                       if current_time - t < CLICK_DURATION]
    
    # Iterate through each tile in the grid
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            # Get tile position and size
            x, y, size = positions[row][col]
            
            # Check if this tile was recently clicked
            is_recently_clicked = any(r == row and c == col 
                                     for r, c, _ in click_animations)
            
            # Determine tile color based on current state
            if is_recently_clicked:
                # Show click feedback
                tile_color = current_theme['tile_clicked']
            elif show_numbers:
                # Memorization phase - use revealed color
                tile_color = current_theme['tile_revealed']
            else:
                # Testing phase - use hidden color
                tile_color = current_theme['tile_hidden']
            
            # Draw tile with optional transparency for fade effects
            if transparency < 255:
                # Create temporary surface with alpha channel
                tile_surface = pygame.Surface((size, size))
                tile_surface.set_alpha(transparency)
                tile_surface.fill(tile_color)
                display.blit(tile_surface, (x, y))
            else:
                # Normal drawing (no transparency needed)
                pygame.draw.rect(display, tile_color, (x, y, size, size), 
                               border_radius=8)
            
            # Render number on tile if in reveal mode
            if show_numbers:
                number_text = str(grid[row][col])
                
                # Use larger font for large tiles
                if current_tile_size >= TILE_SIZE_EXTRA_LARGE:
                    number_font = pygame.font.SysFont("opensans", 48)
                elif current_tile_size >= TILE_SIZE_LARGE:
                    number_font = pygame.font.SysFont("opensans", 42)
                else:
                    number_font = FONT_LARGE
                
                text_surface = number_font.render(number_text, True, 
                                                current_theme['text_primary'])
                
                # Apply same transparency to text as tile
                if transparency < 255:
                    text_surface.set_alpha(transparency)
                
                # Center number on tile
                text_x = x + (size - text_surface.get_width()) // 2
                text_y = y + (size - text_surface.get_height()) // 2
                
                display.blit(text_surface, (text_x, text_y))

def get_tile_at_position(mouse_x, mouse_y, grid, positions):
    """
    Determine which tile (if any) was clicked at the given mouse position.
    
    This function performs hit detection to convert screen coordinates
    into grid coordinates and retrieve the number at that position.
    
    Functions:
        mouse_x (int): Mouse X coordinate in pixels
        mouse_y (int): Mouse Y coordinate in pixels
        grid (list[list[int]]): The number grid
        positions (list[list[tuple]]): Tile positions from calculate_tile_positions()
        
    Returns:
        tuple: (number, row, col) if click is on a tile
               (None, None, None) if click is not on any tile
               
    Algorithm:
        Iterates through all tiles checking if mouse position is within
        the rectangular bounds of each tile.
        
    Use Case:
        Called when player clicks during the testing phase to validate
        their answer and provide visual feedback.
    """
    # Check each tile position
    for row in range(len(positions)):
        for col in range(len(positions[row])):
            tile_x, tile_y, tile_size = positions[row][col]
            
            # Check if click is within tile boundaries
            # Tile occupies rectangle from (tile_x, tile_y) to 
            # (tile_x + tile_size, tile_y + tile_size)
            if (tile_x <= mouse_x <= tile_x + tile_size and 
                tile_y <= mouse_y <= tile_y + tile_size):
                # Return the number at this position and its coordinates
                return grid[row][col], row, col
    
    # Click was not on any tile
    return None, None, None

# =============================================================================
# DIFFICULTY PROGRESSION SYSTEM
# =============================================================================

def get_difficulty_settings(score):
    """
    Calculate appropriate grid size and time limit based on player's score.
    
    This implements the game's difficulty curve - as players progress,
    grids get larger and memorization time decreases.
    
    Functions:
        score (int): Player's current score (successful rounds completed)
        
    Returns:
        tuple: (grid_size, memorization_time)
               - grid_size (int): Dimensions of grid (3-5)
               - memorization_time (float): Seconds to memorize
               
    Difficulty Tiers:
        Score 0-2:  3×3 grid, 10.3 seconds (easy, learning phase)
        Score 3-6:  4×4 grid, 10.0 seconds (medium, standard gameplay)
        Score 7-11: 5×5 grid, 9.8 seconds (hard, increased challenge)
        Score 12+:  5×5 grid, 9.5 seconds (expert, minimum time, capped at 3.0s)
        
    Design Philosophy:
        - Gradual difficulty increase to avoid frustration
        - Grid size increases first (spatial challenge)
        - Time pressure increases second (temporal challenge)
        - Minimum time limit prevents impossibility
    """
    if score < 3:
        # Beginner tier: Small grid with extra time
        return 3, MEMORIZATION_TIME + 0.3
    elif score < 7:
        # Intermediate tier: Medium grid, standard time
        return 4, MEMORIZATION_TIME
    elif score < 12:
        # Advanced tier: Large grid, slightly less time
        return 5, MEMORIZATION_TIME - 0.2
    else:
        # Expert tier: Large grid, reduced time (but never below 3 seconds)
        return 5, max(MEMORIZATION_TIME - 0.5, 3.0)

def cycle_theme():
    """
    Cycle through theme modes: Light -> Dark -> High Contrast -> Light
    
    Updates the global theme state and applies the new color scheme.
    This function is called when the user presses 'D' or clicks the
    theme toggle button.
    
    Global Variables Modified:
        - theme_mode: Cycles through 0, 1, 2 (Light, Dark, High Contrast)
        - current_theme: Updated with new theme colors
        
    Returns:
        None
    """
    global theme_mode, current_theme
    
    # Toggle the flag
    theme_mode = (theme_mode + 1) % 3
    
    # Apply the appropriate theme (using copy to avoid reference issues)
    if theme_mode == 0:
        current_theme = LIGHT_THEME.copy()
    elif theme_mode == 1:
        current_theme = DARK_THEME.copy()
    else:
        current_theme = HIGH_CONTRAST_THEME.copy()

def toggle_large_tiles():
    """
    Toggle between standard and large tile sizes.
    
    Global Variables Modified:
        - use_large_tiles: Flipped to opposite state
        - current_tile_size: Updated with new tile size
        
    Returns:
        None
    """
    global use_large_tiles, current_tile_size
    
    use_large_tiles = not use_large_tiles
    
    if use_large_tiles:
        current_tile_size = TILE_SIZE_LARGE
    else:
        current_tile_size = TILE_SIZE_STANDARD

def set_extra_large_tiles(enabled):
    """
    Enable or disable extra large tile size.
    
    Functions:
        enabled (bool): True for extra large, False for standard/large
    
    Global Variables Modified:
        - current_tile_size: Updated with new tile size
        
    Returns:
        None
    """
    global current_tile_size
    
    if enabled:
        current_tile_size = TILE_SIZE_EXTRA_LARGE
    else:
        toggle_large_tiles()

# FADE ANIMATION HELPERS

def fade_in_screen():
    """
    Fade in the entire screen from black when pygame initializes.
    
    This creates a smooth entrance animation for the game.
    
    Returns:
        None
    """
    clock = pygame.time.Clock()
    fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Fade from black to transparent over approximately 500ms
    for alpha in range(255, 0, -ANIMATION_SPEED * 2):
        fade_surface.set_alpha(alpha)
        fade_surface.fill((0, 0, 0))
        display.blit(fade_surface, (0, 0))
        pygame.display.update()
        clock.tick(60)

def fade_transition(duration_ms=500):
    """
    Smooth fade transition between game states.
    
    Creates a fade-to-black then fade-from-black effect for smooth transitions
    between rounds or game states.
    
    Functions:
        duration_ms (int): Duration of fade in milliseconds
        
    Returns:
        None
    """
    clock = pygame.time.Clock()
    fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    frames = max(1, duration_ms // 16)  # ~60 FPS
    
    # Fade to black
    for alpha in range(0, 255, 255 // frames):
        fade_surface.set_alpha(alpha)
        fade_surface.fill((0, 0, 0))
        display.blit(fade_surface, (0, 0))
        pygame.display.update()
        clock.tick(60)
    
    # Hold black briefly
    pygame.time.delay(100)
    
    # Fade from black
    for alpha in range(255, 0, -255 // frames):
        fade_surface.set_alpha(alpha)
        fade_surface.fill((0, 0, 0))
        display.blit(fade_surface, (0, 0))
        pygame.display.update()
        clock.tick(60)

# =============================================================================
# GAME ROUND LOGIC
# =============================================================================

def execute_game_round(grid_size, reveal_duration):
    """
    Execute a complete game round from memorization to completion/failure.
    
    This is the core game loop for a single round. It handles:
    - Grid generation and positioning
    - Fade-in animation
    - Memorization phase (showing numbers)
    - Testing phase (hidden numbers, player clicks)
    - Input validation
    - Win/loss determination
        
    Functions:
        grid_size (int): Grid dimensions (creates size × size grid)
        reveal_duration (float): Seconds to show numbers for memorization
        
    Returns:
        bool: True if player completed sequence correctly
              False if player made a mistake
              None if player quit (ESC pressed)
              
    Game Flow:
        1. Generate random number grid
        2. Fade in with numbers visible
        3. Memorization phase (timed)
        4. Testing phase (numbers hidden, accept clicks)
        5. Validate each click immediately
        6. Return result when sequence is complete or error occurs
        
    Technical Details:
        - Uses pygame event system for user input
        - Tracks elapsed time with pygame.time.get_ticks()
        - Validates clicks in real-time for immediate feedback
        - Supports ESC (menu) and D (theme toggle) at any time
    """
    global click_animations
    
    # -------------------------------------------------------------------------
    # Round Setup
    # -------------------------------------------------------------------------
    
    # Generate a new random grid for this round
    grid = create_number_grid(grid_size)
    
    # Calculate where each tile should be drawn on screen
    tile_positions = calculate_tile_positions(grid_size)
    
    # The correct sequence is simply 1, 2, 3, ..., N²
    correct_sequence = list(range(1, grid_size * grid_size + 1))
    
    # -------------------------------------------------------------------------
    # Game State Initialization
    # -------------------------------------------------------------------------
    
    # Start in memorization phase (showing numbers)
    is_revealing_numbers = True
    
    # Record when memorization phase started (in milliseconds)
    reveal_start_time = pygame.time.get_ticks()
    
    # Track player's clicked sequence
    player_clicks = []
    
    # Clear any previous click animations
    click_animations = []
    

    # Fade In Animation
    # Gradually increase opacity from 0 to 255 for smooth appearance
    
    clock = pygame.time.Clock()
    for alpha in range(0, 255, ANIMATION_SPEED):
        # Clear screen
        display.fill(current_theme['background'])
        
        # Draw header
        render_text_centered(display, "MonkeyTrain", 10, FONT_TITLE, 
                           current_theme['text_primary'])
        render_text_centered(display, 
                           "Memorize the positions, then click in order: 1, 2, 3...", 
                           80, FONT_SMALL, current_theme['text_secondary'])
        
        # Draw grid with increasing transparency
        render_grid(grid, tile_positions, show_numbers=True, transparency=alpha)
        
        # Update display
        pygame.display.update()
        
        # Small delay for smooth animation (target 60 FPS)
        clock.tick(60)
    
    # -------------------------------------------------------------------------
    # Main Round Loop
    # -------------------------------------------------------------------------
    # Continues until player completes sequence, makes error, or quits
    
    while True:
        # Clear screen for this frame
        display.fill(current_theme['background'])
        
        # Header (shown in all phases)
        render_text_centered(display, "MonkeyTrain", 10, FONT_TITLE, 
                           current_theme['text_primary'])
        render_text_centered(display, 
                           "Memorize the positions, then click in order: 1, 2, 3...", 
                           80, FONT_SMALL, current_theme['text_secondary'])
        

        # Time Calculation
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - reveal_start_time) / 1000.0  # Convert to seconds
        

        # Phase 1: Memorization (Reveal Phase)
        if is_revealing_numbers:
            # Calculate remaining time
            time_left = max(0, reveal_duration - elapsed)
            
            # Display countdown timer
            timer_display = f"Memorize: {time_left:.1f}s"
            render_text_centered(display, timer_display, 120, FONT_MEDIUM, 
                               current_theme['success'])
            
            # Show grid with numbers visible
            render_grid(grid, tile_positions, show_numbers=True)
            
            # Check if memorization time has elapsed
            if elapsed >= reveal_duration:
                is_revealing_numbers = False  # Transition to testing phase
                
                # Smooth transition: fade out numbers
                for alpha in range(255, 0, -ANIMATION_SPEED * 3):
                    display.fill(current_theme['background'])
                    render_text_centered(display, "MonkeyTrain", 10, FONT_TITLE, 
                                       current_theme['text_primary'])
                    render_text_centered(display, 
                                       "Memorize the positions, then click in order: 1, 2, 3...", 
                                       80, FONT_SMALL, current_theme['text_secondary'])
                    render_grid(grid, tile_positions, show_numbers=True, transparency=alpha)
                    pygame.display.update()
                    clock.tick(60)
        
        # Phase 2: Testing (Click Phase)
        else:
            # Display progress counter
            progress_display = f"Progress: {len(player_clicks)} / {len(correct_sequence)}"
            render_text_centered(display, progress_display, 120, FONT_MEDIUM, 
                               current_theme['text_primary'])
            
            # Show grid with numbers hidden
            render_grid(grid, tile_positions, show_numbers=False)
        
        # Footer Controls (shown in all phases)
        render_text_centered(display, "ESC: Menu | D: Theme Toggle", 
                           WINDOW_HEIGHT - 35, FONT_TINY, 
                           current_theme['text_secondary'])
        
        # Update the display with all drawn elements
        pygame.display.update()
        
        # Event Handling
        # Process all queued events (clicks, key presses, window close, etc.)
        
        for event in pygame.event.get():
            # Window close button clicked
            if event.type == pygame.QUIT:
                return None  # Signal to quit game
            
            # Keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESC pressed - return to menu
                    return None
                elif event.key == pygame.K_d:
                    # D pressed - cycle theme
                    cycle_theme()
            
            # Mouse clicks (only processed during testing phase)
            if event.type == pygame.MOUSEBUTTONDOWN and not is_revealing_numbers:
                # Get mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Determine which tile (if any) was clicked
                clicked_value, row, col = get_tile_at_position(
                    mouse_x, mouse_y, grid, tile_positions)
                
                # If a tile was clicked (not empty space)
                if clicked_value is not None:
                    # Add visual click feedback
                    click_animations.append((row, col, pygame.time.get_ticks()))
                    
                    # Play click sound feedback
                    play_sound_effect(sound_click)
                    
                    # Add to player's click sequence
                    player_clicks.append(clicked_value)
                    
                    # Get index of this click (0-based)
                    click_index = len(player_clicks) - 1
                    
                    # Validate Click 
                    if player_clicks[click_index] != correct_sequence[click_index]:
                        # Wrong number clicked - immediate failure
                        play_sound_effect(sound_failure)
                        return False  # End round with failure
                    
                    # If player has clicked all numbers correctly
                    if len(player_clicks) == len(correct_sequence):
                        # Success! Player completed the sequence
                        play_sound_effect(sound_success)
                        return True  # End round with success

# =============================================================================
# MENU SCREENS
# =============================================================================

def display_settings_menu():
    """
    Display accessibility settings menu.
    
    Allows players to configure accessibility options including:
    - High contrast mode toggle
    - Large and extra large tile sizes
    - Sound effects toggle
    
    Returns:
        None (returns to menu when back button clicked or ESC pressed)
    """
    global current_tile_size, use_large_tiles, sound_effects_enabled
    
    clock = pygame.time.Clock()
    
    while True:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        display.fill(current_theme['background'])
        
        render_text_centered(display, "Accessibility Settings", 60, FONT_TITLE, current_theme['text_primary'])
        
        button_width, button_height = 320, 50
        button_x = (WINDOW_WIDTH - button_width) // 2
        
        y_pos = 300

        # High Contrast Mode button
        hc_text = f"High Contrast Mode: {'ON' if theme_mode == 2 else 'OFF'}"
        hc_hover = (button_x <= mouse_x <= button_x + button_width and y_pos <= mouse_y <= y_pos + button_height)
        hc_btn = draw_button(display, hc_text, button_x, y_pos, button_width, button_height, FONT_MEDIUM, hc_hover)
        
        y_pos += 65
        
        # Large Tiles button
        large_text = f"Large Tiles: {'ON' if use_large_tiles else 'OFF'}"
        large_hover = (button_x <= mouse_x <= button_x + button_width and y_pos <= mouse_y <= y_pos + button_height)
        large_btn = draw_button(display, large_text, button_x, y_pos, button_width, button_height, FONT_MEDIUM, large_hover)
        
        y_pos += 65
        
        # Extra Large Tiles button
        xlarge_text = f"Extra Large Tiles: {'ON' if current_tile_size == TILE_SIZE_EXTRA_LARGE else 'OFF'}"
        xlarge_hover = (button_x <= mouse_x <= button_x + button_width and y_pos <= mouse_y <= y_pos + button_height)
        xlarge_btn = draw_button(display, xlarge_text, button_x, y_pos, button_width, button_height, FONT_MEDIUM, xlarge_hover)
        
        y_pos += 65
        
        # Sound Effects button
        sound_text = f"Sound Effects: {'ON' if sound_effects_enabled else 'OFF'}"
        sound_hover = (button_x <= mouse_x <= button_x + button_width and y_pos <= mouse_y <= y_pos + button_height)
        sound_btn = draw_button(display, sound_text, button_x, y_pos, button_width, button_height, FONT_MEDIUM, sound_hover)
        
        y_pos += 90
        
        # Back button
        back_hover = (button_x <= mouse_x <= button_x + button_width and y_pos <= mouse_y <= y_pos + button_height)
        back_btn = draw_button(display, "Back to Menu", button_x, y_pos, button_width, button_height, FONT_MEDIUM, back_hover)
        
        render_text_centered(display, "Press ESC to return to menu", 
                           WINDOW_HEIGHT - 30, FONT_TINY, current_theme['text_secondary'])
        
        pygame.display.update()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hc_btn.collidepoint(mouse_x, mouse_y):
                    cycle_theme()
                    play_sound_effect(sound_click)
                elif large_btn.collidepoint(mouse_x, mouse_y):
                    if current_tile_size == TILE_SIZE_EXTRA_LARGE:
                        current_tile_size = TILE_SIZE_STANDARD
                        use_large_tiles = False
                    else:
                        toggle_large_tiles()
                    play_sound_effect(sound_click)
                elif xlarge_btn.collidepoint(mouse_x, mouse_y):
                    if current_tile_size == TILE_SIZE_EXTRA_LARGE:
                        current_tile_size = TILE_SIZE_STANDARD
                        use_large_tiles = False
                    else:
                        set_extra_large_tiles(True)
                        use_large_tiles = True
                    play_sound_effect(sound_click)
                elif sound_btn.collidepoint(mouse_x, mouse_y):
                    sound_effects_enabled = not sound_effects_enabled
                    play_sound_effect(sound_click)
                elif back_btn.collidepoint(mouse_x, mouse_y):
                    play_sound_effect(sound_click)
                    return

def display_start_menu():
    """
    Display the main menu screen with game instructions and options.
    
    This is the first screen players see. It provides:
    - Game title and description
    - How to play instructions
    - Navigation buttons (Start, Help, Settings, Theme Toggle)
    - Keyboard shortcuts
             
    Menu Loop:
        - Runs at 60 Frames Per Second for smooth animations
        - Tracks mouse position for hover effects
        - Processes clicks and keyboard input
        - Re-renders on theme changes
        
    Navigation:
        User can click buttons or close window to quit
        
    Returns:
        str: 'play', 'help', or None if quit
    """
    clock = pygame.time.Clock()
    
    # Menu loop - continues until user makes a choice
    while True:
        # Get current mouse position for hover detection
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Clear screen
        display.fill(current_theme['background'])
        
        # ---------------------------------------------------------------------
        # Title Section
        # ---------------------------------------------------------------------
        render_text_centered(display, "MonkeyTrain", 65, FONT_TITLE, 
                           current_theme['text_primary'])
        render_text_centered(display, "A Memory Training Game", 165, FONT_MEDIUM, 
                           current_theme['text_secondary'])
        
        # ---------------------------------------------------------------------
        # Instructions Section
        # ---------------------------------------------------------------------
        instructions = [
            "How to Play:",
            "1. Watch as numbers appear on the grid",
            "2. Memorize all number positions",
            "3. Click tiles in order: (1, 2, 3, ... n)",
            "4. Complete sequences to level up!"
        ]
        
        # Draw each instruction line
        y = 210  # Starting Y position
        for line in instructions:
            if line:  # Skip empty lines (used for spacing)
                render_text_centered(display, line, y, FONT_SMALL, 
                                   current_theme['text_primary'])
            y += 32  # Vertical spacing between lines
        
        # ---------------------------------------------------------------------
        # Button Section
        # ---------------------------------------------------------------------
        button_width, button_height = 280, 50
        button_x = (WINDOW_WIDTH - button_width) // 2  # Center horizontally
        
        # Start Game Button
        play_hover = (button_x <= mouse_x <= button_x + button_width and 
                     420 <= mouse_y <= 470)
        play_btn = draw_button(display, "Start Game", button_x, 400, 
                              button_width, button_height, FONT_MEDIUM, play_hover)
        
        # Controls & Help Button
        help_hover = (button_x <= mouse_x <= button_x + button_width and 
                     465 <= mouse_y <= 535)
        help_btn = draw_button(display, "Controls & Help", button_x, 465, 
                              button_width, button_height, FONT_MEDIUM, help_hover)
        
        # Accessibility Settings Button
        settings_hover = (button_x <= mouse_x <= button_x + button_width and 
                         530 <= mouse_y <= 600)
        settings_btn = draw_button(display, "Accessibility Settings", button_x, 530, 
                                   button_width, button_height, FONT_MEDIUM, settings_hover)
        
        # Theme Toggle Button
        theme_hover = (button_x <= mouse_x <= button_x + button_width and 
                      595 <= mouse_y <= 665)
        theme_text = f"Theme: {['Light', 'Dark', 'High Contrast'][theme_mode]}"
        theme_btn = draw_button(display, theme_text, button_x, 595, 
                               button_width, button_height, FONT_MEDIUM, theme_hover)
        
        # ---------------------------------------------------------------------
        # Footer
        # ---------------------------------------------------------------------
        render_text_centered(display, "Press ESC anytime to return to menu", 
                           WINDOW_HEIGHT - 30, FONT_TINY, 
                           current_theme['text_secondary'])
        
        # Update display
        pygame.display.update()
        
        # Cap frame rate at 60 FPS
        clock.tick(60)
        
        # ---------------------------------------------------------------------
        # Event Processing
        # ---------------------------------------------------------------------
        for event in pygame.event.get():
            # Window close button
            if event.type == pygame.QUIT:
                return None  # Exit game
            
            # Mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if click is on any button using collision detection
                if play_btn.collidepoint(mouse_x, mouse_y):
                    play_sound_effect(sound_click)
                    return 'play'  # Start game
                elif help_btn.collidepoint(mouse_x, mouse_y):
                    play_sound_effect(sound_click)
                    return 'help'  # Show help screen
                elif settings_btn.collidepoint(mouse_x, mouse_y):
                    play_sound_effect(sound_click)
                    display_settings_menu()
                elif theme_btn.collidepoint(mouse_x, mouse_y):
                    cycle_theme()
                    play_sound_effect(sound_click)

def display_help_screen():
    """
    Display the help/controls information screen.
    
    Shows detailed information about:
    - Keyboard controls
    - Difficulty progression system
    - Pro tips for better performance
    
    Returns:
        None (returns to menu when back button clicked or ESC pressed)
        
    Navigation:
        - Back button returns to main menu
        - ESC key also returns to menu
        - Window close exits game completely
        
    Layout:
        Content is organized into labeled sections with consistent spacing
    """
    clock = pygame.time.Clock()
    
    # Help screen loop
    while True:
        # Get mouse position for button hover detection
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Clear screen
        display.fill(current_theme['background'])
        
        # ---------------------------------------------------------------------
        # Title
        # ---------------------------------------------------------------------
        render_text_centered(display, "Controls & Help", 40, FONT_TITLE, 
                           current_theme['text_primary'])
        
        # ---------------------------------------------------------------------
        # Help Content
        # ---------------------------------------------------------------------
        help_lines = [
            "",  # Spacing
            "Keyboard Controls:",
            "ESC - Return to menu / Pause game",
            "D - Cycle through themes (Light/Dark/High Contrast)",
            "S - Open accessibility settings",
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
            "• Take short breaks to maintain focus!",
            ""
        ]
        
        # Draw each line with appropriate formatting
        y = 130  # Starting Y position
        for line in help_lines:
            # Section headers (colored differently for emphasis)
            if line.startswith(("Keyboard", "Difficulty", "Pro")):
                render_text_centered(display, line, y, FONT_MEDIUM, 
                                   current_theme['success'])
                y += 35  # Extra spacing after headers
            # Content lines
            elif line:
                render_text_centered(display, line, y, FONT_SMALL, 
                                   current_theme['text_primary'])
                y += 28  # Normal line spacing
            # Empty lines (spacing only)
            else:
                y += 15  # Smaller spacing for empty lines
        
        # ---------------------------------------------------------------------
        # Back Button
        # ---------------------------------------------------------------------
        button_width, button_height = 280, 50
        button_x = (WINDOW_WIDTH - button_width) // 2
        
        # Check if mouse is hovering over button
        back_hover = (button_x <= mouse_x <= button_x + button_width and 
                     WINDOW_HEIGHT - 90 <= mouse_y <= WINDOW_HEIGHT - 40)
        
        back_btn = draw_button(display, "Back to Menu", button_x, 
                              WINDOW_HEIGHT - 90, button_width, button_height, 
                              FONT_MEDIUM, back_hover)
        
        # Update display
        pygame.display.update()
        
        # Cap frame rate
        clock.tick(60)
        
        # ---------------------------------------------------------------------
        # Event Processing
        # ---------------------------------------------------------------------
        for event in pygame.event.get():
            # Window close
            if event.type == pygame.QUIT:
                return  # Exit to main menu (which will then exit game)
            
            # Mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(mouse_x, mouse_y):
                    play_sound_effect(sound_click)
                    return  # Return to main menu
            
            # Keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # ESC also returns to menu

def show_round_feedback(success, score, grid_size):
    """
    Display feedback screen after round completion (success or failure).
    
    Shows:
    - Success/failure message
    - Current score
    - Preview of next difficulty level
        
    Functions:
        success (bool): True if round was successful, False if failed
        score (int): Player's current score after the round
        grid_size (int): Size of the grid used in the round just completed
        
    Returns:
        None
        
    Display Duration:
        Automatically closes after 2.0 seconds
        
    Visual Design:
        - Success: Green "Correct!" message
        - Failure: Red "Wrong!" message with encouragement
        - Shows next challenge preview for planning
    """
    # Smooth fade transition
    fade_transition(400)
    
    # Clear screen
    display.fill(current_theme['background'])
    
    # -------------------------------------------------------------------------
    # Feedback Message
    # -------------------------------------------------------------------------
    if success:
        # Success message in green
        render_text_centered(display, "Correct!", WINDOW_HEIGHT // 2 - 80, 
                           FONT_TITLE, current_theme['success'])
        render_text_centered(display, f"You completed the {grid_size}×{grid_size} grid!", 
                           WINDOW_HEIGHT // 2 - 20, FONT_MEDIUM, 
                           current_theme['text_primary'])
    else:
        # Failure message in red with encouragement
        render_text_centered(display, "Wrong!", WINDOW_HEIGHT // 2 - 80, 
                           FONT_TITLE, current_theme['failure'])
        render_text_centered(display, "Don't give up! Try again!", 
                           WINDOW_HEIGHT // 2 - 20, FONT_MEDIUM, 
                           current_theme['text_primary'])
    
    # Score Display
    render_text_centered(display, f"Current Score: {score}", 
                       WINDOW_HEIGHT // 2 + 30, FONT_LARGE, 
                       current_theme['text_primary'])
    
    # Calculate what the next round will be like
    next_size, next_time = get_difficulty_settings(score)
    render_text_centered(display, 
                       f"Next Challenge: {next_size}×{next_size} grid, {next_time:.1f}s", 
                       WINDOW_HEIGHT // 2 + 80, FONT_SMALL, 
                       current_theme['text_secondary'])
    
    # Update display to show all elements
    pygame.display.update()
    
    # Hold screen for 2.0 seconds before continuing
    time.sleep(2.0)

# =============================================================================
# MAIN GAME LOOP
# =============================================================================

def run_game():
    """
    Main game loop - manages continuous gameplay across multiple rounds.
    
    Procedure:
        1. Start with score of 0
        2. Get difficulty settings based on score
        3. Execute a game round
        4. Process result:
           - Success: Increment score, continue
           - Failure: Reset score to 0, continue
           - Quit: Exit to menu
        5. Show feedback screen
        6. Repeat from step 2
        
    Function Returns:
        None (returns to main menu when player quits)
    
    Score System:
        - Starts at 0
        - +1 for each successful round
        - Resets to 0 on failure (but player can continue)
        
    Difficulty Scaling:
        Difficulty automatically adjusts based on score via
        get_difficulty_settings() function
    """
    # Initialize player score
    player_score = 0
    
    # Game loop - continues until player quits
    while True:
        # ---------------------------------------------------------------------
        # Get Current Difficulty Settings
        # ---------------------------------------------------------------------
        # Difficulty scales with score (larger grids, less time)
        grid_size, reveal_time = get_difficulty_settings(player_score)
        
        # ---------------------------------------------------------------------
        # Execute Round
        # ---------------------------------------------------------------------
        # Returns: True (success), False (failure), or None (quit)
        round_result = execute_game_round(grid_size, reveal_time)
        
        # ---------------------------------------------------------------------
        # Process Round Result
        # ---------------------------------------------------------------------
        if round_result is None:
            break # Player pressed ESC or closed window - quit to menu
        
        elif round_result:
            # Success - player completed sequence correctly
            player_score += 1  # Increments score
            show_round_feedback(True, player_score, grid_size)
        
        else:
            # Failure - player made a mistake
            show_round_feedback(False, player_score, grid_size)
            player_score = 0  # Resets score, but player can continue

def main():
    """
    Main program entry point - manages top-level menu navigation.
    
    This function controls the overall program flow:
        1. Show main menu
        2. Handle menu selection:
           - Play: Start game loop
           - Help: Show help screen
           - Quit: Exit program
        3. Return to menu after game/help
        4. Repeat until program exit   
    Returns:
        None

    Exit Conditions:
        - User closes window (menu returns None)
        - pygame.quit() and sys.exit() ensure clean shutdown
    """
    clock = pygame.time.Clock()
    
    # Initial fade-in when game starts
    display.fill((0, 0, 0))  # Start with black screen
    pygame.display.update()
    fade_in_screen()
    
    # Main menu loop
    while True:
        # Show menu and get user choice
        menu_choice = display_start_menu()
        
        # ---------------------------------------------------------------------
        # Process Menu Choice
        # ---------------------------------------------------------------------
        if menu_choice is None:
            break # User closed window - exit program
        
        # Start game - run_game() handles all rounds until quit
        elif menu_choice == 'play': 
            run_game()
        
        # Show help screen - returns to menu when done
        elif menu_choice == 'help':
            display_help_screen()
    
    # -------------------------------------------------------------------------
    # Clean Shutdown
    # -------------------------------------------------------------------------
    # Properly close pygame and exit Python
    pygame.quit()
    sys.exit()

# =============================================================================
# PROGRAM EXECUTION
# =============================================================================

if __name__ == "__main__":
    main()
