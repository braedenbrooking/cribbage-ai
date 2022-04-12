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
                # TODO When we are finished obviously we shouldn't print out what the AI does
                print("AI Player discards " + str(chosenCard))
                crib.add(self.hand.get(str(chosenCard)))
                self.cardsPutInCrib.add((chosenCard))
        self.handCopy = copy.deepcopy(self.hand)
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
                playableCards.append(card)

        # no playable cards, go
        if len(playableCards) == 0:
            return

        card = self.pickPlay(playableCards)
        cardValue = convertCardToInt(card.value)

        sumOnTable += cardValue
        cardsOnTable.add(card)
        self.pegPoints(cardsOnTable, sumOnTable)
        return sumOnTable

    def discardByUtility(self):
        utilities = []
        bestScore = -999999
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
        # I know this could be more efficient by not checking certain pairs that the optimal player would likely never throw away (ex 2 5s)
        """
        for k in range(len(deckList) - 2):
            for l in range(k + 1, len(deckList) - 1):
                for m in range(l + 1, len(deckList)):
                    tempStack = pydealer.Stack()
                    tempStack.add(deckList[k])
                    tempStack.add(deckList[l])
                    tempStack.add(card1)
                    tempStack.add(card2)
                    cribScoreValue = calculateScore(tempStack, deckList[m])
                    if cribScoreValue in potentialCribPoints.keys():
                        potentialCribPoints[cribScoreValue] += 1
                    else:
                        potentialCribPoints[cribScoreValue] = 1
        """

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
        # Placeholder
        # strategy:
        #   maximize 15s for self, minimize 15s for adversary
        #   maximize completing runs, minimize setting up runs
        #   maximize pairs/triplets etc
        #   priority: triplets and above > runs > 15s

        # TODO: currentState is the state of the game currently
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
        cardToPlay = self.minimax(currentState, None, 3, True)
        return cardToPlay[1]

    # Find the best card to play for the AI
    # Parameters:
    #   node             = the current node to score
    #   cardPlayed       = the card played during this turn
    #   depth            = how many turns ahead we want to check. Depth of 3 = bot turn, player turn, bot turn
    #   maximizingPlayer = True if it's the bot's turn, otherwise false
    # Return:
    #   a tuple (score, card) representing what score is expected by playing the best card and what card that is
    def minimax(self, node, cardPlayed, depth, maximizingPlayer):
        if depth == 0:  # TODO: potentially need to add: OR node is a terminal node
            score = node.score()

            # Return a tuple of the score and the card played in that round
            return (score, cardPlayed)

        if maximizingPlayer:
            # Value tuple follows same format as return tuple
            value = (-1 * float("inf"), None)

            # TODO: cards need to be removed from this temp hand when played; dont copy actual hand every time
            #! now hand is taken from the node. this SHOULD be accurate i believe?
            handAsList = node.StackToList("ai")

            # Play optimally, picking the card that results in the greatest "score"
            # for the CPU
            for card in handAsList:
                # nextNode is the state of the game as a result of playing the card variable
                # They ARE the AI player (true)
                nextNode = node.playCard(card, True)

                childValue = self.minimax(nextNode, card, depth - 1, False)

                # Maximize
                if childValue[0] > value[0]:
                    value = (childValue[0], card)
            return value

        else:
            # Value tuple follows same format as return tuple
            value = (float("inf"), None)

            # TODO: Placeholder, in reality, will need to find out what to put for the real player's hand...
            #       i.e. replace this with something. Should the bot "know" the player's actual hand to
            #       make it seem like a better opponent?
            #! this should work but is also EXTREMELY big
            handAsList = node.StackToList("player")

            # Assuming the player plays optimally, and picks the card that results
            # in lowest "score" for the CPU
            for card in handAsList:
                # nextNode is the state of the game as a result of playing the card variable
                # They are NOT the ai player (false)
                nextNode = node.playCard(card, False)

                childValue = self.minimax(nextNode, card, depth - 1, True)

                # Minimize
                if childValue[0] < value[0]:
                    value = (childValue[0], card)
            return value


