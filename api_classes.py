"""
This module contains classes to organize
the responses sent by the API
"""


class Asset:
    def __init__(self, display_name="", symbol="", contracts=[]):
        self.display_name = display_name
        self.symbol = symbol
        self.contracts = contracts

    def add_contract(self, _type, subtype, min_duration, max_duration):
        self.contracts.append({"type": _type,
                               "subtype": subtype,
                               "min_duration": min_duration,
                               "max_duration": max_duration})


class Symbol:
    def __init__(self, display_name, market, symbol, symbol_type, market_display_name="",
                 exchange_is_open=True, is_trading_suspended=False):
        self.display_name = display_name
        self.exchange_is_open = exchange_is_open
        self.is_trading_suspended = is_trading_suspended
        self.market = market
        self.market_display_name = market_display_name
        self.symbol = symbol
        self.symbol_type = symbol_type


class User:
    def __init__(self, balance, country, currency, email, is_virtual, landing_company_fullname,
                 landing_company_name, login_id, scopes=[], fullname="", account_list=[]):
        self.account_list = account_list
        self.balance = balance
        self.country = country
        self.currency = currency
        self.email = email
        self.is_virtual = is_virtual
        self.landing_company_fullname = landing_company_fullname
        self.landing_company_name = landing_company_name
        self.login_id = login_id
        self. scopes = scopes
        self.fullname = fullname

    def add_account(self, currency, is_disabled, is_virtual, landing_company_name, login_id):
        account = {"currency": currency,
                   "is_disabled": is_disabled,
                   "is_virtual": is_virtual,
                   "landing_company_name": landing_company_name,
                   "login_id": login_id}
        self.account_list.append(account)

    def add_scope(self, scope):
        self.scopes.append(scope)


class History:
    def __init__(self, symbol, history={}):
        self.symbol = symbol
        self.training_prices = {}
        self.trained = False
        self.prices = {}
        self.last_prices = {}
        self.add_history(history)
        self.neural_network = None

    def add_history(self, history={}):
        for i in range(len(history["prices"])):
            if history["times"][i] not in self.last_prices.keys():
                self.last_prices[str(history["times"][i])] = history["prices"][i]

            if history["times"][i] not in self.training_prices.keys():
                self.training_prices[str(history["times"][i])] = history["prices"][i]

        while len(self.training_prices) > 10000:
            _ = self.training_prices.pop(self.last_training_price())

        if not self.trained and len(self.training_prices):
            import neural_network
            self.neural_network = neural_network.NeuralNetwork(self.training_prices)
            self.trained = True

        while len(self.last_prices) > 100:
            _ = self.last_prices.pop(self.last_price())

        # with open(f"{self.symbol}_history.txt", "w") as text_file:
        #     for key in sorted(self.prices.keys()):
        #         text_file.write(f"{key} : {self.prices[key]}\n")

    def last(self):
        return str(min(self.prices, key=int))

    def last_training_price(self):
        return str(min(self.training_prices, key=int))

    def last_price(self):
        return str(min(self.last_prices, key=int))
