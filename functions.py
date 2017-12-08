import hashlib, json, sys


def hashMe(msg=""):
    # For convenience, this is a helper function that wraps our hashing algorithm
    if type(msg) != str:
        msg = json.dumps(msg, sort_keys=True)  # If we don't sort keys, we can't guarantee repeatability!

    return hashlib.sha256(str(msg).encode('utf-8')).hexdigest()


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

def isValidTxn(txn, state):
    # Assume that the transaction is a dictionary keyed by account names

    # Check that the sum of the deposits and withdrawals is 0
    if sum(txn.values()) is not 0:
        return False

    # Check that the transaction does not cause an overdraft
    for key in txn.keys():
        if key in state.keys():
            acctBalance = state[key]
        else:
            acctBalance = 0
        if (acctBalance + txn[key]) < 0:
            return False

    return True

def checkBlockHash(block):
    # Raise an exception if the hash does not match the block contents
    expectedHash = hashMe(block['contents'])
    if block['hash'] != expectedHash:
        raise Exception('Hash does not match contents of block %s' %
                        block['contents']['blockNumber'])
    return


def checkBlockValidity(block, parent, state):
    # We want to check the following conditions:
    # - Each of the transactions are valid updates to the system state
    # - Block hash is valid for the block contents
    # - Block number increments the parent block number by 1
    # - Accurately references the parent block's hash
    parentNumber = parent['contents']['blockNumber']
    parentHash = parent['hash']
    blockNumber = block['contents']['blockNumber']

    # Check transaction validity; throw an error if an invalid transaction was found.
    for txn in block['contents']['txns']:
        if isValidTxn(txn, state):
            state = updateState(txn, state)
        else:
            raise Exception('Invalid transaction in block %s: %s' % (blockNumber, txn))

    checkBlockHash(block)  # Check hash integrity; raises error if inaccurate

    if blockNumber != (parentNumber + 1):
        raise Exception('Hash does not match contents of block %s' % blockNumber)

    if block['contents']['parentHash'] != parentHash:
        raise Exception('Parent hash not accurate at block %s' % blockNumber)

    return state

def checkChain(chain):
    # Work through the chain from the genesis block (which gets special treatment),
    #  checking that all transactions are internally valid,
    #    that the transactions do not cause an overdraft,
    #    and that the blocks are linked by their hashes.
    # This returns the state as a dictionary of accounts and balances,
    #   or returns False if an error was detected

    ## Data input processing: Make sure that our chain is a list of dicts
    if type(chain) == str:
        try:
            chain = json.loads(chain)
            assert (type(chain) == list)
        except:  # This is a catch-all, admittedly crude
            return False
    elif type(chain) != list:
        return False

    state = {}
    ## Prime the pump by checking the genesis block
    # We want to check the following conditions:
    # - Each of the transactions are valid updates to the system state
    # - Block hash is valid for the block contents

    for txn in chain[0]['contents']['txns']:
        state = updateState(txn, state)
    checkBlockHash(chain[0])
    parent = chain[0]

    ## Checking subsequent blocks: These additionally need to check
    #    - the reference to the parent block's hash
    #    - the validity of the block number
    for block in chain[1:]:
        state = checkBlockValidity(block, parent, state)
        parent = block

    return state


def makeBlock(txns, chain):
    parentBlock = chain[-1]
    parentHash = parentBlock[u'hash']
    blockNumber = parentBlock[u'contents'][u'blockNumber'] + 1
    txnCount = len(txns)
    blockContents = {u'blockNumber': blockNumber, u'parentHash': parentHash,
                     u'txnCount': len(txns), 'txns': txns}
    blockHash = hashMe(blockContents)
    block = {u'hash': blockHash, u'contents': blockContents}

    return block