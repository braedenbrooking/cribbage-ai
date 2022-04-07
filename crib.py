import player
from ai_player import PlayerAI
from game_state import GameState


def main():
    p1 = player.Player("Player 1")
    ai = PlayerAI("AI")
    gs = GameState(p1, ai)
    gs.gameFlow()


if __name__ == "__main__":
    main()
