from unittest import TestCase
from ballot_box import BallotBox

class TestBallotBox(TestCase):
    def test_vote(self):
        voterList = ['Alice', 'Bob', 'Charlie', 'Dave']
        partyList = ['VVD', 'PVDA', 'D66']
        box = BallotBox(voterList, partyList)
        box.printLastBlock()
        box.vote('Alice', 'VVD')
        box.printLastBlock()
        box.vote('Alice', 'VVD')
        box.printLastBlock()
        box.vote('Bob', 'D66')
        box.vote('Charlie', 'D66')
        box.printLastBlock()

        box.printOutcome()
        box.checkChain()

    def test_isValidVote(self):
        self.fail()

    def test_getInitialState(self):
        self.fail()

    def test_makeBlock(self):
        self.fail()
