

from typing import List, Optional, Dict

import websocket
import json

import math


class Vec2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def sq_len(self):
        return self.x * self.x + self.y * self.y

    def __len__(self):
        return math.sqrt(self.sq_len())

    def __str__(self):
        return str(self.x) + "," + str(self.y)

    def step_distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)


class Board:
    def __init__(self, a: List):
        self.width = int(math.sqrt(len(a)))
        self.height = self.width

        self.data = []

        for i in range(self.height):
            self.data.append([])
            for j in range(self.width):
                self.data[i].append(a[i * self.width + j])

        self.can_move = self.has_valid_moves()

    def get_from_index(self, index: int):
        return self.data[index // self.width][index % self.width]

    def index_from_coordinate(self, c: Vec2):
        return c.x + self.width * c.y

    def get_from_coordinate(self, c: Vec2):
        return self.data[c.y][c.x]

    def in_bounds(self, c: Vec2):
        return 0 <= c.x < self.width and 0 <= c.y < self.height

    def __str__(self):
        return '\n'.join([str(self.data[i]) for i in range(self.height)])

    def build_move(self, points: List[Vec2]) -> List[int]:
        move = []
        for point in points:
            move.append(self.index_from_coordinate(point))
        return move

    def has_valid_moves(self) -> bool:
        for i in range(self.height - 1):
            for j in range(self.width - 1):
                if self.data[i][j] == self.data[i][j+1] or self.data[i][j] == self.data[i+1][j]:
                    return True
        for i in range(self.height - 1):
            if self.data[i][self.width-1] == self.data[i+1][self.width-1]:
                return True
        for j in range(self.width - 1):
            if self.data[self.height-1][j] == self.data[self.height-1][j+1]:
                return True
        return False

    def move_is_valid(self, move: List[Vec2]) -> bool:

        # Must have at least two points
        if len(move) <= 1:
            return False

        # Make sure all moves are on board and all points are same number
        number = self.get_from_coordinate(move[0])
        for pos in move:
            if not self.in_bounds(pos) or self.get_from_coordinate(pos) != number:
                return False

        for i in range(len(move) - 1):
            p1 = move[i]
            p2 = move[i+1]

            # Make sure all moves are adjacent.
            if p1.x != p2.x and p1.y != p2.y:
                return False

        return True


class Client:

    def __init__(self, user_name, timeout=True):
        self.connection = websocket.create_connection("wss://server.lucasholten.com:21212")

        if timeout:
            self.connection.timeout = 0.5

        self.connection.send(json.dumps(user_name))

        self.board: Optional[Board] = None

        self.is_waiting_for_response = True

    def update(self):

        if self.is_waiting_for_response:
            try:
                packet = self.connection.recv()

                self.board = Board(json.loads(packet))

                self.is_waiting_for_response = False

            except websocket.WebSocketTimeoutException:
                pass

    def send(self, data):
        if not self.is_waiting_for_response:
            self.connection.send(json.dumps(data))
            self.is_waiting_for_response = True

    def destroy(self):
        self.connection.close()


class Score:
    def __init__(self, score: Dict):
        self.name = score.get("name")
        self.score = score.get("score")


class HighscoresList:
    def __init__(self, highscores):
        self.scores: List[Score] = [Score(s) for s in highscores]


class Highscores:
    def __init__(self):
        self.connection = websocket.create_connection("wss://server.lucasholten.com:12121")

        self.connection.timeout = 0.01

        self.highscores: Optional[HighscoresList] = None

        self.is_waiting_for_response = True

    def format_highscores(self) -> str:
        scores = self.highscores.scores
        return '\n'.join([s.name + ": " + str(s.score) for s in scores])

    def update(self):

        if self.is_waiting_for_response:
            try:
                packet = self.connection.recv()

                self.highscores = HighscoresList(json.loads(packet))

                self.is_waiting_for_response = False

                self.connection.close()

            except websocket.WebSocketTimeoutException:
                pass










