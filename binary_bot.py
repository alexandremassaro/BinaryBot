from web_socket_handler import WebSocketHandler
from json_handler import JsonHandler
import threading
import api_classes
import time

APP_ID = 16155
USR_TOKEN = "TViTFwxHvEN5uAE"
API_URL = "wss://ws.binaryws.com/websockets/v3?app_id="
API_PORT = 443


class Binary:

    def __init__(self):
        """
        This method initializes all variables and starts
        all functions and threads needed in order for the
        application to work properly
        """

        self.is_closed = False
        self.ws_handler = None
        self.user = None
        self.assets = []
        self.symbols = []
        self.available_symbols = []
        self.symbols_history = []
        self.authenticate()
        self.start_ticks()
        self.start_responses()

    def authenticate(self):
        """
        Opens the connection to the API and authenticates the user
        :return: Nothing
        """

        json_messages = [JsonHandler.authorize(USR_TOKEN)]

        self.ws_handler = WebSocketHandler(API_URL, APP_ID, json_messages)

    def start_ticks(self):
        """
        This method must get all historical values of all
        available indices and mounts a dictionary with 10,000
        values to train the Neural Network. It also starts
        listening to the ticks and updates the dictionary
        with new values

        :return: Nothing
        """

        self.ws_handler.json_messages.append(JsonHandler.asset_index())
        self.ws_handler.json_messages.append(JsonHandler.active_symbols())
        self.check_available_symbols()

    def start_responses(self):
        """
        Starts a thread that runs through the responses
        sent by the API and starts the decoding process
        :return: Nothing
        """

        def responses():
            while not self.is_closed:
                if self.ws_handler is not None:
                    for response in self.ws_handler.responses:
                        self.decode_response(response)
                        self.ws_handler.responses.remove(response)

            print("Exiting responses loop")

        t = threading.Thread(name="responses", target=responses)
        t.start()

    def update_assets(self, assets):
        for item in assets:
            for contract in item[2]:
                if (contract[0].lower() == "callput" and
                        contract[1].lower() == "rise/fall" and
                        contract[2].lower() == "5t"):
                    self.assets.append(api_classes.Asset(item[1], item[0]))
                    self.assets[-1].add_contract(contract[0], contract[1], contract[2], contract[3])

    def update_symbols(self, symbols):
        for item in symbols:
            if (item["exchange_is_open"] == 1 and
                    item["is_trading_suspended"] == 0):
                self.symbols.append(api_classes.Symbol(item["display_name"],
                                                       item["market"],
                                                       item["symbol"],
                                                       item["symbol_type"],
                                                       item["market_display_name"]))

    def check_available_symbols(self):
        def check_symbols_available():
            print(" -- CHECKING FOR AVAILABLE SYMBOLS --")
            while len(self.symbols) == 0 or len(self.assets) == 0:
                time.sleep(1)
            for symbol in self.symbols:
                for asset in self.assets:
                    if symbol.symbol == asset.symbol and symbol not in self.available_symbols:
                        self.available_symbols.append(symbol)

            for symbol in self.available_symbols:
                self.ws_handler.json_messages.append(JsonHandler.tick_history(symbol=symbol.symbol))
                self.ws_handler.json_messages.append(JsonHandler.tick_stream(symbols=symbol.symbol))

            self.start_console()

        t = threading.Thread(target=check_symbols_available)
        t.start()

    def decode_response(self, response):
        """
        Gives appropriate treatment to the response passed
        as parameter, depending on it's type
        :param response: The response sent by the API
        :return: Nothing
        """
        for key, value in response.items():
            if key == "asset_index":
                self.update_assets(value)

            elif key == "active_symbols":
                self.update_symbols(value)

            elif key == "history":
                self.get_history(response["echo_req"]["ticks_history"], value)

            elif key == "tick":
                self.update_tick(value)

    def update_tick(self, tick):
        history = {"prices": [tick["quote"]], "times": [tick["epoch"]]}
        self.get_history(tick["symbol"], history)

    def get_history(self, symbol, history):
        found = None
        for symbol_history in self.symbols_history:
            if symbol_history.symbol == symbol:
                found = symbol_history
                break

        if found is not None:
            found.add_history(history)
            if len(found.training_prices) < 10000:
                self.ws_handler.json_messages.append(JsonHandler.tick_history(symbol=symbol,
                                                                              # count=5000,
                                                                              end=found.last()))

        else:
            new_history = api_classes.History(symbol, history)
            self.symbols_history.append(new_history)
            self.ws_handler.json_messages.append(JsonHandler.tick_history(symbol=symbol,
                                                                          # count=10,
                                                                          end=new_history.last()))

    def start_console(self):
        print(" -- Welcome to the Binary Options Bot -- ")

        def console():
            while True:
                usr_input = input("BinaryBot -> ")
                print(self.decode_input(usr_input))
                if self.is_closed:
                    print("Exiting console")
                    break

            print("Closing application")
            quit()

        t = threading.Thread(target=console)
        t.start()

    def decode_input(self, usr_input):
        if usr_input == "exit":
            self.is_closed = True
            print("Closing connection to the API")
            self.ws_handler.close()
            del self.ws_handler
            return "Bye!"
        else:
            return "Unknown command"


if __name__ == "__main__":
    binary = Binary()

