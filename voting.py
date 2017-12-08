import json
import sys
from functions import isValidTxn, hashMe, updateState, checkBlockHash, checkBlockValidity, checkChain, getInitialState
import random
import copy





def newVote(voter, party):
    return {'voter': voter, 'party': party}


voterList = [u'Alice', u'Bob', u'Charlie', u'Dave']
partyList = ['VVD', 'PVDA', 'D66']

state = getInitialState(voterList, partyList)

genesisBlockTxns = [state]
genesisBlockContents = {u'blockNumber': 0, u'parentHash': None, u'txnCount': 1, u'txns': genesisBlockTxns}
genesisHash = hashMe(genesisBlockContents)
genesisBlock = {u'hash': genesisHash, u'contents': genesisBlockContents}
genesisBlockStr = json.dumps(genesisBlock, sort_keys=True)

chain = [genesisBlock]

blockSizeLimit = 1


def vote(vote, state):
    # Inputs: txn, state: dictionaries keyed with account names, holding numeric values for transfer amount (txn) or account balance (state)
    # Returns: Updated state, with additional users added to state if necessary
    # NOTE: This does not not validate the transaction- just updates the state!

    # If the transaction is valid, then update the state
    state = state.copy()  # As dictionaries are mutable, let's avoid any confusion by creating a working copy of the data.
    state['voters'][vote['voter']] = 0
    state['parties'][vote['party']] += 1

    return state

while len(txnBuffer) > 0:
    bufferStartSize = len(txnBuffer)

    ## Gather a set of valid transactions for inclusion
    txnList = []
    while (len(txnBuffer) > 0) & (len(txnList) < blockSizeLimit):
        newTxn = txnBuffer.pop()
        validTxn = isValidTxn(newTxn, state)  # This will return False if txn is invalid

        if validTxn:  # If we got a valid state, not 'False'
            txnList.append(newTxn)
            state = updateState(newTxn, state)
        else:
            print("ignored transaction")
            sys.stdout.flush()
            continue  # This was an invalid transaction; ignore it and move on

    ## Make a block
    myBlock = makeBlock(txnList, chain)
    chain.append(myBlock)

# txnBuffer = [makeTransaction() for i in range(30)]

