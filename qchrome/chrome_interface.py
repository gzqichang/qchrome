#!/usr/bin/python3

import time

import requests
import websocket

from . import json_hook as json

TIMEOUT = 1


class QChromeException(BaseException):
    pass


class AlreadyRegisteredError(QChromeException):
    pass


class WebSocketError(QChromeException):
    pass


class ProtocolError(QChromeException):
    pass


class UnknownMessageError(QChromeException):
    pass


class GenericMethod(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, attr):
        func_name = '{}.{}'.format(self.name, attr)

        def generic_function(**args):
            # 清空之前的消息
            self.parent.clear_messages()
            # 生成新的ID
            self.parent.message_counter += 1
            message_id = self.parent.message_counter
            # 调用与等待
            call_obj = {'id': message_id, 'method': func_name, 'params': args}
            self.parent.ws.send(json.dumps(call_obj))
            return self.parent.wait(message_id)

        return generic_function


class ChromeInterface(object):

    def __init__(self, host='localhost', port=9222, tab=0, timeout=None, auto_connect=True):
        self.host = host
        self.port = port
        self.ws = None
        self.tabs = None
        self.timeout = timeout if timeout else TIMEOUT
        self.message_counter = 0
        self._method_map = {}

        if auto_connect:
            self.connect(tab=tab)

    def get_tabs(self):
        response = requests.get('http://{}:{}/json'.format(self.host, self.port))
        self.tabs = json.loads(response.text)

    def connect(self, tab=0, update_tabs=True):
        if update_tabs or self.tabs is None:
            self.get_tabs()
        wsurl = self.tabs[tab]['webSocketDebuggerUrl']
        self.close()
        self.ws = websocket.create_connection(wsurl)
        self.ws.settimeout(self.timeout)

    def connect_targetID(self, targetID):
        try:
            wsurl = 'ws://{}:{}/devtools/page/{}'.format(self.host, self.port, targetID)
            self.close()
            self.ws = websocket.create_connection(wsurl)
            self.ws.settimeout(self.timeout)
        except:
            wsurl = self.tabs[0]['webSocketDebuggerUrl']
            self.ws = websocket.create_connection(wsurl)
            self.ws.settimeout(self.timeout)

    def close(self):
        if self.ws:
            self.ws.close()

    def register(self, method, func):
        if method in self._method_map:
            raise AlreadyRegisteredError(f'{method} is already registered.')
        self._method_map[method] = func

    # # Blocking
    # def wait_message(self, timeout=None):
    #     timeout = timeout if timeout is not None else self.timeout
    #     self.ws.settimeout(timeout)
    #     try:
    #         message = self.ws.recv()
    #     except:
    #         return None
    #     finally:
    #         self.ws.settimeout(self.timeout)
    #     return json.loads(message)
    #
    # # Blocking
    # def wait_event(self, event, timeout=None):
    #     timeout = timeout if timeout is not None else self.timeout
    #     start_time = time.time()
    #     messages = []
    #     matching_message = None
    #     while True:
    #         now = time.time()
    #         if now - start_time > timeout:
    #             break
    #         try:
    #             message = self.ws.recv()
    #             parsed_message = json.loads(message)
    #             messages.append(parsed_message)
    #             if 'method' in parsed_message and parsed_message['method'] == event:
    #                 matching_message = parsed_message
    #                 break
    #         except:
    #             break
    #     return (matching_message, messages)

    # # Blocking
    # def wait_result(self, result_id, timeout=None):
    #     timeout = timeout if timeout is not None else self.timeout
    #     start_time = time.time()
    #     messages = []
    #     matching_result = None
    #     while True:
    #         now = time.time()
    #         if now - start_time > timeout:
    #             break
    #         try:
    #             message = self.ws.recv()
    #             parsed_message = json.loads(message)
    #             messages.append(parsed_message)
    #             if 'result' in parsed_message and parsed_message['id'] == result_id:
    #                 matching_result = parsed_message
    #                 break
    #         except:
    #             break
    #     return (matching_result, messages)

    # # Non Blocking
    # def pop_messages(self):
    #     messages = []
    #     self.ws.settimeout(0)
    #     while True:
    #         try:
    #             message = self.ws.recv()
    #             messages.append(json.loads(message))
    #         except:
    #             break
    #     self.ws.settimeout(self.timeout)
    #     return messages

    # Non Blocking
    def clear_messages(self):
        self.ws.settimeout(0)

        while True:
            try:
                message = self.ws.recv()
            # except websocket.WebSocketTimeoutException:
            #     break
            # except websocket.WebSocketException as e:
            #     raise WebSocketError(str(e))
            except BaseException:
                break

            try:
                parsed_message = json.loads(message)
            except BaseException as e:
                raise ProtocolError(str(e))

            if 'id' in parsed_message:
                pass
            elif 'method' in parsed_message:
                method = parsed_message['method']
                if method in self._method_map:
                    func = self._method_map[method]
                    func(**(parsed_message.get('params', {})))
            else:
                raise UnknownMessageError(parsed_message)

        self.ws.settimeout(self.timeout)

    # Blocking
    def wait(self, message_id, timeout=None):
        timeout = timeout if timeout else self.timeout
        start_time = time.time()

        while True:
            now = time.time()
            if now - start_time > timeout:
                break

            try:
                message = self.ws.recv()
            except websocket.WebSocketException as e:
                raise WebSocketError(str(e))

            try:
                parsed_message = json.loads(message)
            except BaseException as e:
                raise ProtocolError(str(e))

            if 'id' in parsed_message:
                if parsed_message['id'] == message_id:
                    return parsed_message
            elif 'method' in parsed_message:
                method = parsed_message['method']
                if method in self._method_map:
                    func = self._method_map[method]
                    func(**(parsed_message.get('params', {})))
            else:
                raise UnknownMessageError(parsed_message)

        return None

    def __getattr__(self, attr):
        method = GenericMethod(attr, self)
        self.__setattr__(attr, method)
        return method
