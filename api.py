import requests, jwt
import os
from dotenv import load_dotenv
from pprint import pprint
from urllib.parse import urlparse, parse_qs
from datetime import datetime

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

    # The authorization headers, sent in every request to any api addresses
    authHeaders = { "Authorization" : f"Bearer {token}"}
    
    # application information
    response = requests.get(f"{url}/application", headers=authHeaders)
    appDetails = response.json()
    print("The application details")
    pprint(appDetails)

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
            "valid_until": "2022-02-01T00:00:00Z" # Change date to the future
        },
        "aspsp": {
            "country": country,
            "name": bank
        }, # Account Servicing Payment Service Providers
        "state": "3a57e2d3-2e0c-4336-af9b-7fa94f0606a3",
        "redirect_url": appDetails["redirect_urls"][0],
    }

    # Authentication Post request
    response = requests.post(f"{url}/auth", json=body, headers=authHeaders)
    pprint(response.json())
    authenticationUrl = response.json()["url"]
    print(f'To authenticate your bank account, paste into your browser: {authenticationUrl}')
 
    
    # Reading auth code and creating user session
    redirected_url = input("Please paste into the console the URL that you were redirected to: ")
    # The code 
    print(parse_qs(urlparse(redirected_url).query))
    code = parse_qs(urlparse(redirected_url).query)["code"][0]
    print(code)
    response = requests.post(f"{url}/sessions", json= {"code": code}, headers=authHeaders)
    print("Information of the session")
    session = response.content
    pprint(session)


API() # run the application


