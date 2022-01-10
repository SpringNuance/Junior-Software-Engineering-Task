import requests, jwt
import os
import uuid
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone, timedelta

def API():
    load_dotenv()

    # Private key and kid obtained from the application, sotred in environment files
    RSA256_PRIVATE_KEY = os.getenv('RSA256_PRIVATE_KEY')
    KID = os.getenv('KID')
    currentStamp = int(datetime.now().timestamp())

    payload = {
        "iss": "enablebanking.com",
        "aud": "api.tilisy.com",
        "iat": currentStamp, #(timestamp when the token is being created) // Convert date to Numeric Date
        "exp": currentStamp + 86400 #(timestamp when the token expires)
    }

    # Generated encoded JWT token from private key and kid
    token = jwt.encode(payload, RSA256_PRIVATE_KEY, algorithm="RS256", headers = {'kid': f"{KID}"})
    print("\nThe encoded JWT token is \n\n" + token + "\n")

    # The base URL for banking API
    url = "https://api.tilisy.com"

    # The authorization headers, sent in every request to api addresses
    authHeaders = { "Authorization" : f"Bearer {token}"}
    
    # application information
    response = requests.get(f"{url}/application", headers=authHeaders)
    appDetails = response.json()
    print("The application details")
    for detail in appDetails:
        print(detail + ": ", end="")
        print(appDetails[detail])

    # Getting the bank details 
    response = requests.get(f"{url}/aspsps", headers=authHeaders)
    bankDetails = response.json()["aspsps"]
    
    print("\n ----- Bank details -----")
    for bank in bankDetails:
        print(bank["name"] + ": " + bank["country"])

    print("The available banks above are in the form of <name>: <country ID>")
    print("Please input your bank's name and country ID")
    
    # Inputting the bank name and country
    bank = input("Enter your bank's name: ")
    country = input("Enter your bank's country ID: ")

    # JSON body sent in POST request to /auth
    body = {
        "access": {
            "valid_until": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
            # Change date to the future, possibly one month ahead of your current time
        },
        "aspsp": {
            "country": country,
            "name": bank
        }, # Account Servicing Payment Service Providers
        "state": str(uuid.uuid4()),
        "redirect_url": appDetails["redirect_urls"][0],
    }

    # Authentication Post request
    response = requests.post(f"{url}/auth", json=body, headers=authHeaders)
    authenticationUrl = response.json()["url"]
    print(f'To authenticate your bank account, paste into your browser: {authenticationUrl}')
 
    
    # User session can be created from captured code parameter in the redirected link from authorization request
    redirectUrl = input("After authentication, please paste into the console the URL that you were redirected to: ")
    # The code in the redirected link 
    capturedCode = parse_qs(urlparse(redirectUrl).query)["code"][0]
    print("\nThe code in the authenticate redirected link is\n" + capturedCode)
    response = requests.post(f"{url}/sessions", json= {"code": capturedCode}, headers=authHeaders)
    
    # Session details are obtained from the response
    session = response.json()

    # Find the retrieved bank account from IBAN number
    
    IBAN = input("\nPlease input your IBAN number: ")
    retrievedAccount = list(filter(lambda account : account["account_id"]["iban"] == IBAN, session["accounts"]))[0]

    # Account details
    print("\n-----Your account information-----\n")
    for detail in retrievedAccount:
        print(detail + ": ", end="")
        print(retrievedAccount[detail])

    # Retrieving account balances
    uid = retrievedAccount["uid"]
    response = requests.get(f"{url}/accounts/{uid}/balances", headers=authHeaders)
    print("\n-----Your bank balances-----\n")
    balances = response.json()
    for balance in balances['balances']:
        for detail in balance:
            if (detail == "balance_amount"):
                print(detail + ": ", end="")
                print(balance[detail]["amount"] + " " + balance[detail]["amount"])
            else:    
                print(detail + ": ", end="")
                print(balance[detail])
        print('\n')
    
    # Transaction details within the last 30 days
    input("Press Enter to continue to see your transactions in the last 30 days...")
    
    chosenKeys = ["credit_debit_indicator","reference_number","transaction_amount","transaction_date"]
    print("\n-----Transactions in the last 30 days-----\n:")
    numTrans, max, credit, debit = 0
    query = {
        "date_from": (datetime.now(timezone.utc) - timedelta(days=30)).date().isoformat(),
    }
    continuationKey = None
    while True:
        # In each get request, continuation key is checked with the date_from property
        if continuationKey:
            query["continuation_key"] = continuationKey
        response = requests.get(f"{url}/accounts/{uid}/transactions", params=query, headers=authHeaders)
        # data is an object that has 2 properties continuation key and transactions object.   
        data = response.json()
        transactions = data["transactions"]
        for transaction in transactions:
            for detail in transaction:
                if detail in chosenKeys:
                    print(detail + ": ", end="")
                    print(transaction[detail])
            amount = float(transaction['transaction_amount']['amount']) # Transaction amount
            if (transaction["credit_debit_indicator"] == 'CRDT'):
                credit += amount # Find total credit transactions
            else:
                debit += amount # Find total dedit transactions
            if (amount > max):
                max = amount # Find maximum transaction
            print("")
            numTrans += 1 # Find total transaction
        continuationKey = data.get("continuation_key")
        # If surpassing the date_from, the continuation_key would become undefined/None to break the loop
        if not continuationKey:
            break

    # Short summary of the transactions for the last 30 days
    print("\n-----Transaction Summary in 30 Days-----\n")
    print("Number of transactions: " + str(numTrans))
    print("Transaction with maximum value: " + str(max) + " euros")
    print("Total credit transactions: " + str(credit) + " euros")
    print("Total debit transactions: " + str(debit) + " euros")

    # Enable Banking only operates in Europe, so it is assumed that the currency is Euro
    

API() # run the application


