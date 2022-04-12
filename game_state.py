import copy
from urllib.request import AbstractBasicAuthHandler
import pydealer
import random
from player import Player
from util import *


class GameState:
    players = []
    playerHand = None
    playerHandCopy = None
    playerScore = 0
    aiHand = None
    aiScore = 0
    cardsOnTable = None
    discardPile = None
    cutCard = None
    crib = None
    deck = None
    dealer = None


    def __init__(self, p1: Player, ai: Player):
        self.players = [p1, ai]
        if random.randint(0, 1):  # Reverses the starting crib 50% of the time
            p1.setmyCrib(True)
        else:
            ai.setmyCrib(True)
        self.dealer = ai.myCrib() # index of the player with the crib in the players list
        for p in self.players:
            p.setGameState(self)

    # Set player's hand (used only for minimax, use this on a copy of the object)
    def setPlayerHand(self, hand):
        self.playerHand = hand
        self.playerHandCopy = copy.deepcopy(hand)
    
    def setAIHand(self, playable):
        newHand = pydealer.Stack()
        for card in playable:
            newHand.add(card)
        self.aiHand = newHand

    # Creates a copy of its self modified with the attributes given; Used by ai to predict possible futures
    def createModCopy(
                      self,
                      newPlayers=None,
                      newDeck=None,
                      newPlayerHandCopy=None,
                      newAiHandCopy=None,
                      newCardsOnTable=None,
                      newDiscardPile=None,
                      newCutCard=None,
                      newCrib=None,
                      newDealer=None,
                      newPlayerScore=None,
                      newAiScore=None):

        stateCopy = copy.deepcopy(self)
        stateCopy.players = newPlayers if newPlayers is not None else stateCopy.players
        stateCopy.deck = newDeck if newDeck is not None else stateCopy.deck
        stateCopy.playerHandCopy = newPlayerHandCopy if newPlayerHandCopy is not None else stateCopy.playerHand
        stateCopy.aiHandCopy = newAiHandCopy if newAiHandCopy is not None else stateCopy.aiHand
        stateCopy.cardsOnTable = newCardsOnTable if newCardsOnTable is not None else stateCopy.cardsOnTable
        stateCopy.discardPile = newDiscardPile if newDiscardPile is not None else stateCopy.discardPile
        stateCopy.cutCard = newCutCard if newCutCard is not None else stateCopy.cutCard
        stateCopy.crib = newCrib if newCrib is not None else stateCopy.crib
        stateCopy.dealer = newDealer if newDealer is not None else stateCopy.dealer
        stateCopy.playerScore = newPlayerScore if newPlayerScore is not None else stateCopy.playerScore
        stateCopy.aiScore = newAiScore if newAiScore is not None else stateCopy.aiScore
        return stateCopy

    # returns a new state with this state as the base
    def playCard(self, card, isAiPlayer):
        newPlayerHandCopy = self.copyStack("player", copy=True)
        newAiHandCopy = self.copyStack("ai", copy=True)
        newTable = self.copyStack("table")

        # Remove the card from the correct player's hand
        if isAiPlayer:
            newAiHandCopy.get(newAiHandCopy.find(str(card))[0])
        else:
            newPlayerHandCopy.get(newPlayerHandCopy.find(str(card))[0])

        # Add the new card to the top of the table pile
        newTable.add(card)
        points = self.aiScore + calculatePegPoints(newTable, calculateSumOnTable(newTable), player=None, prints=False)


        return self.createModCopy(
            newPlayerHandCopy=newPlayerHandCopy,
            newAiHandCopy=newAiHandCopy,
            newCardsOnTable=newTable,
            newPlayerScore=self.playerScore+points if not isAiPlayer else None,
            newAiScore=self.aiScore+points if isAiPlayer else None
        )

    # type: "player", "ai", "table"
    def copyStack(self, type, copy=False):
        stackAsList = self.StackToList(type, copy)
        copiedHand = pydealer.Stack()
        for card in stackAsList:
            copiedHand.add(card)
        return copiedHand
    
    def StackToList(self, type, copy=False):
        if type == "player":
            if not copy:
                return self.playerHand
            else:
                return self.playerHandCopy
        if type == "ai":
            if not copy:
                return self.players[1].getHand()[:]
            else:
                return self.players[1].getHandCopy()[:]
        if type == "table":
            return self.cardsOnTable[:]
        else:
            return

    # Score the state of this state for the AI
    def score(self, scoringAi=True):
        if scoringAi:
            return self.aiScore
        else:
            return self.playerScore


    def cutTheDeck(self, deck):
        return deck.deal(1)[0]

    def layCards(self):
        p1 = self.players[0]
        p2 = self.players[1]  # We can change this to be called ai if you want but I was lazy

        # current is the index of the current player in the players and playerGo lists
        # this way, the same code doesn't have to be explicitly written for each player
        current = not p1.myCrib() # Needs to start reversed
        lastPlayed = None
        playerGo = [False, False]
        sumOnTable = 0
        self.cardsOnTable = pydealer.Stack()
        while p1.cardsRemaining() > 0 or p2.cardsRemaining() > 0:

            current = not current

            if self.players[current].cardsRemaining() == 0:
                playerGo[current] = True
                current = not current


            newSumOnTable = 0

            #DEBUG
            #print("DEBUG")
            #self.printHand(copy=True)
            #self.printScore()
            if not playerGo[current]:
                newSumOnTable = self.players[current].promptToPlay(self.cardsOnTable, sumOnTable)
                if newSumOnTable == sumOnTable:
                    print(self.players[current].getName() + " says go")
                    playerGo[current] = True
                    if all(playerGo):
                        self.players[lastPlayed].scorePoints(1)
                else:
                    lastPlayed = current

                if self.players[current].cardsRemaining() == 0:
                    print(self.players[current].getName() + " says go")
                    playerGo[current] = True
                    if all(playerGo):
                        self.players[lastPlayed].scorePoints(1)

                if self.players[current].checkVictory():
                    print(self.players[current].getName() + " has won the game")
                    return True

            sumOnTable = newSumOnTable

            if sumOnTable == 31:
                print("31!")
                self.players[lastPlayed].scorePoints(2)

                playerGo = [True, True]

            if all(playerGo):  # Resets
                sumOnTable = 0
                self.cardsOnTable.empty()
                playerGo = [False, False]

            if self.players[current].cardsRemaining() == 0:
                playerGo[current] = True

        print("Last card played")

        return False  # returns false if no one has claimed victory

    # Updates variables based on the players
    def update(self):
        self.playerHand = self.players[0].getHand()
        self.aiHand = self.players[1].getHand()
        self.playerScore = self.players[0].getScore()
        self.aiScore = self.players[1].getScore()

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
            print("Please wait while AI decides what to discard...")
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

    def printHand(self, player=None, copy=False):
        for i in range(len(self.players)):
            if i == player or player is None:
                print("====" + self.players[i].getName() + "'s Hand ====")
                print(self.players[i].getHand() if not copy else self.players[i].getHandCopy())
                print("=====================")

