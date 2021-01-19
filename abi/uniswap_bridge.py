from abi.basicABI import BasicABI

abi_dict = [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [],
      "name": "_active",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "stateMutability": "payable",
      "type": "receive",
      "payable": True
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "tokenAmountIn",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "minAmountOut",
          "type": "uint256"
        },
        {
          "internalType": "address[3]",
          "name": "tokenPaths",
          "type": "address[3]"
        }
      ],
      "name": "swap",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "tokenOutAmount",
          "type": "uint256"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "executor",
          "type": "address"
        },
        {
          "internalType": "bool",
          "name": "active",
          "type": "bool"
        }
      ],
      "name": "setExecutor",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "withdrawEth",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "tokenAddress",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "amount",
          "type": "uint256"
        }
      ],
      "name": "withdrawToken",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "toggleActive",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "fake",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]

abi = BasicABI(abi_dict)

