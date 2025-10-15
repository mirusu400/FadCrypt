"""Snake Game Module for FadCrypt"""

import os
import sys
import json
import time
import random
import threading
import traceback
import pygame


def start_snake_game(gui_instance):
    """Start the snake game in a separate thread"""
    # Get resource_path function from gui_instance
    if hasattr(gui_instance, 'resource_path'):
        resource_path = gui_instance.resource_path
    else:
        # Fallback resource_path if not available
        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
    
    def run_snake_game():
        try:
            # Initialize Pygame
            pygame.init()

            # Direction constants (must be defined before Snake class)
            UP = (0, -1)
            DOWN = (0, 1)
            LEFT = (-1, 0)
            RIGHT = (1, 0)

            # Colors
            BLACK = (0, 0, 0)
            WHITE = (255, 255, 255)
            RED = (255, 0, 0)
            GREEN = (0, 255, 0)
            YELLOW = (255, 255, 0)
            TRANSPARENT = (0, 0, 0)

            # New dark mode colors
            DARK_GRAY = (30, 30, 30)
            DARKER_GRAY = (20, 20, 20)
            OBSTACLE_COLOR = (100, 100, 100)  # Single color for obstacles

            # Game settings
            FPS = 14

            # Pygame setup
            info = pygame.display.Info()
            WINDOW_WIDTH = info.current_w
            WINDOW_HEIGHT = info.current_h
            
            window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
            pygame.display.set_caption('Minimal Snake Game - FadSec-Lab')
            clock = pygame.time.Clock()

            # Fonts
            font_small = pygame.font.SysFont('arial', 25)
            font_medium = pygame.font.SysFont('arial', 50)
            font_large = pygame.font.SysFont('arial', 80)
            print("Fonts loaded successfully")

            # Calculate game area to maintain aspect ratio
            game_area_height = int(WINDOW_HEIGHT * 0.9)
            game_area_width = int(game_area_height * 4 / 3)
            if game_area_width > int(WINDOW_WIDTH * 0.9):
                game_area_width = int(WINDOW_WIDTH * 0.9)
                game_area_height = int(game_area_width * 3 / 4)


            game_area_top = (WINDOW_HEIGHT - game_area_height) // 2
            game_area_left = (WINDOW_WIDTH - game_area_width) // 2

            BLOCK_SIZE = min(game_area_width // 60, game_area_height // 45)
            BORDER_WIDTH = 8  # Increase border width for visibility

            class Snake:
                def __init__(self):
                    self.length = 1
                    self.positions = [((game_area_width // 2), (game_area_height // 2))]
                    self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
                    self.color1 = (0, 200, 0)
                    self.color2 = (0, 255, 0)
                    self.score = 0

                def get_head_position(self):
                    return self.positions[0]

                def move(self):
                    cur = self.get_head_position()
                    x, y = self.direction
                    new = (((cur[0] + (x * BLOCK_SIZE)) % (game_area_width - 2*BORDER_WIDTH)), 
                        ((cur[1] + (y * BLOCK_SIZE)) % (game_area_height - 2*BORDER_WIDTH)))
                    
                    if len(self.positions) > 2 and new in self.positions[2:]:
                        return False
                    
                    self.positions.insert(0, new)
                    if len(self.positions) > self.length:
                        self.positions.pop()
                    return True

                def reset(self):
                    self.length = 1
                    self.positions = [((game_area_width // 2), (game_area_height // 2))]
                    self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
                    self.score = 0

                def draw(self, surface):
                    for i, p in enumerate(self.positions):
                        color = self.color1 if i % 2 == 0 else self.color2
                        pygame.draw.rect(surface, color, 
                                        (p[0] + game_area_left + BORDER_WIDTH, 
                                        p[1] + game_area_top + BORDER_WIDTH, 
                                        BLOCK_SIZE, BLOCK_SIZE))

                def handle_keys(self):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            print("handle_keys: Quitting game...")
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_UP:
                                self.turn(UP)
                            elif event.key == pygame.K_DOWN:
                                self.turn(DOWN)
                            elif event.key == pygame.K_LEFT:
                                self.turn(LEFT)
                            elif event.key == pygame.K_RIGHT:
                                self.turn(RIGHT)
                            elif event.key == pygame.K_ESCAPE:
                                return "PAUSE"
                    
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        return "FAST"
                    return "NORMAL"

                def turn(self, direction):
                    if (direction[0] * -1, direction[1] * -1) == self.direction:
                        return
                    else:
                        self.direction = direction

            class Food:
                def __init__(self):
                    self.position = (0, 0)
                    self.color = RED
                    self.randomize_position()

                def randomize_position(self):
                    self.position = (random.randint(0, (game_area_width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE,
                                    random.randint(0, (game_area_height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE)

                def draw(self, surface):
                    pygame.draw.rect(surface, self.color, 
                                    (self.position[0] + game_area_left + BORDER_WIDTH, 
                                    self.position[1] + game_area_top + BORDER_WIDTH, 
                                    BLOCK_SIZE, BLOCK_SIZE))

            class Obstacle:
                def __init__(self):
                    self.positions = []

                def add_obstacle(self):
                    new_pos = (random.randint(0, (game_area_width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE,
                            random.randint(0, (game_area_height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE)
                    if new_pos not in self.positions:
                        self.positions.append(new_pos)

                def draw(self, surface):
                    for pos in self.positions:
                        pygame.draw.rect(surface, OBSTACLE_COLOR, 
                                        (pos[0] + game_area_left + BORDER_WIDTH, 
                                        pos[1] + game_area_top + BORDER_WIDTH, 
                                        BLOCK_SIZE, BLOCK_SIZE))
            
            class PowerUp:
                def __init__(self):
                    self.position = (0, 0)
                    self.color = YELLOW
                    self.active = False
                    self.type = None

                def spawn(self):
                    self.position = (random.randint(0, (game_area_width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE,
                                    random.randint(0, (game_area_height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE)
                    self.type = random.choice(['speed', 'slow', 'shrink'])
                    self.active = True

                def draw(self, surface):
                    if self.active:
                        pygame.draw.rect(surface, self.color, 
                                        (self.position[0] + game_area_left + BORDER_WIDTH, 
                                        self.position[1] + game_area_top + BORDER_WIDTH, 
                                        BLOCK_SIZE, BLOCK_SIZE))

            def draw_patterned_background(surface, rect, color1, color2, block_size):
                for y in range(rect.top, rect.bottom, block_size):
                    for x in range(rect.left, rect.right, block_size):
                        color = color1 if (x // block_size + y // block_size) % 2 == 0 else color2
                        pygame.draw.rect(surface, color, (x, y, block_size, block_size))

            def draw_text(surface, text, size, x, y, color=WHITE):
                try:
                    print(f"draw_text: '{text}' size={size} at ({x},{y}) color={color}")
                    font = pygame.font.SysFont('arial', size)
                    print(f"  Font created: {font}")
                    text_surface = font.render(text, True, color)
                    print(f"  Text surface created: {text_surface.get_size()}")
                    text_rect = text_surface.get_rect()
                    text_rect.midtop = (x, y)
                    print(f"  Text rect: {text_rect}")
                    surface.blit(text_surface, text_rect)
                    print(f"  Text blitted successfully")
                except Exception as e:
                    print(f"ERROR in draw_text: {e}")
                    import traceback
                    traceback.print_exc()

            def show_menu(surface, snake=None, food=None, obstacles=None):
                print("=== SHOW_MENU CALLED ===")
                print(f"Surface: {surface}, Size: {surface.get_size()}")
                surface.fill(BLACK)
                print("Filled screen with BLACK")
                
                # TEST: Draw a big white rectangle in the center
                test_rect = pygame.Rect(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 4, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
                pygame.draw.rect(surface, (255, 255, 255), test_rect)
                print(f"Drew white test rectangle: {test_rect}")
                pygame.display.flip()
                print("Flipped display after white rectangle")
                
                import time
                time.sleep(2)  # Wait 2 seconds so you can see the white rectangle
                
                surface.fill(BLACK)
                print("Re-filled screen with BLACK")
                
                # If game objects exist, draw them in the background
                if snake and food and obstacles:
                    print("Drawing game objects in background")
                    # Draw patterned background
                    draw_patterned_background(surface, 
                                            pygame.Rect(game_area_left + BORDER_WIDTH, 
                                                        game_area_top + BORDER_WIDTH, 
                                                        game_area_width - 1.5*BORDER_WIDTH, 
                                                        game_area_height - 2*BORDER_WIDTH),
                                            DARK_GRAY, DARKER_GRAY, BLOCK_SIZE)
                    
                    # Draw game objects
                    snake.draw(surface)
                    food.draw(surface)
                    obstacles.draw(surface)
                    
                    # Draw semi-transparent overlay
                    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                    overlay.set_alpha(180)
                    overlay.fill(BLACK)
                    surface.blit(overlay, (0, 0))
                else:
                    print("No game objects - showing clean welcome screen")
                
                # Draw menu text
                print("Drawing menu text...")
                draw_text(surface, "SNAKE GAME", 80, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 6, GREEN)
                print("Drew title")
                
                # Draw controls/instructions
                y_offset = WINDOW_HEIGHT // 3
                draw_text(surface, "CONTROLS:", 40, WINDOW_WIDTH // 2, y_offset, YELLOW)
                y_offset += 60
                draw_text(surface, "Arrow Keys - Move the snake", 30, WINDOW_WIDTH // 2, y_offset)
                y_offset += 45
                draw_text(surface, "SHIFT (hold) - Move faster", 30, WINDOW_WIDTH // 2, y_offset)
                y_offset += 45
                draw_text(surface, "ESC - Pause game", 30, WINDOW_WIDTH // 2, y_offset)
                y_offset += 70
                
                # Draw start/quit instructions
                draw_text(surface, "Press SPACE to start", 50, WINDOW_WIDTH // 2, y_offset, GREEN)
                y_offset += 60
                draw_text(surface, "Press Q to quit", 40, WINDOW_WIDTH // 2, y_offset, RED)
                print("All text drawn, calling pygame.display.flip()")
                
                pygame.display.flip()
                print("Display flipped, waiting for input...")
                waiting = True
                while waiting:
                    clock.tick(FPS)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_SPACE:
                                waiting = False
                            elif event.key == pygame.K_q:
                                pygame.quit()
                                sys.exit()

            def pause_menu(surface):
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.set_alpha(128)
                overlay.fill(BLACK)
                surface.blit(overlay, (0, 0))
                draw_text(surface, "PAUSED", 80, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4)
                draw_text(surface, "Press SPACE to continue", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
                draw_text(surface, "Press Q to quit", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT * 3 // 4)
                pygame.display.flip()
                waiting = True
                while waiting:
                    clock.tick(FPS)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_SPACE:
                                return "CONTINUE"
                            elif event.key == pygame.K_q:
                                return "QUIT"

            def game_over(surface, score, high_score):
                surface.fill(BLACK)
                draw_text(surface, "GAME OVER", 80, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4)
                draw_text(surface, f"Score: {score}", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
                draw_text(surface, f"High Score: {high_score}", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
                draw_text(surface, "Press SPACE to play again", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT * 3 // 4)
                draw_text(surface, "Press Q to quit", 50, WINDOW_WIDTH // 2, WINDOW_HEIGHT * 7 // 8)
                pygame.display.flip()
                waiting = True
                while waiting:
                    clock.tick(FPS)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_SPACE:
                                return "PLAY_AGAIN"
                            elif event.key == pygame.K_q:
                                return "QUIT"

            def load_high_score():
                try:
                    # Get the FadCrypt folder path using the gui_instance
                    if hasattr(gui_instance, 'app_locker'):
                        folder_path = gui_instance.app_locker.get_fadcrypt_folder()
                    else:
                        # For PyQt6, use a default folder
                        folder_path = os.path.join(os.path.expanduser('~'), '.FadCrypt')
                        os.makedirs(folder_path, exist_ok=True)
                    # Define the full path to the snake_high_score.json file
                    file_path = os.path.join(folder_path, "snake_high_score.json")
                    # Load the high score from the file
                    with open(file_path, "r") as f:
                        return json.load(f)["high_score"]
                except (FileNotFoundError, json.JSONDecodeError, KeyError):
                    return 0

            def save_high_score(high_score):
                try:
                    # Get the FadCrypt folder path using the gui_instance
                    if hasattr(gui_instance, 'app_locker'):
                        folder_path = gui_instance.app_locker.get_fadcrypt_folder()
                    else:
                        # For PyQt6, use a default folder
                        folder_path = os.path.join(os.path.expanduser('~'), '.FadCrypt')
                        os.makedirs(folder_path, exist_ok=True)
                    # Define the full path to the snake_high_score.json file
                    file_path = os.path.join(folder_path, "snake_high_score.json")
                    # Save the high score to the file
                    with open(file_path, "w") as f:
                        json.dump({"high_score": high_score}, f)
                except Exception as e:
                    print(f"Error saving high score: {e}")
                    

            def main():
                # Show initial welcome menu (before creating game objects)
                show_menu(window)
                
                snake = Snake()
                food = Food()
                obstacles = Obstacle()
                power_up = PowerUp()
                
                high_score = load_high_score()
                
                level = 1
                obstacles_per_level = 5
                
                for _ in range(obstacles_per_level):
                    obstacles.add_obstacle()

                while True:
                    # After first game, show menu with game preview
                    if snake.score > 0 or len(snake.positions) > 1:
                        show_menu(window, snake, food, obstacles)
                    
                    game_over_flag = False
                    power_up_timer = 0
                    speed_modifier = 0
                    
                    while not game_over_flag:
                        move_speed = FPS + speed_modifier
                        action = snake.handle_keys()
                        if action == "PAUSE":
                            pause_action = pause_menu(window)
                            if pause_action == "QUIT":
                                pygame.quit()
                                sys.exit()
                            continue
                        elif action == "FAST":
                            move_speed = FPS + 10
                        
                        clock.tick(move_speed)
                        
                        if not snake.move():
                            game_over_flag = True
                            break
                        
                        head_pos = snake.get_head_position()
                        if (abs(head_pos[0] - food.position[0]) < BLOCK_SIZE and 
                            abs(head_pos[1] - food.position[1]) < BLOCK_SIZE):
                            snake.length += 1
                            snake.score += 10
                            food.randomize_position()
                            while any(abs(food.position[0] - obs[0]) < BLOCK_SIZE and 
                                    abs(food.position[1] - obs[1]) < BLOCK_SIZE 
                                    for obs in obstacles.positions + snake.positions):
                                food.randomize_position()
                            if snake.score % 50 == 0:
                                level += 1
                                for _ in range(obstacles_per_level):
                                    obstacles.add_obstacle()
                        
                        if not power_up.active and random.randint(1, 100) == 1:
                            power_up.spawn()
                            while any(abs(power_up.position[0] - obs[0]) < BLOCK_SIZE and 
                                    abs(power_up.position[1] - obs[1]) < BLOCK_SIZE 
                                    for obs in obstacles.positions + snake.positions + [food.position]):
                                power_up.spawn()
                        
                        if power_up.active and (abs(head_pos[0] - power_up.position[0]) < BLOCK_SIZE and 
                                                abs(head_pos[1] - power_up.position[1]) < BLOCK_SIZE):
                            if power_up.type == 'speed':
                                speed_modifier = 5
                            elif power_up.type == 'slow':
                                speed_modifier = -5
                            elif power_up.type == 'shrink':
                                snake.length = max(1, snake.length - 2)
                            power_up.active = False
                            power_up_timer = pygame.time.get_ticks()
                        
                        if pygame.time.get_ticks() - power_up_timer > 5000:
                            speed_modifier = 0
                        
                        if any(abs(head_pos[0] - obs[0]) < BLOCK_SIZE and 
                            abs(head_pos[1] - obs[1]) < BLOCK_SIZE 
                            for obs in obstacles.positions):
                            game_over_flag = True
                            break

                        # Clear the entire window
                        window.fill(BLACK)
                        
                        # Draw patterned background with new dark mode colors
                        draw_patterned_background(window, 
                                                pygame.Rect(game_area_left + BORDER_WIDTH, 
                                                            game_area_top + BORDER_WIDTH, 
                                                            game_area_width - 1.5*BORDER_WIDTH, 
                                                            game_area_height - 2*BORDER_WIDTH),
                                                DARK_GRAY, DARKER_GRAY, BLOCK_SIZE)
                        
                        # Draw game area border
                        # pygame.draw.rect(window, BLACK, 
                        #                 (game_area_left, game_area_top, game_area_width, game_area_height), 
                        #                 BORDER_WIDTH)
                        
                        snake.draw(window)
                        food.draw(window)
                        obstacles.draw(window)
                        if power_up.active:
                            power_up.draw(window)
                        
                        # Load the logo
                        logo = pygame.image.load(resource_path("img/fadsec.png"))  # Ensure 'fadsec.png' is in the same directory
                        # Determine the new size for the logo
                        scale_factor = 0.5  # Scale to 50% of the original size
                        logo_width, logo_height = logo.get_size()
                        new_logo_width = int(logo_width * scale_factor)
                        new_logo_height = int(logo_height * scale_factor)

                        # Scale the logo
                        scaled_logo = pygame.transform.scale(logo, (new_logo_width, new_logo_height))

                        # Position for the bottom center
                        logo_x = (WINDOW_WIDTH - new_logo_width) // 2  # Center horizontally
                        logo_y = WINDOW_HEIGHT - new_logo_height - -50  # 10 pixels from the bottom
                        

                        draw_text(window, f"Score: {snake.score}", 25, WINDOW_WIDTH - 70, 10)
                        draw_text(window, f"High Score: {high_score}", 25, WINDOW_WIDTH - 100, 40)
                        draw_text(window, f"Level: {level}", 25, 70, 10)
                        draw_text(window, "Press ESC to pause, and hold SHIFT to move faster.", 25, WINDOW_WIDTH // 2, 10)

                        # Draw the scaled logo
                        window.blit(scaled_logo, (logo_x, logo_y))
                        
                        # # logo in gray at the bottom left
                        # logo_text = "FadSec-Lab © 2024-2025"
                        # logo_color = (169, 169, 169)  # Gray color (RGB)
                        # # the value after logo text is for font
                        # draw_text(window, logo_text, 15, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40, color=logo_color)
                        
                        pygame.display.update()
                    
                    if snake.score > high_score:
                        high_score = snake.score
                        save_high_score(high_score)
                    
                    action = game_over(window, snake.score, high_score)
                    if action == "QUIT":
                        pygame.quit()
                        sys.exit()
                    snake.reset()
                    level = 1
                    obstacles = Obstacle()
                    for _ in range(obstacles_per_level):
                        obstacles.add_obstacle()

            # Start the main game loop
            main()
        
        except Exception as e:
            print(f"!!! SNAKE GAME ERROR: {e}")
            import traceback
            traceback.print_exc()
            pygame.quit()

    # Run the game in a new thread
    snake_game_thread = threading.Thread(target=run_snake_game)
    snake_game_thread.daemon = True
    snake_game_thread.start()





