import pygame
import sys
import random
import math

# Inicializar Pygame
pygame.init()

# Constantes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 20
MAZE_WIDTH = SCREEN_WIDTH // CELL_SIZE
MAZE_HEIGHT = (SCREEN_HEIGHT - 100) // CELL_SIZE  # Espacio para UI

# Colores estilo arcade vintage
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
GREEN = (0, 255, 0)
WALL_COLOR = (0, 0, 139)

# Laberinto simple estilo Pacman
MAZE = [
    "########################################",
    "#..................##..................#",
    "#.####.###########.##.###########.####.#",
    "#o####.###########.##.###########.####o#",
    "#......................................#",
    "#.####.##.####################.##.####.#",
    "#......##........##........##......#",
    "######.#########.##.#########.######",
    "######.#########.##.#########.######",
    "######.##................##.######",
    "######.##.####  ####.##.######",
    "#........####    ####........#",
    "######.##.####  ####.##.######",
    "######.##................##.######",
    "######.##.##############.##.######",
    "#..................##..................#",
    "#.####.###########.##.###########.####.#",
    "#o..##.............  .............##..o#",
    "###.##.##.####################.##.##.###",
    "#......##........##........##......#",
    "#.############.####.############.#",
    "#......................................#",
    "########################################"
]


class Pacman:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 0  # 0=derecha, 1=abajo, 2=izquierda, 3=arriba
        self.next_direction = 0
        self.animation_frame = 0
        self.animation_speed = 8
        self.speed = 2
        self.mouth_open = True

    def update(self):
        # Animación de la boca
        self.animation_frame += 1
        if self.animation_frame >= self.animation_speed:
            self.mouth_open = not self.mouth_open
            self.animation_frame = 0

        # Movimiento
        dx, dy = 0, 0
        if self.direction == 0:  # Derecha
            dx = self.speed
        elif self.direction == 1:  # Abajo
            dy = self.speed
        elif self.direction == 2:  # Izquierda
            dx = -self.speed
        elif self.direction == 3:  # Arriba
            dy = -self.speed

        # Verificar colisión antes de moverse
        new_x = self.x + dx
        new_y = self.y + dy

        if not self.check_wall_collision(new_x, new_y):
            self.x = new_x
            self.y = new_y

        # Teletransporte en los túneles laterales
        if self.x < 0:
            self.x = SCREEN_WIDTH - CELL_SIZE
        elif self.x >= SCREEN_WIDTH:
            self.x = 0

    def check_wall_collision(self, x, y):
        # Verificar múltiples puntos del círculo de Pacman
        points = [
            (x + CELL_SIZE//4, y + CELL_SIZE//4),
            (x + 3*CELL_SIZE//4, y + CELL_SIZE//4),
            (x + CELL_SIZE//4, y + 3*CELL_SIZE//4),
            (x + 3*CELL_SIZE//4, y + 3*CELL_SIZE//4),
            (x + CELL_SIZE//2, y + CELL_SIZE//2)
        ]

        for px, py in points:
            maze_x = int(px // CELL_SIZE)
            maze_y = int(py // CELL_SIZE)

            if (maze_y >= 0 and maze_y < len(MAZE) and
                maze_x >= 0 and maze_x < len(MAZE[0]) and
                    MAZE[maze_y][maze_x] == '#'):
                return True
        return False

    def change_direction(self, new_direction):
        self.next_direction = new_direction

        # Intentar cambiar inmediatamente
        dx, dy = 0, 0
        if new_direction == 0:  # Derecha
            dx = self.speed
        elif new_direction == 1:  # Abajo
            dy = self.speed
        elif new_direction == 2:  # Izquierda
            dx = -self.speed
        elif new_direction == 3:  # Arriba
            dy = -self.speed

        if not self.check_wall_collision(self.x + dx, self.y + dy):
            self.direction = new_direction

    def draw(self, screen):
        center_x = self.x + CELL_SIZE // 2
        center_y = self.y + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - 2

        if self.mouth_open:
            # Dibujar Pacman con boca abierta
            start_angle = math.radians(30 + self.direction * 90)
            end_angle = math.radians(330 + self.direction * 90)

            # Crear puntos para el arco
            points = [(center_x, center_y)]
            for angle in [i * 0.1 for i in range(int(start_angle * 10), int(end_angle * 10))]:
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.append((x, y))
            points.append((center_x, center_y))

            pygame.draw.polygon(screen, YELLOW, points)
        else:
            # Dibujar círculo completo
            pygame.draw.circle(screen, YELLOW, (center_x, center_y), radius)


class Ghost:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.direction = random.randint(0, 3)
        self.speed = 1
        self.mode = "chase"  # chase, scatter, frightened
        self.mode_timer = 0

    def update(self, pacman_x, pacman_y):
        self.mode_timer += 1

        # Cambiar modo ocasionalmente
        if self.mode_timer > 300:  # 5 segundos aprox
            self.mode = "scatter" if self.mode == "chase" else "chase"
            self.mode_timer = 0

        # Movimiento simple de AI
        possible_directions = []

        for direction in range(4):
            dx, dy = 0, 0
            if direction == 0:  # Derecha
                dx = self.speed
            elif direction == 1:  # Abajo
                dy = self.speed
            elif direction == 2:  # Izquierda
                dx = -self.speed
            elif direction == 3:  # Arriba
                dy = -self.speed

            if not self.check_wall_collision(self.x + dx, self.y + dy):
                possible_directions.append(direction)

        if possible_directions:
            if self.mode == "chase":
                # Elegir dirección hacia Pacman
                best_direction = self.direction
                min_distance = float('inf')

                for direction in possible_directions:
                    dx, dy = 0, 0
                    if direction == 0:
                        dx = self.speed
                    elif direction == 1:
                        dy = self.speed
                    elif direction == 2:
                        dx = -self.speed
                    elif direction == 3:
                        dy = -self.speed

                    new_x = self.x + dx
                    new_y = self.y + dy
                    distance = math.sqrt(
                        (new_x - pacman_x)**2 + (new_y - pacman_y)**2)

                    if distance < min_distance:
                        min_distance = distance
                        best_direction = direction

                self.direction = best_direction
            else:
                # Movimiento aleatorio
                if random.randint(0, 10) == 0:  # Cambiar dirección ocasionalmente
                    self.direction = random.choice(possible_directions)

        # Mover
        dx, dy = 0, 0
        if self.direction == 0:
            dx = self.speed
        elif self.direction == 1:
            dy = self.speed
        elif self.direction == 2:
            dx = -self.speed
        elif self.direction == 3:
            dy = -self.speed

        if not self.check_wall_collision(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
        else:
            # Si choca con pared, cambiar dirección
            possible_directions = [d for d in range(4) if d != self.direction]
            if possible_directions:
                self.direction = random.choice(possible_directions)

        # Teletransporte
        if self.x < 0:
            self.x = SCREEN_WIDTH - CELL_SIZE
        elif self.x >= SCREEN_WIDTH:
            self.x = 0

    def check_wall_collision(self, x, y):
        maze_x = int((x + CELL_SIZE//2) // CELL_SIZE)
        maze_y = int((y + CELL_SIZE//2) // CELL_SIZE)

        if (maze_y >= 0 and maze_y < len(MAZE) and
            maze_x >= 0 and maze_x < len(MAZE[0]) and
                MAZE[maze_y][maze_x] == '#'):
            return True
        return False

    def draw(self, screen):
        center_x = self.x + CELL_SIZE // 2
        center_y = self.y + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - 2

        # Cuerpo del fantasma (semicírculo + rectángulo)
        pygame.draw.circle(screen, self.color,
                           (center_x, center_y - 2), radius)
        pygame.draw.rect(screen, self.color,
                         (center_x - radius, center_y - 2, radius * 2, radius + 2))

        # Parte inferior ondulada
        wave_points = []
        for i in range(5):
            x = center_x - radius + (i * radius * 2 // 4)
            y = center_y + radius if i % 2 == 0 else center_y + radius - 4
            wave_points.append((x, y))

        if len(wave_points) >= 3:
            pygame.draw.polygon(screen, self.color,
                                [(center_x - radius, center_y + radius)] + wave_points +
                                [(center_x + radius, center_y + radius)])

        # Ojos
        eye_size = 3
        pygame.draw.circle(
            screen, WHITE, (center_x - 6, center_y - 6), eye_size)
        pygame.draw.circle(
            screen, WHITE, (center_x + 6, center_y - 6), eye_size)
        pygame.draw.circle(screen, BLACK, (center_x - 5, center_y - 6), 2)
        pygame.draw.circle(screen, BLACK, (center_x + 5, center_y - 6), 2)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pacman Vintage Arcade")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Crear puntos y power pellets
        self.dots = []
        self.power_pellets = []
        self.create_dots()

        # Crear Pacman
        start_x, start_y = self.find_start_position()
        self.pacman = Pacman(start_x * CELL_SIZE, start_y * CELL_SIZE)

        # Crear fantasmas
        self.ghosts = [
            Ghost(18 * CELL_SIZE, 10 * CELL_SIZE, RED),
            Ghost(19 * CELL_SIZE, 10 * CELL_SIZE, PINK),
            Ghost(20 * CELL_SIZE, 10 * CELL_SIZE, CYAN),
            Ghost(21 * CELL_SIZE, 10 * CELL_SIZE, ORANGE)
        ]

        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False

    def find_start_position(self):
        for y, row in enumerate(MAZE):
            for x, cell in enumerate(row):
                if cell == ' ' or cell == '.':
                    return x, y
        return 1, 1

    def create_dots(self):
        for y, row in enumerate(MAZE):
            for x, cell in enumerate(row):
                if cell == '.':
                    self.dots.append((x * CELL_SIZE + CELL_SIZE//2,
                                      y * CELL_SIZE + CELL_SIZE//2))
                elif cell == 'o':
                    self.power_pellets.append((x * CELL_SIZE + CELL_SIZE//2,
                                               y * CELL_SIZE + CELL_SIZE//2))

    def check_dot_collision(self):
        pacman_center = (self.pacman.x + CELL_SIZE//2,
                         self.pacman.y + CELL_SIZE//2)

        # Verificar puntos normales
        for dot in self.dots[:]:  # Copia de la lista
            if math.sqrt((pacman_center[0] - dot[0])**2 +
                         (pacman_center[1] - dot[1])**2) < CELL_SIZE//2:
                self.dots.remove(dot)
                self.score += 10

        # Verificar power pellets
        for pellet in self.power_pellets[:]:
            if math.sqrt((pacman_center[0] - pellet[0])**2 +
                         (pacman_center[1] - pellet[1])**2) < CELL_SIZE//2:
                self.power_pellets.remove(pellet)
                self.score += 50

        # Verificar victoria
        if len(self.dots) == 0 and len(self.power_pellets) == 0:
            self.win = True

    def check_ghost_collision(self):
        pacman_center = (self.pacman.x + CELL_SIZE//2,
                         self.pacman.y + CELL_SIZE//2)

        for ghost in self.ghosts:
            ghost_center = (ghost.x + CELL_SIZE//2, ghost.y + CELL_SIZE//2)
            if math.sqrt((pacman_center[0] - ghost_center[0])**2 +
                         (pacman_center[1] - ghost_center[1])**2) < CELL_SIZE:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                else:
                    # Resetear posición de Pacman
                    start_x, start_y = self.find_start_position()
                    self.pacman.x = start_x * CELL_SIZE
                    self.pacman.y = start_y * CELL_SIZE
                break

    def draw_maze(self):
        for y, row in enumerate(MAZE):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * CELL_SIZE, y *
                                   CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if cell == '#':
                    pygame.draw.rect(self.screen, WALL_COLOR, rect)
                    pygame.draw.rect(self.screen, BLUE, rect, 1)

    def draw_dots(self):
        for dot in self.dots:
            pygame.draw.circle(self.screen, WHITE, dot, 2)

        for pellet in self.power_pellets:
            pygame.draw.circle(self.screen, WHITE, pellet, 6)

    def draw_ui(self):
        # Puntuación
        score_text = self.font.render(f"SCORE: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (10, SCREEN_HEIGHT - 90))

        # Vidas
        lives_text = self.font.render(f"LIVES: {self.lives}", True, YELLOW)
        self.screen.blit(lives_text, (10, SCREEN_HEIGHT - 50))

        # Título
        title_text = self.font.render("PACMAN VINTAGE", True, YELLOW)
        title_rect = title_text.get_rect(
            center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 70))
        self.screen.blit(title_text, title_rect)

        if self.game_over:
            game_over_text = self.font.render(
                "GAME OVER - Press R to Restart", True, RED)
            text_rect = game_over_text.get_rect(
                center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)

        if self.win:
            win_text = self.font.render(
                "YOU WIN! - Press R to Restart", True, GREEN)
            text_rect = win_text.get_rect(
                center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(win_text, text_rect)

    def restart_game(self):
        self.__init__()

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.pacman.change_direction(0)
                    elif event.key == pygame.K_DOWN:
                        self.pacman.change_direction(1)
                    elif event.key == pygame.K_LEFT:
                        self.pacman.change_direction(2)
                    elif event.key == pygame.K_UP:
                        self.pacman.change_direction(3)
                    elif event.key == pygame.K_r and (self.game_over or self.win):
                        self.restart_game()

            if not self.game_over and not self.win:
                # Actualizar juego
                self.pacman.update()
                for ghost in self.ghosts:
                    ghost.update(self.pacman.x, self.pacman.y)

                self.check_dot_collision()
                self.check_ghost_collision()

            # Dibujar todo
            self.screen.fill(BLACK)
            self.draw_maze()
            self.draw_dots()
            self.pacman.draw(self.screen)
            for ghost in self.ghosts:
                ghost.draw(self.screen)
            self.draw_ui()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
