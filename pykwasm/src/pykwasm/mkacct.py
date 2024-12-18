from web3 import Web3

def mkaddr():
    w3 = Web3()
    return w3.to_hex(w3.eth.account.create().key)

def main():
    print(mkaddr())

if __name__ == "__main__":
    main()
