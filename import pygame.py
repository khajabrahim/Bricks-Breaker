import pygame
import random
import time
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 10
BALL_RADIUS = 10
BRICK_WIDTH, BRICK_HEIGHT = 75, 20
ROWS, COLS = 5, 10

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
BRIGHT_GREEN = (0, 255, 0)
LIGHT_GREEN = (144, 238, 144)

# Default speed settings
PADDLE_SPEED = 8
BALL_SPEED = 5

# Set up screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout (Brick Breaker)")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)

# Brick colors for different rows
BRICK_COLORS = [RED, ORANGE, YELLOW, GREEN, CYAN, PURPLE]

# Paddle Class
class Paddle:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def draw(self):
        pygame.draw.rect(screen, BRIGHT_GREEN, self.rect)
        pygame.draw.rect(screen, LIGHT_GREEN, self.rect, 3)
        pygame.draw.rect(screen, (0, 255, 0, 50), self.rect.inflate(10, 10), 3)

# BALL CLASS
class Ball:
    def __init__(self, paddle):
        self.radius = BALL_RADIUS
        self.x = paddle.rect.centerx
        self.y = paddle.rect.top - self.radius
        self.dx = BALL_SPEED * random.choice([-1, 1])
        self.dy = -BALL_SPEED
        self.touches = 0
        self.launched = False

    def launch(self, paddle):
        if not self.launched:
            self.x = paddle.rect.centerx
            self.y = paddle.rect.top - self.radius
            self.dx = BALL_SPEED * random.choice([-1, 1])
            self.dy = -BALL_SPEED
            self.launched = True

    def move(self, paddle):
        if not self.launched:
            self.x = paddle.rect.centerx
            self.y = paddle.rect.top - self.radius
            return False
        
        self.x += self.dx
        self.y += self.dy

        if self.x - self.radius <= 0:
            self.x = self.radius
            self.dx = -self.dx
        elif self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.dx = -self.dx
        
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.dy = -self.dy
        
        if self.y + self.radius >= HEIGHT:
            return True

        if self.dy > 0:
            if self.y + self.radius >= paddle.rect.top and self.y + self.radius <= paddle.rect.bottom:
                if self.x >= paddle.rect.left and self.x <= paddle.rect.right:
                    hit_pos = (self.x - paddle.rect.centerx) / (PADDLE_WIDTH / 2)
                    hit_pos = max(-1, min(1, hit_pos))
                    
                    self.dx = hit_pos * BALL_SPEED * 1.5
                    self.dy = -BALL_SPEED
                    
                    if abs(self.dx) < BALL_SPEED * 0.5:
                        self.dx = BALL_SPEED * 0.5 * (1 if self.dx >= 0 else -1)
                    
                    self.y = paddle.rect.top - self.radius
                    self.touches += 1
                    return False

        return False

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (200, 200, 200), (int(self.x), int(self.y)), self.radius, 2)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

# Brick class
class Brick:
    def __init__(self, x, y, row):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = BRICK_COLORS[row % len(BRICK_COLORS)]

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 1)

# Function to reset game
def reset_game():
    global PADDLE_SPEED, BALL_SPEED
    paddle = Paddle()
    ball = Ball(paddle)
    bricks = []
    for row in range(ROWS):
        for col in range(COLS):
            x = col * (BRICK_WIDTH + 5) + 20
            y = row * (BRICK_HEIGHT + 5) + 50
            bricks.append(Brick(x, y, row))
    return paddle, ball, bricks

# Game loop
def main():
    global PADDLE_SPEED, BALL_SPEED
    
    paddle, ball, bricks = reset_game()
    
    running = True
    paused = False
    lives = 3
    score = 0
    misses = 0
    game_start_time = time.time()
    game_over = False
    game_won = False

    while running:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # Pause/Resume
                if event.key == pygame.K_p and not game_over and not game_won:
                    paused = not paused
                
                # Restart
                if event.key == pygame.K_r:
                    paddle, ball, bricks = reset_game()
                    lives = 3
                    score = 0
                    misses = 0
                    game_start_time = time.time()
                    game_over = False
                    game_won = False
                    paused = False
                    PADDLE_SPEED = 8
                    BALL_SPEED = 5
                    paddle.speed = PADDLE_SPEED
                    ball.dx = BALL_SPEED * random.choice([-1, 1])
                    ball.dy = -BALL_SPEED
                
                # Launch ball
                if event.key == pygame.K_SPACE and not ball.launched and not game_over and not game_won and not paused:
                    ball.launch(paddle)
                
                # Exit
                if event.key == pygame.K_e and (game_over or game_won):
                    running = False
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # ===== SPEED ADJUSTMENT KEYS (works even when paused) =====
                if not game_over and not game_won:
                    # Increase paddle speed with '1' key
                    if event.key == pygame.K_1:
                        PADDLE_SPEED = min(PADDLE_SPEED + 1, 20)
                        paddle.speed = PADDLE_SPEED
                    
                    # Decrease paddle speed with '2' key
                    if event.key == pygame.K_2:
                        PADDLE_SPEED = max(PADDLE_SPEED - 1, 2)
                        paddle.speed = PADDLE_SPEED
                    
                    # Increase ball speed with '3' key
                    if event.key == pygame.K_3:
                        BALL_SPEED = min(BALL_SPEED + 1, 15)
                        if ball.launched:
                            current_speed = math.sqrt(ball.dx**2 + ball.dy**2)
                            if current_speed > 0:
                                scale = BALL_SPEED / (current_speed / math.sqrt(2))
                                ball.dx *= scale
                                ball.dy *= scale
                    
                    # Decrease ball speed with '4' key
                    if event.key == pygame.K_4:
                        BALL_SPEED = max(BALL_SPEED - 1, 1)
                        if ball.launched:
                            current_speed = math.sqrt(ball.dx**2 + ball.dy**2)
                            if current_speed > 0:
                                scale = BALL_SPEED / (current_speed / math.sqrt(2))
                                ball.dx *= scale
                                ball.dy *= scale

        # Clear screen
        screen.fill(BLACK)

        # Update game time
        elapsed_time = time.time() - game_start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)

        # Draw UI elements at top
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        misses_text = font.render(f"Misses: {misses}", True, WHITE)
        touches_text = font.render(f"Touches: {ball.touches}", True, WHITE)
        timer_text = font.render(f"Time: {minutes}:{seconds:02d}", True, WHITE)
        score_text = font.render(f"Score: {score}", True, WHITE)
        
        screen.blit(lives_text, (10, 10))
        screen.blit(misses_text, (160, 10))
        screen.blit(touches_text, (320, 10))
        screen.blit(timer_text, (470, 10))
        screen.blit(score_text, (620, 10))

        # Draw bricks
        for brick in bricks:
            brick.draw()

        # Draw paddle and ball
        paddle.draw()
        ball.draw()

        # Show launch instruction (only when ball not launched)
        if not ball.launched and not game_over and not game_won:
            launch_text = font.render("Press SPACE to launch!", True, YELLOW)
            screen.blit(launch_text, (WIDTH // 2 - 120, HEIGHT // 2 - 50))

        # Handle game logic
        if not paused and not game_over and not game_won:
            # Ball movement
            if ball.move(paddle):
                lives -= 1
                misses += 1
                if lives == 0:
                    game_over = True
                else:
                    ball.launched = False
                    ball.x = paddle.rect.centerx
                    ball.y = paddle.rect.top - ball.radius

            # Paddle movement
            paddle.move()

            # Brick collision
            if ball.launched:
                ball_rect = ball.get_rect()
                for brick in bricks[:]:
                    if ball_rect.colliderect(brick.rect):
                        bricks.remove(brick)
                        score += 10
                        
                        overlap_left = ball_rect.right - brick.rect.left
                        overlap_right = brick.rect.right - ball_rect.left
                        overlap_top = ball_rect.bottom - brick.rect.top
                        overlap_bottom = brick.rect.bottom - ball_rect.top
                        
                        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                        
                        if min_overlap == overlap_left or min_overlap == overlap_right:
                            ball.dx = -ball.dx
                        else:
                            ball.dy = -ball.dy
                        
                        if min_overlap == overlap_left:
                            ball.x = brick.rect.left - ball.radius
                        elif min_overlap == overlap_right:
                            ball.x = brick.rect.right + ball.radius
                        elif min_overlap == overlap_top:
                            ball.y = brick.rect.top - ball.radius
                        else:
                            ball.y = brick.rect.bottom + ball.radius
                        
                        break

            # Check win condition
            if len(bricks) == 0:
                game_won = True

        # ===== PAUSE OVERLAY WITH SPEED AND CONTROLS =====
        if paused:
            # Create semi-transparent overlay
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))
            
            # Pause title
            pause_text = big_font.render("PAUSED", True, YELLOW)
            pause_rect = pause_text.get_rect(center=(WIDTH // 2, 150))
            screen.blit(pause_text, pause_rect)
            
            # Current speeds display
            if ball.launched:
                current_speed = math.sqrt(ball.dx**2 + ball.dy**2)
                speed_text = font.render(f"Ball Speed: {current_speed:.1f}", True, WHITE)
            else:
                speed_text = font.render(f"Ball Speed: {BALL_SPEED:.1f}", True, WHITE)
            speed_rect = speed_text.get_rect(center=(WIDTH // 2, 220))
            screen.blit(speed_text, speed_rect)
            
            paddle_speed_text = font.render(f"Paddle Speed: {PADDLE_SPEED}", True, WHITE)
            paddle_speed_rect = paddle_speed_text.get_rect(center=(WIDTH // 2, 260))
            screen.blit(paddle_speed_text, paddle_speed_rect)
            
            # Controls manual
            controls_title = font.render("CONTROLS", True, YELLOW)
            controls_title_rect = controls_title.get_rect(center=(WIDTH // 2, 310))
            screen.blit(controls_title, controls_title_rect)
            
            # Control list
            controls = [
                "1 - Increase Paddle Speed",
                "2 - Decrease Paddle Speed",
                "3 - Increase Ball Speed",
                "4 - Decrease Ball Speed",
                "SPACE - Launch Ball",
                "P - Resume Game",
                "R - Restart Game",
                "ESC - Exit Game"
            ]
            
            y_offset = 350
            for control in controls:
                control_text = small_font.render(control, True, WHITE)
                control_rect = control_text.get_rect(center=(WIDTH // 2, y_offset))
                screen.blit(control_text, control_rect)
                y_offset += 30

        # Game over overlay
        if game_over:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))
            
            game_over_text = big_font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2 - 80))
            
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(final_score_text, (WIDTH // 2 - 80, HEIGHT // 2 - 20))
            
            restart_text = font.render("Press 'R' to Restart     Press 'E' to Exit", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - 230, HEIGHT // 2 + 40))

        # Win overlay
        if game_won:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))
            
            win_text = big_font.render("YOU WIN!", True, GREEN)
            screen.blit(win_text, (WIDTH // 2 - 130, HEIGHT // 2 - 80))
            
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(final_score_text, (WIDTH // 2 - 80, HEIGHT // 2 - 20))
            
            final_time_text = font.render(f"Time: {minutes}:{seconds:02d}", True, WHITE)
            screen.blit(final_time_text, (WIDTH // 2 - 70, HEIGHT // 2 + 20))
            
            restart_text = font.render("Press 'R' to Restart     Press 'E' to Exit", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - 230, HEIGHT // 2 + 60))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()