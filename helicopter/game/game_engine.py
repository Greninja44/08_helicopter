"""
GameEngine: owns the helicopter and all obstacles.

Touching either wall of an obstacle ends the game; press R on the
game-over screen to start a new game. Distance travelled is tracked as
the score. Space activates a shield that absorbs exactly one collision.
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
        self.shield_active = False
        self.shield_absorbed = None   # obstacle the shield last absorbed; ignored while passing through it

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
        elif key == pygame.K_SPACE and not self.game_over:
            self.shield_active = True

    def _hit_obstacle(self):
        heli_rect = self.helicopter.get_rect()
        for obstacle in self.obstacles:
            if obstacle is self.shield_absorbed:
                continue
            if heli_rect.colliderect(obstacle.get_top_rect()) or heli_rect.colliderect(obstacle.get_bottom_rect()):
                return obstacle
        return None

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
        if self.shield_absorbed not in self.obstacles:
            self.shield_absorbed = None

        hit = self._hit_obstacle()
        if hit is not None:
            if self.shield_active:
                self.shield_active = False
                self.shield_absorbed = hit
            else:
                self.game_over = True

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.helicopter, self.obstacles)
        if self.shield_active:
            renderer.draw_shield(surface, self.helicopter.get_rect())
        if self.game_over:
            renderer.draw_banner(surface, font, "GAME OVER - press R to restart")
            renderer.draw_banner(surface, font, f"Final distance: {self.distance_m} m", y_offset=32)
        else:
            renderer.draw_text(surface, font, f"Distance: {self.distance_m} m", (10, 10))
            if self.shield_active:
                renderer.draw_text(surface, font, "SHIELD ON", (10, 36), color=renderer.COLOR_SHIELD)
            else:
                renderer.draw_text(surface, font, "SPACE: shield", (10, 36))
