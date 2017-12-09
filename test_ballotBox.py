from unittest import TestCase
from ballot_box import BallotBox, newElection
import copy

class TestBallotBox(TestCase):
    def test_vote(self):
        voterList = ['Alice', 'Bob', 'Charlie', 'Dave']
        partyList = ['VVD', 'PVDA', 'D66']

        box1 = newElection(voterList, partyList)
        box2 = BallotBox(copy.deepcopy(box1.chain))

        box1.printLastBlock()
        box1.vote('Alice', 'VVD')

        box2.updateChain(box1.chain)

        box2.printLastBlock()
        box2.vote('Alice', 'VVD')
        box2.printLastBlock()
        box2.vote('Bob', 'D66')

        box1.updateChain(box2.chain)

        box1.printLastBlock()
        box1.vote('Charlie', 'D66')
        box1.printLastBlock()

        box2.updateChain(box1.chain)

        box1.printOutcome()
        box1.checkChain()

        box2.printOutcome()
        box2.checkChain()
