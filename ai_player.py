import pydealer
import copy
from player import Player
from game_state import GameState
from util import *

# Use AB pruning tree to determine what cards to discard and what cards to play
class PlayerAI(Player):

    cardsPutInCrib = pydealer.Stack()  # Used later so we remember what we discarded

    # Pick a card to discard automagically
    def discardPrompt(self, crib):
        while self.hand.size > 4:
            chosenCards = self.discardByUtility()
            for chosenCard in chosenCards:
                #print("AI Player discards " + str(chosenCard)) #DEBUG
                crib.add(self.hand.get(str(chosenCard)))
                self.cardsPutInCrib.add((chosenCard))
        self.handCopy = copy.deepcopy(self.hand)
        return crib

    # Play a card automagically
    def promptToPlay(self, cardsOnTable, sumOnTable):
        # Determine the playable cards
        print("Please wait while the AI makes its decision...")
        playableCards = []
        handAsList = self.handCopy[:]
        for card in handAsList:
            cardValue = convertCardToInt(card.value)
            sumIfPlayed = sumOnTable + cardValue

            if sumIfPlayed <= 31:
                playableCards.append(card)

        # no playable cards, go
        if len(playableCards) == 0:
            return sumOnTable
        elif len(playableCards) == 1:
            card = playableCards[0]
            cardValue = convertCardToInt(card.value)
        else:
            card = self.pickPlay(playableCards)
            cardValue = convertCardToInt(card.value)

        sumOnTable += cardValue
        cardsOnTable.add(card)
        print("AI Plays: " + str(card))
        self.handCopy.get(str(card))
        calculatePegPoints(cardsOnTable, sumOnTable, self)

        return sumOnTable

    def discardByUtility(self):
        utilities = []
        bestScore = -1*float("inf")
        bestCards = []
        deck = pydealer.Deck()
        # Removes the cards in hand from the deck
        deck.get_list([str(x) for x in self.hand[:]])

        for i in range(len(self.hand) - 1):
            for j in range(i, len(self.hand) - 1):
                tempHand = copy.deepcopy(self.hand)  # For Safety
                card1 = tempHand.get(i)[0]
                card2 = tempHand.get(j)[0]
                self.calculateUtility(card1, card2, tempHand, deck, utilities)

        for elem in utilities:
            if elem["score"] > bestScore:
                bestScore = elem["score"]
                bestCards = elem["cards"]

        return bestCards

    def calculateUtility(self, card1, card2, hand, deck, utilityList):
        potentialHandPoints = {}
        potentialCribPoints = {}
        guaranteedHandPts = calculateScore(hand)

        guaranteedCribPts = calculateTwoCardsPoints(card1, card2)

        for possibleCut in deck:
            scoreValueHand = calculateScore(hand, possibleCut)
            if scoreValueHand in potentialHandPoints.keys():
                potentialHandPoints[scoreValueHand] += 1
            else:
                potentialHandPoints[scoreValueHand] = 1
            tempStack = pydealer.Stack()
            tempStack.add(pydealer.Card("Joker", "Joker"))
            tempStack.add(pydealer.Card("Joker", None))
            tempStack.add(card1)
            tempStack.add(card2)
            scoreValueCrib = calculateScore(tempStack, possibleCut)
            if scoreValueCrib in potentialCribPoints.keys():
                potentialCribPoints[scoreValueCrib] += 1
            else:
                potentialCribPoints[scoreValueCrib] = 1

        deckList = deck[:]

        potentialHandScore = 0
        for score in potentialHandPoints.keys():
            potentialHandScore += (score-guaranteedHandPts) * (potentialHandPoints[score] / len(deckList))

        potentialCribScore = 0
        for score in potentialCribPoints.keys():
            potentialCribScore += (score-guaranteedCribPts) * (potentialCribPoints[score] / 15180)  # (52-6) choose 3

        if not self.myCrib():
            potentialCribScore = potentialCribScore * -1
            guaranteedCribPts = guaranteedCribPts * -1

        utilityScore = (
            guaranteedHandPts
            + guaranteedCribPts
            + potentialHandScore
            + potentialCribScore
        )
        cards = [card1, card2]
        utilityList.append({"score": utilityScore, "cards": cards})

    # Use AB pruning tree to play a card
    # return: the card to play
    def pickPlay(self, playableCards):
        # i.e. use the game_state constructor
        currentState = copy.deepcopy(self.gameStateRef)

        # Use the whole deck that the AI doesn't have as the player's prospective hand
        # i.e. assume the player will always be able to counter with the best move
        deck = pydealer.Deck()
        # Removes the cards in hand from the deck
        deck.get_list([str(x) for x in currentState.StackToList("ai")])
        deck.get_list([str(x) for x in currentState.StackToList("table")])
        deck.get_list([str(x) for x in self.cardsPutInCrib[:]])

        remainderStack = pydealer.Stack()
        for card in deck:
            remainderStack.add(card)

        currentState.setPlayerHand(remainderStack)
        currentState.setAIHand(playableCards)

        # Current depth is 3, maybe change later?
        cardToPlay = self.decisionTree(node=currentState, cardPlayed=None, depth=3, maximizingAi=True)
        return cardToPlay[1]


    def decisionTree(self, node, cardPlayed, depth, maximizingAi):
        if depth == 0 or len(self.handCopy[:]) == 0 or calculateSumOnTable(node.cardsOnTable) == 31:
            additionalPoints = 0
            if calculateSumOnTable(node.cardsOnTable) == 31:
                additionalPoints = 2 if not maximizingAi else -2

            return (node.aiScore - node.playerScore + additionalPoints, cardPlayed)

        if maximizingAi:
            handAsList = node.StackToList("ai", copy=True)
        else:
            handAsList = node.StackToList("player", copy=True)


        if maximizingAi:
            bestCard = None
            bestScore = -1*float("inf")
            for card in handAsList:
                nextNode = node.playCard(card, maximizingAi)
                heuristicScore = self.decisionTree(nextNode, card, depth-1, not maximizingAi)[0] + (node.aiScore - node.playerScore)

                if heuristicScore > bestScore:
                    bestScore = heuristicScore
                    bestCard = card
            return (bestScore, bestCard)
        else:
            probability = 1/len(handAsList)
            netHeuristic = node.aiScore - node.playerScore
            for card in handAsList:
                nextNode = node.playCard(card, maximizingAi)
                netHeuristic += probability * self.decisionTree(nextNode, card, depth-1, not maximizingAi)[0]

            return (netHeuristic, cardPlayed)

