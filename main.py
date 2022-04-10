from player import Player
from ai_player import PlayerAI
from game_state import GameState


def main():
    p1 = Player("Player 1")
    ai = PlayerAI("AI")
    gs = GameState(None, p1, ai)
    gs.gameFlow()


if __name__ == "__main__":
    main()
