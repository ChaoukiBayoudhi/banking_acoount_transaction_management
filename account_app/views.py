from spyne.service import ServiceBase
from spyne.application import Application
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from django.views.decorators.csrf import csrf_exempt
from spyne import Iterable, Unicode,rpc,Double
from .complexTypes import Account as ComplexAccount, Client as  ComplexClient
from .models import Account as ModelAccount, Client as ModelClient

from django.core.exceptions import ObjectDoesNotExist
class AccountService(ServiceBase):
    @rpc(ComplexAccount, _returns=Unicode)
    def add_account(self, account: ComplexAccount) -> str:
    # Check if an account with the given RIB already exists
        if ModelAccount.objects.filter(pk=account.rib).exists():
            return "An account with the same RIB already exists"

        try:
            # Check if a client with the given CIN exists
            clt = ModelClient.objects.get(cin=account.client.cin)
        except ModelClient.DoesNotExist:
            # If the client does not exist, create a new one
            clt = ModelClient(
                cin=account.client.cin,
                name=account.client.name,
                familyName=account.client.familyName,
                email=account.client.email
            )
            clt.save()

        # Create and save the new account
        acc = ModelAccount(
            rib=account.rib,
            balance=account.balance,
            creation_date=account.creationDate,
            client=clt,
            accountType=account.accountType
        )
        acc.save()
        return f"The account with RIB {acc.rib} has been created"
    @rpc(_returns=Iterable(ComplexAccount))
    def get_all_accounts(self)->Iterable:
        accounts=ModelAccount.objects.all()
        l=[]
        for account in accounts:
            acc=ComplexAccount(
                rib=account.rib,
                creationDate=account.creation_date,
                balance=account.balance,
                accountType=account.accountType,
            )
            l.append(acc)
        return l
    # Get Account by RIB
    @rpc(Unicode, _returns=ComplexAccount)
    def get_account_by_rib(self, rib: str) -> ComplexAccount:
        try:
            acc = ModelAccount.objects.get(pk=rib)
            return ComplexAccount(
                rib=acc.rib,
                balance=acc.balance,
                creationDate=acc.creation_date,
                accountType=acc.accountType,
                client=ComplexClient(
                    cin=acc.client.cin,
                    name=acc.client.name,
                    familyName=acc.client.familyName,
                    email=acc.client.email,
                )
            )
        except ModelAccount.DoesNotExist:
            raise ObjectDoesNotExist("Account does not exist.")

    # Get Accounts by Client CIN
    @rpc(Unicode, _returns=Iterable(ComplexAccount))
    def get_accounts_by_client_cin(self, cin: str) -> list[ComplexAccount]:
        try:
            client = ModelClient.objects.get(pk=cin)
            accounts = ModelAccount.objects.filter(client=client)

            return [
                ComplexAccount(
                    rib=acc.rib,
                    balance=Double(acc.balance),
                    creationDate=acc.creation_date,
                    accountType=acc.accountType,
                    client=ComplexClient(
                        cin=client.cin,
                        name=client.name,
                        familyName=client.familyName,
                        email=client.email,
                    )
                )
                for acc in accounts
            ]
        except ModelClient.DoesNotExist:
            raise ObjectDoesNotExist("Client does not exist or has no accounts.")


# Update Account
    @rpc(ComplexAccount, _returns=Unicode)
    def update_account(self, account: ComplexAccount) -> str:
        try:
            acc = ModelAccount.objects.get(pk=account.rib)
            acc.balance = account.balance
            acc.accountType = account.type
            acc.save()
            return f"The account with RIB {acc.rib} has been updated"
        except ModelAccount.DoesNotExist:
            raise ObjectDoesNotExist("Account does not exist.")

    # Delete Account
    @rpc(Unicode, _returns=Unicode)
    def delete_account(self, rib: str) -> str:
        try:
            acc = ModelAccount.objects.get(pk=rib)
            client = acc.client  # Reference to the account's client

            # Delete the account
            acc.delete()

            # Check if client has other accounts
            if client and not ModelAccount.objects.filter(client=client).exists():
                client.delete()  # Delete client if no other accounts are linked

            return f"The account with RIB {rib} has been deleted."
        except ModelAccount.DoesNotExist:
            raise ObjectDoesNotExist("Account does not exist.")


#configure the SOAP API
application=Application(
    [AccountService,],
    tns='bank.isg.tn',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)
django_app=DjangoApplication(application)
soap_bank_app=csrf_exempt(django_app)