from helpers.test_factory import TestFactory


def run():
    quovo = TestFactory.get_quovo_source()
    user = TestFactory.create_user(quovo, "test21@test.com", "Gibson973675123!", "02/13/1995")
    account = TestFactory.create_account(quovo, user)
    portfolios = TestFactory.create_portfolios(quovo, user)
    transactions = TestFactory.create_transactions(quovo, user)

