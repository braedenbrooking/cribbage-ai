import pydealer

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
def checkForRun(
    stack,
):
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
