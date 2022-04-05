import pydealer
import player
import game_state
from util import *

# Use AB pruning tree to determine what cards to discard and what cards to play
class PlayerAI(player.Player):

    # Pick a card to discard automagically
    def discardPrompt(self, crib):
        isMyCrib = self.myCrib()
        while self.hand.size > 4:
            chosenCards = pickDiscard(self, crib)
            for chosenCard in chosenCards:
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


# Use AI method to pick cards to discard
# return: the cards to discard
def pickDiscard(self, crib):
    # Use BFS to determine if it's possible to reach goal state (15 sum)
    cardsToDiscard = canDiscardFifteen(self)
    handAsList = self.hand[:]

    # The AI hand is able to make 15
    if cardsToDiscard != -1:
        return cardsToDiscard

    # Can't make 15, use a performance measure to pick 2 cards
    else:
        return bestTwoToDiscard(self)


# Use performance measure to pick worst 2 cards in hand
def bestTwoToDiscard(self):
    handAsList = self.hand[:]

    scoredHand = []
    for card in handAsList:
        # How much to scale doubles/triples by
        doublesScale = 0.5

        # How much to scale 15ability by
        fifteenScale = 0.15

        # How much to scale 31ability by
        # Lower than 15 since will usually not hit 31 exactly, but prevent
        # opponent from hitting it. Also worth less points (2 for 15, 1 for 31)
        thirtyOneScale = 0.075

        # Card score counts how "good" a card is
        cardScore = 0

        cardValue = convertCardToInt(card.value)

        # Performance measure: run value, considers how useful the card is to
        # make or shut down a run. 11 total values so divide by 11
        cardScore += cardValue / 11

        # Performance measure: pair value, considers how useful the card is in
        # making pairs. Try to have many unique values
        # - Having 2 of the same value means the opponent needs 2 (unlikely)
        # - Having 3 of the same value is useless
        numDoubles = 0
        for otherCard in handAsList:
            if otherCard == card:
                continue
            otherCardValue = convertCardToInt(otherCard.value)
            if otherCardValue == cardValue:
                numDoubles += 1
        cardScore -= numDoubles * doublesScale

        # Performance measure: 15ability, considers how useful the card is in
        # summing to 15. Prefer smaller values.
        cardScore += -1 * fifteenScale * (cardValue - 5)

        # Performance measure: 31ability, considers how useful the card is in
        # summing to 31 (or preventing the opponent from reaching it).
        # prefer greater values
        cardScore += thirtyOneScale * (cardValue - 5)

        scoredHand.append((cardScore, card))

    # Pick the 2 worst cards to discard
    scoredHand.sort(key=lambda y: y[1])
    return scoredHand[0:2]


# Possible to discard 2 to make 15? Use BFS search
def canDiscardFifteen(self):
    handAsList = self.hand[:]

    queue = []
    for card in handAsList:
        queue.append([card])

    while len(queue) != 0:
        # Check the state of the discardPile
        currentDiscard = queue.pop(0)

        # Limit: We can only discard 2 cards
        if len(currentDiscard) > 2:
            return -1

        # Check if the goal state is found (discard sum is 15)
        sum = 0
        for card in currentDiscard:
            sum += convertCardToInt(card.value)
            if sum == 15:
                print(currentDiscard)
                return currentDiscard

        # Continue BFS
        for card in handAsList:
            if not card in currentDiscard:
                newDiscard = currentDiscard.copy()
                newDiscard.append(card)
                queue.append(newDiscard)

    return -1


# Use AB pruning tree to play a card
# return: the card to play
def pickPlay(self, playableCards, cardsOnTable, sumOnTable):
    # Placeholder
    # strategy:
    #   maximize 15s for self, minimize 15s for adversary
    #   maximize completing runs, minimize setting up runs
    #   maximize pairs/triplets etc
    #   priority: triplets and above > runs > 15s

    # TODO: currentState is the state of the game currently
    # i.e. use the game_state constructor
    currentState = None

    # Current depth is 2, maybe change later?
    cardToPlay = minimax(self, currentState, None, 2, True)
    return cardToPlay[1]


# Find the best card to play for the AI
# Parameters:
#   node             = the current node to score
#   cardPlayed       = the card played during this turn
#   depth            = how many turns ahead we want to check. Depth of 2 = bot turn, player turn, bot turn
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

        handAsList = self.hand[:]

        # Play optimally, picking the card that results in the greatest "score"
        # for the CPU
        for card in handAsList:
            # nextNode is the state of the game as a result of playing the card variable
            # They ARE the AI player (true)
            nextNode = node.playCard(card, True)

            childValue = minimax(nextNode, card, depth - 1, False)

            # Maximize
            if childValue[0] > value[0]:
                value = childValue
        return value

    else:
        # Value tuple follows same format as return tuple
        value = (float("inf"), None)

        # TODO: Placeholder, in reality, will need to find out what to put for the real player's hand...
        #       i.e. replace this with something. Should the bot "know" the player's actual hand to
        #       make it seem like a better opponent?
        realPlayerHand = self.hand
        handAsList = realPlayerHand[:]

        # Assuming the player plays optimally, and picks the card that results
        # in lowest "score" for the CPU
        for card in handAsList:
            # nextNode is the state of the game as a result of playing the card variable
            # They are NOT the ai player (false)
            nextNode = node.playCard(card, False)

            childValue = minimax(nextNode, card, depth - 1, True)

            # Minimize
            if childValue[0] < value[0]:
                value = childValue
        return value
