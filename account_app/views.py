from spyne.service import ServiceBase
from spyne.application import Application
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from django.views.decorators.csrf import csrf_exempt
from spyne import Iterable, Unicode,rpc
from .complexTypes import Account as ComplexAccount
from .models import Account as ModelAccount, Client as ModelClient
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

#configure the SOAP API
application=Application(
    [AccountService,],
    tns='bank.isg.tn',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)
django_app=DjangoApplication(application)
soap_bank_app=csrf_exempt(django_app)