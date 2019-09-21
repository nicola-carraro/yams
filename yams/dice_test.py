from dice import *
from helpers import COMBINATION_ENTRIES


dice = Dice()

def is_straight_test():
    print("[]")
    print(is_straight([]))
    print("[2]")
    print(is_straight([2]))
    print("[2, 3, 4]")
    print(is_straight([2, 3, 4]))
    print("[4, 2, 3]")
    print(is_straight([4, 2, 3]))


def __init__test():
    print("1")
    try:
        Dice([1])
    except ValueError as err:
        print(err)
    print("7, 6, 5, 6, 7")
    try:
        Dice([7, 6, 5, 6, 7])
    except ValueError as err:
        print(err)

def roll_test():
    print(dice)
    print("Dice 0, 1, 2:")
    dice.roll([0, 1, 2])
    print(dice)

    print("Dice 3, 4:")
    dice.roll([3, 4])
    print(dice)

    print("Invalid index: 5")
    try:
        dice.roll([1, 2, 5])
    except ValueError:
        print("ValueError")

def roll_all_test():
    print(dice)
    for i in range(0, 5):
        dice.roll_all()
        print(dice)

def is_poker_test():
    print("1, 2, 3, 4, 5:")
    dice = Dice([1 , 2, 3, 4, 5])
    print(dice.is_poker())
    print("4, 4, 4, 4, 2:")
    dice = Dice([4, 4, 4, 4, 2])
    print(dice.is_poker())


def is_full_test():
    print("1, 2, 3, 4, 5:")
    dice = Dice([1 , 2, 3, 4, 5])
    print(dice)
    print(dice.is_full())
    print("4, 2, 4, 4, 2:")
    dice = Dice([4, 2, 4, 4, 2])
    print(dice.is_full())


def is_small_straight_test():
    print("[1, 2, 3, 4, 5]:")
    dice = Dice([1 , 2, 3, 4, 5])
    print(dice)
    print(dice.is_small_straight())

    print("[6, 2, 3, 4, 5]:")
    dice = Dice([6, 2, 3, 4, 5])
    print(dice)
    print(dice.is_small_straight())

    print("[6, 5, 3, 4, 2]:")
    dice = Dice([6, 5, 3, 4, 2])
    print(dice)
    print(dice.is_small_straight())

    print("[1, 5, 3, 4, 1]:")
    dice = Dice([1, 5, 3, 4, 1])
    print(dice)
    print(dice.is_small_straight())


def is_large_straight_test():
    print("[1, 2, 3, 4, 5]:")
    dice = Dice([1 , 2, 3, 4, 5])
    print(dice)
    print(dice.is_large_straight())

    print("[6, 2, 3, 4, 5]:")
    dice = Dice([6, 2, 3, 4, 5])
    print(dice)
    print(dice.is_large_straight())

    print("[6, 5, 3, 4, 2]:")
    dice = Dice([6, 5, 3, 4, 2])
    print(dice)
    print(dice.is_large_straight())

    print("[1, 2, 3, 4, 1]:")
    dice = Dice([1, 5, 3, 4, 1])
    print(dice)
    print(dice.is_large_straight())

def is_yams_test():

    print("[1, 2, 3, 4, 1]:")
    dice = Dice([1, 5, 3, 4, 1])
    print(dice)
    print(dice.is_yams())

    print("[1, 1, 1, 1, 1]:")
    dice = Dice([1, 1, 1, 1, 1])
    print(dice)
    print(dice.is_yams())

def is_rigole_test():
    print("[1, 2, 3, 4, 1]:")
    dice = Dice([1, 5, 3, 4, 1])
    print(dice)
    print(dice.is_rigole())
    print(dice)

    print("[1, 1, 1, 1, 1]:")
    dice = Dice([1, 1, 1, 1, 1])
    print(dice)
    print(dice.is_rigole())
    print(dice)

    print("[1, 1, 1, 1, 6]:")
    dice = Dice([1, 1, 1, 1, 6])
    print(dice)
    print(dice.is_rigole())
    print(dice)

    print("[1, 1, 6, 1, 1]:")
    dice = Dice([1, 1, 6, 1, 1])
    print(dice)
    print(dice.is_rigole())
    print(dice)

    print("[1, 1, 5, 1, 1]:")
    dice = Dice([1, 1, 5, 1, 1])
    print(dice)
    print(dice.is_rigole())
    print(dice)



def calculate_score_test():
    print("[1, 2, 3, 4, 5]")
    dice = Dice([1, 2, 3, 4, 5])
    for entry in COMBINATION_ENTRIES:
        print("%s: %i" % (entry, dice.calculate_score(entry)))


    print("[3, 2, 3, 4, 3]")
    dice = Dice([3, 2, 3, 4, 3])
    for entry in COMBINATION_ENTRIES:
        print("%s: %i" % (entry, dice.calculate_score(entry)))


    print("[1, 1, 1, 1, 1]")
    dice = Dice([1, 1, 1, 1, 1])
    for entry in COMBINATION_ENTRIES:
        print("%s: %i" % (entry, dice.calculate_score(entry)))

    print("[1, 2, 1, 2, 1]")
    dice = Dice([1, 1, 1, 1, 1])
    for entry in COMBINATION_ENTRIES:
        print("%s: %i" % (entry, dice.calculate_score(entry)))

    print("[1, 2, 1, 3, 4]")
    dice = Dice([1, 1, 1, 1, 1])
    for entry in COMBINATION_ENTRIES:
        print("%s: %i" % (entry, dice.calculate_score(entry)))



print("Roll test:")
roll_test()
print()

print("Calculate score test:")
calculate_score_test()
print()



print("is_straight_test():")
print()
is_straight_test()

print("__init__test:")
__init__test()
print()

print("roll_test")
roll_test()
print()

print("roll_all_test")
roll_all_test()
print()

print("is_poker_test")
is_poker_test()
print()

print("is_full_test:")
is_full_test()
print()

print("is_small_straight_test:")
is_small_straight_test()
print()

print("is_large_straight_test:")
is_large_straight_test()
print()


print("is_yams_test():")
is_yams_test()
print()


print("is_rigole_test():")
is_rigole_test()
print()

print("calculate_score_test:")
calculate_score_test()
print()
