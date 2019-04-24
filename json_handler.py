"""
This module deals with the creation and decoding of
all json messages for communicating with the API
"""

import json


class JsonHandler:
    """This class handles all json formatting for API communication"""

    @staticmethod
    def get_object(json_string):
        """
        Returns an object according to the json string
        :param json_string: String returned from the API
        :return: Object containing all data returned from the API
        """

        return json.loads(json_string)

    @staticmethod
    def active_symbols():
        """
        Retrieve a list of all active symbols
        (underlying markets upon which contracts
        are available for trading).
        :return: Json formatted string
        """
        return json.dumps({"active_symbols": "full"})

    @staticmethod
    def asset_index():
        """
        Retrieve a list of all available underlyings
        and the corresponding contract types and
        duration boundaries. If the user is logged in,
        only the assets available for that user's
        landing company will be returned.
        :return:  Json formatted string
        """

        return json.dumps({"asset_index": 1})

    @staticmethod
    def authorize(usr_token):
        """
        Authorize current WebSocket session to act on
        behalf of the owner of a given token. Must
        precede request thats needs to access client
        account, for example purchasing and selling
        contracts or viewing portfolio.
        :param usr_token: Authentication token of the user to act on behalf of
        :return: Json formatted string
        """

        return json.dumps({"authorize": usr_token})

    @staticmethod
    def ping():
        """
        Ping the server to keep connection alive
        :return: Json formatted string
        """

        return json.dumps({"ping": 1})

    @staticmethod
    def tick_stream(symbols):
        """
        Initiate a continuous stream of spot price
        updates for a given symbol.
        :param symbols: Array of symbols to subscribe to (obtained from the active_symbols call)
        :return: Json formatted string
        """

        return json.dumps({"ticks": symbols})

    @staticmethod
    def tick_history(symbol, count=5000, subscribe=False, end="latest"):
        """
        Get historic tick data for a given symbol.
        :param symbol: Short symbol name (obtained from the active_symbols call)
        :param count: An upper limit on ticks to receive. Default 5000
        :param subscribe: [Optional] True - to send updates whenever a new tick is received.
        :return:
        """
        if subscribe:
            return json.dumps({"ticks_history": symbol,
                               "end": end,
                               "start": 1,
                               "style": "ticks",
                               "adjust_start_time": 1,
                               "count": count,
                               "subscribe": 1})
        else:
            return json.dumps({"ticks_history": symbol,
                               "end": end,
                               "start": 1,
                               "style": "ticks",
                               "adjust_start_time": 1,
                               "count": count})
