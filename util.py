import pydealer
import copy

RANKS = {
    "values": {
        "Ace": 1,
        "King": 13,
        "Queen": 12,
        "Jack": 11,
        "10": 10,
        "9": 9,
        "8": 8,
        "7": 7,
        "6": 6,
        "5": 5,
        "4": 4,
        "3": 3,
        "2": 2,
        "Joker": 0,
    }
}


def checkNobs(cut, card):
    return card.value == "Jack" and cut.suit == card.suit


# Helps to clean everything up
def checkForPair(card1, card2):
    return card1.value == card2.value


# checks if all the cards in the stack are sequent if not all returns False
def checkForRun(stack):
    stack.sort(RANKS)
    for i in range(stack.size - 1):
        if getNextValue(stack[i]) != stack[i + 1].value:
            return False
    return True


def find15sTwoCard(values):
    points = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if values[i] + values[j] == 15:
                points += 2
    return points


def find15sThreeCard(values):
    points = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            for k in range(j + 1, len(values)):
                if values[i] + values[j] + values[k] == 15:
                    points += 2
    return points


def find15sFourCard(values):
    points = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            for k in range(j + 1, len(values)):
                for l in range(k + 1, len(values)):
                    if values[i] + values[j] + values[k] + values[l] == 15:
                        points += 2
    return points


def find15sFiveCard(values):
    if values[0] + values[1] + values[2] + values[3] + values[4] == 15:
        return 2
    else:
        return 0


def getNextValue(card):
    if card.value == "10":
        return "Jack"
    try:
        return str(int(card.value) + 1)
    except ValueError:
        if card.value == "Ace":
            return 2
        elif card.value == "Jack":
            return "Queen"
        elif card.value == "Queen":
            return "King"
        else:
            return "Null"


def convertCardToInt(value):
    if value == "Ace":
        return 1
    try:
        return int(value)
    except ValueError:
        return 10


def calculateTwoCardsPoints(card1, card2):
    if card1.value == card2.value:
        return 2
    elif convertCardToInt(card1) + convertCardToInt(card2) == 15:
        return 2
    else:
        return 0

def calculateScore(scoringHand, cutCard, prints=False):
    scoringHand2 = copy.deepcopy(scoringHand)  # For Safety
    scoringHand2.add(cutCard)

    totalHandScore = calculateScore(scoringHand2)

    # Nobs (The right jack)
    if cutCard is not None:
        for card in scoringHand:
            if card != cutCard and checkNobs(cutCard, card):
                totalHandScore += 1
                if prints:
                    print("The right Jack (nobs) is" + str(totalHandScore))
    return totalHandScore


def calculateScore(scoringHand, prints=False):
    scoringHand = copy.deepcopy(scoringHand)  # For Safety
    totalHandScore = 0

    # Flush
    if (
            scoringHand[0].suit == scoringHand[1].suit
            and scoringHand[0].suit == scoringHand[2].suit
            and scoringHand[0].suit == scoringHand[3].suit
    ):
        if scoringHand[0].suit == scoringHand[4].suit:
            totalHandScore += 5
            if prints:
                print("Flush including the cut for " + str(totalHandScore))
        else:
            totalHandScore += 4
            if prints:
                print("Flush excluding the cut for " + str(totalHandScore))

    scoringHand.sort(RANKS)  # For ease of calculations

    # 15s
    handValues = [convertCardToInt(x.value) for x in scoringHand]
    fifteenspoints = 0
    fifteenspoints += find15sTwoCard(handValues)  # i.e. scoringHand.size choose 2
    fifteenspoints += find15sThreeCard(handValues)  # i.e. scoringHand.size choose 3
    fifteenspoints += find15sFourCard(handValues)  # i.e. scoringHand.size choose 4
    if len(handValues) >= 5:
        fifteenspoints += find15sFiveCard(handValues)  # i.e. scoringHand.size choose 5
    if fifteenspoints:
        if prints:
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
        if prints:
            print("A pair of " + val + "s is " + str(totalHandScore))

    if threeValue is not None:
        totalHandScore += 6
        if prints:
            print("3 " + threeValue + "s is " + str(totalHandScore))

    if fourValue is not None:
        totalHandScore += 12
        if prints:
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

    for run in runs:
        if prints:
            print("Run of " + str(len(run)))
        totalHandScore += len(run)

    return totalHandScore
