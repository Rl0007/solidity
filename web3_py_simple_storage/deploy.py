from itertools import chain
import json
from web3 import Web3
import os
from solcx import compile_standard, install_solc
install_solc("0.6.0")
from dotenv import load_dotenv
load_dotenv()

with open("./SimpleStorage.sol","r") as file:
    simple_storage_file = file.read()


compiled_sol = compile_standard(
    {"language":"Solidity",
    "sources": {
        "SimpleStorage.sol":{"content": simple_storage_file} },
        "settings":{
            "outputSelection":{
                "*":{"*":["abi","metadata","evm.bytecode","evm.sourceMap"]}}},

    },
        solc_version="0.6.0"
)
with open("compiled_code.json","w")as file:
    json.dump(compiled_sol,file)

bytecode =compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
# print(abi)
# for connection to ganache
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
chain_id = w3.eth.chain_id
public_add ='0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
private_add = os.getenv("private_add")

# create contract in python
SimpleStorage = w3.eth.contract(abi=abi,bytecode=bytecode)
# get latest trancsaction
nonce = w3.eth.getTransactionCount(public_add)
print(nonce)
# build sign and send a transcation
transaction = SimpleStorage.constructor().buildTransaction({"gasPrice": w3.eth.gas_price,"chainId":chain_id,"from":public_add,"nonce":nonce})
# print("transaction")
# print(private_add)
# # print(transaction)
signed_txn = w3.eth.account.sign_transaction(transaction,private_key=private_add)
# send signed txn
txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

# working with contract
# contract address
# contaract abi
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print("helo")
print(simple_storage.functions.retrieve().call())
store_txn = simple_storage.functions.store(15).buildTransaction({
"gasPrice": w3.eth.gas_price,"chainId":chain_id,"from":public_add,"nonce":nonce+1
})
signed_store_txn = w3.eth.account.sign_transaction(store_txn,private_key=private_add)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print(simple_storage.functions.retrieve().call())
