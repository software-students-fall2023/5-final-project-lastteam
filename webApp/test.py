import bcrypt
from flask import template_rendered, session
from contextlib import contextmanager
import unittest
from unittest.mock import patch
from app import app, is_authenticated, get_poker_news
from bson.objectid import ObjectId


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class TestIsAuthenticated(unittest.TestCase):

    @patch('app.session', {'user_id': 123})
    def test_authenticated_with_user_id(self):
        self.assertTrue(is_authenticated(), "is_authenticated should return True when 'user_id' is in session")

    @patch('app.session', {})
    def test_not_authenticated_without_user_id(self):
        self.assertFalse(is_authenticated(), "is_authenticated should return False when 'user_id' is not in session")


# Test class for Flask routes
class TestFlaskRoutes(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_home_authenticated_user(self):
        with patch('app.is_authenticated', return_value=True):
            with patch('app.session', {'user_id': 123, 'username': 'testuser'}):
                with captured_templates(app) as templates:
                    response = self.client.get('/')
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(len(templates) == 1)
                    self.assertIn('pokerMain.html', templates[0][0].name)
                    self.assertIn('username', templates[0][1])
                    self.assertEqual(templates[0][1]['username'], 'testuser')

    def test_poker_main_authenticated_with_news(self):
        with patch('app.is_authenticated', return_value=True), \
                patch('app.session', {'username': 'testuser'}), \
                patch('app.get_poker_news', return_value=[{'title': 'News 1'}, {'title': 'News 2'}]):
            with captured_templates(app) as templates:
                response = self.client.get('/pokerMain')
                self.assertEqual(response.status_code, 200)
                self.assertIn('pokerMain.html', templates[0][0].name)
                self.assertIn('username', templates[0][1])
                self.assertEqual(templates[0][1]['username'], 'testuser')
                self.assertIn('newsItems', templates[0][1])
                self.assertEqual(len(templates[0][1]['newsItems']), 2)

    def test_poker_main_authenticated_no_news(self):
        with patch('app.is_authenticated', return_value=True), \
                patch('app.session', {'username': 'testuser'}), \
                patch('app.get_poker_news', side_effect=Exception('Error')):
            with captured_templates(app) as templates:
                response = self.client.get('/pokerMain')
                self.assertEqual(response.status_code, 200)
                self.assertIn('pokerMain.html', templates[0][0].name)
                self.assertIn('username', templates[0][1])
                self.assertEqual(templates[0][1]['username'], 'testuser')
                self.assertIn('error', templates[0][1])
                self.assertEqual(templates[0][1]['error'], 'Error fetching poker news.')

    def test_login_page_get_request(self):
        with patch('app.is_authenticated', return_value=False):
            response = self.client.get('/login')
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Login" in response.get_data(as_text=True))  # Check for login page content

    def test_login_post_request_failed(self):
        with patch('app.is_authenticated', return_value=False), \
                patch('app.poker_users.find_one', return_value=None):
            response = self.client.post('/login', data={'username': 'wronguser', 'password': 'wrongpassword'})
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Invalid username or password!" in response.get_data(as_text=True))

    def test_login_post_request_successful(self):
        with patch('app.is_authenticated', return_value=False), \
                patch('app.poker_users.find_one', return_value={'_id': '123', 'username': 'testuser',
                                                                'password': bcrypt.hashpw(b'password',
                                                                                          bcrypt.gensalt()),
                                                                'button_press_count': 0}), \
                patch('app.bcrypt.checkpw', return_value=True):
            response = self.client.post('/login', data={'username': 'testuser', 'password': 'password'},
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            # Access session after the response
            with self.client as c:
                response = c.get('/')  # or any route that will trigger session access
                self.assertIn('user_id', session)
                self.assertEqual(session['username'], 'testuser')

    def test_register_page_get_request(self):
        with patch('app.is_authenticated', return_value=False):
            response = self.client.get('/register')
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Register" in response.get_data(as_text=True))  # Check for register page content

    def test_register_post_request_existing_user(self):
        with patch('app.is_authenticated', return_value=False), \
                patch('app.poker_users.find_one', return_value={'username': 'existinguser'}):
            response = self.client.post('/register', data={'username': 'existinguser', 'password': 'password'})
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Username already exists!" in response.get_data(as_text=True))

    def test_register_post_request_successful(self):
        with patch('app.is_authenticated', return_value=False), \
                patch('app.poker_users.find_one',
                      side_effect=[None, {'_id': '123', 'username': 'newuser', 'button_press_count': 0}]), \
                patch('app.poker_users.insert_one'):
            response = self.client.post('/register', data={'username': 'newuser', 'password': 'password'},
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            with self.client as c:
                response = c.get('/pokerMain')  # or any other route to check session
                self.assertIn('user_id', session)
                self.assertEqual(session['username'], 'newuser')

    def test_logout(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '123'
                sess['username'] = 'testuser'
                sess['button_press_count'] = 0

            response = c.get('/logout', follow_redirects=True)

            self.assertEqual(response.status_code, 200)

            with c.session_transaction() as sess:
                self.assertNotIn('user_id', sess)
                self.assertNotIn('username', sess)
                self.assertNotIn('button_press_count', sess)

            self.assertTrue("Login" in response.get_data(as_text=True))

    def test_get_button_press_count_authenticated(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '123'
                sess['button_press_count'] = 5

            response = c.get('/getButtonPressCount')
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertEqual(data['count'], 5)

    def test_get_button_press_count_unauthenticated(self):
        with patch('app.is_authenticated', return_value=False):
            response = self.client.get('/getButtonPressCount', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Login" in response.get_data(as_text=True))

    def test_my_sessions_unauthenticated(self):
        with patch('app.is_authenticated', return_value=False):
            response = self.client.get('/my-sessions', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Login" in response.get_data(as_text=True))

    def test_create_session_unauthenticated(self):
        with patch('app.is_authenticated', return_value=False):
            response = self.client.get('/create-session', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Login" in response.get_data(as_text=True))

    def test_create_session_page_get_request(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '123'
                sess['username'] = 'testuser'

            response = c.get('/create-session')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                "Create Session" in response.get_data(as_text=True))  # Check for create session page content

    def test_view_sessions_unauthenticated(self):
        with patch('app.is_authenticated', return_value=False):
            response = self.client.get('/view-sessions', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Login" in response.get_data(as_text=True))  # Adjust according to your login page content

    def test_delete_session_unauthenticated(self):
        test_session_id = '507f1f77bcf86cd799439011'
        with patch('app.is_authenticated', return_value=False):
            response = self.client.post(f'/delete-session/{test_session_id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Login" in response.get_data(as_text=True))

    def test_session_data_unauthenticated(self):
        with patch('app.is_authenticated', return_value=False):
            response = self.client.get('/session-data', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Login" in response.get_data(as_text=True))

    def test_user_settings_unauthenticated(self):
        with patch('app.is_authenticated', return_value=False):
            response = self.client.get('/settings', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Login" in response.get_data(as_text=True))

    def test_change_username_unauthenticated(self):
        with patch('app.is_authenticated', return_value=False):
            response = self.client.get('/settings/change-username', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Login" in response.get_data(as_text=True))  # Adjust according to your login page content

    def test_change_username_page_get_request(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '123'
                sess['username'] = 'testuser'

            response = c.get('/settings/change-username')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                "Change Username" in response.get_data(as_text=True))

    def test_delete_account_authenticated(self):
        test_user_id = '507f1f77bcf86cd799439011'
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = test_user_id
                sess['username'] = 'testuser'
                sess['button_press_count'] = 0

            # Mock the delete operations
            with patch('app.poker_users.delete_one') as mock_user_delete, \
                    patch('app.sessions.delete_many') as mock_sessions_delete:
                response = c.post('/delete-account')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_data(as_text=True),
                                 "Account and associated sessions deleted successfully.")

                mock_user_delete.assert_called_once_with({"_id": ObjectId(test_user_id)})
                mock_sessions_delete.assert_called_once_with({"user_id": ObjectId(test_user_id)})
            with c.session_transaction() as sess:
                self.assertNotIn('user_id', sess)
                self.assertNotIn('username', sess)
                self.assertNotIn('button_press_count', sess)

    def test_search_unauthenticated(self):
        with patch('app.is_authenticated', return_value=False):
            response = self.client.get('/search', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Login" in response.get_data(as_text=True))  # Adjust according to your login page content

    def test_search_page_get_request(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '123'
                sess['username'] = 'testuser'

            response = c.get('/search')
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Search" in response.get_data(as_text=True))  # Check for search page content

    def test_search_result_unauthenticated(self):
        with patch('app.is_authenticated', return_value=False):
            response = self.client.post('/search-result', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Login" in response.get_data(as_text=True))  # Adjust according to your login page content

    def test_search_result_authenticated(self):
        test_data = {
            'date': '2021-01-01',
            'buyIn': '100.0',
            'location': 'Casino',
            'profitLossSelection': 'profit'
        }
        expected_query = {
            'date': '2021-01-01',
            'buyIn': 100.0,
            'location': 'Casino',
            'profit': {'$gt': 0}
        }

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '123'
                sess['username'] = 'testuser'

            with patch('app.sessions.find',
                       return_value=[{'_id': '507f1f77bcf86cd799439011', 'data': 'example session data'}]) as mock_find:
                response = c.post('/search-result', data=test_data)
                self.assertEqual(response.status_code, 200)

                mock_find.assert_called_once_with(expected_query)

                self.assertTrue("Search Results" in response.get_data(as_text=True))

    def test_change_password_unauthenticated(self):
        with patch('app.is_authenticated', return_value=False):
            response = self.client.get('/settings/change-password', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Login" in response.get_data(as_text=True))

    def test_change_password_page_get_request(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '123'
                sess['username'] = 'testuser'

            response = c.get('/settings/change-password')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                "Change Password" in response.get_data(as_text=True))  # Check for change password page content


class TestGetPokerNews(unittest.TestCase):

    @patch('feedparser.parse')
    def test_get_poker_news_exception(self, mock_parse):
        mock_parse.side_effect = Exception("An error occurred")

        with self.assertRaises(Exception):
            get_poker_news()


if __name__ == '__main__':
    unittest.main()
