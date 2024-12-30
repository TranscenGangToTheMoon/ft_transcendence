import json
import re
import time
import unittest
from threading import Thread

import httpx

from services.auth import register, create_guest
from services.user import me
from utils.generate_random import rnstr


class UnitTest(unittest.TestCase):
    def new_user(self, username=None, password=None, tests_sse: list[str] = None, still_connected=False):
        if username is None:
            username = 'user-' + rnstr(10)
        if password is None:
            password = 'password-' + rnstr(15)
        _new_user = {'username': username, 'password': password}
        token = self.assertResponse(register(_new_user['username'], password), 201)
        _new_user['token'] = token['access']
        _new_user['refresh'] = token['refresh']
        _new_user['id'] = self.assertResponse(me(_new_user), 200, get_field=True)
        self.connect_to_sse(_new_user, tests_sse, still_connected=still_connected)
        return _new_user

    def user_sse(self, tests: list[str] = None, still_connected=False):
        return self.new_user(tests_sse=tests, still_connected=still_connected)

    def guest_user(self, tests_sse: list[str] = None, still_connected=False):
        _new_user = {}
        token = self.assertResponse(create_guest(), 201)
        _new_user['token'] = token['access']
        _new_user['refresh'] = token['refresh']
        response = self.assertResponse(me(_new_user), 200)
        _new_user['id'] = response['id']
        _new_user['username'] = response['username']
        self.connect_to_sse(_new_user, tests_sse, still_connected=still_connected)
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
        self.assertEqual(responses[0].json['id'], responses[1].json['id'])
        return responses[1].json['id']

    def connect_to_sse(self, user, tests: list[str] = None, timeout=50, status_code=200, still_connected=False):
        user['thread'] = Thread(target=self._thread_connect_to_sse, args=(user, tests, timeout, status_code, still_connected))
        user['thread'].start()
        time.sleep(0.5)
        return user['thread']

    def _thread_connect_to_sse(self, user, tests, timeout, status_code, still_connected):
        if tests is None:
            user['expected_thread_result'] = 0
        else:
            user['expected_thread_result'] = len(tests)
        user['thread_result'] = 0
        user['thread_tests'] = tests
        user['thread_assertion'] = []
        timeout_count = 0

        print(f"SSE CONNECTING {user['username']}...\n", flush=True)
        with httpx.Client(verify=False) as client:
            headers = {
                'Authorization': f'Bearer {user["token"]}',
                'Content-Type': 'text/event-stream',
            }
            with client.stream('GET', 'https://localhost:4443/sse/users/', headers=headers) as response:
                self.assertEqual(status_code, response.status_code)
                if status_code == 200:
                    for line in response.iter_text():
                        if line:
                            event, data = re.findall(r'event: ([a-z0-9\-]+)\ndata: (.+)\n\n', line)[0]
                            timeout_count += 1
                            if (tests is None and timeout_count > timeout) or timeout_count > 100 or event == 'delete-user': # todo remove later
                                return
                            if event == 'ping':
                                continue
                            data = json.loads(data)

                            print(f"SSE RECEIVED {user['username']}: {data}", flush=True)
                            user['thread_assertion'].append(data['event_code'])
                            user['thread_result'] += 1
                            if (tests is not None and user['thread_result'] == len(tests)) and not still_connected:
                                return

    def assertThread(self, user):
        user['thread'].join()
        print(f"SSE DISCONNECTING {user['username']}...\n", flush=True)
        if user['thread_tests'] is None:
            user['thread_tests'] = []
        self.assertListEqual(user['thread_tests'], user['thread_assertion'])
        self.assertEqual(user['expected_thread_result'], user['thread_result'])
        time.sleep(0.5)
