import os
import numpy as np
import pygame

from sys import exit
from random import choice
from .settings import *
from .matrix import Matrix
from .score import Score
from .preview import Preview


class Tetris:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Tetris Smart Agent")

        # self.next_shapes = ['Z' for shape in range(3)]
        self.next_shapes = [choice(list(TETROMINOS.keys())) for shape in range(3)]
        # print(self.next_shapes)

        self.game = Matrix(self.get_next_shape, self.update_score)
        self.score = Score()
        self.preview = Preview()

        self.game_over_screen = None
        # self.game_over_screen = os.path.join(
        #     IMG_DIR, "game_over.jpg"
        # )

    def update_score(self, lines, scores, level):
        self.score.lines = lines
        self.score.level = level
        self.score.scores = scores

    def get_next_shape(self):
        next_shape = self.next_shapes.pop(0)
        # self.next_shapes.append('Z')
        self.next_shapes.append(choice(list(TETROMINOS.keys())))
        return next_shape

    def run(self):
        while True:
            if self.game.tetromino.game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                if self.game_over_screen is None:
                    self.game_over_screen = os.path.join(IMG_DIR, "game_over.jpg")
                    pygame.image.save(self.display_surface, self.game_over_screen)
                    self.game_over_screen = pygame.image.load(self.game_over_screen)
                     
                font = pygame.font.Font(None, 36)
                game_over_text = font.render("Game Over", True, (255, 255, 255))
                score_text = font.render("Score: " + str(self.score.scores), True, (255, 255, 255))

                # Menempatkan teks di tengah layar
                game_over_rect = game_over_text.get_rect(center=(self.display_surface.get_width() // 2, 200))
                score_rect = score_text.get_rect(center=(self.display_surface.get_width() // 2, 250))

                # Menambahkan teks ke gambar game over
                self.display_surface.blit(self.game_over_screen, (0, 0))
                self.display_surface.blit(game_over_text, game_over_rect)
                self.display_surface.blit(score_text, score_rect)
                pygame.display.update()
                self.clock.tick(24)
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.game.drop()

                        if event.key == pygame.K_DOWN:
                            if not self.game.speedup:
                                self.game.speedup = True
                                self.game.timers["verticalMove"].duration = (
                                    self.game.down_speed_faster
                                )

                        if event.key == pygame.K_UP:
                            if not self.game.timers["rotate"].active:
                                self.game.tetromino.rotate()
                                self.game.timers["rotate"].activate()

                        if not self.game.timers["horizontalMove"].active:
                            if event.key == pygame.K_RIGHT:
                                self.game.input(1)
                                self.game.timers["horizontalMove"].activate()

                            if event.key == pygame.K_LEFT:
                                self.game.input(-1)
                                self.game.timers["horizontalMove"].activate()

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_DOWN:
                            if self.game.speedup:
                                self.game.speedup = False
                                self.game.timers["verticalMove"].duration = (
                                    self.game.down_speed
                                )

                self.display_surface.fill((67, 70, 75))
                self.game.run()
                self.score.run()
                self.preview.run(self.next_shapes)
                pygame.display.update()
                self.clock.tick(FPS)

    def step(self, action):
        if action == 0:
            if not self.game.timers["rotate"].active:
                self.game.tetromino.rotate()
                self.game.timers["rotate"].activate()

        if not self.game.timers["horizontalMove"].active:
            if action == 1:
                self.game.input(1)
                self.game.timers["horizontalMove"].activate()

            if action == 2:
                self.game.input(-1)
                self.game.timers["horizontalMove"].activate()

        if action == 3:
            self.game.drop()

        if action == 4:
            if not self.game.speedup:
                self.game.speedup = True
                self.game.timers["verticalMove"].duration = self.game.down_speed_faster

        if action == 4:
            if self.game.speedup:
                self.game.speedup = False
                self.game.timers["verticalMove"].duration = self.game.down_speed

    def _get_obs(self):
        observation_value = np.zeros_like(self.game.field_data, dtype=np.uint8)
        for i in range(len(self.game.field_data)):
            for j in range(len(self.game.field_data[i])):
                if self.game.field_data[i][j]:
                    observation_value[i][j] = 1
        return {"board": np.array(observation_value)}

    def _get_info(self):
        return {
            "scores": self.score.scores,
            "lines": self.score.lines,
            "block_placed": self.game.block_placed,
        }

    def evaluate(self):
        reward = 0

        if self.game.tetromino.game_over:
            reward = -100
        else:
            reward = 100 * self.score.lines
            reward += 10 * self.game.block_placed

        return reward

    def is_done(self):
        return self.game.tetromino.game_over

    def view(self):
        if not self.game.tetromino.game_over:
            self.display_surface.fill((67, 70, 75))
            self.game.run()
            self.score.run()
            self.preview.run(self.next_shapes)
            pygame.event.pump()
            pygame.display.update()
            self.clock.tick(24)
        else:
            if self.game_over_screen is None:
                self.game_over_screen = os.path.join(IMG_DIR, "game_over.jpg")
                pygame.image.save(self.display_surface, self.game_over_screen)
                self.game_over_screen = pygame.image.load(self.game_over_screen)
                     
            font = pygame.font.Font(None, 36)
            game_over_text = font.render("Game Over", True, (255, 255, 255))
            score_text = font.render("Score: " + str(self.score.scores), True, (255, 255, 255))

            # Menempatkan teks di tengah layar
            game_over_rect = game_over_text.get_rect(center=(self.display_surface.get_width() // 2, 200))
            score_rect = score_text.get_rect(center=(self.display_surface.get_width() // 2, 250))

            # Menambahkan teks ke gambar game over
            self.display_surface.blit(self.game_over_screen, (0, 0))
            self.display_surface.blit(game_over_text, game_over_rect)
            self.display_surface.blit(self.game_over_screen, (0, 0))
            pygame.display.update()
            pygame.event.pump()
            self.clock.tick(24)
