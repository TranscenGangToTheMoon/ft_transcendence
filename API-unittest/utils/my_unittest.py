import json
import time
import unittest
from threading import Thread

import httpx

from services.auth import register, create_guest
from services.user import me
from utils.generate_random import rnstr


class UnitTest(unittest.TestCase):
    def new_user(self, username=None, password=None, get_me=False, connect_sse=False, tests_sse: list[str] = None):
        if username is None:
            username = 'user-' + rnstr(10)
        if password is None:
            password = 'password-' + rnstr(15)
        _new_user = {'username': username, 'password': password}
        token = self.assertResponse(register(_new_user['username'], password), 201)
        _new_user['token'] = token['access']
        _new_user['refresh'] = token['refresh']
        if get_me:
            _new_user['id'] = self.assertResponse(me(_new_user), 200, get_field=True)
        if connect_sse:
            _new_user['thread'] = self.connect_to_sse(_new_user, tests_sse)
        return _new_user

    def user_sse(self, tests: list[str] = None):
        return self.new_user(connect_sse=True, tests_sse=tests)

    def guest_user(self, get_me=False, connect_sse=False):
        _new_user = {}
        token = self.assertResponse(create_guest(), 201)
        _new_user['token'] = token['access']
        _new_user['refresh'] = token['refresh']
        if get_me:
            response = self.assertResponse(me(_new_user), 200)
            _new_user['id'] = response['id']
            _new_user['username'] = response['username']
        if connect_sse:
            _new_user['thread'] = self.connect_to_sse(_new_user)
        return _new_user

    def assertResponse(self, response, status_code, json_assertion=None, count=None, get_field=None, get_user=False):
        self.assertEqual(status_code, response.status_code)
        if json_assertion is not None:
            self.assertEqual(json_assertion, response.json)
        if count is not None:
            self.assertEqual(count, response.json['count'])
        if get_user:
            return {'token': response.json['access']}
        if get_field is not None:
            if get_field is True:
                get_field = 'id'
            return response.json[get_field]
        return response.json

    def assertFriendResponse(self, responses, status_code=201, json_assertion=None):
        self.assertEqual(201, responses[0].status_code)
        self.assertEqual(status_code, responses[1].status_code)
        if json_assertion is not None:
            self.assertEqual(json_assertion, responses[1].json)
        return responses[1].json['id']

    def connect_to_sse(self, user, tests: list[str] = None, timeout=5, status_code=200, ignore_connection_message=True, thread=True):
        if thread:
            thread = Thread(target=self._thread_connect_to_sse, args=(user, tests, timeout, status_code, ignore_connection_message))
            thread.start()
            time.sleep(0.5)
            return thread
        else:
            self._thread_connect_to_sse(user, tests, timeout, status_code, ignore_connection_message)

    def _thread_connect_to_sse(self, user, tests, timeout, status_code, ignore_connection_message):
        i = 0
        if user is None:
            user = self.new_user()

        try:
            with httpx.Client(verify=False, timeout=timeout) as client:
                headers = {
                    'Authorization': f'Bearer {user["token"]}',
                    'Content-Type': 'text/event-stream',
                }
                with client.stream('GET', 'https://localhost:4443/sse/users/', headers=headers) as response:
                    self.assertEqual(status_code, response.status_code)
                    if status_code == 200:
                        for line in response.iter_text():
                            if line.strip():
                                data = json.loads(line.strip())
                                if ignore_connection_message and data['event_code'] == 'connection-success':
                                    continue
                                print(f"SSE RECEIVED: {data}", flush=True)
                                self.assertEqual(tests[i], data['event_code'])
                                i += 1
                                if i == len(tests):
                                    return
        except httpx.ReadTimeout:
            pass
        if tests is not None:
            self.assertEqual(i, len(tests))
