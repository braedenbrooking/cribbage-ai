import pydealer
import player
from util import *

# Use AB pruning tree to determine what cards to discard and what cards to play
class PlayerAI(player.Player):

    # Pick a card to discard automagically
    def discardPrompt(self, crib):
        isMyCrib = self.myCrib()
        while self.hand.size > 4:
            chosenCard = pickDiscard(self, crib)
            print("AI Player discards " + chosenCard)
            crib.add(self.hand.get(chosenCard))
        return crib

    # Play a card automagically
    def promptToPlay(self, cardsOnTable, sumOnTable):
        # Determine the playable cards
        playableCards = []
        handAsList = self.hand[:]
        for card in handAsList:
            cardValue = convertCardToInt(card.value)
            sumIfPlayed = sumOnTable + cardValue

            if sumIfPlayed <= 31:
                playableCards.add(card)

        # no playable cards, go
        if len(playableCards) == 0:
            return

        card = pickPlay(self, playableCards, cardsOnTable, sumOnTable)
        cardValue = convertCardToInt(card.value)

        sumOnTable += cardValue
        cardsOnTable.add(card)
        self.pegPoints(cardsOnTable, sumOnTable)
        return sumOnTable


# Use AI method to pick a card to discard
# return: the card to discard
def pickDiscard(self, crib):
    # Placeholder
    handAsList = self.hand[:]
    return handAsList[0]


# Use AB pruning tree to play a card
# return: the card to play
def pickPlay(self, playableCards, cardsOnTable, sumOnTable):
    # Placeholder
    # strategy:
    #   maximize 15s for self, minimize 15s for adversary
    #   maximize completing runs, minimize setting up runs
    #   maximize pairs/triplets etc
    #   priority: triplets and above > runs > 15s
    return playableCards[0]
