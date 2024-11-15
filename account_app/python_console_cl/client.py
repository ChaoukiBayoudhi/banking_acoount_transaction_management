import datetime
try:
    from suds.client import Client
except ImportError:
    print('Could not import suds library')

from suds.plugin import MessagePlugin
import re

class DecimalFixPlugin(MessagePlugin):
    def received(self, context):
        # Decode bytes to string, replace Decimal patterns, and re-encode to bytes
        context.reply = context.reply.decode('utf-8')  # Decode bytes to string
        context.reply = re.sub(r"Decimal\('([\d\.]+)'\)", r"\1", context.reply)
        context.reply = context.reply.encode('utf-8')  # Re-encode back to bytes


# Initialize the bank client with the DecimalFixPlugin
"""This plugin searches for any Decimal('...') pattern in the SOAP response
and replaces it with the plain number, allowing suds to parse it as a float."""
bank_client = Client('http://127.0.0.1:8000/bank/?wsdl',plugins=[DecimalFixPlugin()])
print(bank_client)  # Print SOAP Service information

def add_accounts():
    n = int(input('Enter the number of accounts to add: '))
    for i in range(n):
        account = bank_client.factory.create('ns0:Account')
        account.rib = input('RIB = ')
        account.creationDate = datetime.datetime.now()
        account.balance = float(input('Balance = '))
        account.accountType = input('Account type (current, saving, fixed, loan) = ')

        client = bank_client.factory.create('ns0:Client')
        client.cin = input('Client CIN = ')
        client.name = input('Client name = ')
        client.familyName = input('Client family name = ')
        client.email = input('Client email = ')
        account.client = client

        response = bank_client.service.add_account(account)
        print(f"Account added: {response}")

def get_all_accounts():

    accounts = bank_client.service.get_all_accounts()
    print("List of accounts:")
    for acc in accounts:
        print(acc)

def update_account():
    rib = input("Enter the RIB of the account to update: ")
    try:
        account = bank_client.service.get_account_by_rib(rib)
        if account:
            account.balance = float(input(f"New balance for account {rib} (current: {account.balance}): "))
            account.accountType = input(f"New account type (current: {account.accountType}): ")

            response = bank_client.service.update_account(account)
            print(f"Account updated: {response}")
    except Exception as e:
        print(f"Error updating account: {e}")

def delete_account():
    rib = input("Enter the RIB of the account to delete: ")
    try:
        response = bank_client.service.delete_account(rib)
        print(f"Account deleted: {response}")
    except Exception as e:
        print(f"Error deleting account: {e}")

def get_account_by_rib():
    rib = input("Enter the RIB of the account to retrieve: ")
    try:
        account = bank_client.service.get_account_by_rib(rib)
        print("Account details:")
        print(account)
    except Exception as e:
        print(f"Error retrieving account: {e}")

def get_accounts_by_client_cin():
    cin = input("Enter the CIN of the client: ")
    try:
        accounts = bank_client.service.get_accounts_by_client_cin(cin)
        print(f"Accounts for client CIN {cin}:")
        for acc in accounts:
            print(acc)
    except Exception as e:
        print(f"Error retrieving accounts for client: {e}")

# Menu for user to select an action
while True:
    print("\nSelect an option:")
    print("1. Add accounts")
    print("2. Get all accounts")
    print("3. Update an account")
    print("4. Delete an account")
    print("5. Get account by RIB")
    print("6. Get accounts by client CIN")
    print("0. Exit")

    choice = input("Enter your choice: ")
    if choice == '1':
        add_accounts()
    elif choice == '2':
        get_all_accounts()
    elif choice == '3':
        update_account()
    elif choice == '4':
        delete_account()
    elif choice == '5':
        get_account_by_rib()
    elif choice == '6':
        get_accounts_by_client_cin()
    elif choice == '0':
        break
    else:
        print("Invalid choice. Please try again.")
