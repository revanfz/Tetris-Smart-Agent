import pygame
from .settings import *
from .tetromino import Tetromino, Block
from .timer import Timer
from numpy import uint8, zeros
from random import choice

class Matrix:
    def __init__(self, get_next_shape, update_score, initial_shape=None):
        self.sprites = pygame.sprite.Group()

        self.get_next_shape = get_next_shape
        self.update_score = update_score

        self.current_level = 1
        self.current_scores = 0
        self.current_lines = 0
        self.block_placed = 0
        self.last_block_placed = 0
        self.last_deleted_rows = 0
        self.last_landing_height = 0

        # self.field_data = zeros((ROW, COL), dtype=uint8)
        self.field_data = [[0 for x in range(COL)] for y in range(ROW)]

        self.tetromino = Tetromino(
            initial_shape,
            self.sprites,
            self.create_new_tetromino,
            self.field_data,
        )

        self.down_speed = FALL_SPEED
        self.down_speed_faster = self.down_speed * 0.25

        self.timers = {
            # "verticalMove": Timer(self.down_speed, True, self.move_down),
            # "horizontalMove": Timer(MOVE_WAIT_TIME),
            # "rotate": Timer(ROTATE_WAIT_TIME),
        }
        # self.timers["verticalMove"].activate()

    def soft_drop(self):
        # self.tetromino.soft_drop()
        self.move_down()

    def drop(self):
        self.tetromino.drop_shape()

    def calculate_score(self):
        if self.last_deleted_rows != 0:
            self.current_lines += self.last_deleted_rows
            self.current_scores += CLEAR_REWARDS[self.last_deleted_rows] * self.current_level

            if self.current_lines % 10 == 0 and self.current_lines > 0:
                self.current_level += 1
                self.down_speed *= 0.75
                self.down_speed_faster = self.down_speed * 0.25
                # self.timers["verticalMove"].duration = self.down_speed

            self.update_score(self.current_lines, self.current_scores, self.current_level)

    def create_new_tetromino(self):
        # self.timers["verticalMove"].duration = self.down_speed
        self.last_block_placed = self.block_placed
        self.block_placed += 1
        self.check_finished_row()
        self.tetromino = Tetromino(
            self.get_next_shape(),
            self.sprites,
            self.create_new_tetromino,
            self.field_data,
        )

    def timer_update(self):
        for timer in self.timers.values():
            timer.update()

    def input(self, amount):
        return self.tetromino.move_horizontal(amount)

    def move_down(self):
        self.tetromino.move_down()

    def draw_pixel(self, surface, line_surface):
        for col in range(1, COL):
            x = col * PIXEL
            pygame.draw.line(
                line_surface, "WHITE", (x, 0), (x, surface.get_height()), 1
            )

        for row in range(1, ROW):
            y = row * PIXEL
            pygame.draw.line(
                line_surface, "WHITE", (0, y), (surface.get_width(), y)
            )

        surface.blit(line_surface, (0, 0))

    def check_finished_row(self):
        delete_rows = []
        for i, row in enumerate(self.field_data):
            if all(row):
                delete_rows.append(i)

        if delete_rows:
            for target_row in delete_rows:
                for block in self.field_data[target_row]:
                    block.kill()

                for row in self.field_data:
                    for block in row:
                        if block and block.pos.y < target_row:
                            block.pos.y += 1

            self.field_data = [[0 for x in range(COL)] for y in range(ROW)]
            for block in self.sprites:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block
        
        self.last_deleted_rows = len(delete_rows)
        self.calculate_score()

    def get_falling_block(self, falling_tetromino: Tetromino, next_tetromino: str):
        falling_surface = pygame.Surface((84, 84))
        next_surface = pygame.Surface((84, 84))
        self.sprites.update()
        falling_surface.fill((67, 70, 75))
        next_surface.fill((67, 70, 75))
        
        block_shape = falling_tetromino.shape
        falling_tetromino = falling_tetromino.blocks.copy()
        offset = 2 if block_shape != 'I' else 1
        for block in falling_tetromino:
            block.rect.y += PIXEL * (offset + 2)
            block.rect.x -= PIXEL * 3
            image = pygame.image.load(block.image)
            image = pygame.transform.scale(image, (PIXEL, PIXEL))
            falling_surface.blit(image, block.rect)

        tetromino_target = TETROMINOS[next_tetromino]
        tetromino_image =  BLOCK_IMG_DIR + "/" + tetromino_target["image"]
        next_block = [
            Block(self.sprites, pos, tetromino_target["color"], tetromino_image) for pos in tetromino_target["shape"]
        ]
        for block in next_block:
            block.rect.y += PIXEL * (offset + 2)
            block.rect.x -= PIXEL * 3
            image = pygame.image.load(block.image)
            image = pygame.transform.scale(image, (PIXEL, PIXEL))
            next_surface.blit(image, block.rect)

        return (falling_surface, next_surface)
        

    def run(self, display_surface):
        surface = pygame.Surface((MATRIX_WIDTH, MATRIX_HEIGHT))
        rect = surface.get_rect(topleft=(PIXEL, PIXEL))

        self.timer_update()
        self.sprites.update()
        surface.fill((67, 70, 75))
        # self.sprites.draw(self.surface)
        for sprite in self.sprites:
            image = pygame.image.load(sprite.image)
            image = pygame.transform.scale(image, (PIXEL, PIXEL))
            # image = pygame.Surface([PIXEL, PIXEL])
            # image.fill(color=sprite.color)
            surface.blit(image, sprite.rect)
            
        display_surface.blit(surface, (PIXEL, PIXEL))

        return surface

    def draw_line(self, display_surface, surface):
        rect = surface.get_rect(topleft=(PIXEL, PIXEL))
        line_surface = surface.copy()
        line_surface.fill((0, 255, 0))
        line_surface.set_colorkey((0, 255, 0))
        line_surface.set_alpha(125)
        self.draw_pixel(surface, line_surface)
        display_surface.blit(surface, (PIXEL, PIXEL))
        pygame.draw.rect(display_surface, "WHITE", rect, 2, 2)

