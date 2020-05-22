

import math
import colorsys
import random
from typing import Dict, Optional, ClassVar, Any

import pyglet
from pyglet.gl import glEnable, glBlendFunc, glClearColor, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, \
    glColor4f, glDisable, GL_DEPTH_TEST
from pyglet.window import key

from constants import GRID_SIZE
from client import Client, Board, Vec2, Highscores


def center(img: pyglet.image.ImageData):
    img.anchor_x = img.width * 0.5
    img.anchor_y = img.height * 0.5


def get_grid_space(mx, my):
    return Vec2((mx // GRID_SIZE), (my // GRID_SIZE))


class SceneManager:
    def __init__(self):
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None

    def add_scene(self, name: str, scene):
        self.scenes[name] = scene

    def change_scene(self, name: str):
        scene = self.scenes.get(name)
        if scene is not None:
            if self.current_scene is not None:
                self.current_scene.on_close_scene()
            scene.on_scene_init()
            self.current_scene = scene


class Scene:

    def __init__(self, scene_manager: SceneManager):
        self.scene_manager: SceneManager = scene_manager

    def on_scene_init(self):
        pass

    def on_close_scene(self):
        pass

    def on_draw(self, window: pyglet.window.Window):
        pass

    def on_text(self, text):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_release(self, x, y, buttons, modifiers):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_key_press(self, symbol, modifiers):
        pass


class GameScene(Scene):
    def __init__(self, username: str, scene_manager: SceneManager, window: pyglet.window.Window):
        super().__init__(scene_manager)

        self.bot = None

        self.USERNAME = username
        self.client = Client(self.USERNAME)
        self.h = Highscores()
        self.moves = []

        self.game_over = pyglet.text.Label('GAME OVER',
                                           font_name='Times New Roman',
                                           font_size=48,
                                           x=window.width // 2, y=window.height // 2,
                                           anchor_x='center', anchor_y='center')

        self.score = pyglet.text.Label('score:',
                                       font_name='Times New Roman',
                                       font_size=24,
                                       x=window.width // 2, y=window.height // 2 - 60,
                                       anchor_x='center', anchor_y='center')

        self.current_score = 0

        self.game_over_2 = pyglet.text.Label('press r to retry',
                                             font_name='Times New Roman',
                                             font_size=24,
                                             x=window.width // 2, y=window.height // 2 - 90,
                                             anchor_x='center', anchor_y='center')
        self.game_over_3 = pyglet.text.Label('press h for highscores',
                                             font_name='Times New Roman',
                                             font_size=24,
                                             x=window.width // 2, y=window.height // 2 - 120,
                                             anchor_x='center', anchor_y='center')

        self.in_game_score = pyglet.text.Label('score',
                                               font_name='Times New Roman',
                                               font_size=28,
                                               x=window.width // 2, y=window.height - 2,
                                               anchor_x='center', anchor_y='top')

        self.game_over.color = (255, 0, 0, 255)
        self.game_over_2.color = self.game_over.color
        self.game_over_3.color = self.game_over.color

        self.label = pyglet.text.Label('Hello, world',
                                       font_name='Times New Roman',
                                       font_size=36,
                                       x=window.width // 2, y=window.height // 2,
                                       anchor_x='center', anchor_y='center')

        self.grid_space = pyglet.resource.image("images/grid_space.png")
        self.grid_space_selected = pyglet.resource.image("images/grid_space_selected.png")
        self.grid_fill = pyglet.resource.image("images/grid_fill.png")

        center(self.grid_space)
        center(self.grid_space_selected)
        center(self.grid_fill)

        self.currently_over = Vec2()
        self.board_overlay = BoardOverlay(25, self.grid_fill)

    def on_draw(self, window: pyglet.window.Window):

        # Todo: Move highscores to different menu
        self.h.update()

        self.client.update()

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        board = self.client.board

        if board is not None:
            if board.can_move:
                glColor4f(1, 1, 1, 1)
                self.label.color = (255, 255, 255, 255)
            else:
                glColor4f(1, 1, 1, 0.2)
                self.label.color = (255, 255, 255, 128)

            self.board_overlay.update_colors(board)
            self.board_overlay.draw()

            for i in range(board.height):
                for j in range(board.width):
                    pos = Vec2(j, i)

                    if (pos == self.currently_over or is_in_move(pos, self.moves)) \
                            and board.can_move:
                        self.grid_space_selected.blit((j + 0.5) * GRID_SIZE, (i + 0.5) * GRID_SIZE)
                    else:
                        # grid_fill.blit((j + 0.5) * GRID_SIZE, (i + 0.5) * GRID_SIZE)
                        self.grid_space.blit((j + 0.5) * GRID_SIZE, (i + 0.5) * GRID_SIZE)

                    self.label.text = str(board.get_from_coordinate(pos))

                    self.label.x = (j + 0.5) * GRID_SIZE
                    self.label.y = (i + 0.5) * GRID_SIZE

                    self.label.draw()

            if board.can_move:
                self.in_game_score.text = "Score: " + str(self.current_score)
                self.in_game_score.draw()
            else:
                self.game_over.draw()
                self.score.text = "Final score: " + str(self.current_score)
                self.score.draw()
                self.game_over_2.draw()
                self.game_over_3.draw()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        now_over = get_grid_space(x, y)

        if now_over != self.currently_over:
            for i in range(len(self.moves)):
                if now_over == self.moves[i]:
                    self.moves = self.moves[0:i]
                    break

            self.moves.append(now_over)

            self.currently_over = now_over

    def on_mouse_motion(self, x, y, dx, dy):
        self.currently_over = get_grid_space(x, y)

    def on_mouse_release(self, x, y, buttons, modifiers):
        board = self.client.board

        if board is not None:
            if board.move_is_valid(self.moves):

                for move in self.moves:
                    self.current_score += board.get_from_coordinate(move)

                built = board.build_move(self.moves)
                self.client.send(built)

        self.moves = []

    def on_mouse_press(self, x, y, button, modifiers):
        self.moves.append(self.currently_over)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.R:
            self.client = Client(self.USERNAME)
            self.current_score = 0
        elif symbol == key.H:
            self.scene_manager.change_scene("HIGHSCORE")


class HighscoreScene(Scene):
    def __init__(self, scene_manager, window):
        super().__init__(scene_manager)

        self.USERNAME = ""

        self.list = pyglet.text.Label('',
                                      font_name='Times New Roman',
                                      font_size=12,
                                      x=5, y=window.height - 2,
                                      anchor_x='left', anchor_y='top', multiline=True, width=window.width)

        self.waiting = pyglet.text.Label('LOADING HIGHSCORES',
                                         font_name='Times New Roman',
                                         font_size=36,
                                         x=window.width // 2, y=window.height // 2,
                                         anchor_x='center', anchor_y='center')

        self.highscores: Optional[Highscores] = None

    def on_scene_init(self):
        self.highscores = Highscores()

    def on_close_scene(self):
        self.highscores = None

    def on_draw(self, window: pyglet.window.Window):
        self.highscores.update()

        if self.highscores.is_waiting_for_response:
            self.waiting.draw()
        else:
            self.list.text = self.highscores.format_highscores()
            self.list.draw()

    def on_key_press(self, symbol, modifiers):
        self.scene_manager.change_scene("GAME")


class UsernameSelectScene(Scene):

    def __init__(self, scene_manager, window):
        super().__init__(scene_manager)

        self.window = window

        self.USERNAME = ""

        self.label_a = pyglet.text.Label('Enter Username:',
                                         font_name='Times New Roman',
                                         font_size=36,
                                         x=window.width // 2, y=window.height // 2 + 50,
                                         anchor_x='center', anchor_y='center')

        self.label = pyglet.text.Label('Hello, world',
                                       font_name='Times New Roman',
                                       font_size=36,
                                       x=window.width // 2, y=window.height // 2,
                                       anchor_x='center', anchor_y='center')

    def on_draw(self, window: pyglet.window.Window):
        self.label.text = self.USERNAME
        self.label_a.draw()
        self.label.draw()

    def on_text(self, text):
        self.USERNAME += text

    def on_key_press(self, symbol, modifiers):
        if symbol == key.RETURN or symbol == key.ENTER:
            self.scene_manager.add_scene("HIGHSCORE", HighscoreScene(self.scene_manager, self.window))

            game_scene = GameScene(self.USERNAME, self.scene_manager, self.window)

            self.scene_manager.add_scene("GAME", game_scene)
            self.scene_manager.change_scene("GAME")
        elif symbol == key.BACKSPACE:
            if len(self.USERNAME) > 0:
                self.USERNAME = self.USERNAME[:-1]


class BoardOverlay:
    def __init__(self, squares, grid_fill):
        self.width = int(math.sqrt(squares))
        self.height = self.width

        self.colors = []

        self.data = []

        for i in range(self.height):
            self.data.append([])
            for j in range(self.width):
                self.data[i].append(pyglet.sprite.Sprite(
                    grid_fill, (j + 0.5) * GRID_SIZE, (i + 0.5) * GRID_SIZE))

    @staticmethod
    def create_color(index: int):
        if index == 0:
            return 0, 0, 0

        h, s, v = (0.4, 0.5, 0.3)

        i = 1
        while index % (2 ** i) == 0:
            h += 0.1
            i += 1

        i = 1
        while index % (3 ** i) == 0:
            v += 0.3
            i += 1

        i = 1
        while index % (5 ** i) == 0:
            s += 0.2
            i += 1

        if index % 7 == 0:
            v = 1

        if index % 11 == 0:
            v = 0

        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)

    def get_color(self, index):
        while len(self.colors) <= index:
            print(len(self.colors))
            self.colors.append(BoardOverlay.create_color(len(self.colors)))

        return self.colors[index]

    def update_colors(self, board: Board):
        for x in range(self.width):
            for y in range(self.height):
                self.data[y][x].color = self.get_color(board.get_from_coordinate(Vec2(x, y)))

    def draw(self):
        for x in range(self.width):
            for y in range(self.height):
                self.data[y][x].draw()


def is_in_move(pos: Vec2, moves):
    return any(pos == move for move in moves)
