import unittest


class UnitTest(unittest.TestCase):

    def assertResponse(self, response, status_code, json=None):
        self.assertEqual(status_code, response.status_code)
        if json is not None:
            self.assertEqual(json, response.json)

    def assertFriendResponse(self, responses, status_code=201, json=None):
        self.assertEqual(201, responses[0].status_code)
        self.assertEqual(status_code, responses[1].status_code)
        if json is not None:
            self.assertEqual(json, responses[1].json)
