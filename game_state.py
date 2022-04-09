from urllib.request import AbstractBasicAuthHandler
import pydealer
from player import Player
import random
from util import *


class GameState:
    players = []
    playerHand = None
    aiHand = None
    cardsOnTable = None
    discardPile = None
    cutCard = None
    crib = None
    deck = None
    dealer = None

    def __init__(self, p1: Player, ai: Player):  # Used to start a game
        self.players = [p1, ai]
        if random.randint(0, 1):  # Reverses the starting crib 50% of the time
            p1.setmyCrib(True)
        else:
            ai.setmyCrib(True)
        self.dealer = ai.myCrib()  # index of the player with the crib in the players list
        for p in self.players:
            p.setGameState(self)

    """ #TIL Python does not support multiple constructors
    def __init__(self, deck, player, ai, table, discard, cutCard, crib):  # Used by ai when looking at possible futures
        self.deck = deck
        self.playerHand = player
        self.aiHand = ai
        self.cardsOnTable = table
        self.discardPile = discard
        self.cutCard = cutCard
        self.crib = crib
    """

    # returns a new state with this state as the base
    def playCard(self, card, isAiPlayer):
        newPlayerHand = self.copyStack("player")
        newAiHand = self.copyStack("ai")
        newTable = self.copyStack("table")

        # Remove the card from the correct player's hand
        if isAiPlayer:
            newAiHand.get(card)
        else:
            newPlayerHand.get(card)

        # Add the new card to the top of the table pile
        newTable.add(card)

        return GameState(self.deck, newPlayerHand, newAiHand, newTable, self.discardPile, self.cutCard, self.crib)

    # type: "player", "ai", "table"
    def copyStack(self, type):
        stackAsList = None

        if type == "player":
            stackAsList = self.playerHand[:]
        if type == "ai":
            stackAsList = self.aiHand[:]
        if type == "table":
            stackAsList = self.cardsOnTable[:]

        copiedHand = pydealer.Stack()
        for card in stackAsList:
            copiedHand.add(card)
        return copiedHand

    # Score the state of this state for the AI
    def scoreForAI(self):
        if self.cutCard is not None:
            aiHandCopy = self.copyStack("ai")
            aiHandCopy.add(self.cutCard)
            return calculateScore(aiHandCopy)
        else:
            newStack = pydealer.Stack(self.copyStack("ai"))
            return calculateScore(self.copyStack("ai"))

    def cutTheDeck(self, deck):
        return deck.deal(1)[0]

    def layCards(self):
        p1 = self.players[0]
        p2 = self.players[1]  # We can change this to be called ai if you want but I was lazy

        # current is the index of the current player in the players and playerGo lists
        # this way, the same code doesn't have to be explicitly written for each player
        current = not p1.myCrib()  # Needs to start reversed
        playerGo = [False, False]
        sumOnTable = 0
        self.cardsOnTable = pydealer.Stack()
        while p1.cardsRemaining() > 0 or p2.cardsRemaining() > 0:
            current = not current
            newSumOnTable = 0

            if self.players[current].cardsRemaining() == 0:
                playerGo[current] = True

            if not playerGo[current]:
                newSumOnTable = self.players[current].promptToPlay(self.cardsOnTable, sumOnTable)
                if newSumOnTable == sumOnTable:
                    print("Player " + str(current + 1) + " says go")
                    if playerGo[not current]:
                        self.players[current].scorePoints(1)
                    playerGo[current] = True
                elif self.players[current].checkVictory():
                    print("Player " + str(current + 1) + " has won the game")
                    return True

            sumOnTable = newSumOnTable

            if sumOnTable == 31:
                print("31!")
                self.players[current].scorePoints(2)

                playerGo = [True, True]

            if all(playerGo):  # Resets
                sumOnTable = 0
                self.cardsOnTable.empty()
                playerGo = [False, False]

        print("Last card played")
        self.players[current].scorePoints(1)

        return False  # returns false if no one has claimed victory

    #Updates variables based on the players
    def update(self):
        self.playerHand = self.players[0].getHand()
        self.aiHand = self.players[1].getHand()


    def gameFlow(self):
        p1 = self.players[0]
        ai = self.players[1]
        while True:
            self.deck = pydealer.Deck()
            self.deck.shuffle()
            p1.deal6(self.deck)
            ai.deal6(self.deck)
            self.aiHand = ai.getHand()
            self.playerHand = p1.getHand()
            self.printScore()

            self.crib = pydealer.Stack()
            self.crib = p1.discardPrompt(self.crib)
            self.crib = ai.discardPrompt(self.crib)
            self.crib.sort(RANKS)
            self.update()
            self.cutCard = self.cutTheDeck(self.deck)
            self.printCutCard()
            if self.cutCard.value == "Jack":
                self.players[self.dealer].scorePoints(2)

            if self.layCards():
                break  # Victory Achieved

            self.players[not self.dealer].scoreHand(self.cutCard)
            self.players[self.dealer].scoreHand(self.cutCard)
            self.players[self.dealer].scoreHand(self.cutCard, self.crib)
            self.players[not self.dealer].setmyCrib(True)
            self.players[self.dealer].setmyCrib(False)
            self.dealer = not self.dealer

    # Gamestate Print functions below here
    def printScore(self):
        print("==CURRENT SCORE==")
        print(self.players[0].getName() + ": " + str(self.players[0].getScore()))
        print(self.players[1].getName() + ": " + str(self.players[1].getScore()))
        print("=================")
        print()

    def printCutCard(self):
        print("===")
        print("The cut card is: " + str(self.cutCard))
        print("===")

