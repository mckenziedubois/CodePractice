from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."

A_statement_0 = And(AKnight, AKnave)

knowledge0 = And(

    Or(AKnight, AKnave),
    Not(A_statement_0),
    Implication(AKnight, A_statement_0),
    Implication(AKnave, Not(A_statement_0))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.

A_statement_1 = And(AKnave, BKnave)
B_statement_1 = None

knowledge1 = And(
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Not(A_statement_1),
    Implication(AKnight, A_statement_1),
    Implication(AKnave, Not(A_statement_1))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."

A_statement_2 = Or(And(AKnave, BKnave), And(AKnight, BKnight))
B_statement_2 = Or(And(AKnave, BKnight), And(AKnight, BKnave))

knowledge2 = And(
    # General Logic
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),

    # Statement Logic
    Implication(AKnight, A_statement_2),
    Implication(AKnave, Not(A_statement_2)),
    Implication(BKnight, B_statement_2),
    Implication(BKnave, Not(B_statement_2))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."

A_said_Knight = Symbol("A said 'I am a Knight'")
A_said_Knave = Symbol("A said 'I am a Knave'")

A_statement_3 = Or(AKnight, AKnave)
B_statement_3_1 = A_said_Knight
B_statement_3_2 = CKnave
C_statement_3 = AKnight

knowledge3 = And(
    # General Logic
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Or(CKnight, CKnave),
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),
    Not(And(CKnight, CKnave)),

    # A statements
    Implication(A_said_Knight, AKnight),
    Implication(A_said_Knave, AKnave),
    Implication(AKnight, Implication(A_said_Knight, AKnight)),
    Implication(AKnight, Implication(A_said_Knave, AKnave)),
    Implication(AKnave, Implication(A_said_Knight, Not(AKnight))),
    Implication(AKnave, Implication(A_said_Knave, Not(AKnave))),

    # B statements
    Implication(BKnight, B_statement_3_1),
    Implication(BKnave, Not(B_statement_3_1)),
    Implication(BKnight, B_statement_3_2),
    Implication(BKnave, Not(B_statement_3_2)),

    # C statements
    Implication(CKnight, C_statement_3),
    Implication(CKnave, Not(C_statement_3))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
