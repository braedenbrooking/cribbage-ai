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
        self.__score += points

    def getHand(self):
        return self.hand

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
            selection = input("Select a card to play: (or 'go' if cannot play)")
            if selection == 'go':
                return sumOnTable
            try:
                card = self.handCopy.get(selection)
            except:
                print("Error try again!")
                continue
            
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

        if cardsOnTable[cardsOnTable.size-1] == cardsOnTable[cardsOnTable.size-2]:
            if cardsOnTable[cardsOnTable.size-1] == cardsOnTable[cardsOnTable.size-3]:
                if cardsOnTable[cardsOnTable.size-1] == cardsOnTable[cardsOnTable.size-4]:
                    self.scorePoints(12)
                else:
                    self.scorePoints(6)
            else:
                self.scorePoints(2)

def convertCardToInt(value):
    if value == 'Ace':
        return 1
    try:
        return int(value)
    except ValueError:
        return 10
        

def layCards(p1, p2):
    currentTurnP1 = not p1.myCrib()
    p1.copyHand()
    p2.copyHand()
    sumOnTable = 0
    cardsOnTable = pydealer.Stack()
    while True:
        if currentTurnP1:
            p1.promptToPlay(cardsOnTable, sumOnTable)


def cutTheDeck(deck):
    return deck.deal(1)[0]



def main():
    p1 = Player(False)
    p2 = Player(True) 
    if random.randint(0,1):
        p1.setmyCrib(True)
        p2.setmyCrib(False)
    
    deck = pydealer.Deck()
    while True:
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

        layCards(p1, p2)



    
