import socketio
from rework_backtrader.config import DataServerConfig
import json
from threading import Thread, Lock
import time
import math
import requests


class HFTExternalNamespace(socketio.ClientNamespace):
    def __init__(self, *args, data_list=[], name=None):
        super(HFTExternalNamespace, self).__init__(*args)
        self.data_list = data_list
        self.name = name

    def on_received_data(self, data):
        if data is not None:
            if data["data"] is None:
                print("DATA : ", data)
            else:
                if len(self.data_list):
                    self.data_list.pop(0)
                self.data_list.append(data["data"])

    def on_connect(self):
        self.emit("join_room_request", {"name": self.name})


class HFTExternalConnector:
    def __init__(self, name, data_list=[]):
        self.name = name
        self.data_list = data_list
        self.init_orderbook_snapshot()
        self.sio = socketio.Client(json=json)
        self.sio.register_namespace(HFTExternalNamespace("/data", data_list=self.data_list, name=self.name))
        print(DataServerConfig.URL)
        self.sio.connect(DataServerConfig.URL)
        self.join_room()
        self.thread_lock = Lock()
        self.thread = Thread(target=self.run)
        self.thread.start()

    def join_room(self):
        self.sio.emit("join_room_request", {"name": self.name})

    def run(self):
        self.sio.wait()

    def get_orderbook_snapshot(self):
        self.thread_lock.acquire()
        if len(self.data_list):
            data = self.data_list[0]
        else:
            data = None
        self.thread_lock.release()
        return data

    def get_OHLCV_snapshot(self, freq, fromtime=None, totime=None, nof_row=None):
        url_prefix = DataServerConfig.FLASK_URL
        url = url_prefix + "/intraday/api/list"
        params = {"symbol": self.name,
                  "freq": freq,
                  "folder": "ws_live_data"}
        if fromtime is not None:
            params.update({"from": fromtime})
        if totime is not None:
            params.update({"to": totime})
        if type(nof_row) == int:
            params.update({"nof_row": nof_row})
        data = requests.get(url, params)
        if data.status_code // 100 == 2:
            return data.json()
        return None

    def init_orderbook_snapshot(self):
        try:
            orderbook_data = self.get_OHLCV_snapshot(freq="HFT", nof_row=1)
            orderbook_data = orderbook_data[-1]
            self.data_list.append(orderbook_data)
        except Exception as e:
            print("Error at init_orderbook_snapshot : ", e)

    def stop(self):
        self.sio.disconnect()
        self.thread.join()


if __name__ == '__main__':
    data = []
    connector = HFTExternalConnector("VN30F1M", data)
    while True:
        snapshot = connector.get_orderbook_snapshot()
        print(snapshot)