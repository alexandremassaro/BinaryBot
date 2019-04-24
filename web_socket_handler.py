""" This module handles all websocket interactions """

import websocket
from websocket import create_connection
from json_handler import JsonHandler as jsh
import time
import threading


def send_receive(api_url, app_id, json_message):
    """
    This method opens a connection to the API,
    sends and receives a message
    and closes the connection
    :param api_url: URL of the API to connect
    :param app_id: APP Id to authenticate the connection
    :param json_message: Json message to send to the API
    :return: Response of the API to the message sent (Json string)
    """
    ws = create_connection(api_url + str(app_id))
    print("sending --> " + json_message)
    ws.send(json_message)
    result = ws.recv()
    ws.close()

    return result


class WebSocketHandler:

    def __init__(self, api_url, app_id, json_messages=[]):
        """
        Starts a connection to the API, if any json message is passed, sends them to the API.
        This connection is kept alive as long as the instance of this is is alive,
        whenever a new message is added to json_messages array it is sent to the API.
        If no message is available them it sends a ping to keep the connection alive
        :param api_url: URL of the API to connect
        :param app_id: APP Id to authenticate the connection
        :param json_messages: Array with Json messages to send to the API
        """
        self.apiUrl = api_url
        self.json_messages = json_messages
        self.app_id = app_id
        self.ws = websocket.WebSocketApp(api_url + str(app_id),
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.idle_time = time.time()
        self.is_closed = False
        self.responses = []

        def run_forever():
            self.ws.run_forever()
            print("Exiting run forever")

        t = threading.Thread(name="run_forever", target=run_forever)  # .start_new_thread(run, ())
        t.start()

    def on_open(self):
        def send_messages():
            while not self.is_closed:
                for message in self.json_messages:
                    self.ws.send(message)
                    # time.sleep(1)
                    self.json_messages.remove(message)
                    self.idle_time = time.time()

                if time.time() - self.idle_time >= 60:
                    self.json_messages.append(jsh.ping())

                time.sleep(1)

            print("Exiting send messages loop")

        t = threading.Thread(name="send_messages", target=send_messages)  # .start_new_thread(run, ())
        t.start()

    def on_message(self, message):
        self.responses.append(jsh.get_object(message))

    def on_error(self, error):
        print(error)

    def on_close(self):
        """
        This function runs when the connection to the websocket is closed
        """
        print(" -- CONNECTION TO BINARY OPTIONS API IS CLOSED -- ")

    def close(self):
        self.is_closed = True
        self.ws.close()
