
import pygame
import random
import time
import os

# Initialize pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
ROAD_WIDTH, LANE_COUNT = 300, 3
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT
FPS = 60

# Colors
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
YELLOW, GRAY = (255, 255, 0), (100, 100, 100)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing Game")
clock = pygame.time.Clock()

# Load/Create assets
def create_car_surface(color, width=40, height=60):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surface, color, (0, 0, width, height), border_radius=5)
    pygame.draw.rect(surface, BLACK, (0, 0, width, height), 2, border_radius=5)
    pygame.draw.rect(surface, BLACK, (5, 5, width-10, 10))
    pygame.draw.rect(surface, BLACK, (5, height-15, width-10, 10))
    return surface

# Player Car
player_car = create_car_surface(RED)
player_y = HEIGHT - 100
player_speed = 5
player_lane = 1
player_x = (WIDTH - ROAD_WIDTH) // 2 + player_lane * LANE_WIDTH + (LANE_WIDTH - player_car.get_width()) // 2

# Enemy Car Class
class EnemyCar:
    def __init__(self):
        self.width, self.height = 40, 60
        self.lane = random.randint(0, LANE_COUNT - 1)
        self.x = (WIDTH - ROAD_WIDTH) // 2 + self.lane * LANE_WIDTH + (LANE_WIDTH - self.width) // 2
        self.y = -self.height
        self.speed = random.randint(3, 7)
        self.color = random.choice([BLUE, GREEN, YELLOW])
        self.surface = create_car_surface(self.color)

    def move(self):
        self.y += self.speed

    def draw(self):
        screen.blit(self.surface, (self.x, self.y))

    def is_off_screen(self):
        return self.y > HEIGHT

# High Score
high_score_file = "high_score.txt"
high_score = 0
if os.path.exists(high_score_file):
    try:
        with open(high_score_file, "r") as f:
            high_score = int(f.read().strip())
    except:
        pass

# Road Markings
road_marks = [pygame.Rect(WIDTH // 2 - 5, i * 40, 10, 20) for i in range(-1, HEIGHT // 40 + 1)]

# Game Variables
enemy_cars, spawn_timer = [], 0
score, speed_factor = 0, 1.0
game_started, game_over = False, False

# Main Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not game_started:
                game_started = True
            elif game_over:
                # Reset game
                enemy_cars.clear()
                score = 0
                speed_factor = 1.0
                game_over = False
                player_lane = 1
                player_x = (WIDTH - ROAD_WIDTH) // 2 + player_lane * LANE_WIDTH + (LANE_WIDTH - player_car.get_width()) // 2
            elif event.key == pygame.K_LEFT and player_lane > 0:
                player_lane -= 1
            elif event.key == pygame.K_RIGHT and player_lane < LANE_COUNT - 1:
                player_lane += 1

    # Screens
    if not game_started:
        screen.fill(BLACK)
        font_big = pygame.font.SysFont(None, 64)
        font_med = pygame.font.SysFont(None, 36)
        font_small = pygame.font.SysFont(None, 24)
        screen.blit(font_big.render("CAR RACING", True, WHITE), (WIDTH//2 - 150, HEIGHT//3))
        screen.blit(font_med.render("High Score: {}".format(high_score), True, YELLOW), (WIDTH//2 - 90, HEIGHT//2 - 50))
        screen.blit(font_med.render("Press any key to start", True, WHITE), (WIDTH//2 - 130, HEIGHT//2))
        screen.blit(font_small.render("Use LEFT and RIGHT arrow keys to move", True, WHITE), (WIDTH//2 - 160, HEIGHT//2 + 50))
        pygame.display.flip()
        clock.tick(FPS)
        continue

    if game_over:
        screen.fill(BLACK)
        font_big = pygame.font.SysFont(None, 64)
        font_med = pygame.font.SysFont(None, 36)
        screen.blit(font_big.render("GAME OVER", True, RED), (WIDTH//2 - 150, HEIGHT//3))
        screen.blit(font_med.render(f"Score: {score}", True, WHITE), (WIDTH//2 - 60, HEIGHT//2))
        screen.blit(font_med.render(f"High Score: {high_score}", True, YELLOW), (WIDTH//2 - 90, HEIGHT//2 + 50))
        screen.blit(font_med.render("Press any key to restart", True, WHITE), (WIDTH//2 - 140, HEIGHT//2 + 100))
        pygame.display.flip()
        clock.tick(FPS)
        continue

    # Game Logic
    target_x = (WIDTH - ROAD_WIDTH) // 2 + player_lane * LANE_WIDTH + (LANE_WIDTH - player_car.get_width()) // 2
    player_x += player_speed if player_x < target_x else -player_speed if player_x > target_x else 0

    spawn_timer += 1
    if spawn_timer > FPS // speed_factor:
        enemy_cars.append(EnemyCar())
        spawn_timer = 0

    for car in enemy_cars[:]:
        car.move()
        if car.is_off_screen():
            enemy_cars.remove(car)
            score += 1
            if score % 10 == 0:
                speed_factor += 0.2

    # Update road markings
    for mark in road_marks:
        mark.y += 5 * speed_factor
        if mark.y > HEIGHT:
            mark.y = -40

    # Collision detection
    player_rect = pygame.Rect(player_x, player_y, player_car.get_width(), player_car.get_height())
    for car in enemy_cars:
        car_rect = pygame.Rect(car.x, car.y, car.width, car.height)
        if player_rect.colliderect(car_rect):
            if score > high_score:
                high_score = score
                with open(high_score_file, "w") as f:
                    f.write(str(high_score))
            game_over = True

    # Drawing
    screen.fill(BLACK)
    road_x = (WIDTH - ROAD_WIDTH) // 2
    pygame.draw.rect(screen, GRAY, (road_x, 0, ROAD_WIDTH, HEIGHT))

    for i in range(1, LANE_COUNT):
        lane_x = road_x + i * LANE_WIDTH - 5
        for y in range(-40, HEIGHT, 40):
            pygame.draw.rect(screen, WHITE, (lane_x, y + int(time.time() * 250) % 40, 10, 20))

    screen.blit(player_car, (player_x, player_y))
    for car in enemy_cars:
        car.draw()

    font = pygame.font.SysFont(None, 36)
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"High Score: {high_score}", True, YELLOW), (10, 50))

    pygame.display.flip()
    clock.tick(FPS)

# Save final score
if score > high_score:
    with open(high_score_file, "w") as f:
        f.write(str(score))

pygame.quit()
