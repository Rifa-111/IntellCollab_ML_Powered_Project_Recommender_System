import unittest
from app import app

class FlaskTestCase(unittest.TestCase):
    
    # Ensure that the index page returns a 200 status code
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/home')
        self.assertEqual(response.status_code, 200)
    
    # Ensure that the login page loads correctly
    def test_login_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertTrue(b'Login' in response.data)
    
    # Ensure that the login behaves correctly given the correct credentials
    def test_correct_login(self):
        tester = app.test_client(self)
        response = tester.post('/login', 
                               data=dict(username="test_user", password="test_password"), 
                               follow_redirects=True)
        self.assertIn(b'Welcome', response.data)
    
    # Ensure that the login behaves correctly given incorrect credentials
    def test_incorrect_login(self):
        tester = app.test_client(self)
        response = tester.post('/login', 
                               data=dict(username="wrong_user", password="wrong_password"), 
                               follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)
    
    # Add more test cases as needed...
    
if __name__ == '__main__':
    unittest.main()


''' import unittest
from app import app

class FlaskTestCase(unittest.TestCase):
    
    # Ensure that the index page returns a 200 status code
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/')
        self.assertEqual(response.status_code, 200)
    
    # Ensure that the login page loads correctly
    def test_login_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertTrue(b'Login' in response.data)
    
    # Ensure that the login behaves correctly given the correct credentials
    def test_correct_login(self):
        tester = app.test_client(self)
        response = tester.post('/login', 
                               data=dict(username="test_user", password="test_password"), 
                               follow_redirects=True)
        self.assertIn(b'Welcome', response.data)
    
    # Ensure that the login behaves correctly given incorrect credentials
    def test_incorrect_login(self):
        tester = app.test_client(self)
        response = tester.post('/login', 
                               data=dict(username="wrong_user", password="wrong_password"), 
                               follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)
    
    # Ensure that the logout page behaves correctly
    def test_logout(self):
        tester = app.test_client(self)
        tester.post('/login', 
                    data=dict(username="test_user", password="test_password"), 
                    follow_redirects=True)
        response = tester.get('/logout', follow_redirects=True)
        self.assertIn(b'You were logged out', response.data)
    
    # Ensure that the profile page requires login
    def test_profile_login_required(self):
        tester = app.test_client(self)
        response = tester.get('/profile', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)
    
    # Ensure that the project creation page requires login
    def test_project_creation_login_required(self):
        tester = app.test_client(self)
        response = tester.get('/create_project', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)
    
    # Ensure that the project creation page loads correctly after login
    def test_project_creation_page_loads(self):
        tester = app.test_client(self)
        tester.post('/login', 
                    data=dict(username="test_user", password="test_password"), 
                    follow_redirects=True)
        response = tester.get('/create_project', follow_redirects=True)
        self.assertTrue(b'Create Project' in response.data)
    
    # Ensure that the sign-up page loads correctly
    def test_signup_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/signup', content_type='html/text')
        self.assertTrue(b'Sign Up' in response.data)
    
    # Ensure that the footer displays essential information
    def test_footer_displays_essential_info(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'Contact Us' in response.data)
        self.assertTrue(b'Quick Links' in response.data)
    
    # Ensure that the drop-down menu contains user types
    def test_drop_down_menu_user_types(self):
        tester = app.test_client(self)
        response = tester.get('/signup', content_type='html/text')
        self.assertTrue(b'Student' in response.data)
        self.assertTrue(b'Faculty' in response.data)
        self.assertTrue(b'Industry Partner' in response.data)
    
    # Add more test cases as needed...
    
if __name__ == '__main__':
    unittest.main() '''


# import unittest
# from app import app

# class FlaskTestCase(unittest.TestCase):
    
#     # Ensure that the index page returns a 200 status code
#     def test_index(self):
#         tester = app.test_client(self)
#         response = tester.get('/')
#         self.assertEqual(response.status_code, 200)
    
#     # Ensure that the login page loads correctly
#     def test_login_page_loads(self):
#         tester = app.test_client(self)
#         response = tester.get('/login', content_type='html/text')
#         self.assertTrue(b'Login' in response.data)
    
#     # Ensure that the login behaves correctly given the correct credentials
#     def test_correct_login(self):
#         tester = app.test_client(self)
#         response = tester.post('/login', 
#                                data=dict(username="test_user", password="test_password"), 
#                                follow_redirects=True)
#         self.assertIn(b'Welcome', response.data)
    
#     # Ensure that the login behaves correctly given incorrect credentials
#     def test_incorrect_login(self):
#         tester = app.test_client(self)
#         response = tester.post('/login', 
#                                data=dict(username="wrong_user", password="wrong_password"), 
#                                follow_redirects=True)
#         self.assertIn(b'Invalid username or password', response.data)
    
#     # Ensure that the logout page behaves correctly
#     def test_logout(self):
#         tester = app.test_client(self)
#         tester.post('/login', 
#                     data=dict(username="test_user", password="test_password"), 
#                     follow_redirects=True)
#         response = tester.get('/logout', follow_redirects=True)
#         self.assertIn(b'You were logged out', response.data)
    
#     # Ensure that the profile page requires login
#     def test_profile_login_required(self):
#         tester = app.test_client(self)
#         response = tester.get('/profile', follow_redirects=True)
#         self.assertIn(b'Please log in to access this page', response.data)
    
#     # Add more test cases as needed...
    
# if __name__ == '__main__':
#     unittest.main()



''' import unittest
from app import app

class TestProjectCreation(unittest.TestCase):
    
    def test_company_name_input(self):
        # Test whether the company name input field accepts text input
        self.assertTrue(is_text_input_accepted("company_name"))

    def test_required_skills_input(self):
        # Test whether the required skills input field accepts skill keywords
        self.assertTrue(is_text_input_accepted("required_skills"))

    def test_project_description_input(self):
        # Test whether the project description text area accepts text input
        self.assertTrue(is_text_area_accepted("project_description"))

    def test_save_project_to_profile(self):
        # Test whether the project is successfully saved to the user's profile
        self.assertTrue(is_project_saved("project_details"))

    def test_add_project_to_database(self):
        # Test whether the project details are correctly added to the database
        self.assertTrue(is_project_added_to_database("project_details"))


class TestUserAuthentication(unittest.TestCase):
    
    def test_password_match(self):
        # Test whether entered password matches the one stored in the database
        self.assertTrue(is_password_matched("entered_password", "stored_password"))

    def test_sign_in_success(self):
        # Test whether users can sign in successfully with correct credentials
        self.assertTrue(is_sign_in_successful("username", "password"))

    def test_password_requirements_display(self):
        # Test whether additional instructions for password requirements are displayed
        self.assertTrue(is_password_requirements_displayed())


class TestUserRegistration(unittest.TestCase):

    def test_add_username_to_database(self):
        # Test whether the entered username is successfully added to the database
        self.assertTrue(is_username_added_to_database("username"))

    def test_add_email_to_database(self):
        # Test whether the entered email is correctly added to the database
        self.assertTrue(is_email_added_to_database("email"))

    def test_create_password(self):
        # Test whether users can successfully create a password
        self.assertTrue(is_password_created("password"))

    def test_save_password_to_database(self):
        # Test whether the user password is saved in the database
        self.assertTrue(is_password_saved_to_database("password"))

    def test_create_profile(self):
        # Test whether a user profile is successfully created upon sign-up
        self.assertTrue(is_profile_created("profile_details"))

    def test_preview_profile_info(self):
        # Test whether users can preview profile information before signing up
        self.assertTrue(is_profile_info_previewed())

    def test_verify_email_address(self):
        # Test whether users can verify their email address before sign-up
        self.assertTrue(is_email_verified())


class TestNavigation(unittest.TestCase):
    
    def test_navigate_to_main_page(self):
        # Test whether users can navigate to the main page
        self.assertTrue(is_main_page_accessible())

    def test_navigate_to_dashboard(self):
        # Test whether users can navigate to the dashboard
        self.assertTrue(is_dashboard_accessible())

    def test_login_option(self):
        # Test whether the login option is visible and accessible
        self.assertTrue(is_login_option_visible())

    def test_create_profile_option(self):
        # Test whether the option to create a profile is accessible
        self.assertTrue(is_create_profile_option_accessible())

    def test_add_project_option(self):
        # Test whether the option to add a project is accessible
        self.assertTrue(is_add_project_option_accessible())

    def test_sign_out_option(self):
        # Test whether the sign-out option is available when logged in
        self.assertTrue(is_sign_out_option_available())


class TestFooter(unittest.TestCase):

    def test_footer_information_display(self):
        # Test whether essential information is displayed on the footer
        self.assertTrue(is_footer_information_displayed())

    def test_visually_appealing_footer(self):
        # Test whether visually appealing graphics are included on the footer
        self.assertTrue(is_footer_visually_appealing())


if __name__ == '__main__':
    unittest.main()
 '''














''' import unittest
from app import app

class FlaskTestCase(unittest.TestCase):
    
    
    # Ensure that the index page returns a 200 status code
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/')
        self.assertEqual(response.status_code, 200)
    
    # Ensure that the login page loads correctly
    def test_login_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertTrue(b'Login' in response.data)
    
    # Ensure that the login behaves correctly given the correct credentials
    def test_correct_login(self):
        tester = app.test_client(self)
        response = tester.post('/login', 
                               data=dict(username="test_user", password="test_password"), 
                               follow_redirects=True)
        self.assertIn(b'Welcome', response.data)
    
    # Ensure that the login behaves correctly given incorrect credentials
    def test_incorrect_login(self):
        tester = app.test_client(self)
        response = tester.post('/login', 
                               data=dict(username="wrong_user", password="wrong_password"), 
                               follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)
    
    # Add more test cases as needed...
    
if __name__ == '__main__':
    unittest.main()
 '''