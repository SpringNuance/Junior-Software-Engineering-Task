# Junior-Software-Engineering-Task
Instructions on how to run the program:
The application shall integrate with Tilisy API (https://api.tilisy.com/) and use it for initiating the user
authentication and data retrieval. Documentation for the application is available at
https://enablebanking.com/docs/tilisy/latest/. You can use the API’s sandbox for simulating
authentication flow and getting sample data. Nordea and S-Pankki provide good sample data.
In order to use the API you would need to sign up for the Enable Banking Control Panel (simply go
to https://enablebanking.com/sign-in/ and enter your email where you would get a one time
authentication link) and register a new application (when signed in, go to
https://enablebanking.com/cp/applications and fill in the app registration form). When your app is
registered, you will get the private RSA key for the application. You need to use the RSA private
key for signing JWTs used for authorisation of the API calls made from your application. The format
of the JWT is described in the documentation
https://enablebanking.com/docs/tilisy/latest/#jwt-format-and-signature.

Install python on your computer, open cmd and install pip with command
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py.
After that, use pip to install the necessary libraries to run the application:
pip install requests, jwt, dotenv, datetime

Download this project file, and create a file called .env at the root of the project, with 2 properties:
RSA256_PRIVATE_KEY ="-----BEGIN PRIVATE KEY-----<private_key>-----END PRIVATE KEY-----"
KID="application-id"

The private key and kid can be obtained from the instructions in the links above
Run the program. It will generate a list of banks. 
Please enter your name bank and countryID accurately like what is listed in the console. Otherwise it wouldn't work
After than, copy the generated authentication link and run it on the browser. You will be redirected to your registered redirect URL.
Copy that redirected URL and paste it into the console as requested

After authentication succeeds, you will be asked to input your bank IBAN number. 
From this onwards, you can check your bank details, balances and your transactions in the last 30 days and your transaction summary

Happy sending APIs! 


 
