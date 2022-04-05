from urllib.request import AbstractBasicAuthHandler
import pydealer


class GameState:
    playerHand = None
    aiHand = None
    cardsOnTable = None
    discardPile = None

    def __init__(self, player, ai, table, discard):
        self.playerHand = player
        self.aiHand = ai
        self.cardsOnTable = table
        self.discardPile = discard

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

        return GameState(newPlayerHand, newAiHand, newTable, self.discardPile)

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

    # TODO: Score the state of this state for the AI
    def scoreForAI(self):
        return 0
