class TestFactory:
    def __init__(self):
        pass

    def create_user(self, username, password, birthday):
        pass

    def create_holding(self, ticker, cusip, morning_star_id, portfolio):
        pass

    def create_account(self, user):
        pass

    def create_portfolio(self, user, account):
        pass

    def create_transaction(self, account, holding, amount):
        pass
