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
DARK_BLUE = (0, 0, 139)

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

# Lista de frutas bonus con colores y puntos
BONUS_FRUITS = [
    {"name": "cherry", "color": RED, "points": 100},
    {"name": "strawberry", "color": PINK, "points": 300},
    {"name": "orange", "color": ORANGE, "points": 500},
    {"name": "apple", "color": GREEN, "points": 700},
    {"name": "melon", "color": CYAN, "points": 1000},
]

class Pacman:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 0  # 0=derecha, 1=abajo, 2=izquierda, 3=arriba
        self.next_direction = None
        self.animation_frame = 0
        self.animation_speed = 6
        self.speed = 3
        self.mouth_open = True
        
        # Para movimiento más suave
        self.target_x = x
        self.target_y = y
        self.moving = False
        
    def update(self):
        # Animación de la boca
        self.animation_frame += 1
        if self.animation_frame >= self.animation_speed:
            self.mouth_open = not self.mouth_open
            self.animation_frame = 0
        
        # Manejar cambio de dirección pendiente
        if self.next_direction is not None:
            if self.can_move_in_direction(self.next_direction):
                self.direction = self.next_direction
                self.next_direction = None
        
        # Si no nos estamos moviendo hacia un objetivo, empezar nuevo movimiento
        if not self.moving:
            if self.can_move_in_direction(self.direction):
                self.start_movement()
        
        # Movimiento suave
        if self.moving:
            self.move_towards_target()
    
    def can_move_in_direction(self, direction):
        # Calcular próxima celda
        next_cell_x = int(self.x // CELL_SIZE)
        next_cell_y = int(self.y // CELL_SIZE)
        
        if direction == 0:  # Derecha
            next_cell_x += 1
        elif direction == 1:  # Abajo
            next_cell_y += 1
        elif direction == 2:  # Izquierda
            next_cell_x -= 1
        elif direction == 3:  # Arriba
            next_cell_y -= 1
        
        # Verificar teletransporte horizontal
        if next_cell_x < 0 or next_cell_x >= len(MAZE[0]):
            return True
        
        # Verificar colisión con paredes
        if (next_cell_y >= 0 and next_cell_y < len(MAZE) and 
            next_cell_x >= 0 and next_cell_x < len(MAZE[0]) and 
            MAZE[next_cell_y][next_cell_x] == '#'):
            return False
        
        return True
    
    def start_movement(self):
        # Calcular objetivo basado en dirección
        target_x = int(self.x // CELL_SIZE) * CELL_SIZE
        target_y = int(self.y // CELL_SIZE) * CELL_SIZE
        
        if self.direction == 0:  # Derecha
            target_x += CELL_SIZE
        elif self.direction == 1:  # Abajo
            target_y += CELL_SIZE
        elif self.direction == 2:  # Izquierda
            target_x -= CELL_SIZE
        elif self.direction == 3:  # Arriba
            target_y -= CELL_SIZE
        
        self.target_x = target_x
        self.target_y = target_y
        self.moving = True
    
    def move_towards_target(self):
        # Movimiento suave hacia el objetivo
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance <= self.speed:
            # Llegamos al objetivo
            self.x = self.target_x
            self.y = self.target_y
            self.moving = False
            
            # Manejar teletransporte
            if self.x < 0:
                self.x = SCREEN_WIDTH - CELL_SIZE
                self.target_x = self.x
            elif self.x >= SCREEN_WIDTH:
                self.x = 0
                self.target_x = self.x
        else:
            # Moverse hacia el objetivo
            move_x = (dx / distance) * self.speed
            move_y = (dy / distance) * self.speed
            
            self.x += move_x
            self.y += move_y
    
    def change_direction(self, new_direction):
        # Si podemos cambiar inmediatamente, hacerlo
        if not self.moving and self.can_move_in_direction(new_direction):
            self.direction = new_direction
        else:
            # Guardar para el próximo movimiento
            self.next_direction = new_direction
    
    def get_current_cell(self):
        return (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))
    
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
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.color = color
        self.original_color = color
        self.name = name
        self.direction = random.randint(0, 3)
        self.speed = 2
        self.mode = "chase"  # chase, scatter, frightened
        self.mode_timer = 0
        self.frightened_timer = 0
        self.frightened_blink_timer = 0
        self.is_frightened = False
        
        # Para movimiento más suave
        self.target_x = x
        self.target_y = y
        self.moving = False
        
    def update(self, pacman_x, pacman_y):
        self.mode_timer += 1
        
        # Manejar modo asustado
        if self.is_frightened:
            self.frightened_timer -= 1
            self.frightened_blink_timer += 1
            
            # Parpadeo cuando está por terminar el modo asustado
            if self.frightened_timer < 120:  # 2 segundos
                if self.frightened_blink_timer % 10 < 5:
                    self.color = WHITE
                else:
                    self.color = DARK_BLUE
            else:
                self.color = DARK_BLUE
            
            if self.frightened_timer <= 0:
                self.is_frightened = False
                self.color = self.original_color
                self.mode = "chase"
        
        # Cambiar modo ocasionalmente (solo si no está asustado)
        if not self.is_frightened and self.mode_timer > 300:  # 5 segundos aprox
            self.mode = "scatter" if self.mode == "chase" else "chase"
            self.mode_timer = 0
        
        # Si no nos estamos moviendo hacia un objetivo, empezar nuevo movimiento
        if not self.moving:
            self.start_movement(pacman_x, pacman_y)
        
        # Movimiento suave
        if self.moving:
            self.move_towards_target()
    
    def start_movement(self, pacman_x, pacman_y):
        possible_directions = []
        current_cell_x = int(self.x // CELL_SIZE)
        current_cell_y = int(self.y // CELL_SIZE)
        
        for direction in range(4):
            next_cell_x = current_cell_x
            next_cell_y = current_cell_y
            
            if direction == 0:  # Derecha
                next_cell_x += 1
            elif direction == 1:  # Abajo
                next_cell_y += 1
            elif direction == 2:  # Izquierda
                next_cell_x -= 1
            elif direction == 3:  # Arriba
                next_cell_y -= 1
            
            # Verificar teletransporte
            if next_cell_x < 0 or next_cell_x >= len(MAZE[0]):
                possible_directions.append(direction)
                continue
            
            if not self.check_wall_collision_at_cell(next_cell_x, next_cell_y):
                possible_directions.append(direction)
        
        if possible_directions:
            if self.is_frightened:
                # Movimiento aleatorio cuando está asustado
                self.direction = random.choice(possible_directions)
            elif self.mode == "chase":
                # Elegir dirección hacia Pacman
                best_direction = self.direction
                min_distance = float('inf')
                
                for direction in possible_directions:
                    next_x = current_cell_x * CELL_SIZE
                    next_y = current_cell_y * CELL_SIZE
                    
                    if direction == 0:
                        next_x += CELL_SIZE
                    elif direction == 1:
                        next_y += CELL_SIZE
                    elif direction == 2:
                        next_x -= CELL_SIZE
                    elif direction == 3:
                        next_y -= CELL_SIZE
                    
                    distance = math.sqrt((next_x - pacman_x)**2 + (next_y - pacman_y)**2)
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_direction = direction
                
                self.direction = best_direction
            else:
                # Movimiento aleatorio en modo scatter
                if random.randint(0, 5) == 0:
                    self.direction = random.choice(possible_directions)
        
        # Calcular objetivo
        target_x = current_cell_x * CELL_SIZE
        target_y = current_cell_y * CELL_SIZE
        
        if self.direction == 0:  # Derecha
            target_x += CELL_SIZE
        elif self.direction == 1:  # Abajo
            target_y += CELL_SIZE
        elif self.direction == 2:  # Izquierda
            target_x -= CELL_SIZE
        elif self.direction == 3:  # Arriba
            target_y -= CELL_SIZE
        
        self.target_x = target_x
        self.target_y = target_y
        self.moving = True
    
    def move_towards_target(self):
        # Movimiento suave hacia el objetivo
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance <= self.speed:
            # Llegamos al objetivo
            self.x = self.target_x
            self.y = self.target_y
            self.moving = False
            
            # Manejar teletransporte
            if self.x < 0:
                self.x = SCREEN_WIDTH - CELL_SIZE
                self.target_x = self.x
            elif self.x >= SCREEN_WIDTH:
                self.x = 0
                self.target_x = self.x
        else:
            # Moverse hacia el objetivo
            move_speed = self.speed * 0.7 if self.is_frightened else self.speed
            move_x = (dx / distance) * move_speed
            move_y = (dy / distance) * move_speed
            
            self.x += move_x
            self.y += move_y
    
    def check_wall_collision_at_cell(self, cell_x, cell_y):
        if (cell_y >= 0 and cell_y < len(MAZE) and 
            cell_x >= 0 and cell_x < len(MAZE[0]) and 
            MAZE[cell_y][cell_x] == '#'):
            return True
        return False
    
    def make_frightened(self):
        self.is_frightened = True
        self.frightened_timer = 300  # 5 segundos
        self.frightened_blink_timer = 0
        self.color = DARK_BLUE
        self.mode = "frightened"
    
    def reset_position(self):
        self.x = self.start_x
        self.y = self.start_y
        self.target_x = self.start_x
        self.target_y = self.start_y
        self.moving = False
        self.is_frightened = False
        self.color = self.original_color
        self.mode = "chase"
    
    def get_current_cell(self):
        return (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))
    
    def draw(self, screen):
        center_x = self.x + CELL_SIZE // 2
        center_y = self.y + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - 2
        
        # Cuerpo del fantasma (semicírculo + rectángulo)
        pygame.draw.circle(screen, self.color, (center_x, center_y - 2), radius)
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
        
        # Ojos (diferentes si está asustado)
        eye_size = 3
        if self.is_frightened:
            # Ojos asustados (más pequeños, blancos)
            pygame.draw.circle(screen, WHITE, (center_x - 4, center_y - 4), 2)
            pygame.draw.circle(screen, WHITE, (center_x + 4, center_y - 4), 2)
        else:
            # Ojos normales
            pygame.draw.circle(screen, WHITE, (center_x - 6, center_y - 6), eye_size)
            pygame.draw.circle(screen, WHITE, (center_x + 6, center_y - 6), eye_size)
            pygame.draw.circle(screen, BLACK, (center_x - 5, center_y - 6), 2)
            pygame.draw.circle(screen, BLACK, (center_x + 5, center_y - 6), 2)

class BonusFruit:
    def __init__(self, x, y, fruit_type):
        self.x = x
        self.y = y
        self.fruit_type = fruit_type
        self.timer = 600  # 10 segundos de vida
        self.blink_timer = 0
        self.visible = True
        
    def update(self):
        self.timer -= 1
        self.blink_timer += 1
        
        # Parpadear cuando está por desaparecer
        if self.timer < 120:  # Últimos 2 segundos
            self.visible = self.blink_timer % 10 < 5
        
        return self.timer > 0
    
    def draw(self, screen):
        if self.visible:
            center_x = self.x + CELL_SIZE // 2
            center_y = self.y + CELL_SIZE // 2
            radius = CELL_SIZE // 3
            
            # Dibujar fruta como círculo con el color correspondiente
            pygame.draw.circle(screen, self.fruit_type["color"], (center_x, center_y), radius)
            pygame.draw.circle(screen, WHITE, (center_x, center_y), radius, 2)

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
            Ghost(18 * CELL_SIZE, 10 * CELL_SIZE, RED, "Blinky"),
            Ghost(19 * CELL_SIZE, 10 * CELL_SIZE, PINK, "Pinky"),
            Ghost(20 * CELL_SIZE, 10 * CELL_SIZE, CYAN, "Inky"),
            Ghost(21 * CELL_SIZE, 10 * CELL_SIZE, ORANGE, "Clyde")
        ]
        
        # Sistema de frutas bonus
        self.bonus_fruit = None
        self.fruit_spawn_timer = 0
        self.fruit_spawn_interval = 1800  # 30 segundos
        
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False
        self.power_pellet_mode = False
        self.power_pellet_timer = 0
    
    def find_start_position(self):
        for y, row in enumerate(MAZE):
            for x, cell in enumerate(row):
                if cell == ' ' or cell == '.':
                    return x, y
        return 1, 1
    
    def find_empty_position(self):
        """Encuentra una posición vacía para spawn de frutas"""
        empty_positions = []
        for y, row in enumerate(MAZE):
            for x, cell in enumerate(row):
                if cell == ' ' or cell == '.':
                    empty_positions.append((x, y))
        
        if empty_positions:
            return random.choice(empty_positions)
        return (1, 1)
    
    def create_dots(self):
        for y, row in enumerate(MAZE):
            for x, cell in enumerate(row):
                if cell == '.':
                    self.dots.append((x * CELL_SIZE + CELL_SIZE//2, 
                                    y * CELL_SIZE + CELL_SIZE//2))
                elif cell == 'o':
                    self.power_pellets.append((x * CELL_SIZE + CELL_SIZE//2, 
                                             y * CELL_SIZE + CELL_SIZE//2))
    
    def spawn_bonus_fruit(self):
        if self.bonus_fruit is None:
            fruit_type = random.choice(BONUS_FRUITS)
            x, y = self.find_empty_position()
            self.bonus_fruit = BonusFruit(x * CELL_SIZE, y * CELL_SIZE, fruit_type)
    
    def check_dot_collision(self):
        pacman_center = (self.pacman.x + CELL_SIZE//2, self.pacman.y + CELL_SIZE//2)
        
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
                
                # Activar modo power pellet
                self.power_pellet_mode = True
                self.power_pellet_timer = 300  # 5 segundos
                
                # Hacer que todos los fantasmas se asusten
                for ghost in self.ghosts:
                    ghost.make_frightened()
        
        # Verificar fruta bonus
        if self.bonus_fruit:
            fruit_center = (self.bonus_fruit.x + CELL_SIZE//2, self.bonus_fruit.y + CELL_SIZE//2)
            if math.sqrt((pacman_center[0] - fruit_center[0])**2 + 
                        (pacman_center[1] - fruit_center[1])**2) < CELL_SIZE//2:
                self.score += self.bonus_fruit.fruit_type["points"]
                self.bonus_fruit = None
        
        # Verificar victoria
        if len(self.dots) == 0 and len(self.power_pellets) == 0:
            self.win = True
    
    def check_ghost_collision(self):
        pacman_center = (self.pacman.x + CELL_SIZE//2, self.pacman.y + CELL_SIZE//2)
        
        for ghost in self.ghosts:
            ghost_center = (ghost.x + CELL_SIZE//2, ghost.y + CELL_SIZE//2)
            distance = math.sqrt((pacman_center[0] - ghost_center[0])**2 + 
                               (pacman_center[1] - ghost_center[1])**2)
            
            if distance < CELL_SIZE * 0.8:
                if ghost.is_frightened:
                    # Comer fantasma
                    self.score += 200
                    ghost.reset_position()
                else:
                    # Pacman muere
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        # Resetear posición de Pacman
                        start_x, start_y = self.find_start_position()
                        self.pacman.x = start_x * CELL_SIZE
                        self.pacman.y = start_y * CELL_SIZE
                        self.pacman.target_x = self.pacman.x
                        self.pacman.target_y = self.pacman.y
                        self.pacman.moving = False
                    break
    
    def draw_maze(self):
        for y, row in enumerate(MAZE):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if cell == '#':
                    pygame.draw.rect(self.screen, WALL_COLOR, rect)
                    pygame.draw.rect(self.screen, BLUE, rect, 1)
    
    def draw_dots(self):
        for dot in self.dots:
            pygame.draw.circle(self.screen, WHITE, dot, 2)
        
        for pellet in self.power_pellets:
            # Power pellets parpadean
            if pygame.time.get_ticks() % 500 < 250:
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
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 70))
        self.screen.blit(title_text, title_rect)
        
        # Indicador de power pellet
        if self.power_pellet_mode:
            power_text = self.small_font.render(f"POWER MODE: {self.power_pellet_timer // 60 + 1}s", True, CYAN)
            self.screen.blit(power_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 90))
        
        # Mostrar puntos de fruta bonus
        if self.bonus_fruit:
            fruit_text = self.small_font.render(f"BONUS: {self.bonus_fruit.fruit_type['points']}", True, self.bonus_fruit.fruit_type['color'])
            self.screen.blit(fruit_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50))
        
        if self.game_over:
            game_over_text = self.font.render("GAME OVER - Press R to Restart", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            pygame.draw.rect(self.screen, BLACK, text_rect.inflate(20, 10))
            self.screen.blit(game_over_text, text_rect)
        
        if self.win:
            win_text = self.font.render("YOU WIN! - Press R to Restart", True, GREEN)
            text_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            pygame.draw.rect(self.screen, BLACK, text_rect.inflate(20, 10))
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
                
                # Manejar modo power pellet
                if self.power_pellet_mode:
                    self.power_pellet_timer -= 1
                    if self.power_pellet_timer <= 0:
                        self.power_pellet_mode = False
                
                # Manejar spawn de frutas bonus
                self.fruit_spawn_timer += 1
                if self.fruit_spawn_timer >= self.fruit_spawn_interval:
                    self.spawn_bonus_fruit()
                    self.fruit_spawn_timer = 0
                
                # Actualizar fruta bonus
                if self.bonus_fruit:
                    if not self.bonus_fruit.update():
                        self.bonus_fruit = None
                
                self.check_dot_collision()
                self.check_ghost_collision()
            
            # Dibujar todo
            self.screen.fill(BLACK)
            self.draw_maze()
            self.draw_dots()
            self.pacman.draw(self.screen)
            for ghost in self.ghosts:
                ghost.draw(self.screen)
            
            # Dibujar fruta bonus
            if self.bonus_fruit:
                self.bonus_fruit.draw(self.screen)
            
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
