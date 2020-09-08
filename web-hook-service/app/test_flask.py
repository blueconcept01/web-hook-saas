import unittest
from main import app
import time

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_post_web_hook(self):
        web_hook_data = {'headers': [], 'request_type': 'GET', 'params': {}, 'data': [], 'url': 'https://www.google.com/'}
        rv = self.app.post('/post_web_hook', data=web_hook_data)
        hook_id = rv.get_json()["id"]
        self.assertEqual(len(hook_id), len("bcbb78c3-a41c-4156-bb25-c68b3d22b945"))
        
        rv = self.app.post('/get_hook_status', data={'id': hook_id})
        
        expected_data = {'id': hook_id, 'request_payload': {'id': hook_id, 'params': '', 'request_type': 'GET', 'retry_count': 3, 'status': 'attempting', 'try_count': 0, 'url': 'https://www.google.com/'}}
        
        self.assertEqual(expected_data, rv.get_json())
        
        expected_success = {'id': hook_id, 'request_payload': {'id': hook_id, 'params': '', 'request_type': 'GET', 'retry_count': 3, 'status': 'sent', 'try_count': 1, 'url': 'https://www.google.com/'}}
        
        time.sleep(8)
        
        self.assertEqual(self.app.post('/get_hook_status', data={'id': hook_id}).get_json(), expected_success)

if __name__ == '__main__':
    unittest.main()
