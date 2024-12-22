import json
import unittest
from threading import Thread

import httpx

from utils.credentials import new_user


class UnitTest(unittest.TestCase):

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

    def connect_to_sse(self, user=None, tests: list = None, timeout=5000, status_code=200, thread=True):
        if thread:
            Thread(target=self._thread_connect_to_sse, args=(user, tests, timeout, status_code)).start()
        else:
            self._thread_connect_to_sse(user, tests, timeout, status_code)

    def _thread_connect_to_sse(self, user, tests, timeout, status_code):
        i = 0
        if user is None:
            user = new_user()

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
                                print(f"Received: {data}")
                                self.assertEqual(tests[i]['service'], data['service'])
                                self.assertEqual(tests[i]['event_code'], data['event_code'])
                                i += 1
        except httpx.ReadTimeout:
            self.assertEqual(i, len(tests))
