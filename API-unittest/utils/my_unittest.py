import unittest


class UnitTest(unittest.TestCase):

    def assertResponse(self, response, status_code, json=None, count=None, get_field=None, get_user=False):
        self.assertEqual(status_code, response.status_code)
        if json is not None:
            self.assertEqual(json, response.json)
        if count is not None:
            self.assertEqual(count, response.json['count'])
        if get_user:
            return {'token': response.json['access']}
        if get_field is not None:
            if get_field is True:
                get_field = 'id'
            return response.json[get_field]
        return response.json

    def assertFriendResponse(self, responses, status_code=201, json=None):
        self.assertEqual(201, responses[0].status_code)
        self.assertEqual(status_code, responses[1].status_code)
        if json is not None:
            self.assertEqual(json, responses[1].json)
        return responses[1].json['id']
