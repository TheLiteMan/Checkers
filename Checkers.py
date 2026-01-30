import arcade
import math
import random
import time
from typing import Optional, List

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Шашки"
SQUARE_SIZE = 100
BOARD_SIZE = 8
PIECE_RADIUS = 40

# Цвета
BLACK = arcade.color.BLACK
WHITE = arcade.color.WHITE
RED = arcade.color.RED
BLUE = arcade.color.BLUE
GREEN = arcade.color.GREEN
YELLOW = arcade.color.YELLOW
GOLD = arcade.color.GOLD
LIGHT_BROWN = arcade.color.LIGHT_BROWN
DARK_BROWN = arcade.color.BROWN
DARK_GREEN = arcade.color.DARK_GREEN
DARK_BLUE = arcade.color.DARK_BLUE
DARK_PURPLE = arcade.color.PURPLE
LIGHT_GRAY = arcade.color.LIGHT_GRAY
LIGHT_BLUE = arcade.color.LIGHT_BLUE
HIGHLIGHT = arcade.color.YELLOW  # Полупрозрачный желтый


class Particle:
    """Класс для частиц анимации"""

    def __init__(self, x, y, color, size=5, velocity_x=0, velocity_y=0, lifetime=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = 0.1
        self.fade = True

    def update(self, delta_time):
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            return False

        # Применяем гравитацию
        self.velocity_y -= self.gravity

        # Обновляем позицию
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Немного замедляемся
        self.velocity_x *= 0.98
        self.velocity_y *= 0.98

        return True

    def draw(self):
        alpha = int(255 * (self.lifetime / self.max_lifetime)) if self.fade else 255
        color_with_alpha = (self.color[0], self.color[1], self.color[2], alpha)
        arcade.draw_circle_filled(self.x, self.y, self.size, color_with_alpha)


class ParticleSystem:
    """Система управления частицами"""

    def __init__(self):
        self.particles = []

    def create_capture_particles(self, x, y, is_white):
        """Создание частиц при взятии шашки"""
        color = WHITE if is_white else RED
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            size = random.uniform(3, 8)
            lifetime = random.uniform(0.5, 1.5)
            particle = Particle(x, y, color, size, velocity_x, velocity_y, lifetime)
            self.particles.append(particle)

    def create_move_particles(self, from_x, from_y, to_x, to_y, is_white):
        """Создание частиц при перемещении шашки"""
        color = WHITE if is_white else RED
        steps = 10
        for i in range(steps):
            t = i / steps
            px = from_x + (to_x - from_x) * t
            py = from_y + (to_y - from_y) * t

            for _ in range(3):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.5, 2)
                velocity_x = math.cos(angle) * speed
                velocity_y = math.sin(angle) * speed
                size = random.uniform(2, 4)
                lifetime = random.uniform(0.3, 0.8)
                particle = Particle(px, py, color, size, velocity_x, velocity_y, lifetime)
                self.particles.append(particle)

    def create_king_particles(self, x, y, is_white):
        """Создание частиц при превращении в дамку"""
        crown_color = GOLD if is_white else YELLOW
        for _ in range(25):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            size = random.uniform(2, 6)
            lifetime = random.uniform(0.8, 1.5)
            particle = Particle(x, y, crown_color, size, velocity_x, velocity_y, lifetime)
            self.particles.append(particle)

    def create_button_press_particles(self, x, y, color):
        """Создание частиц при нажатии кнопки калькулятора"""
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            size = random.uniform(2, 4)
            lifetime = random.uniform(0.5, 1.0)
            particle = Particle(x, y, color, size, velocity_x, velocity_y, lifetime)
            self.particles.append(particle)

    def create_win_particles(self, x, y, color):
        """Создание частиц при победе"""
        for _ in range(50):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            size = random.uniform(4, 10)
            lifetime = random.uniform(1.0, 2.0)
            particle = Particle(x, y, color, size, velocity_x, velocity_y, lifetime)
            self.particles.append(particle)

    def update(self, delta_time):
        """Обновление всех частиц"""
        self.particles = [p for p in self.particles if p.update(delta_time)]

    def draw(self):
        """Отрисовка всех частиц"""
        for particle in self.particles:
            particle.draw()


class Calculator:
    """Класс калькулятора для отображения после окончания игры"""

    def __init__(self):
        self.display = "0"
        self.expression = ""
        self.is_active = False
        self.position_x = SCREEN_WIDTH // 2
        self.position_y = SCREEN_HEIGHT // 2
        self.width = 400
        self.height = 500

        # Кнопки калькулятора
        self.buttons = []
        self.button_width = 80
        self.button_height = 60
        self.button_margin = 10
        self.setup_buttons()

        # Анимация кнопок
        self.button_animations = {}
        self.start_time = time.time()

    def setup_buttons(self):
        """Создание кнопок калькулятора"""
        button_layout = [
            ['C', '←', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=', 'K']
        ]

        start_x = self.position_x - self.width // 2 + self.button_width // 2 + self.button_margin
        # Начинаем ниже, чтобы оставить место для дисплея
        start_y = self.position_y + self.height // 2 - 100 - self.button_height // 2

        for row_idx, row in enumerate(button_layout):
            for col_idx, text in enumerate(row):
                x = start_x + col_idx * (self.button_width + self.button_margin)
                y = start_y - row_idx * (self.button_height + self.button_margin)

                # Определение цвета кнопки
                if text in ['C', '←', '%', '/', '*', '-', '+']:
                    color = DARK_BLUE
                elif text == '=':
                    color = DARK_GREEN
                elif text == 'K':
                    color = RED
                else:
                    color = LIGHT_GRAY

                self.buttons.append({
                    'text': text,
                    'x': x,
                    'y': y,
                    'color': color,
                    'original_color': color,
                    'pressed': False
                })

    def draw(self):
        """Отрисовка калькулятора"""
        if not self.is_active:
            return

        current_time = time.time() - self.start_time

        # Фон калькулятора с легкой анимацией
        time_factor = math.sin(current_time * 5) * 0.05 + 0.95
        alpha = int(220 * time_factor)
        arcade.draw_lrbt_rectangle_filled(
            left=self.position_x - self.width // 2,
            right=self.position_x + self.width // 2,
            top=self.position_y + self.height // 2,
            bottom=self.position_y - self.height // 2,
            color=(0, 0, 0, alpha)  # Пульсирующая прозрачность
        )

        # Дисплей калькулятора
        display_top = self.position_y + self.height // 2 - 20
        display_bottom = display_top - 80

        # Анимация дисплея
        pulse = math.sin(current_time * 10) * 5
        arcade.draw_lrbt_rectangle_filled(
            left=self.position_x - self.width // 2 + 20 - pulse,
            right=self.position_x + self.width // 2 - 20 + pulse,
            top=display_top,
            bottom=display_bottom,
            color=BLACK
        )

        # Текст на дисплее с мерцанием
        display_text = self.display if len(self.display) <= 20 else "..." + self.display[-17:]
        text_alpha = int(255 * (0.8 + 0.2 * math.sin(current_time * 2)))
        arcade.draw_text(
            display_text,
            self.position_x,
            (display_top + display_bottom) // 2,
            (LIGHT_BLUE[0], LIGHT_BLUE[1], LIGHT_BLUE[2], text_alpha),
            32,
            align="right",
            anchor_x="center",
            anchor_y="center"
        )

        # Кнопки с анимацией нажатия
        for button in self.buttons:
            # Анимация нажатия
            button_offset = 0
            if button['pressed']:
                button_offset = -2

            # Цвет кнопки с анимацией
            color = button['color']
            if button['text'] == '=':
                # Пульсирующая анимация для кнопки "="
                pulse = math.sin(current_time * 10) * 0.2 + 0.8
                color = (
                    int(color[0] * pulse),
                    int(color[1] * pulse),
                    int(color[2] * pulse)
                )

            # Фон кнопки
            arcade.draw_lrbt_rectangle_filled(
                left=button['x'] - self.button_width // 2,
                right=button['x'] + self.button_width // 2,
                top=button['y'] + self.button_height // 2 + button_offset,
                bottom=button['y'] - self.button_height // 2 + button_offset,
                color=color
            )

            # Текст на кнопке
            arcade.draw_text(
                button['text'],
                button['x'],
                button['y'] + button_offset,
                WHITE,
                24,
                align="center",
                anchor_x="center",
                anchor_y="center"
            )

            # Контур кнопки
            arcade.draw_lrbt_rectangle_outline(
                left=button['x'] - self.button_width // 2,
                right=button['x'] + self.button_width // 2,
                top=button['y'] + self.button_height // 2 + button_offset,
                bottom=button['y'] - self.button_height // 2 + button_offset,
                color=WHITE,
                border_width=2
            )

            # Сброс состояния нажатия
            if button['pressed']:
                button['pressed'] = False
                button['color'] = button['original_color']

        # Инструкция с мерцанием
        blink = int(255 * (0.5 + 0.5 * math.sin(current_time * 10)))
        arcade.draw_text(
            "Нажмите K чтобы закрыть калькулятор",
            self.position_x,
            self.position_y - self.height // 2 + 30,
            (LIGHT_GRAY[0], LIGHT_GRAY[1], LIGHT_GRAY[2], blink),
            18,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )

    def handle_click(self, x, y, particle_system):
        """Обработка клика по калькулятору"""
        if not self.is_active:
            return False

        for button in self.buttons:
            if (abs(x - button['x']) < self.button_width // 2 and
                    abs(y - button['y']) < self.button_height // 2):
                # Анимация нажатия кнопки
                button['pressed'] = True
                button['color'] = YELLOW

                # Создаем частицы для кнопки
                particle_system.create_button_press_particles(button['x'], button['y'], button['original_color'])

                # Обрабатываем нажатие
                self.process_button(button['text'])
                return True

        return False

    def process_button(self, button_text):
        """Обработка нажатия кнопки калькулятора"""
        if button_text == 'C':
            self.display = "0"
            self.expression = ""
        elif button_text == '←':
            if len(self.display) > 1:
                self.display = self.display[:-1]
            else:
                self.display = "0"
        elif button_text == '=':
            try:
                # Заменяем символы для корректного вычисления
                eval_expression = self.expression.replace('×', '*').replace('÷', '/')
                result = eval(eval_expression)
                self.display = str(result)
                self.expression = self.display
            except:
                self.display = "Ошибка"
                self.expression = ""
        elif button_text == 'K':
            self.is_active = False
        else:
            if self.display == "0" or self.display == "Ошибка":
                self.display = button_text
            else:
                self.display += button_text

            # Обновляем выражение для вычисления
            if button_text in ['+', '-', '*', '/', '%']:
                self.expression = self.display
            elif button_text != '=':
                # Заменяем символы для отображения
                display_text = self.display
                display_text = display_text.replace('*', '×')
                display_text = display_text.replace('/', '÷')
                self.display = display_text

                # Для вычисления оставляем стандартные операторы
                self.expression += button_text if button_text not in ['×', '÷'] else \
                    '*' if button_text == '×' else '/'


class CheckerPiece:
    def __init__(self, row: int, col: int, is_white: bool, board_offset_x: int = 0, board_offset_y: int = 0):
        self.row = row
        self.col = col
        self.is_white = is_white
        self.is_king = False
        self.board_offset_x = board_offset_x
        self.board_offset_y = board_offset_y
        self.update_position()

        # Анимационные параметры
        self.bounce_time = 0
        self.bounce_amplitude = 2
        self.selected_time = 0
        self.start_time = time.time()

    def update_position(self):
        self.x = self.col * SQUARE_SIZE + SQUARE_SIZE // 2 + self.board_offset_x
        self.y = self.row * SQUARE_SIZE + SQUARE_SIZE // 2 + self.board_offset_y

    def update_offset(self, offset_x: int, offset_y: int):
        self.board_offset_x = offset_x
        self.board_offset_y = offset_y
        self.update_position()

    def update_animation(self, delta_time):
        """Обновление анимации шашки"""
        # Обновляем время для анимации подпрыгивания
        self.bounce_time += delta_time * 2

        # Анимация выделения
        if self.selected_time > 0:
            self.selected_time -= delta_time

    def draw(self):
        # Плавная анимация подпрыгивания на основе синуса
        bounce_offset = math.sin(self.bounce_time) * self.bounce_amplitude

        color = WHITE if self.is_white else RED

        # Рисуем шашку
        arcade.draw_circle_filled(self.x, self.y + bounce_offset, PIECE_RADIUS, color)

        if self.is_king:
            crown_color = GOLD if self.is_white else YELLOW
            # Анимация короны
            current_time = time.time() - self.start_time
            crown_scale = 1 + 0.1 * math.sin(current_time * 2)
            arcade.draw_circle_filled(self.x, self.y + bounce_offset, PIECE_RADIUS * 0.4 * crown_scale, crown_color)

            # Рисуем букву K для дамки с пульсацией
            k_scale = 1 + 0.1 * math.sin(current_time * 1.5)
            arcade.draw_text("K", self.x, self.y + bounce_offset, BLACK, int(20 * k_scale),
                             align="center", anchor_x="center", anchor_y="center")

        # Контур шашки с анимацией выделения
        outline_width = 2
        outline_color = BLACK

        if self.selected_time > 0:
            # Пульсирующий контур для выбранной шашки
            pulse = math.sin(self.selected_time * 10) * 0.5 + 0.5
            outline_color = (
                int(YELLOW[0] * pulse + BLACK[0] * (1 - pulse)),
                int(YELLOW[1] * pulse + BLACK[1] * (1 - pulse)),
                int(YELLOW[2] * pulse + BLACK[2] * (1 - pulse))
            )
            outline_width = 3

        arcade.draw_circle_outline(self.x, self.y + bounce_offset, PIECE_RADIUS, outline_color, outline_width)

    def start_selection_animation(self):
        """Запуск анимации выделения"""
        self.selected_time = 0.5  # Полсекунды анимации


class GameBoard:
    def __init__(self, board_offset_x: int = 0, board_offset_y: int = 0):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected_piece = None
        self.valid_moves = []
        self.current_player = True  # True - белые, False - черные
        self.white_pieces = 12
        self.black_pieces = 12
        self.white_score = 0
        self.black_score = 0
        self.game_over = False
        self.winner = None
        self.board_offset_x = board_offset_x
        self.board_offset_y = board_offset_y
        self.setup_pieces()

        # Анимационные параметры
        self.last_move_from = None
        self.last_move_to = None
        self.move_animation_time = 0
        self.win_animation_active = False
        self.win_animation_time = 0
        self.start_time = time.time()

    def setup_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:  # Только на черных клетках
                    if row < 3:
                        self.board[row][col] = CheckerPiece(row, col, False,
                                                            self.board_offset_x, self.board_offset_y)
                    elif row > 4:
                        self.board[row][col] = CheckerPiece(row, col, True,
                                                            self.board_offset_x, self.board_offset_y)

    def update_offset(self, offset_x: int, offset_y: int):
        self.board_offset_x = offset_x
        self.board_offset_y = offset_y
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    piece.update_offset(offset_x, offset_y)

    def update_animations(self, delta_time):
        """Обновление всех анимаций на доске"""
        # Обновление анимации последнего хода
        if self.move_animation_time > 0:
            self.move_animation_time -= delta_time

        # Обновление анимации победы
        if self.win_animation_active:
            self.win_animation_time += delta_time

        # Обновление анимаций шашек
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    piece.update_animation(delta_time)

    def draw(self):
        # Анимация доски (легкое мерцание клеток)
        current_time = time.time() - self.start_time
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                base_color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN

                # Добавляем легкое мерцание
                flicker = math.sin(current_time * 0.5 + row * 0.5 + col * 0.5) * 0.05 + 0.95
                color = (
                    int(base_color[0] * flicker),
                    int(base_color[1] * flicker),
                    int(base_color[2] * flicker)
                )

                x = col * SQUARE_SIZE + self.board_offset_x
                y = row * SQUARE_SIZE + self.board_offset_y

                # Рисуем квадрат доски
                arcade.draw_lrbt_rectangle_filled(
                    left=x,
                    right=x + SQUARE_SIZE,
                    top=y + SQUARE_SIZE,
                    bottom=y,
                    color=color
                )

        # Анимация возможных ходов (пульсирующие кружки)
        for move in self.valid_moves:
            row, col = move
            x = col * SQUARE_SIZE + SQUARE_SIZE // 2 + self.board_offset_x
            y = row * SQUARE_SIZE + SQUARE_SIZE // 2 + self.board_offset_y

            # Пульсация размера
            pulse = math.sin(current_time * 10) * 5 + 20
            alpha_pulse = int(100 * (0.7 + 0.3 * math.sin(current_time * 15)))
            arcade.draw_circle_filled(x, y, pulse, (255, 255, 0, alpha_pulse))

        # Отрисовка шашек
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    piece.draw()

        # Анимация траектории последнего хода
        if self.last_move_from and self.last_move_to and self.move_animation_time > 0:
            from_x, from_y = self.last_move_from
            to_x, to_y = self.last_move_to

            # Рисуем линию хода с эффектом исчезновения
            alpha = int(255 * (self.move_animation_time / 0.5))
            arcade.draw_line(from_x, from_y, to_x, to_y, (0, 255, 255, alpha), 3)

            # Рисуем кружки на концах
            arcade.draw_circle_filled(from_x, from_y, 10, (0, 255, 255, alpha))
            arcade.draw_circle_filled(to_x, to_y, 10, (0, 255, 255, alpha))

        # Отрисовка выделения выбранной шашки
        if self.selected_piece:
            # Пульсирующее выделение
            pulse = math.sin(current_time * 20) * 3 + 5
            arcade.draw_circle_outline(
                self.selected_piece.x,
                self.selected_piece.y,
                PIECE_RADIUS + pulse,
                YELLOW,
                3
            )

    def get_piece_at(self, row: int, col: int) -> Optional[CheckerPiece]:
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.board[row][col]
        return None

    def select_piece(self, row: int, col: int):
        # Преобразуем в целые числа, если это еще не сделано
        row = int(row)
        col = int(col)

        piece = self.get_piece_at(row, col)
        if piece and piece.is_white == self.current_player:
            self.selected_piece = piece
            self.valid_moves = self.get_valid_moves(piece)

            # Запускаем анимацию выделения
            piece.start_selection_animation()

            return True
        return False

    def get_valid_moves(self, piece: CheckerPiece) -> List[tuple]:
        moves = []
        row, col = piece.row, piece.col

        # Направления движения
        directions = []
        if piece.is_white or piece.is_king:
            directions.extend([(-1, -1), (-1, 1)])  # Вверх
        if not piece.is_white or piece.is_king:
            directions.extend([(1, -1), (1, 1)])  # Вниз

        # Проверка простых ходов
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                if not self.get_piece_at(new_row, new_col):
                    moves.append((new_row, new_col))

        # Проверка взятия
        for dr, dc in directions:
            new_row, new_col = row + 2 * dr, col + 2 * dc
            mid_row, mid_col = row + dr, col + dc

            if (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and
                    not self.get_piece_at(new_row, new_col)):
                mid_piece = self.get_piece_at(mid_row, mid_col)
                if mid_piece and mid_piece.is_white != piece.is_white:
                    moves.append((new_row, new_col))

        return moves

    def move_piece(self, row: int, col: int, particle_system: ParticleSystem) -> bool:
        if not self.selected_piece or (row, col) not in self.valid_moves:
            return False

        # Преобразуем в целые числа, если это еще не сделано
        row = int(row)
        col = int(col)

        # Сохраняем позиции для анимации
        old_x, old_y = self.selected_piece.x, self.selected_piece.y
        new_x = col * SQUARE_SIZE + SQUARE_SIZE // 2 + self.board_offset_x
        new_y = row * SQUARE_SIZE + SQUARE_SIZE // 2 + self.board_offset_y

        # Проверка на взятие
        dr = row - self.selected_piece.row
        dc = col - self.selected_piece.col

        if abs(dr) == 2:  # Взятие
            mid_row = self.selected_piece.row + dr // 2
            mid_col = self.selected_piece.col + dc // 2
            captured_piece = self.get_piece_at(mid_row, mid_col)

            if captured_piece:
                # Создаем частицы при взятии
                particle_system.create_capture_particles(
                    captured_piece.x, captured_piece.y, captured_piece.is_white
                )

                self.board[mid_row][mid_col] = None
                if captured_piece.is_white:
                    self.white_pieces -= 1
                    self.black_score += 1
                else:
                    self.black_pieces -= 1
                    self.white_score += 1

        # Перемещение шашки
        old_row, old_col = self.selected_piece.row, self.selected_piece.col
        self.board[old_row][old_col] = None

        self.selected_piece.row = row
        self.selected_piece.col = col
        self.selected_piece.update_position()

        # Проверка на превращение в дамку
        became_king = False
        if (self.selected_piece.is_white and row == 0) or \
                (not self.selected_piece.is_white and row == BOARD_SIZE - 1):
            if not self.selected_piece.is_king:  # Только если еще не дамка
                self.selected_piece.is_king = True
                became_king = True
                # Создаем частицы при превращении в дамку
                particle_system.create_king_particles(
                    self.selected_piece.x, self.selected_piece.y, self.selected_piece.is_white
                )

        self.board[row][col] = self.selected_piece

        # Создаем частицы при перемещении
        particle_system.create_move_particles(
            old_x, old_y, new_x, new_y, self.selected_piece.is_white
        )

        # Устанавливаем анимацию последнего хода
        self.last_move_from = (old_x, old_y)
        self.last_move_to = (new_x, new_y)
        self.move_animation_time = 0.5  # Полсекунды анимации

        # Смена игрока
        self.current_player = not self.current_player
        self.selected_piece = None
        self.valid_moves = []

        # Проверка окончания игры
        self.check_game_over()

        return True

    def check_game_over(self):
        if self.white_pieces == 0:
            self.game_over = True
            self.winner = "Черные"
            self.win_animation_active = True
        elif self.black_pieces == 0:
            self.game_over = True
            self.winner = "Белые"
            self.win_animation_active = True

        # Проверка наличия ходов
        has_moves = False
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.get_piece_at(row, col)
                if piece and piece.is_white == self.current_player:
                    if self.get_valid_moves(piece):
                        has_moves = True
                        break
            if has_moves:
                break

        if not has_moves:
            self.game_over = True
            self.winner = "Белые" if not self.current_player else "Черные"
            self.win_animation_active = True


class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.title_text = None
        self.instruction_text = None
        self.control_text = None
        self.particle_system = ParticleSystem()
        self.start_time = time.time()

    def on_show_view(self):
        arcade.set_background_color(DARK_BLUE)
        self.setup_text()

    def setup_text(self):
        self.title_text = arcade.Text(
            "ШАШКИ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.7,
            WHITE,
            50,
            anchor_x="center",
            anchor_y="center"
        )

        self.instruction_text = arcade.Text(
            "Нажмите любую клавишу для начала игры",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.4,
            YELLOW,
            24,
            anchor_x="center",
            anchor_y="center"
        )

        self.control_text = arcade.Text(
            "После окончания игры при нажатии на K будет открыт калькулятор",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.3,
            LIGHT_GRAY,
            18,
            anchor_x="center",
            anchor_y="center"
        )

    def on_update(self, delta_time):
        current_time = time.time() - self.start_time

        # Создаем случайные частицы на стартовом экране
        if random.random() < 0.1:
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            color = random.choice([WHITE, YELLOW, LIGHT_BLUE, GOLD])
            self.particle_system.create_button_press_particles(x, y, color)

        self.particle_system.update(delta_time)

    def on_draw(self):
        self.clear()
        current_time = time.time() - self.start_time

        # Рисуем частицы
        self.particle_system.draw()

        # Анимация заголовка (пульсация)
        scale = 1 + 0.1 * math.sin(current_time * 2)
        arcade.Text(
            "ШАШКИ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.7,
            WHITE,
            int(50 * scale),
            anchor_x="center",
            anchor_y="center"
        ).draw()

        # Анимация текста инструкции (мерцание)
        blink = 0.5 + 0.5 * math.sin(current_time * 3)
        alpha = int(255 * blink)
        arcade.Text(
            "Нажмите любую клавишу для начала игры",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.4,
            (YELLOW[0], YELLOW[1], YELLOW[2], alpha),
            24,
            anchor_x="center",
            anchor_y="center"
        ).draw()

        # Анимация управляющего текста
        slide = math.sin(current_time) * 10
        arcade.Text(
            "После окончания игры при нажатии на K будет открыт калькулятор",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.3 + slide,
            LIGHT_GRAY,
            18,
            anchor_x="center",
            anchor_y="center"
        ).draw()

    def on_key_press(self, key, modifiers):
        game_view = GameView()
        self.window.show_view(game_view)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.board_offset_x = (SCREEN_WIDTH - BOARD_SIZE * SQUARE_SIZE) // 2
        self.board_offset_y = (SCREEN_HEIGHT - BOARD_SIZE * SQUARE_SIZE) // 2
        self.board = GameBoard(self.board_offset_x, self.board_offset_y)

        # Калькулятор
        self.calculator = Calculator()

        # Система частиц
        self.particle_system = ParticleSystem()

        # Текстовые объекты
        self.score_text = None
        self.player_text = None
        self.pieces_text = None
        self.exit_button_text = None
        self.winner_text = None
        self.final_text = None
        self.calculator_hint_text = None

        # Анимационные параметры
        self.start_time = time.time()

        # Инициализируем текстовые объекты сразу
        self.setup_text()

    def setup_text(self):
        # Статические тексты (не меняются)
        self.exit_button_text = arcade.Text(
            "Выход",
            SCREEN_WIDTH - 80,
            SCREEN_HEIGHT - 40,
            WHITE,
            18,
            anchor_x="center",
            anchor_y="center"
        )

        self.winner_text = arcade.Text(
            "",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 30,
            YELLOW,
            36,
            anchor_x="center",
            anchor_y="center"
        )

        self.final_text = arcade.Text(
            "",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 40,
            WHITE,
            20,
            anchor_x="center",
            anchor_y="center"
        )

        self.calculator_hint_text = arcade.Text(
            "Нажмите K для открытия калькулятора",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 120,
            LIGHT_BLUE,
            18,
            anchor_x="center",
            anchor_y="center"
        )

        # Динамические тексты (будут обновляться)
        self.score_text = arcade.Text(
            "",
            20,
            SCREEN_HEIGHT - 30,
            WHITE,
            18
        )

        self.player_text = arcade.Text(
            "",
            20,
            SCREEN_HEIGHT - 60,
            WHITE,
            18
        )

        self.pieces_text = arcade.Text(
            "",
            20,
            SCREEN_HEIGHT - 90,
            WHITE,
            18
        )

    def on_show_view(self):
        arcade.set_background_color(DARK_GREEN)
        self.update_text()

    def on_update(self, delta_time):
        self.board.update_animations(delta_time)
        self.particle_system.update(delta_time)

        # Создаем частицы победы если игра окончена
        if self.board.game_over and self.board.win_animation_active:
            color = WHITE if self.board.winner == "Белые" else RED
            center_x = self.board_offset_x + BOARD_SIZE * SQUARE_SIZE // 2
            center_y = self.board_offset_y + BOARD_SIZE * SQUARE_SIZE // 2

            # Создаем частицы победы
            if self.board.win_animation_time < 2:  # Создаем частицы только первые 2 секунды
                if random.random() < 0.3:
                    self.particle_system.create_win_particles(center_x, center_y, color)

            # Продолжаем создавать легкие частицы
            if random.random() < 0.1:
                x = random.randint(self.board_offset_x, self.board_offset_x + BOARD_SIZE * SQUARE_SIZE)
                y = random.randint(self.board_offset_y, self.board_offset_y + BOARD_SIZE * SQUARE_SIZE)
                self.particle_system.create_button_press_particles(x, y, color)

    def update_text(self):
        """Обновление текстов с текущими значениями"""
        current_time = time.time() - self.start_time

        if self.score_text:
            self.score_text.text = f"Белые: {self.board.white_score}   Черные: {self.board.black_score}"

            # Анимация текста текущего игрока
            if self.board.current_player:
                alpha = int(255 * (0.7 + 0.3 * math.sin(current_time * 3)))
                self.player_text.color = (WHITE[0], WHITE[1], WHITE[2], alpha)
                self.player_text.text = f"Ходят: Белые"
            else:
                alpha = int(255 * (0.7 + 0.3 * math.sin(current_time * 3)))
                self.player_text.color = (RED[0], RED[1], RED[2], alpha)
                self.player_text.text = f"Ходят: Черные"

            self.pieces_text.text = f"Осталось шашек: Белые - {self.board.white_pieces}, Черные - {self.board.black_pieces}"

    def on_draw(self):
        self.clear()
        current_time = time.time() - self.start_time

        # Рисуем частицы
        self.particle_system.draw()

        # Рисуем доску (она сама знает свое смещение)
        self.board.draw()

        # Анимация кнопки выхода (пульсация)
        pulse = math.sin(current_time * 2) * 0.1 + 0.9
        exit_left = SCREEN_WIDTH - 140
        exit_right = SCREEN_WIDTH - 20
        exit_top = SCREEN_HEIGHT - 20
        exit_bottom = SCREEN_HEIGHT - 60

        arcade.draw_lrbt_rectangle_filled(
            left=exit_left,
            right=exit_right,
            top=exit_top,
            bottom=exit_bottom,
            color=(
                int(RED[0] * pulse),
                int(RED[1] * pulse),
                int(RED[2] * pulse)
            )
        )

        if self.exit_button_text:
            self.exit_button_text.draw()

        # Подсказка про калькулятор с анимацией
        if self.board.game_over and not self.calculator.is_active:
            blink = 0.5 + 0.5 * math.sin(current_time * 2)
            alpha = int(255 * blink)
            self.calculator_hint_text.color = (LIGHT_BLUE[0], LIGHT_BLUE[1], LIGHT_BLUE[2], alpha)
            self.calculator_hint_text.draw()

        # Обновляем и рисуем тексты
        self.update_text()
        if self.score_text:
            # Анимация текста счета
            scale = 1 + 0.05 * math.sin(current_time * 1.5)
            arcade.Text(
                self.score_text.text,
                self.score_text.x,
                self.score_text.y,
                self.score_text.color,
                int(18 * scale)
            ).draw()

            self.player_text.draw()

            # Анимация текста остатка шашек
            slide = math.sin(current_time) * 2
            arcade.Text(
                self.pieces_text.text,
                self.pieces_text.x,
                SCREEN_HEIGHT - 90 + slide,
                self.pieces_text.color,
                self.pieces_text.font_size
            ).draw()

        # Рисуем калькулятор, если он активен
        self.calculator.draw()

        # Если игра окончена и калькулятор не активен
        if self.board.game_over and not self.calculator.is_active:
            # Пульсирующий полупрозрачный черный прямоугольник
            pulse = 0.7 + 0.3 * math.sin(current_time * 2)
            overlay_left = SCREEN_WIDTH // 2 - 200
            overlay_right = SCREEN_WIDTH // 2 + 200
            overlay_top = SCREEN_HEIGHT // 2 + 100
            overlay_bottom = SCREEN_HEIGHT // 2 - 100

            arcade.draw_lrbt_rectangle_filled(
                left=overlay_left,
                right=overlay_right,
                top=overlay_top,
                bottom=overlay_bottom,
                color=(0, 0, 0, int(200 * pulse))
            )

            if self.winner_text:
                # Анимация текста победителя
                winner_scale = 1 + 0.1 * math.sin(current_time * 3)
                arcade.Text(
                    f"Победили {self.board.winner}!",
                    self.winner_text.x,
                    self.winner_text.y,
                    self.winner_text.color,
                    int(36 * winner_scale),
                    anchor_x="center",
                    anchor_y="center"
                ).draw()

                # Анимация финального текста
                blink = 0.5 + 0.5 * math.sin(current_time * 2)
                alpha = int(255 * blink)
                arcade.Text(
                    "Нажмите любую клавишу для завершения",
                    self.final_text.x,
                    self.final_text.y,
                    (WHITE[0], WHITE[1], WHITE[2], alpha),
                    20,
                    anchor_x="center",
                    anchor_y="center"
                ).draw()

    def on_mouse_press(self, x, y, button, modifiers):
        # Обработка кликов по калькулятору
        if self.calculator.is_active and self.calculator.handle_click(x, y, self.particle_system):
            return

        if self.board.game_over and not self.calculator.is_active:
            end_view = EndView(self.board.winner, self.board.white_score, self.board.black_score)
            self.window.show_view(end_view)
            return

        # Проверка нажатия кнопки выхода
        exit_left = SCREEN_WIDTH - 140
        exit_right = SCREEN_WIDTH - 20
        exit_top = SCREEN_HEIGHT - 20
        exit_bottom = SCREEN_HEIGHT - 60

        if (exit_left <= x <= exit_right and
                exit_bottom <= y <= exit_top):
            end_view = EndView("Игра прервана", self.board.white_score, self.board.black_score)
            self.window.show_view(end_view)
            return

        # Преобразование координат мыши в координаты доски (учитываем смещение)
        board_x = x - self.board_offset_x
        board_y = y - self.board_offset_y

        if 0 <= board_x < BOARD_SIZE * SQUARE_SIZE and 0 <= board_y < BOARD_SIZE * SQUARE_SIZE:
            # Используем целочисленное деление // чтобы получить целые числа
            col = board_x // SQUARE_SIZE
            row = board_y // SQUARE_SIZE

            # Преобразуем в целые числа на всякий случай
            row = int(row)
            col = int(col)

            if self.board.selected_piece:
                if self.board.move_piece(row, col, self.particle_system):
                    return

            self.board.select_piece(row, col)

    def on_key_press(self, key, modifiers):
        # Обработка клавиши K для открытия/закрытия калькулятора
        if key == arcade.key.K and self.board.game_over:
            if not self.calculator.is_active:
                # Открываем калькулятор
                self.calculator.is_active = True
                # Создаем частицы при открытии калькулятора
                self.particle_system.create_king_particles(
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, True
                )
            else:
                # Закрываем калькулятор
                self.calculator.is_active = False
            return

        # Если калькулятор активен, обрабатываем ESC для его закрытия
        if key == arcade.key.ESCAPE and self.calculator.is_active:
            self.calculator.is_active = False
            return


class EndView(arcade.View):
    def __init__(self, winner: str, white_score: int, black_score: int):
        super().__init__()
        self.winner = winner
        self.white_score = white_score
        self.black_score = black_score
        self.title_text = None
        self.winner_text = None
        self.score_title_text = None
        self.score_text = None
        self.instruction_text = None
        self.control_text = None
        self.particle_system = ParticleSystem()
        self.start_time = time.time()

        # Инициализируем текстовые объекты сразу
        self.setup_text()

    def setup_text(self):
        self.title_text = arcade.Text(
            "ИГРА ОКОНЧЕНА",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.7,
            GOLD,
            50,
            anchor_x="center",
            anchor_y="center"
        )

        self.winner_text = arcade.Text(
            f"Победитель: {self.winner}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.5,
            WHITE,
            36,
            anchor_x="center",
            anchor_y="center"
        )

        self.score_title_text = arcade.Text(
            "Финальный счет:",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.4,
            LIGHT_BLUE,
            28,
            anchor_x="center",
            anchor_y="center"
        )

        self.score_text = arcade.Text(
            f"Белые: {self.white_score}   Черные: {self.black_score}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.33,
            WHITE,
            32,
            anchor_x="center",
            anchor_y="center"
        )

        self.instruction_text = arcade.Text(
            "Нажмите любую клавишу для выхода",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.2,
            YELLOW,
            24,
            anchor_x="center",
            anchor_y="center"
        )

        self.control_text = arcade.Text(
            "ESC для выхода, R для рестарта",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.1,
            LIGHT_GRAY,
            20,
            anchor_x="center",
            anchor_y="center"
        )

    def on_show_view(self):
        arcade.set_background_color(DARK_PURPLE)
        # Создаем частицы победы
        color = WHITE if self.winner == "Белые" else RED
        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            self.particle_system.create_win_particles(x, y, color)

    def on_update(self, delta_time):
        self.particle_system.update(delta_time)

        # Продолжаем создавать частицы
        current_time = time.time() - self.start_time
        if current_time % 0.3 < 0.1:
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            color = WHITE if self.winner == "Белые" else RED
            self.particle_system.create_button_press_particles(x, y, color)

    def on_draw(self):
        self.clear()
        current_time = time.time() - self.start_time

        # Рисуем частицы
        self.particle_system.draw()

        # Анимация заголовка
        title_scale = 1 + 0.1 * math.sin(current_time * 2)
        arcade.Text(
            "ИГРА ОКОНЧЕНА",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.7,
            GOLD,
            int(50 * title_scale),
            anchor_x="center",
            anchor_y="center"
        ).draw()

        # Анимация текста победителя
        winner_color = WHITE if self.winner == "Белые" else RED
        blink = 0.7 + 0.3 * math.sin(current_time * 3)
        alpha = int(255 * blink)
        arcade.Text(
            f"Победитель: {self.winner}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.5,
            (winner_color[0], winner_color[1], winner_color[2], alpha),
            36,
            anchor_x="center",
            anchor_y="center"
        ).draw()

        # Анимация заголовка счета
        slide = math.sin(current_time) * 5
        arcade.Text(
            "Финальный счет:",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.4 + slide,
            LIGHT_BLUE,
            28,
            anchor_x="center",
            anchor_y="center"
        ).draw()

        # Анимация текста счета
        score_scale = 1 + 0.05 * math.sin(current_time * 1.5)
        arcade.Text(
            f"Белые: {self.white_score}   Черные: {self.black_score}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.33,
            WHITE,
            int(32 * score_scale),
            anchor_x="center",
            anchor_y="center"
        ).draw()

        # Анимация текста инструкции
        blink = 0.5 + 0.5 * math.sin(current_time * 2)
        alpha = int(255 * blink)
        arcade.Text(
            "Нажмите любую клавишу для выхода",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.2,
            (YELLOW[0], YELLOW[1], YELLOW[2], alpha),
            24,
            anchor_x="center",
            anchor_y="center"
        ).draw()

        # Анимация управляющего текста
        control_alpha = int(255 * (0.6 + 0.4 * math.sin(current_time * 1.5)))
        arcade.Text(
            "ESC для выхода, R для рестарта",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT * 0.1,
            (LIGHT_GRAY[0], LIGHT_GRAY[1], LIGHT_GRAY[2], control_alpha),
            20,
            anchor_x="center",
            anchor_y="center"
        ).draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            game_view = GameView()
            self.window.show_view(game_view)
        elif key == arcade.key.ESCAPE:
            arcade.close_window()
        else:
            arcade.close_window()


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
