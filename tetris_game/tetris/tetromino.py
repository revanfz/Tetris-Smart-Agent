import pygame
from .settings import *


class Tetromino:
    def __init__(self, shape, group, create_new_tetromino, field_data):
        self.shape = shape
        self.block_position = TETROMINOS[shape]["shape"]
        self.color = TETROMINOS[shape]["color"]
        self.image = BLOCK_IMG_DIR + "/" + TETROMINOS[shape]["image"]
        self.blocks = [
            Block(group, pos, self.color, self.image) for pos in self.block_position
        ]
        self.create_new_tetromino = create_new_tetromino
        self.field_data = field_data

        self.game_over = False

    def drop_shape(self):
        # y baris, x kolom
        lowest_row_dict = {}

        for block in self.blocks:
            # ekstrak nilai baris tertinggi yang berisi pada setiap kolom
            if (
                block.pos.x not in lowest_row_dict
                or block.pos.y > lowest_row_dict[block.pos.x]
            ):
                lowest_row_dict[block.pos.x] = block.pos.y

        # mapping jarak dari baris yang sudah terisi dengan shape yang akan turun
        distance_dict = {}
        for item in set(block.pos.x for block in self.blocks):
            temp = next(
                (i for i, row in enumerate(self.field_data) if row[int(item)] != 0),
                20,
            )
            if temp is not None:
                distance_dict[item] = temp - lowest_row_dict[item]

        # mengambil jarak yang terdekat untuk collision
        distance = min(distance_dict.values())

        for block in self.blocks:
            block.pos.y += distance - 1

    def set_game_over(self):
        self.game_over = True

    def move_down(self):
        if self.check_vertical_collision(1):
            for block in self.blocks:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block

            if self.check_ceiling_collision():
                self.set_game_over()
                print("Game Over")
            else:
                self.create_new_tetromino()
        else:
            for block in self.blocks:
                block.pos.y += 1

    def move_horizontal(self, amount):
        if self.check_horizontal_collision(amount):
            return
        else:
            for block in self.blocks:
                block.pos.x += amount

    def check_horizontal_collision(self, amount):
        collision_list = [
            block.horizontal_collide(int(block.pos.x + amount), self.field_data)
            for block in self.blocks
        ]
        return True if sum(collision_list) else False

    def check_vertical_collision(self, amount):
        collision_list = [
            block.vertical_collide(int(block.pos.y + amount), self.field_data)
            for block in self.blocks
        ]
        return True if sum(collision_list) else False

    def check_ceiling_collision(self):
        for blocks in self.blocks:
            if blocks.pos.y <= 0:
                return True

        return False

    def rotate(self):
        if self.shape != "O":
            pivot_pos = self.blocks[0].pos  # pivot point
            # new block position after rotating
            new_block_position = [block.rotate(pivot_pos) for block in self.blocks]

            # check collision
            for pos in new_block_position:
                # horizontal
                if pos.x < 0 or pos.x >= COL:
                    return

                # vertical / floor
                if pos.y >= ROW:
                    return

                # field check (with other pieces)
                if self.field_data[int(pos.y)][int(pos.x)]:
                    return

            for i, block in enumerate(self.blocks):
                block.pos = new_block_position[i]


class Block(pygame.sprite.Sprite):
    def __init__(self, group, pos, color, image):
        super().__init__(group)
        self.image = pygame.Surface((PIXEL, PIXEL))
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (PIXEL, PIXEL))
        self.pos = pygame.Vector2(pos) + pygame.Vector2(COL // 2 - 1, -1)

        self.rect = self.image.get_rect(topleft=self.pos * PIXEL)

    def rotate(self, pivot_pos):
        return pivot_pos + (self.pos - pivot_pos).rotate(90)

    def update(self):
        self.rect.topleft = self.pos * PIXEL

    def horizontal_collide(self, target: int, field_data):
        if not 0 <= target < COL:
            return True
        if field_data[int(self.pos.y)][target]:
            return True

        return False

    def vertical_collide(self, target: int, field_data):
        if target >= ROW:
            return True

        if target >= 0 and field_data[target][int(self.pos.x)]:
            return True

        return False
