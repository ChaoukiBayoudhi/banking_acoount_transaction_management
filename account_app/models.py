from django.db import models

class Client(models.Model):
    cin=models.CharField(max_length=9,primary_key=True)
    name = models.CharField(max_length=255)
    familyName = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    def __str__(self):
        return f'cin = {self.cin}, email={self.email}'

    class Meta:
        ordering=['email']
        db_table='clients'

class AccountType(models.TextChoices):
    CURRENT = 'current', 'current'
    SAVING = 'saving', 'saving'
    FIXED = 'fixed', 'fixed'
    LOAN = 'loan', 'loan'

class Bank(models.Model):
    name = models.CharField(max_length=255,unique=True)
    address=models.CharField(max_length=255)
    creationDate=models.DateField(auto_now_add=True)
    class Meta:
        ordering=['name']
        db_table = 'banks'

class Account(models.Model):
    rib=models.CharField(max_length=30,primary_key=True)
    balance=models.DecimalField(max_digits=15,decimal_places=3)
    client=models.ForeignKey(Client, on_delete=models.SET_NULL,null=True)
    creation_date=models.DateField(auto_now_add=True)
    accountType=models.CharField(max_length=20,choices=AccountType.choices,default=AccountType.CURRENT)
    def __str__(self):
        return f'client : {self.client}, balance= {self.balance}'
    class Meta:
        db_table='accounts'
class TransactionType(models.TextChoices):
    WITHDRAW=("WTD",'withdraw transaction')
    DEPOSIT=("DEP",'deposit transaction')
    TRANSFER=('TRAN','transfer transaction')

class Transaction(models.Model):
    amount=models.DecimalField( max_digits=9, decimal_places=3)
    date=models.DateTimeField(auto_now_add=True)
    transactionType=models.CharField(max_length=20,choices=TransactionType.choices)
    account=models.ForeignKey(Account,on_delete=models.CASCADE)
    transfer_to_account=models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f'id = {self.id}; date = {self.date}'

    class Meta:
        db_table='transactions'

    def clean(self):
        if self.transactionType == TransactionType.TRANSFER and self.transfer_to_account is None :
            raise ValueError('You have to specify the RIB to transfer to.')
        if self.transactionType == TransactionType.WITHDRAW and self.amount> self.account.balance:
            raise ValueError(f"You can't withdraw more than {self.account.balance}")
    