"""
GameEngine: owns the helicopter and all obstacles.

Touching either wall of an obstacle ends the game; press R on the
game-over screen to start a new game. Distance travelled is tracked as
the score.
"""

import random

import pygame

from game.helicopter import Helicopter
from game.obstacle import Obstacle
from game.renderer import WIDTH, HEIGHT

SPAWN_INTERVAL_FRAMES = 90
GAP_HEIGHT = 150
WALL_WIDTH = 60
SCROLL_SPEED = 3
PIXELS_PER_METER = 10


class GameEngine:
    def __init__(self):
        self.reset()

    def reset(self):
        self.helicopter = Helicopter(x=100, y=HEIGHT / 2)
        self.obstacles = []
        self.frames_until_spawn = 0
        self.game_over = False
        self.distance = 0.0   # in pixels scrolled

    def _spawn_obstacle(self):
        margin = 60
        gap_y = random.randint(margin + GAP_HEIGHT // 2, HEIGHT - margin - GAP_HEIGHT // 2)
        self.obstacles.append(Obstacle(
            x=WIDTH, gap_y=gap_y, gap_height=GAP_HEIGHT,
            wall_width=WALL_WIDTH, screen_height=HEIGHT, speed=SCROLL_SPEED,
        ))

    @property
    def distance_m(self):
        return int(self.distance // PIXELS_PER_METER)

    def handle_input(self, keys_pressed):
        if self.game_over:
            return
        self.helicopter.handle_input(keys_pressed)

    def handle_keydown(self, key):
        if key == pygame.K_r and self.game_over:
            self.reset()

    def _hit_obstacle(self):
        heli_rect = self.helicopter.get_rect()
        for obstacle in self.obstacles:
            if heli_rect.colliderect(obstacle.get_top_rect()) or heli_rect.colliderect(obstacle.get_bottom_rect()):
                return True
        return False

    def update(self):
        if self.game_over:
            return

        self.helicopter.update(HEIGHT)
        self.distance += SCROLL_SPEED

        self.frames_until_spawn -= 1
        if self.frames_until_spawn <= 0:
            self._spawn_obstacle()
            self.frames_until_spawn = SPAWN_INTERVAL_FRAMES

        for obstacle in self.obstacles:
            obstacle.update()
        self.obstacles = [o for o in self.obstacles if not o.is_off_screen()]

        if self._hit_obstacle():
            self.game_over = True

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.helicopter, self.obstacles)
        if self.game_over:
            renderer.draw_banner(surface, font, "GAME OVER - press R to restart")
            renderer.draw_banner(surface, font, f"Final distance: {self.distance_m} m", y_offset=32)
        else:
            renderer.draw_text(surface, font, f"Distance: {self.distance_m} m", (10, 10))
