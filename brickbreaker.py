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
pygame.display.set_caption("Breakout - Line & Circle Algorithm")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)

# Brick colors for different rows
BRICK_COLORS = [RED, ORANGE, YELLOW, GREEN, CYAN, PURPLE]

# ==================== LINE ALGORITHM (Bresenham's Line) ====================
def draw_line_bresenham(x1, y1, x2, y2, color, width=1):
    """Draw a line using Bresenham's line algorithm"""
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    
    points = []
    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    
    # Draw the line points
    for px, py in points:
        if width == 1:
            screen.set_at((px, py), color)
        else:
            # For thicker lines, draw surrounding pixels
            for w in range(-width//2, width//2 + 1):
                for h in range(-width//2, width//2 + 1):
                    if 0 <= px + w < WIDTH and 0 <= py + h < HEIGHT:
                        screen.set_at((px + w, py + h), color)

# ==================== CIRCLE ALGORITHM (Midpoint Circle) ====================
def draw_circle_midpoint(cx, cy, radius, color, fill=True):
    """Draw a circle using Midpoint Circle Algorithm"""
    points = []
    x = 0
    y = radius
    d = 1 - radius
    
    # Symmetry points for all 8 octants
    def add_circle_points(cx, cy, x, y):
        points.extend([
            (cx + x, cy + y), (cx - x, cy + y),
            (cx + x, cy - y), (cx - x, cy - y),
            (cx + y, cy + x), (cx - y, cy + x),
            (cx + y, cy - x), (cx - y, cy - x)
        ])
    
    while x <= y:
        add_circle_points(cx, cy, x, y)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
    
    if fill:
        # Fill the circle using scanline approach
        for px, py in points:
            # Draw horizontal line at each y coordinate
            y_level = py
            x_coords = []
            for p in points:
                if p[1] == y_level:
                    x_coords.append(p[0])
            if x_coords:
                x_min = min(x_coords)
                x_max = max(x_coords)
                for px in range(x_min, x_max + 1):
                    if 0 <= px < WIDTH and 0 <= y_level < HEIGHT:
                        screen.set_at((px, y_level), color)
    else:
        # Just draw the outline
        for px, py in points:
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                screen.set_at((px, py), color)

# ==================== LINE-CIRCLE COLLISION DETECTION ====================
def distance_point_to_line(px, py, x1, y1, x2, y2):
    """Calculate distance from point to line segment using vector math"""
    # Vector from start to end
    dx = x2 - x1
    dy = y2 - y1
    
    # Vector from start to point
    px_dx = px - x1
    px_dy = py - y1
    
    # Length squared of line
    line_len_sq = dx*dx + dy*dy
    
    if line_len_sq == 0:
        # Line is a point
        return math.sqrt(px_dx*px_dx + px_dy*px_dy)
    
    # Project point onto line
    t = (px_dx * dx + px_dy * dy) / line_len_sq
    t = max(0, min(1, t))  # Clamp to segment
    
    # Closest point on line segment
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    
    # Distance from point to closest point
    dist_x = px - closest_x
    dist_y = py - closest_y
    
    return math.sqrt(dist_x*dist_x + dist_y*dist_y)

def circle_line_collision(circle_x, circle_y, radius, x1, y1, x2, y2):
    """Check if circle collides with line segment"""
    dist = distance_point_to_line(circle_x, circle_y, x1, y1, x2, y2)
    return dist <= radius

def get_circle_line_collision_point(circle_x, circle_y, radius, x1, y1, x2, y2):
    """Get the collision point and normal for circle-line collision"""
    # Vector from start to end
    dx = x2 - x1
    dy = y2 - y1
    
    # Vector from start to circle center
    px_dx = circle_x - x1
    px_dy = circle_y - y1
    
    line_len_sq = dx*dx + dy*dy
    
    if line_len_sq == 0:
        return (x1, y1), (circle_x - x1, circle_y - y1)
    
    # Project circle center onto line
    t = (px_dx * dx + px_dy * dy) / line_len_sq
    t = max(0, min(1, t))
    
    # Closest point on line
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    
    # Normal vector from closest point to circle center
    nx = circle_x - closest_x
    ny = circle_y - closest_y
    dist = math.sqrt(nx*nx + ny*ny)
    
    if dist > 0:
        nx /= dist
        ny /= dist
    
    return (closest_x, closest_y), (nx, ny)

# ==================== PADDLE CLASS ====================
class Paddle:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED
        # Store paddle as line segments for collision
        self.top_line = None
        self.left_line = None
        self.right_line = None
        self.update_lines()

    def update_lines(self):
        """Update paddle line segments for collision detection"""
        # Top edge (line)
        self.top_line = (self.rect.left, self.rect.top, self.rect.right, self.rect.top)
        # Left edge
        self.left_line = (self.rect.left, self.rect.top, self.rect.left, self.rect.bottom)
        # Right edge
        self.right_line = (self.rect.right, self.rect.top, self.rect.right, self.rect.bottom)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        self.update_lines()

    def draw(self):
        # Draw paddle using line algorithm
        x1, y1, x2, y2 = self.top_line
        draw_line_bresenham(x1, y1, x2, y2, BRIGHT_GREEN, 3)
        
        # Draw left and right edges
        x1, y1, x2, y2 = self.left_line
        draw_line_bresenham(x1, y1, x2, y2, LIGHT_GREEN, 2)
        x1, y1, x2, y2 = self.right_line
        draw_line_bresenham(x1, y1, x2, y2, LIGHT_GREEN, 2)

# ==================== BALL CLASS ====================
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

        # Wall collision using circle-line collision
        # Left wall
        if circle_line_collision(self.x, self.y, self.radius, 0, 0, 0, HEIGHT):
            self.x = self.radius
            self.dx = -self.dx
        
        # Right wall
        if circle_line_collision(self.x, self.y, self.radius, WIDTH, 0, WIDTH, HEIGHT):
            self.x = WIDTH - self.radius
            self.dx = -self.dx
        
        # Top wall
        if circle_line_collision(self.x, self.y, self.radius, 0, 0, WIDTH, 0):
            self.y = self.radius
            self.dy = -self.dy
        
        # Bottom (game over)
        if circle_line_collision(self.x, self.y, self.radius, 0, HEIGHT, WIDTH, HEIGHT):
            return True

        # Paddle collision using circle-line collision
        if self.dy > 0:
            # Check collision with paddle's top edge
            x1, y1, x2, y2 = paddle.top_line
            if circle_line_collision(self.x, self.y, self.radius, x1, y1, x2, y2):
                # Calculate hit position for angle
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
        # Draw ball using circle algorithm
        draw_circle_midpoint(int(self.x), int(self.y), self.radius, WHITE, fill=True)
        # Draw outline
        draw_circle_midpoint(int(self.x), int(self.y), self.radius, (200, 200, 200), fill=False)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

# ==================== BRICK CLASS ====================
class Brick:
    def __init__(self, x, y, row):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = BRICK_COLORS[row % len(BRICK_COLORS)]
        # Store brick as 4 line segments
        self.lines = [
            (self.rect.left, self.rect.top, self.rect.right, self.rect.top),      # Top
            (self.rect.right, self.rect.top, self.rect.right, self.rect.bottom),  # Right
            (self.rect.right, self.rect.bottom, self.rect.left, self.rect.bottom), # Bottom
            (self.rect.left, self.rect.bottom, self.rect.left, self.rect.top)     # Left
        ]

    def draw(self):
        # Draw brick outline and fill using line algorithm
        # Fill the brick by drawing horizontal lines
        for y in range(self.rect.top, self.rect.bottom):
            draw_line_bresenham(self.rect.left, y, self.rect.right, y, self.color, 1)
        
        # Draw border lines
        for line in self.lines:
            x1, y1, x2, y2 = line
            draw_line_bresenham(x1, y1, x2, y2, WHITE, 1)

# ==================== GAME FUNCTIONS ====================
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

def check_brick_collision(ball, brick):
    """Check circle-line collision with all 4 edges of brick"""
    for line in brick.lines:
        x1, y1, x2, y2 = line
        if circle_line_collision(ball.x, ball.y, ball.radius, x1, y1, x2, y2):
            # Get collision normal for reflection
            _, normal = get_circle_line_collision_point(ball.x, ball.y, ball.radius, x1, y1, x2, y2)
            
            # Reflect ball based on normal
            # For horizontal edges, reverse dy
            if y1 == y2:  # Horizontal edge
                ball.dy = -ball.dy
                # Adjust position
                if y1 < ball.y:
                    ball.y = y1 - ball.radius
                else:
                    ball.y = y1 + ball.radius
            else:  # Vertical edge
                ball.dx = -ball.dx
                # Adjust position
                if x1 < ball.x:
                    ball.x = x1 - ball.radius
                else:
                    ball.x = x1 + ball.radius
            
            return True
    return False

# ==================== MAIN GAME LOOP ====================
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
                if event.key == pygame.K_p and not game_over and not game_won:
                    paused = not paused
                
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
                
                if event.key == pygame.K_SPACE and not ball.launched and not game_over and not game_won and not paused:
                    ball.launch(paddle)
                
                if event.key == pygame.K_e and (game_over or game_won):
                    running = False
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Speed adjustment
                if not game_over and not game_won:
                    if event.key == pygame.K_1:
                        PADDLE_SPEED = min(PADDLE_SPEED + 1, 20)
                        paddle.speed = PADDLE_SPEED
                    
                    if event.key == pygame.K_2:
                        PADDLE_SPEED = max(PADDLE_SPEED - 1, 2)
                        paddle.speed = PADDLE_SPEED
                    
                    if event.key == pygame.K_3:
                        BALL_SPEED = min(BALL_SPEED + 1, 15)
                        if ball.launched:
                            current_speed = math.sqrt(ball.dx**2 + ball.dy**2)
                            if current_speed > 0:
                                scale = BALL_SPEED / (current_speed / math.sqrt(2))
                                ball.dx *= scale
                                ball.dy *= scale
                    
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

        # Show launch instruction
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

            # Brick collision using circle-line collision
            if ball.launched:
                for brick in bricks[:]:
                    if check_brick_collision(ball, brick):
                        bricks.remove(brick)
                        score += 10
                        break

            # Check win condition
            if len(bricks) == 0:
                game_won = True

        # Pause overlay
        if paused:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))
            
            pause_text = big_font.render("PAUSED", True, YELLOW)
            pause_rect = pause_text.get_rect(center=(WIDTH // 2, 150))
            screen.blit(pause_text, pause_rect)
            
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
            
            controls_title = font.render("CONTROLS", True, YELLOW)
            controls_title_rect = controls_title.get_rect(center=(WIDTH // 2, 310))
            screen.blit(controls_title, controls_title_rect)
            
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
            
            game_over_text = big_font.render("KHATAM TATA BYE BYE", True, RED)
            text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
            screen.blit(game_over_text, text_rect)
            
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(final_score_text, (WIDTH // 2 - 80, HEIGHT // 2 - 20))
            
            restart_text = font.render("Press 'R' to Restart     Press 'E' to Exit", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - 230, HEIGHT // 2 + 40))

        # Win overlay
        if game_won:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))
            
            win_text = big_font.render("SHABBASH", True, GREEN)
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