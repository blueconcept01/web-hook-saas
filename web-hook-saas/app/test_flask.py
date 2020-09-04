import unittest
from main import app

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_post_web_hook(self):
        web_hook_data = {'headers': [], 'request_type': '', 'POST_body': {}, 'URL_params': []}
        rv = self.app.post('/post_web_hook', data=web_hook_data)
        
        self.assertEqual(rv.get_json(), {"hook_id":0})
        

if __name__ == '__main__':
    unittest.main()