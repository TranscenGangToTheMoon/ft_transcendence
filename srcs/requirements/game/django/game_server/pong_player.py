from typing import List


class Player:
    socket_id = 0
    def __init__(self, player_id):
        self.id = player_id


class Team:
    def __init__(self, id: int, players: List[Player]) -> None:
        self.id = id
        self.players = players
