import pydealer
import random


class Player:
    __score = 0
    __myCrib = False
    hand = None
    handCopy = None
    def __init__(self, myCrib):
        self.__myCrib = myCrib

    def myCrib(self):
        return __myCrib

    def setmyCrib(self, isMyCrib):
        self.__myCrib = isMyCrib

    def getScore(self):
        return self.__score

    def scorePoints(self, points):
        print("You scored: " + str(points) + " points")
        self.__score += points
        print("You now have a score of " + str(__score))

    def getHand(self):
        return self.hand

    def cardsRemaining(self):
        return self.handCopy.size

    def deal6(self, deck):
        self.hand = deck.deal(6)
        self.hand.sort()

    def discardPrompt(self, crib):
        print(self.hand)
        if self.myCrib():
                print("It is your crib")
            else:
                print("It is not your crib")
        while self.hand.size > 4:
            card = input("Choose a card to discard: ")
            try:
                crib.add(self.hand.get(card))
                print("Successfully removed " + card)
            except:
                print("Error")
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
        print("Your hand: ")
        print(self.handCopy)

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
                cardsOnTable.add(card)
                self.pegPoints(cardsOnTable, sumOnTable)
                return sumOnTable+cardValue
    
    def pegPoints(self, cardsOnTable, sumOnTable):
        if cardsOnTable.size == 1:
            return
        
        # Points for 15s and 31s
        if sumOnTable == 15 or sumOnTable == 31:
            self.scorePoints(2)

        # Points for pairs, 3 of a kinds, and 4 of a kinds
        if cardsOnTable[cardsOnTable.size-1] == cardsOnTable[cardsOnTable.size-2]:
            if cardsOnTable.size > 2 and cardsOnTable[cardsOnTable.size-1] == cardsOnTable[cardsOnTable.size-3]:
                if cardsOnTable.size > 3 and cardsOnTable[cardsOnTable.size-1] == cardsOnTable[cardsOnTable.size-4]:
                    self.scorePoints(12)
                    return
                else:
                    self.scorePoints(6)
                    return
            else:
                self.scorePoints(2)
                return
        
        # Points for runs (Not possible if there is a pair)
        top = pydealer.Stack()
        top.insert_list([cardsOnTable[cardsOnTable.size-1], cardsOnTable[cardsOnTable.size-2], cardsOnTable[cardsOnTable.size-3]],0)
        runPoints = 0
        for i in range(4,cardsOnTable.size+1):
            if checkForRun(top):
                if runPoints == 0:
                    runPoints = 3
                else:
                    runPoints += 1
                top.add(cardsOnTable[cardsOnTable.size-i])
            else:
                break
        
        if runPoints > 0:
            self.scorePoints(runPoints)

    def scoreHand(self, cutCard, scoringHand=self.hand):
        scoringHand.add(cutCard)
        scoringHand.sort()
        totalHandScore = 0
        # 15s
        for i in range(scoringHand.size): # Size should always be 5
            for j in range(i+1,scoringHand.size):
                if convertCardToInt(scoringHand[i].value)+convertCardToInt(scoringHand[j].value) == 15:
                    totalHandScore += 2
                    print("Fifteen " + str(totalHandScore) + "(" + scoringHand[i] + " + " + scoringHand[j] + ")")



        # 4 of a kinds, 3 of a kinds, and pairs
        pairValues = []
        threeValue = None
        fourValue = None
        for i in range(scoringHand.size):
            for j in range(scoringHand.size):
                if scoringHand[i].value != scoringHand[j].value:
                    break
                elif scoringHand[i].value == threeValue:
                    threeValue = None
                    fourValue = scoringHand[i].value
                    break
                elif scoringHand[i].value in pairs:
                    pairs.remove(scoringHand[i].value)
                    threeValue = scoringHand.value
                else:
                    pairs.append(scoringHand[i].value)

        for val in pairValues:
            totalHandScore += 2
            print("A pair of " + val + "s is " + str(totalHandScore))
        
        if threeValue is not None:
            totalHandScore += 6
            print("3 " + val + "s is " + str(totalHandScore))
        
        if fourValue is not None:
            totalHandScore += 12
            print("4 " + val + "s is " + str(totalHandScore))

        
                

        # Runs
        stack = pydealer.Stack()
        stack.insert_list([scoringHand[0], scoringHand[1], scoringHand[2]])
        for i in range(4, scoringHand.size)
            if checkForRun(stack):
                stack.add(scoringHand[3])
                if checkForRun(stack):
                    totalHandScore += 4
                    print("A run of 4 is " + str(totalHandScore))
                    
                else:
                    stack.get(str(scoringHand[3]))
                    totalHandScore += 3
                    print("A run of 3 is " + str(totalHandScore))
        
            stack.get(str(scoringHand[i-4]))
            stack.add(scoringHand[i])




        
            




def checkForRun(stack): # checks if all the cards in the stack are sequent if not all returns False
    stack.sort()
    for i in range(stack.size-1):
        if getNextValue(stack[i]) != stack[i+1].value:
            return False
    return True

    
def getNextValue(card):
    if card.value == '10':
        return 'Jack'
    try:
        return int(card.value)+1
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
    currentTurnP1 = not p1.myCrib()
    sumOnTable = 0
    cardsOnTable = pydealer.Stack()
    player1Go = False
    player2Go = False
    while p1.cardsRemaining() > 0 or p2.cardsRemaining() > 0 :
        newSumOnTable = 0
        if currentTurnP1 not player1Go:
            newSumOnTable = p1.promptToPlay(cardsOnTable, sumOnTable)
            if newSumOnTable == sumOnTable:
                print("Player 1 says go")
                if player2Go:
                    p1.scorePoints(1)
                player1Go = True
            elif p1.checkVictory():
                print("Player 1 has won the game")
                return True

            if not p1.cardsRemaining() > 0:
                if player2Go and newSumOnTable != 31:
                    p1.scorePoints(1)
                
                player1Go = True
            
        elif not player2Go:
            newSumOnTable = p2.promptToPlay(cardsOnTable, sumOnTable)
            if newSumOnTable == sumOnTable:
                print("Player 2 says go")
                if player1Go:
                    p2.scorePoints(1)
                player2Go = True
            elif p2.checkVictory():
                print("Player 2 has won the game")
                return True

            if not p2.cardsRemaining() > 0:
                if player1Go and newSumOnTable != 31:
                    p2.scorePoints(1)
                player2Go = True
        
        
        if newSumOnTable == 31:
            print("31!")
            if currentTurnP1:
                p1.scorePoints(2)
            else:
                p2.scorePoints(2)
            
            player1Go = True
            player2Go = True

        if player1Go and player2Go: # Resets
            sumOnTable = 0
            cardsOnTable.empty()
            player1Go = False
            player2Go = False

    return False #returns false if no one has claimed victory




def cutTheDeck(deck):
    return deck.deal(1)[0]



def main():
    p1 = Player(False)
    p2 = Player(True) 
    
    if random.randint(0,1): # Reverses the starting crib 50% of the time
        p1.setmyCrib(True)
        p2.setmyCrib(False)
    

    while True:
        deck = pydealer.Deck()
        deck.shuffle()
        p1.deal6(deck)
        p2.deal6(deck)
        
        crib = pydealer.Stack()
        crib = p1.discardPrompt(crib)
        crib = p2.discardPrompt(crib)
        crib.sort()
        cut = cutTheDeck(deck)
        if cut.value == 'Jack':
            if p1.myCrib():
                p1.scorePoints(2)
            else:
                p2.scorePoints(2)

        if layCards(p1, p2):
            break

        if not p1.myCrib():
            p1.scoreHand(cut)
            p2.scoreHand(cut)
            p2.scoreHand(cut, crib)
        else:
            p2.scoreHand(cut)
            p1.scoreHand(cut)
            p1.scoreHand(cut, crib)



    
