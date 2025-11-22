from logic import *

# Symbols
AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says: "I am both a knight and a knave"
knowledge0 = And(
    Or(AKnight, AKnave),                 # A is knight or knave (Exclusive rule)
    Not(And(AKnight, AKnave)),           # A cannot be both
    Implication(AKnight, And(AKnight, AKnave)),   # If A is telling the truth → statement is true
    Implication(AKnave, Not(And(AKnight, AKnave))) # If A is lying → statement is false
)

# Puzzle 1
# A says "We are both knaves"
# B says nothing
knowledge1 = And(
    # Characters must be knight or knave (but not both)
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    # If A is a knight → statement is true → A and B are knaves
    Implication(AKnight, And(AKnave, BKnave)),
    # If A is a knave → statement is false → NOT (A and B knaves)
    Implication(AKnave, Not(And(AKnave, BKnave)))
)

# Puzzle 2
# A says: "We are the same kind"
# B says: "We are of different kinds"
knowledge2 = And(
    # Knight/Knave rules for both characters
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    # A's statement: same kind
    Implication(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    Implication(AKnave, Not(Or(And(AKnight, BKnight), And(AKnave, BKnave)))),

    # B's statement: different kinds
    Implication(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight))),
    Implication(BKnave, Not(Or(And(AKnight, BKnave), And(AKnave, BKnight))))
)

# Puzzle 3
# A says either “I am a knight” or “I am a knave.” (but we don't know which)
# B: "A said 'I am a knave'"
# B: "C is a knave"
# C: "A is a knight"
knowledge3 = And(
    # Knight/Knave rules for A, B, C
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave)),

    # A said one of the two statements (unknown which)
    Or(
        # A said "I am a knight"
        And(AKnight, Implication(AKnight, AKnight), Implication(AKnave, Not(AKnight))),
        # A said "I am a knave"
        And(AKnight, Implication(AKnight, AKnave), Implication(AKnave, Not(AKnave)))
    ),

    # B says A said "I am a knave"
    Implication(BKnight, AKnave),
    Implication(BKnave, Not(AKnave)),

    # B says C is a knave
    Implication(BKnight, CKnave),
    Implication(BKnave, Not(CKnave)),

    # C says A is a knight
    Implication(CKnight, AKnight),
    Implication(CKnave, Not(AKnight))
)

# ALL PUZZLES
puzzles = [
    ("Puzzle 0", knowledge0),
    ("Puzzle 1", knowledge1),
    ("Puzzle 2", knowledge2),
    ("Puzzle 3", knowledge3)
]

def main():
    for puzzle, knowledge in puzzles:
        print(puzzle)
        for symbol in [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]:
            if model_check(knowledge, symbol):
                print(f"    {symbol}")


if __name__ == "__main__":
    main()
