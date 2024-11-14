import datetime
try:
    from suds.client import Client
except ImportError:
    print('Could not import suds library')
bank_client=Client('http://127.0.0.1:8000/bank/?wsdl')
print(bank_client) # print SOAP Service information
# add accounts
n=int(input('enter the number of accounts ='))
for i in range(n):
    account=bank_client.factory.create('ns0:Account')
    account.rib=input('RIB = ')
    account.creationDate=datetime.datetime.now()
    account.balance=float(input('balance'))
    account.accountType=input('type = ')
    client=bank_client.factory.create('ns0:Client')
    client.cin=input('CIN = ')
    client.name=input('name = ')
    client.familyName=input('family name = ')
    client.email=input('email = ')
    account.client=client
    print(bank_client.service.add_account(account))
accounts=bank_client.service.get_all_accounts()
print("list of accounts :")
print(accounts)