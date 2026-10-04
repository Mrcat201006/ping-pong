import pygame
import sys

GAME_WIDTH = 1280
GAME_HEIGHT = 720
GRAVITY = 0.3
TWO_PLAYER_MODE = False  # Переключатель режима игры: True для 2 игроков, False для игры против ИИ

# Enemy constants
ENEMY_X = 1000
ENEMY_Y = 100
ENEMY_WIDTH = 90
ENEMY_HEIGHT = 12
ENEMY_SPEED = 5

# Constants ball
BALL_RADIUS = 10
BALL_X = 640
BALL_Y = 360

# Constants player
PLAYER_DISTANCE = 9
PLAYER_X = 150
PLAYER_Y = 600
PLAYER_WIDTH = 90
PLAYER_HEIGHT = 12

pygame.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
clock = pygame.time.Clock()
font_large = pygame.font.SysFont("Arial", 50, bold=True)
font_medium = pygame.font.SysFont("Arial", 32)

# Переменные состояния игры
game_state = "MENU"  # Состояния: "MENU" или "GAME"
TWO_PLAYER_MODE = False

player_score = 0
enemy_score = 0


class Player(pygame.Rect):
    def __init__(self):
        super().__init__(PLAYER_X, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT)


class Ball(pygame.Rect):
    def __init__(self):
        super().__init__(BALL_X, BALL_Y, BALL_RADIUS * 2, BALL_RADIUS * 2)
        self.velocity_x = 4
        self.velocity_y = 2
        
class Enemy(pygame.Rect):
    def __init__(self):
        super().__init__(ENEMY_X, ENEMY_Y, ENEMY_WIDTH, ENEMY_HEIGHT)
        
def apply_gravity(ball):
    """Применяет гравитацию к мячу."""
    ball.velocity_y += GRAVITY


def move_ball_horizontal(ball):
    """Двигает мяч по X и отталкивает от боковых стен."""
    ball.x += ball.velocity_x
    if ball.left <= 0 or ball.right >= GAME_WIDTH:
        ball.velocity_x *= -1


def move_ball_vertical(ball):
    """Двигает мяч по Y."""
    ball.y += ball.velocity_y
    
def reset_ball(ball):
    """Возвращает мяч в центр экрана и направляет его вниз."""
    ball.center = (GAME_WIDTH // 2, GAME_HEIGHT // 2)
    ball.velocity_x = 4
    ball.velocity_y = 2
    
def check_scoring(ball):
    """Проверяет касание верха/низа, начисляет очки и сбрасывает мяч."""
    global player_score, enemy_score

    # Каснулся верха — очко игроку
    if ball.top <= 0:
        player_score += 1
        reset_ball(ball)

    # Каснулся низа — очко противнику
    elif ball.bottom >= GAME_HEIGHT:
        enemy_score += 1
        reset_ball(ball)

def check_player_collision(ball, player):
    """Проверяет и обрабатывает удар мяча об игрока."""
    if ball.colliderect(player):
        if ball.velocity_y > 0 and ball.bottom - ball.velocity_y <= player.top + 10:
            ball.bottom = player.top
            ball.velocity_y = -abs(ball.velocity_y)
            offset = (ball.centerx - player.centerx) / (player.width / 2)
            ball.velocity_x = offset * 6


def check_enemy_collision(ball, enemy):
    """Проверяет и обрабатывает удар мяча о противника."""
    if ball.colliderect(enemy):
        if ball.velocity_y < 0 and ball.top - ball.velocity_y >= enemy.bottom - 10:
            ball.top = enemy.bottom
            ball.velocity_y = abs(ball.velocity_y)
            offset = (ball.centerx - enemy.centerx) / (enemy.width / 2)
            ball.velocity_x = offset * 6
            
def update_enemy_ai(enemy, ball):
    """ИИ следит за центром мяча."""
    if enemy.centerx < ball.centerx:
        enemy.x += ENEMY_SPEED
    elif enemy.centerx > ball.centerx:
        enemy.x -= ENEMY_SPEED
    enemy.x = max(0, min(enemy.x, GAME_WIDTH - enemy.width))
    
    
def handle_player_input(player, keys):
    """Игрок 1 управляет клавишами A / D или Стрелочками (в соло режиме)."""
    if keys[pygame.K_a] or (not TWO_PLAYER_MODE and keys[pygame.K_LEFT]):
        player.x = max(player.x - PLAYER_DISTANCE, 0)
    if keys[pygame.K_d] or (not TWO_PLAYER_MODE and keys[pygame.K_RIGHT]):
        player.x = min(player.x + PLAYER_DISTANCE, GAME_WIDTH - player.width)


def handle_enemy_input(enemy, keys):
    """Управление для второго игрока (Стрелочки)."""
    if keys[pygame.K_LEFT]:
        enemy.x = max(enemy.x - PLAYER_DISTANCE, 0)
    if keys[pygame.K_RIGHT]:
        enemy.x = min(enemy.x + PLAYER_DISTANCE, GAME_WIDTH - enemy.width)
        
def reset_game():
    """Сброс очков и позиций при новой игре."""
    global player_score, enemy_score
    player_score = 0
    enemy_score = 0
    player.x = PLAYER_X
    enemy_paddle.x = ENEMY_X
    reset_ball(ball)

# --- ОТРИСОВКА ---

def draw_menu():
    window.fill((15, 15, 25))

    title_surf = font_large.render("ВЫБЕРИТЕ РЕЖИМ ИГРЫ", True, (255, 255, 255))
    opt1_surf = font_medium.render("Нажмите [1] — 1 Игрок (против ИИ)", True, (0, 255, 200))
    opt2_surf = font_medium.render("Нажмите [2] — 2 Игрока (на одной клавиатуре)", True, (255, 200, 0))

    window.blit(title_surf, (GAME_WIDTH // 2 - title_surf.get_width() // 2, 200))
    window.blit(opt1_surf, (GAME_WIDTH // 2 - opt1_surf.get_width() // 2, 350))
    window.blit(opt2_surf, (GAME_WIDTH // 2 - opt2_surf.get_width() // 2, 420))


def draw_game():
    window.fill((0, 0, 0))
    pygame.draw.rect(window, (255, 255, 255), player)
    pygame.draw.rect(window, (255, 255, 0), enemy_paddle)
    pygame.draw.circle(window, (255, 0, 0), ball.center, BALL_RADIUS)

    mode_text = "2 Игрока" if TWO_PLAYER_MODE else "VS ИИ"
    score_surf = font_medium.render(f"Игрок 1: {player_score}  |  Враг: {enemy_score}  ({mode_text})", True, (255, 255, 255))
    hint_surf = font_medium.render("[ESC] — Выйти в меню", True, (100, 100, 100))

    window.blit(score_surf, (20, 20))
    window.blit(hint_surf, (GAME_WIDTH - hint_surf.get_width() - 20, 20))


# Инициализация объектов
player = Player()
enemy_paddle = Enemy()
ball = Ball()

# --- ГЛАВНЫЙ ЦИКЛ ---

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Обработка нажатий для меню
        if event.type == pygame.KEYDOWN:
            if game_state == "MENU":
                if event.key == pygame.K_1:
                    TWO_PLAYER_MODE = False
                    reset_game()
                    game_state = "GAME"
                elif event.key == pygame.K_2:
                    TWO_PLAYER_MODE = True
                    reset_game()
                    game_state = "GAME"

            elif game_state == "GAME":
                # Нажатие ESC возвращает в главное меню
                if event.key == pygame.K_ESCAPE:
                    game_state = "MENU"

    # Логика в зависимости от состояния
    if game_state == "MENU":
        draw_menu()

    elif game_state == "GAME":
        keys = pygame.key.get_pressed()

        handle_player_input(player, keys)

        if TWO_PLAYER_MODE:
            handle_enemy_input(enemy_paddle, keys)
        else:
            update_enemy_ai(enemy_paddle, ball)

        apply_gravity(ball)
        move_ball_horizontal(ball)
        move_ball_vertical(ball)

        check_scoring(ball)
        check_player_collision(ball, player)
        check_enemy_collision(ball, enemy_paddle)

        draw_game()

    pygame.display.update()
    clock.tick(60)