import json
import re
import responses
from tornado.testing import AsyncHTTPTestCase

from xdegrees.app import Application


class ApiTestCase(AsyncHTTPTestCase):

    def get_app(self):
        return Application('http://xdegrees.com/separations', 10, debug=False)

    def test_mainhandler(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertIsNotNone(response.body)

    def test_versionhandler(self):
        response = self.fetch('/version')
        self.assertEqual(response.code, 200)
        print(response.body)

        self.assertIsNotNone(response.body)
        self.assertTrue('version' in json.loads(response.body.decode('utf-8')))

    @responses.activate
    def test_separationssearchhandler_200(self):
        url_re = re.compile(r'http://xdegrees.com/separations.*')
        responses.add(**{
            'method': responses.GET,
            'url': url_re,
            'json': [
                {
                    'is_historical': False,
                    'type': 'person_location',
                    'connections': [
                        'Person Lastname',
                        '1234 1st Ave S, Seattle WA 90210'
                    ]
                },
                {
                    'is_historical': False,
                    'type': 'location_person',
                    'connections': [
                        '1234 1st Ave S, Seattle WA 90210'
                        'Another Person'
                    ]
                }
            ],
            'status': 200,
            'content_type': 'application/json'
        })

        # the url_re above captures everything, so the query string doesn't actually matter
        from_params = 'from_name=Person%20Lastname&from_city=Seattle&from_state=WA'
        to_params = 'to_name=Another%20Person&to_city=Seattle&to_state=WA'
        query_string = '{frm}&{to}'.format(frm=from_params, to=to_params)
        path = '/separations?{query}'.format(query=query_string)

        response = self.fetch(path)
        self.assertEqual(response.code, 200)
        self.assertIsNotNone(response.body)
        self.assertTrue('results' in json.loads(response.body.decode('utf-8')))

    @responses.activate
    def test_separationssearchhandler_422(self):
        url_re = re.compile(r'http://xdegrees.com/separations.*')
        responses.add(**{
            'method': responses.GET,
            'url': url_re,
            'json': {
                'status': 'input_errors',
                'from_errors': [],
                'to_errors': [
                    'Invalid Input Address'
                ],
                'path': None
            },
            'status': 422,
            'content_type': 'application/json'
        })

        # the url_re above captures everything, so the query string doesn't actually matter
        from_params = 'from_name=Person%20Lastname&from_city=Seattle&from_state=WA'
        to_params = 'to_name=Another%20Person&to_city=Seattle&to_state=ZZ'
        query_string = '{frm}&{to}'.format(frm=from_params, to=to_params)
        path = '/separations?{query}'.format(query=query_string)

        response = self.fetch(path)
        self.assertEqual(response.code, 422)
        self.assertIsNotNone(response.body)

        body = json.loads(response.body.decode('utf-8'))
        self.assertTrue('status' in body)
        self.assertEqual('input_errors', body['status'])
