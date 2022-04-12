import pydealer
from util import *


class Player:
    __score = 0
    __myCrib = False
    __name = ""
    hand = None
    handCopy = None
    gameStateRef = None

    def __init__(self, name):
        self.__name = name

    def getName(self):
        return self.__name

    def myCrib(self):
        return self.__myCrib

    def setmyCrib(self, isMyCrib):
        self.__myCrib = isMyCrib

    def setGameState(self, gs):
        self.gameStateRef = gs

    def getScore(self):
        return self.__score

    def scorePoints(self, points):
        print(self.getName() + " scored: " + str(points) + " points")
        self.__score += points
        print(self.getName() + " now has a score of " + str(self.__score))

    def getHand(self):
        return self.hand

    def getHandCopy(self):
        return self.handCopy

    def cardsRemaining(self):
        return self.handCopy.size

    def deal6(self, deck):
        self.hand = deck.deal(6)
        self.hand.sort(RANKS)
        self.copyHand()

    def checkVictory(self):
        if self.getScore() >= 120:
            return True
        else:
            return False

    def discardPrompt(self, crib):
        print(self.getName() + "'s hand:")
        print(self.hand)
        print()
        if self.myCrib():
            print("It is your crib")
        else:
            print("It is not your crib")
        while self.hand.size > 4:
            card = input("Choose a card to discard: ")
            startingSize = self.hand.size
            crib.add(self.hand.get(card))
            if startingSize > self.hand.size:
                print("Successfully removed " + card)
            else:
                print("Error")
        self.copyHand()
        return crib

    def copyHand(self):
        self.handCopy = copy.deepcopy(self.hand)

    def mustGo(self, sumOnTable):
        for card in self.handCopy:
            if convertCardToInt(card.value) + sumOnTable <= 31:
                return False
        return True

    def promptToPlay(self, cardsOnTable, sumOnTable):
        print("Cards in play: ")
        print(cardsOnTable)
        print("Sum to: " + str(sumOnTable))
        print()
        print(self.getName() + "'s hand: ")
        print(self.handCopy)
        print()

        while True:
            if self.mustGo(sumOnTable):
                selection = "go"
            else:
                selection = input(
                    "Select a card to play:"
                )

            if selection == "go":
                return sumOnTable  # returns the initial sum if no card can be played

            card = self.handCopy.get(selection)

            if card == []:
                print("Error try again!")
                continue

            card = card[
                0
            ]  # get() returns a list and there should only ever be one card in it
            cardValue = convertCardToInt(card.value)
            if cardValue + sumOnTable > 31:
                print("Cannot Play That Card")
                self.handCopy.add(card)

            else:
                sumOnTable += cardValue
                cardsOnTable.add(card)
                calculatePegPoints(cardsOnTable, sumOnTable, self)
                return sumOnTable

    def scoreHand(self, cutCard=None, scoringHand=None):
        print()
        if scoringHand is None:
            scoringHand = self.hand

        print("Scoring hand: ")
        print(scoringHand)
        print("With Cut Card: ")
        print(cutCard)
        print()

        if cutCard is not None:
            totalHandScore = calculateScore(scoringHand, cutCard, True)
        else:
            totalHandScore = calculateScore(scoringHand, True)

        self.scorePoints(totalHandScore)  # Score points at the end
