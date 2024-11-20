from spyne import ComplexModel,Integer,Unicode, Double,Date
class Client(ComplexModel):
    cin = Integer
    name=Unicode
    familyName=Unicode
    email=Unicode

class Account(ComplexModel):
    rib=Unicode
    client=Client
    balance=Double
    accountType=Unicode
    creationDate=Date

class Transaction(ComplexModel):
    id=Integer
    TransactionType=Unicode
    account=Account
    transactionDate=Date
    amount=Double
    description=Unicode
    transfer_to_acount=Unicode