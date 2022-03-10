import pydealer

import player
import random
from util import *


def layCards(p1, p2):
    # current is the index of the current player in the players and playerGo lists
    # this way, the same code doesn't have to be explicitly written for each player
    current = not p1.myCrib()  # Needs to start reversed
    players = [p1, p2]
    playerGo = [False, False]
    sumOnTable = 0
    cardsOnTable = pydealer.Stack()
    while p1.cardsRemaining() > 0 or p2.cardsRemaining() > 0:
        current = not current
        newSumOnTable = 0

        if players[current].cardsRemaining() == 0:
            playerGo[current] = True

        if not playerGo[current]:
            newSumOnTable = players[current].promptToPlay(cardsOnTable, sumOnTable)
            if newSumOnTable == sumOnTable:
                print("Player " + str(current + 1) + " says go")
                if playerGo[not current]:
                    players[current].scorePoints(1)
                playerGo[current] = True
            elif players[current].checkVictory():
                print("Player " + str(current + 1) + " has won the game")
                return True

        sumOnTable = newSumOnTable

        if sumOnTable == 31:
            print("31!")
            players[current].scorePoints(2)

            playerGo = [True, True]

        if all(playerGo):  # Resets
            sumOnTable = 0
            cardsOnTable.empty()
            playerGo = [False, False]

    print("Last card played")
    players[current].scorePoints(1)

    return False  # returns false if no one has claimed victory


def cutTheDeck(deck):
    return deck.deal(1)[0]


def main():
    p1 = player.Player("Player 1")
    p2 = player.Player("Player 2")
    players = [p1, p2]

    if random.randint(0, 1):  # Reverses the starting crib 50% of the time
        p1.setmyCrib(True)
    else:
        p2.setmyCrib(True)
    dealer = p2.myCrib()  # index of the player with the crib in the players list

    while True:
        deck = pydealer.Deck()
        deck.shuffle()
        p1.deal6(deck)
        p2.deal6(deck)
        print("==CURRENT SCORE==")
        print("Player 1: " + str(p1.getScore()))
        print("Player 2: " + str(p2.getScore()))
        print("=================")
        print()
        crib = pydealer.Stack()
        crib = p1.discardPrompt(crib)
        crib = p2.discardPrompt(crib)
        crib.sort(RANKS)
        print()
        cut = cutTheDeck(deck)
        print("The cut card is: " + str(cut))
        if cut.value == "Jack":
            players[dealer].scorePoints(2)

        if layCards(p1, p2):
            break  # Victory Achieved

        players[not dealer].scoreHand(cut)
        players[dealer].scoreHand(cut)
        players[dealer].scoreHand(cut, crib)
        players[not dealer].setmyCrib(True)
        players[dealer].setmyCrib(False)
        dealer = not dealer
        print()


main()
