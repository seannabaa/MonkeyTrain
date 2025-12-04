import pygame
import random
import time

#Initialize pygame modules
pygame.init()

# =============================================================================
#Constants - Game Configurations
# =============================================================================

#Window Dimensions
Width = 1920
Height = 1080

#Colour definitions (RGB tuples)
colour_bg = (30, 40, 40)
colour_tile_reveealed = (70, 80, 100)
colour_tile_hidden = (110, 120, 140)
colour_text = (255, 255, 255)
colour_sucess = (100, 200, 100)
colour_failure = (200, 100, 100)

#font settings
font_large = pygame.font.SysFont("calibri", 40)
font_small = pygame.font.SysFont("calibri", 28)

#Game settings
base_display_time = 5.0 #Seconds to show numbers
tile_size = 100
tile_padding = 10


#Create the game window - dimensions must be passed with a tuple (width, height)
window = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("MonkeyTrain")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def draw_text(surface, text, x, y, font, colour):
    text_image = font.render(text, True, colour)
    surface.blit(text_image, (x, y))


def draw_text_centered(surface, text, y, font, colour):
     text_image = font.render(text, True, colour)
     x = (Width - text_image.get_width()) // 2
     surface.blit(text_image, (x, y))


def generate_grid(grid_size):
     numbers = list(range(1, grid_size * grid_size + 1))
     random.shuffle(numbers)

     #Build the 2D Grid
     grid = []
     index = 0

     for row in range(grid_size):
        current_row = []
        for col in range(grid_size):
            current_row.append(numbers[index])
            index += 1
        grid.append(current_row)
    
        return grid

def get_tile_position(grid_size):
    total_width = grid_size * tile_size + (grid_size - 1) * tile_padding
    start_x = (Width - total_width) // 2
    start_y = 180

    positions = []

    for row in range(grid_size):
        current_row = []
        for col in range(grid_size):
            x = start_x + col * (tile_size + tile_padding)
            y = start_y + row * (tile_size + tile_padding)
            current_row.append((x, y, tile_size))
        positions.append(current_row)

    return positions

def draw_grid(grid, positions, reveal):
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            x, y, size = positions[row][col]
            
            if reveal:
                # Draw tile with visible number
                pygame.draw.rect(window, colour_tile_reveealed, (x, y, size, size))
                # Center the number on the tile
                number_text = str(grid[row][col])
                text_surface = font_large.render(number_text, True, colour_text)
                text_x = x + (size - text_surface.get_width()) // 2
                text_y = y + (size - text_surface.get_height()) // 2
                window.blit(text_surface, (text_x, text_y))
            else:
                # Draw hidden tile
                pygame.draw.rect(window, colour_tile_hidden, (x, y, size, size))

def get_clicked_tile_value(mouse_pos, grid, positions):

    mouse_x, mouse_y = mouse_pos

    for row in range(len(positions)):
        for col in range(len(positions[row])):
            x, y, size = positions[row][col]
            #check if click is within tile bounds
            if x <= mouse_x <= x + size and y <= mouse_y <= y + size:
                return grid[row][col]
    
    return None

def calculate_difficulty(score):
    if score < 3:
        return 3, base_display_time + 0.3
    elif score < 7:
        return 4, base_display_time
    else:
        return 5, base_display_time - 0.2
    
# =============================================================================
# GAME STATE FUNCTIONS
# =============================================================================


def run_round(level_size, reveal_time):

# Generate the game grid and get tile positions
    grid = generate_grid(level_size)
    positions = get_tile_position(level_size)
    
    # Create the correct sequence (1, 2, 3, ... n)
    correct_sequence = list(range(1, level_size * level_size + 1))
    
    # Game state variables
    is_showing_numbers = True
    show_start_time = pygame.time.get_ticks()
    user_sequence = []
    running = True
    
    while running:
        # Clear the screen
        window.fill(colour_bg)
        
        # Draw title and instructions
        draw_text_centered(window, "MonkeyTrain", 30, font_large, colour_text)
        draw_text_centered(window, "Memorize the numbers, then click in order: 1, 2, 3...", 90, font_small, colour_text)
        
        # Calculate elapsed time
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - show_start_time) / 1000
        
        # Handle reveal phase timing
        if is_showing_numbers:
            draw_grid(grid, positions, reveal=True)
            if elapsed_seconds > reveal_time:
                is_showing_numbers = False
        else:
            draw_grid(grid, positions, reveal=False)
        
        # Update the display
        pygame.display.update()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            # Handle mouse clicks during play phase
            if event.type == pygame.MOUSEBUTTONDOWN and not is_showing_numbers:
                mouse_pos = pygame.mouse.get_pos()
                clicked_value = get_clicked_tile_value(mouse_pos, grid, positions)
                
                # Debug print - remove after testing
                print(f"Mouse clicked at: {mouse_pos}, Clicked value: {clicked_value}")
                
                if clicked_value is not None:
                    user_sequence.append(clicked_value)
                    current_index = len(user_sequence) - 1
                    
                    # Debug print - remove after testing
                    print(f"User sequence: {user_sequence}, Expected: {correct_sequence[current_index]}")
                    
                    # Check if the clicked number is correct
                    if user_sequence[current_index] != correct_sequence[current_index]:
                        return False  # Wrong answer
                    
                    # Check if sequence is complete
                    if len(user_sequence) == len(correct_sequence):
                        return True  # Round completed successfully
    
    return None

def show_start_screen():
    """
    Displays the game's start screen and waits for player input.
    
    Returns:
        bool: True if player wants to start, False if they quit
    """
    waiting = True
    
    while waiting:
        window.fill(colour_bg)
        draw_text_centered(window, "MonkeyTrain", 200, font_large, colour_text)
        draw_text_centered(window, "A Memory Training Game", 260, font_small, colour_text)
        draw_text_centered(window, "Click anywhere to start!", 340, font_small, colour_text)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                return True
    
    return False

def show_feedback_screen(is_correct, score):
    window.fill(colour_bg)
    
    if is_correct:
        draw_text_centered(window, "Correct!", 250, font_large, colour_sucess)
    else:
        draw_text_centered(window, "Wrong! Try Again", 250, font_large, colour_failure)
    
    draw_text_centered(window, "Score: " + str(score), 330, font_small, colour_text)
    
    pygame.display.update()
    time.sleep(1.5)

def game_loop():

    score = 0
    running = True

    while running:
        # Get difficulty settings based on current score
        grid_size, display_time = calculate_difficulty(score)

        # Run a round and get the result
        result = run_round(grid_size, display_time)
        
        # Handle the result
        if result is None:
            # Player quit the game
            running = False
        elif result is True:
            # Player completed the round successfully
            score += 1
            show_feedback_screen(True, score)
        else:
            # Player made a mistake
            show_feedback_screen(False, score)
            score = 0  # Reset score on failure
    
def main():
    """
    Main entry point for the game.
    Initializes the game and starts the main loop.
    
    Returns:
        None
    """
    if show_start_screen():
        game_loop()
    
    pygame.quit()


# =============================================================================
# PROGRAM ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
