from functions import hashMe
import json
import copy

def newElection(voterList, partyList):

    genesisBlockTxns = [BallotBox.getInitialState(voterList, partyList)]
    genesisBlockContents = {u'blockNumber': 0, u'parentHash': None, u'txnCount': 1, u'txns': genesisBlockTxns}
    genesisHash = hashMe(genesisBlockContents)
    genesisBlock = {u'hash': genesisHash, u'contents': genesisBlockContents}
    genesisBlockStr = json.dumps(genesisBlock, sort_keys=True)
    return BallotBox([genesisBlock])

class BallotBox:

    def __init__(self, chain):
        self.chain = chain
        self.state = self.checkChain()

    def vote(self, voter, party):

        vote = self.newVote(voter, party)

        state = self.state
        validVote = self.isValidVote(vote, state)  # This will return False if txn is invalid

        voteList = []
        if validVote:  # If we got a valid state, not 'False'
            self.updateState(state, vote)

            voteList.append(vote)
            ## Make a block
            myBlock = self.makeBlock(voteList, self.chain)
            self.chain.append(myBlock)

        return state

    def updateState(self, state, vote):
        state['voters'][vote['voter']] = 0
        state['parties'][vote['party']] += 1
        return copy.deepcopy(state)

    def newVote(self, voter, party):
        return {'voter': voter, 'party': party}

    def isValidVote(self, vote, state):
        # Assume that the transaction is a dictionary keyed by account names

        voter = vote['voter']
        party = vote['party']
        if not (voter in state['voters'].keys() and party in state['parties'].keys()):
            return False

        # Check that person has not yet voted
        if state['voters'][voter] == 0:
            return False

        return True

    @staticmethod
    def getInitialState(voters, parties):
        state = {
            'voters': {},
            'parties': {}
        }
        for k in voters:
            state['voters'][k] = 1

        for k in parties:
            state['parties'][k] = 0
        return state

    def makeBlock(self, txns, chain):
        parentBlock = chain[-1]
        parentHash = parentBlock[u'hash']
        blockNumber = parentBlock[u'contents'][u'blockNumber'] + 1
        txnCount = len(txns)
        blockContents = {u'blockNumber': blockNumber, u'parentHash': parentHash,
                         u'txnCount': len(txns), 'txns': txns}
        blockHash = hashMe(blockContents)
        block = {u'hash': blockHash, u'contents': blockContents}

        return block

    def checkBlockHash(self, block):
        # Raise an exception if the hash does not match the block contents
        expectedHash = hashMe(block['contents'])
        if block['hash'] != expectedHash:
            raise Exception('Hash does not match contents of block %s' %
                            block['contents']['blockNumber'])
        return

    def checkBlockValidity(self, block, parent, state):
        state = copy.deepcopy(state)
        # We want to check the following conditions:
        # - Each of the transactions are valid updates to the system state
        # - Block hash is valid for the block contents
        # - Block number increments the parent block number by 1
        # - Accurately references the parent block's hash
        parentNumber = parent['contents']['blockNumber']
        parentHash = parent['hash']
        blockNumber = block['contents']['blockNumber']

        # Check transaction validity; throw an error if an invalid transaction was found.
        for vote in block['contents']['txns']:
            if self.isValidVote(vote, state):
                state = self.updateState(state, vote)

        self.checkBlockHash(block)  # Check hash integrity; raises error if inaccurate

        if blockNumber != (parentNumber + 1):
            raise Exception('Hash does not match contents of block %s' % blockNumber)

        if block['contents']['parentHash'] != parentHash:
            raise Exception('Parent hash not accurate at block %s' % blockNumber)

        return state

    def updateChain(self, chain):
        self.chain = copy.deepcopy(chain)
        self.state = self.checkChain()

    def checkChain(self):
        # Work through the chain from the genesis block (which gets special treatment),
        #  checking that all transactions are internally valid,
        #    that the transactions do not cause an overdraft,
        #    and that the blocks are linked by their hashes.
        # This returns the state as a dictionary of accounts and balances,
        #   or returns False if an error was detected

        ## Prime the pump by checking the genesis block
        # We want to check the following conditions:
        # - Each of the transactions are valid updates to the system state
        # - Block hash is valid for the block contents

        self.checkBlockHash(self.chain[0])
        parent = self.chain[0]
        state = self.chain[0]['contents']['txns'][0]
        ## Checking subsequent blocks: These additionally need to check
        #    - the reference to the parent block's hash
        #    - the validity of the block number
        for block in self.chain[1:]:
            state = self.checkBlockValidity(block, parent, state)
            parent = block

        return copy.deepcopy(state)

    def printLastBlock(self):
        print(self.chain[-1]['contents'])

    def printOutcome(self):
        print(self.state['parties'])