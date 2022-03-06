import pydealer
import random

RANKS = {'values': {'Ace': 1, 'King': 13, 'Queen': 12, 'Jack': 11, '10': 10, '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2, 'Joker': 0}}

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


    def promptToPlay(self, cardsOnTable, sumOnTable):
        print("Cards in play: ")
        print(cardsOnTable)
        print("Sum to: " + str(sumOnTable))
        print()
        print(self.getName() + "'s hand: ")
        print(self.handCopy)
        print()

        while True:
            selection = input("Select a card to play: (or 'go' if cannot play)") # TODO implement a checking system to see if you must 'go'
            if selection == 'go':
                return sumOnTable # returns the initial sum if no card can be played
            
            card = self.handCopy.get(selection)
            
            if card == []:
                print("Error try again!")
                continue
            
            card = card[0] # get() returns a list and there should only ever be one card in it
            cardValue = convertCardToInt(card.value)
            if cardValue+sumOnTable > 31:
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
        if checkForPair(cardsOnTable[cardsOnTable.size-1], cardsOnTable[cardsOnTable.size-2]):
            if cardsOnTable.size > 2 and checkForPair(cardsOnTable[cardsOnTable.size-1], cardsOnTable[cardsOnTable.size-3]):
                if cardsOnTable.size > 3 and checkForPair(cardsOnTable[cardsOnTable.size-1], cardsOnTable[cardsOnTable.size-4]):
                    print("4 of a kind for 12")
                    self.scorePoints(12)
                else:
                    print("3 of a kind for 6")
                    self.scorePoints(6)
            else:
                print("Pair for 2")
                self.scorePoints(2)
            return # Points for runs aren't possible if there is a pair, so there's no point in continuing through the function if you get here

        if cardsOnTable.size < 3:
            return

        # Points for runs (Not possible if there is a pair)
        top = pydealer.Stack()
        top.insert_list([cardsOnTable[cardsOnTable.size-1], cardsOnTable[cardsOnTable.size-2], cardsOnTable[cardsOnTable.size-3]],0)
        top.sort(RANKS)
        runPoints = 0
        if cardsOnTable.size == 3:
            if checkForRun(top):
                runPoints = 3
        else:
            for i in range(cardsOnTable.size-3):
                if checkForRun(top):
                    if runPoints == 0:
                        runPoints = 3
                    else:
                        runPoints += 1
                    top.add(cardsOnTable[cardsOnTable.size-(4+i)])
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
        if scoringHand[0].suit == scoringHand[1].suit and scoringHand[0].suit == scoringHand[2].suit and scoringHand[0].suit == scoringHand[3].suit:
            if scoringHand[0].suit == scoringHand[4].suit:
                totalHandScore += 5
                print("Flush including the cut for " + str(totalHandScore))
            else:
                totalHandScore += 4
                print("Flush excluding the cut for " + str(totalHandScore))

        
        scoringHand.sort(RANKS) # For ease of calculations

        # 15s
        handValues = [convertCardToInt(x.value) for x in scoringHand]
        fifteenspoints = 0
        fifteenspoints += find15sTwoCard(handValues) # i.e. scoringHand.size choose 2
        fifteenspoints += find15sThreeCard(handValues) # i.e. scoringHand.size choose 3
        fifteenspoints += find15sFourCard(handValues) # i.e. scoringHand.size choose 4
        fifteenspoints += find15sFiveCard(handValues) # i.e. scoringHand.size choose 5
        if fifteenspoints:
            print(str(fifteenspoints) + " from 15s")
            totalHandScore += fifteenspoints

        # 4 of a kinds, 3 of a kinds, and pairs
        pairValues = [] # Stores the card values of the pairs (ie hand = [3,3,4,4,7] -> pairValues = ['3','4']
        threeValue = None # Same as above but there can only be one 3 of a kind
        fourValue = None # Same as above
        for i in range(scoringHand.size):
            for j in range(i+1, scoringHand.size):
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
        for i in range(scoringHand.size-2): # Runs of 3
            for j in range(i+1, scoringHand.size-1):
                for k in range(j+1, scoringHand.size):
                    stack = pydealer.Stack()
                    stack.insert_list([scoringHand[i], scoringHand[j], scoringHand[k]])
                    if checkForRun(stack):
                        runs.append([i,j,k])
                    
        for run in runs: # Runs of more than 3
            for l in range(scoringHand.size):
                if l in run:
                    continue
                else:
                    stack = pydealer.Stack()
                    stack.insert_list([scoringHand[run[0]], scoringHand[run[1]], scoringHand[run[2]], scoringHand[l]])
                    if checkForRun(stack):
                        run.append(l)

        #Nobs (The right jack)
        for card in scoringHand:
            if card != cutCard and checkNobs(cutCard, card):
                totalHandScore += 1
                print("The right Jack (nobs) is" + str(totalHandScore))

        self.scorePoints(totalHandScore) # Score points at the end

def checkNobs(cut, card):
    return card.value == 'Jack' and cut.suit == card.suit

def checkForPair(card1, card2): # Helps to clean everything up
    return card1.value == card2.value

def checkForRun(stack): # checks if all the cards in the stack are sequent if not all returns False
    stack.sort(RANKS)
    for i in range(stack.size-1):
        if getNextValue(stack[i]) != stack[i+1].value:
            return False
    return True

def find15sTwoCard(values):
    points = 0
    for i in range(len(values)):
        for j in range(i+1, len(values)):
            if values[i] + values[j] == 15:
                points += 2
    return points


def find15sThreeCard(values):
    points = 0
    for i in range(len(values)):
        for j in range(i+1, len(values)):
            for k in range(j+1, len(values)):
                if values[i] + values[j] + values[k] == 15:
                    points += 2
    return points

def find15sFourCard(values):
    points = 0
    for i in range(len(values)):
        for j in range(i+1, len(values)):
            for k in range(j+1, len(values)):
                for l in range(k+1, len(values)):
                    if values[i] + values[j] + values[k] + values[l] == 15:
                        points += 2
    return points

def find15sFiveCard(values):
    if values[0] + values[1] + values[2] + values[3] + values[4] == 15:
        return 2
    else:
        return 0


def getNextValue(card):
    if card.value == '10':
        return 'Jack'
    try:
        return str(int(card.value)+1)
    except ValueError:
        if card.value == 'Ace':
            return 2
        elif card.value == 'Jack':
            return 'Queen'
        elif card.value == 'Queen':
            return 'King'
        else:
            return 'Null'

def convertCardToInt(value):
    if value == 'Ace':
        return 1
    try:
        return int(value)
    except ValueError:
        return 10

def layCards(p1, p2):
    # current is the index of the current player in the players and playerGo lists
    # this way, the same code doesn't have to be explicitly written for each player
    current = not p1.myCrib() # Needs to start reversed
    players = [p1, p2]
    playerGo = [False, False]
    sumOnTable = 0
    cardsOnTable = pydealer.Stack()
    while p1.cardsRemaining() > 0 or p2.cardsRemaining() > 0 :
        current = not current
        newSumOnTable = 0

        if players[current].cardsRemaining() == 0:
            playerGo[current] = True

        if not playerGo[current]:
            newSumOnTable = players[current].promptToPlay(cardsOnTable, sumOnTable)
            if newSumOnTable == sumOnTable:
                print("Player " + str(current+1) + " says go")
                if playerGo[not current]:
                    players[current].scorePoints(1)
                playerGo[current] = True
            elif players[current].checkVictory():
                print("Player " + str(current+1) + " has won the game")
                return True
        
        sumOnTable = newSumOnTable

        if sumOnTable == 31:
            print("31!")
            players[current].scorePoints(2)
            
            playerGo = [True, True]

        if all(playerGo): # Resets
            sumOnTable = 0
            cardsOnTable.empty()
            playerGo = [False, False]

    print("Last card played")
    players[current].scorePoints(1)

    return False #returns false if no one has claimed victory

def cutTheDeck(deck):
    return deck.deal(1)[0]

def main():
    p1 = Player("Player 1")
    p2 = Player("Player 2")
    players = [p1, p2]
    
    if random.randint(0,1): # Reverses the starting crib 50% of the time
        p1.setmyCrib(True)
    else:
        p2.setmyCrib(True)
    dealer = p2.myCrib() # index of the player with the crib in the players list


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
        if cut.value == 'Jack':
            players[dealer].scorePoints(2)

        if layCards(p1, p2): 
            break # Victory Achieved

        players[not dealer].scoreHand(cut)
        players[dealer].scoreHand(cut)
        players[dealer].scoreHand(cut, crib)
        players[not dealer].setmyCrib(True)
        players[dealer].setmyCrib(False)
        dealer = not dealer
        print()

main()