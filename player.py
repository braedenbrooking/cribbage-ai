import pydealer
from util import *


class Player:
    __score = 0
    __myCrib = False
    __name = ""
    hand = None
    handCopy = None

    def __init__(self, name):
        self.__name = name

    def getName(self):
        return self.__name

    def myCrib(self):
        return self.__myCrib

    def setmyCrib(self, isMyCrib):
        self.__myCrib = isMyCrib

    def getScore(self):
        return self.__score

    def scorePoints(self, points):
        print(self.getName() + " scored: " + str(points) + " points")
        self.__score += points
        print(self.getName() + " now has a score of " + str(self.__score))

    def getHand(self):
        return self.hand

    def cardsRemaining(self):
        return self.handCopy.size

    def deal6(self, deck):
        self.hand = deck.deal(6)
        self.hand.sort(RANKS)

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
        handAsList = self.hand[:]
        self.handCopy = pydealer.Stack()
        for card in handAsList:
            self.handCopy.add(card)

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
                self.pegPoints(cardsOnTable, sumOnTable)
                return sumOnTable

    def pegPoints(self, cardsOnTable, sumOnTable):
        if cardsOnTable.size == 1:
            return

        # Points for 15s (31s counted elsewhere)
        if sumOnTable == 15:
            print("15 for 2")
            self.scorePoints(2)

        # Points for pairs, 3 of a kinds, and 4 of a kinds
        if checkForPair(
            cardsOnTable[cardsOnTable.size - 1], cardsOnTable[cardsOnTable.size - 2]
        ):
            if cardsOnTable.size > 2 and checkForPair(
                cardsOnTable[cardsOnTable.size - 1], cardsOnTable[cardsOnTable.size - 3]
            ):
                if cardsOnTable.size > 3 and checkForPair(
                    cardsOnTable[cardsOnTable.size - 1],
                    cardsOnTable[cardsOnTable.size - 4],
                ):
                    print("4 of a kind for 12")
                    self.scorePoints(12)
                else:
                    print("3 of a kind for 6")
                    self.scorePoints(6)
            else:
                print("Pair for 2")
                self.scorePoints(2)
            return  # Points for runs aren't possible if there is a pair, so there's no point in continuing through the function if you get here

        if cardsOnTable.size < 3:
            return

        # Points for runs (Not possible if there is a pair)
        top = pydealer.Stack()
        top.insert_list(
            [
                cardsOnTable[cardsOnTable.size - 1],
                cardsOnTable[cardsOnTable.size - 2],
                cardsOnTable[cardsOnTable.size - 3],
            ],
            0,
        )
        top.sort(RANKS)
        runPoints = 0
        if cardsOnTable.size == 3:
            if checkForRun(top):
                runPoints = 3
        else:
            for i in range(cardsOnTable.size - 3):
                if checkForRun(top):
                    if runPoints == 0:
                        runPoints = 3
                    else:
                        runPoints += 1
                    top.add(cardsOnTable[cardsOnTable.size - (4 + i)])
                    top.sort(RANKS)
                else:
                    break

        if runPoints > 0:
            print(str(runPoints) + " for a run")
            self.scorePoints(runPoints)

    def scoreHand(self, cutCard, scoringHand=None):
        print()
        if scoringHand is None:
            scoringHand = self.hand

        print("Scoring hand: ")
        print(scoringHand)
        print("With Cut Card: ")
        print(cutCard)
        print()

        scoringHand.add(cutCard)
        totalHandScore = 0

        # Flush
        if (
            scoringHand[0].suit == scoringHand[1].suit
            and scoringHand[0].suit == scoringHand[2].suit
            and scoringHand[0].suit == scoringHand[3].suit
        ):
            if scoringHand[0].suit == scoringHand[4].suit:
                totalHandScore += 5
                print("Flush including the cut for " + str(totalHandScore))
            else:
                totalHandScore += 4
                print("Flush excluding the cut for " + str(totalHandScore))

        scoringHand.sort(RANKS)  # For ease of calculations

        # 15s
        handValues = [convertCardToInt(x.value) for x in scoringHand]
        fifteenspoints = 0
        fifteenspoints += find15sTwoCard(handValues)  # i.e. scoringHand.size choose 2
        fifteenspoints += find15sThreeCard(handValues)  # i.e. scoringHand.size choose 3
        fifteenspoints += find15sFourCard(handValues)  # i.e. scoringHand.size choose 4
        fifteenspoints += find15sFiveCard(handValues)  # i.e. scoringHand.size choose 5
        if fifteenspoints:
            print(str(fifteenspoints) + " from 15s")
            totalHandScore += fifteenspoints

        # 4 of a kinds, 3 of a kinds, and pairs
        pairValues = (
            []
        )  # Stores the card values of the pairs (ie hand = [3,3,4,4,7] -> pairValues = ['3','4']
        threeValue = None  # Same as above but there can only be one 3 of a kind
        fourValue = None  # Same as above
        for i in range(scoringHand.size):
            for j in range(i + 1, scoringHand.size):
                if not checkForPair(scoringHand[i], scoringHand[j]):
                    continue
                elif scoringHand[i].value == threeValue:
                    threeValue = None
                    fourValue = scoringHand[i].value
                    break
                elif scoringHand[i].value in pairValues:
                    pairValues.remove(scoringHand[i].value)
                    threeValue = scoringHand[i].value
                else:
                    pairValues.append(scoringHand[i].value)

        for val in pairValues:
            totalHandScore += 2
            print("A pair of " + val + "s is " + str(totalHandScore))

        if threeValue is not None:
            totalHandScore += 6
            print("3 " + threeValue + "s is " + str(totalHandScore))

        if fourValue is not None:
            totalHandScore += 12
            print("4 " + fourValue + "s is " + str(totalHandScore))

        # Runs
        runs = []
        for i in range(scoringHand.size - 2):  # Runs of 3
            for j in range(i + 1, scoringHand.size - 1):
                for k in range(j + 1, scoringHand.size):
                    stack = pydealer.Stack()
                    stack.insert_list([scoringHand[i], scoringHand[j], scoringHand[k]])
                    if checkForRun(stack):
                        runs.append([i, j, k])

        for run in runs:  # Runs of more than 3
            for l in range(scoringHand.size):
                if l in run:
                    continue
                else:
                    stack = pydealer.Stack()
                    stack.insert_list(
                        [
                            scoringHand[run[0]],
                            scoringHand[run[1]],
                            scoringHand[run[2]],
                            scoringHand[l],
                        ]
                    )
                    if checkForRun(stack):
                        run.append(l)

        # Nobs (The right jack)
        for card in scoringHand:
            if card != cutCard and checkNobs(cutCard, card):
                totalHandScore += 1
                print("The right Jack (nobs) is" + str(totalHandScore))

        self.scorePoints(totalHandScore)  # Score points at the end
