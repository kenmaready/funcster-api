import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from models import db, setup_db, Mentor, Coder, Snippet, User

mentor_token = "Bearer {}".format(os.environ.get('AUTH0_MENTOR_TOKEN'))
coder_token = "Bearer {}".format(os.environ.get('AUTH0_CODER_TOKEN'))
bad_token = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlNnZkhjZm04X0FGMnJ3aGp5UFRtaCJ9.eyJodHRwOi8vZnVuY3N0ZXIvcm9sZSI6WyJtZW50b3IiXSwiaXNzIjoiaHR0cHM6Ly9mdW5jc3Rlci5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWVjYWRjZTNmNzkwOGMwYzY4YTZiZTBmIiwiYXVkIasdpbImh0dHBzOi8vZnVuY3N0ZXItYXV0aDAtYXBpIiwiaHR0cHM6Ly9mdW5jc3Rlci5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNTkxMzc1ODEyLCJleHAiOjE1OTEzODMwMTIsImF6cCI6ImY4aGt1TEFYTWR2N3Z0Y2NrTzRuVlloTURUcWpjM0JEIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInBlcm1pc3Npb25zIjpbImFkZDpjb2RlciIsImVkaXQ6c25pcHBldCIsImdldDpjb2RlcnMiLCJnZXQ6c25pcHBldHMiLCJnZXQ6dXNlcmluZm8iXX0.S8tzzMz5ysd8KJ4Ss4p5xK0oUB7Dbpv7UGE7UsY-VSUXbzwpNNV7iLqpUroUItwJ1XQDfgi-aOonM7CYn4Co5IqFew7vxbueISLUMm7XpLW5PloHN1rZBfSr_7hUmnPg6xAV5KI3JDE9j0uz0cnFdxAL1JKd1VqN1dzj3Mbg4SJgM5pEtuaegZzpaitTv9jWnniSuCQ65mk-1GuUrC7n6EgqYMp9PQoFcuRDGhuRyaB6AXNoHAMrUHv0LiY6Hlq8ppIUopIBwn9Pvm0WaP37OLyCG_BRGj4Y4X2yuQemlF9m1nfaLZsUQWu2cK5u10m3V5lQxs8ftqzcA-bIpUgOgA"

mentor_headers = {'Content-Type': 'application/json', 'Authorization': mentor_token}
coder_headers = {'Content-Type': 'application/json', 'Authorization': coder_token}
invalid_headers = {'Content-Type': 'application/json', 'Authorization': bad_token}

class FuncsterCase(unittest.TestCase):
    """This class contains the tests for funcster"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.environ.get('TEST_DATABASE_URL')
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass
    
    #----------------------------------------------------------------------------
    #  Tests:
    #----------------------------------------------------------------------------

    def test_a_check_api_success(self):
        '''Confirm the basic index endpoint is working'''
        res = self.client().get('/')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    # Note: the index ('/') endpoint isn't really a functional endpoint, doesn't require 
    # data or authentification, so no fail test has been created for that endpoint

    def test_b_check_signup_fail(self):
        '''Test the signup endpoint with an existing username'''
        request_body = {
            'username': 'coder1',
            'usertype': 'Coder',
            'email': 'coder1@email.com',
            'password': 'fakePassword'}
        
        res = self.client().post('/signup', json=request_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 409)
        self.assertFalse(data['success'])

    def test_c_check_get_user_info_success(self):
        '''Test the user info endpoint to get user, with proper token'''
        res = self.client().get('/userinfo/mentor1', headers=mentor_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['user_id'], 1)
        self.assertEqual(data['usertype'], 'Mentor')
        self.assertEqual(len(data['coders']), 2)

    def test_d_check_get_user_info_fail(self):
        '''Test the user info endpoint to get user, with invalid token'''
        res = self.client().get('/userinfo/mentor1', headers=invalid_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])

    def test_d2_check_get_user_info_fail_2(self):
        '''Test the user info endpoint with request for nonexistent user'''
        res = self.client().get('/userinfo/codeninja', headers=mentor_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_e_get_all_coders_success(self):
        '''Test the get_all_coders endpoint with valid mentor token/RBAC permissions'''
        res = self.client().get('coders', headers=mentor_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['coders']), 3)

    def test_e_get_all_coders_fail(self):
        '''Test the get_all_coders endpoint with valid, coder token/RBAC permissions'''
        '''(Coders do not have RBAC permission to get all coders, so expect failure)'''
        res = self.client().get('coders', headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_f_get_available_coders_success(self):
        '''Test the get_available_coders endpoint with valid mentor token/RBAC permissions'''
        res = self.client().get('coders/available', headers=mentor_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['coders']), 0)

    def test_g_get_available_coders_fail(self):
        '''Test the get_available_coders endpoint with valid, coder token/RBAC permissions'''
        '''(Coders do not have RBAC permission to get all coders, so expect failure)'''
        res = self.client().get('coders/available', headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_h_select_mentor_success(self):
        '''Test the select_mentor endpoint with valid coder token/RBAC permissions'''
        res = self.client().patch('/coder/2/mentor', json={ 'mentorId': 3}, headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        '''confirm that the switch of mentors above was effective by checking user info for the coder'''
        confirm_res = self.client().get('/userinfo/coder2', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(confirm_data['mentor'], 'mentor2')

    def test_i_select_mentor_fail(self):
        '''Test the select_mentor endpoint with a mentor token, which does not have RBAC permissions
           to change the mentor for a coder'''
        res = self.client().patch('/coder/2/mentor', json={ 'mentorId': 6}, headers=mentor_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

        '''confirm that the switch of mentors above was NOT effective by checking user info for the coder'''
        confirm_res = self.client().get('/userinfo/coder2', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(confirm_data['mentor'], 'mentor2')
    
    def test_i2_select_mentor_fail_2(self):
        '''Test the select_mentor endpoint with request for nonexistent mentor'''
        res = self.client().patch('/coder/2/mentor', json={ 'mentorId': 99}, headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_j_get_all_mentors_success(self):
        '''Test the get_all_mentors endpoint with valid coder token/RBAC permissions'''
        res = self.client().get('mentors', headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['mentors']), 3)

    def test_k_get_all_mentors_fail(self):
        '''Test the get_all_mentors endpoint with valid, mentor token/RBAC permissions'''
        '''(Mentors do not have RBAC permission to get all mentors, so expect failure)'''
        res = self.client().get('mentors', headers=mentor_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_l_select_coder_success(self):
        '''Test the select_coder endpoint with valid mentor token/RBAC permissions'''
        res = self.client().patch('/mentor/1/coder', json={ 'coderId': 2}, headers=mentor_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        '''confirm that the switch of coders above was effective by checking user info for the coder'''
        confirm_res = self.client().get('/userinfo/coder2', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(confirm_data['mentor'], 'mentor1')

    def test_m_select_coder_fail(self):
        '''Test the select_coder endpoint with coder token/RBAC permissions'''
        res = self.client().patch('/mentor/3/coder', json={ 'coderId': 2}, headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

        '''confirm that the switch of coders above was NOT effective by checking user info for the coder'''
        confirm_res = self.client().get('/userinfo/coder2', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(confirm_data['mentor'], 'mentor1')

    def test_m2_select_coder_fail_2(self):
        '''Test the select_coder endpoint with request for nonexistent coder'''
        res = self.client().patch('/mentor/1/coder', json={ 'coderId': 99}, headers=mentor_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

        '''confirm that the switch of coders above was effective by checking user info for the coder'''
        confirm_res = self.client().get('/userinfo/coder2', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(confirm_data['mentor'], 'mentor1')

    def test_n_get_snippet_success(self):
        '''Test the get_snippet endpoint with proper token/RBAC permissions'''
        res = self.client().get('/snippet/9', headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['snippet_name'], 'Add a bird')
        self.assertEqual(data['code'][:18], 'def add_a_bird(s):')
    
    def test_o_get_snippet_fail(self):
        '''Test the get_snippet endpoint with improper token/permissions'''
        res = self.client().get('/snippet/9', headers=invalid_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])

    def test_o2_get_snippet_fail_2(self):
        '''Test the get_snippet endpoint with request for nonexistent snippet'''
        res = self.client().get('/snippet/20', headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
    
    def test_p_post_new_snippet_success(self):
        '''Test the post_new_snippet endpoint with properly formed post request and valid permissions'''
        snippet_body = {
            "coderId": 3,
            "name": "Testing Function",
            "code": "def my_testing_function(a):\n\treturn 42",
            "needsReview": True,
            "comments": ''
        }
        res = self.client().post('/snippet', json=snippet_body, headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        '''Confirm that the new_snippet was added properly to the coder by getting user information for coder'''
        confirm_res = self.client().get('/userinfo/coder3', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(len(confirm_data['snippets']), 1)
        self.assertEqual(confirm_data['snippets'][0]['snippet_name'], "Testing Function")
    
    def test_q_post_new_snippet_fail(self):
        '''Test the post_new_snippet endpoint with mentor token (does not have RBAC permissions to post new snippet)'''
        snippet_body = {
            "coderId": 3,
            "name": "Testing Function 2",
            "code": "def my_testing_function(a):\n\treturn 42",
            "needsReview": True,
            "comments": ''
        }
        res = self.client().post('/snippet', json=snippet_body, headers=mentor_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

        '''Confirm that the new_snippet was NOT added properly to the coder by checking user information for coder'''
        confirm_res = self.client().get('/userinfo/coder3', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(len(confirm_data['snippets']), 1)
    
    def test_q2_post_new_snippet_fail_2(self):
        '''Test the post_new_snippet endpoint with request for nonexistent coder'''
        snippet_body = {
            "coderId": 17,
            "name": "Testing Function 2",
            "code": "def my_testing_function(a):\n\treturn 42",
            "needsReview": True,
            "comments": ''
        }
        res = self.client().post('/snippet', json=snippet_body, headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
    
    def test_r_post_revised_snippet_success(self):
        ''' Test the post_revised_snippet endpoint with proper request/token/permissions from coder'''
        snippet_body = {
            "coderId": 2,
            "userId": 2,
            "usertype": "Coder",
            "name": "Revised adasd",
            "code": "def my_revised_function(a):\n\treturn 42",
            "needsReview": True,
            "comments": ''
        }
        res = self.client().patch('/snippet/11', json=snippet_body, headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        '''Confirm that snippet was updated by checking snippet'''
        confirm_res = self.client().get('/snippet/11', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(confirm_data['snippet_name'], 'Revised adasd')

    def test_r2_post_revised_snippet_success_2(self):
        ''' Test the post_revised_snippet endpoint with proper request/token/permissions from mentor'''
        snippet_body = {
            "coderId": 2,
            "userId": 1,
            "usertype": "Mentor",
            "name": "Reviewed adasd",
            "code": "def my_revised_function(a):\n\treturn 42",
            "needsReview": False,
            "comments": 'Reviewed and approved'
        }
        res = self.client().patch('/snippet/11', json=snippet_body, headers=mentor_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        '''Confirm that snippet was updated by checking snippet'''
        confirm_res = self.client().get('/snippet/11', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(confirm_data['snippet_name'], 'Reviewed adasd')
        self.assertFalse(confirm_data['needs_review'])

    def test_s_post_revised_snippet_fail(self):
        ''' Test the post_revised_snippet endpoint with request for nonexistent snippet'''
        snippet_body = {
            "coderId": 2,
            "userId": 2,
            "usertype": "Coder",
            "name": "Revised adasd",
            "code": "def my_revised_function(a):\n\treturn 42",
            "needsReview": True,
            "comments": ''
        }
        res = self.client().patch('/snippet/99', json=snippet_body, headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
    
    def test_s2_post_revised_snippet_fail_2(self):
        '''Test the post revised_snippet endpoint with request by coder who is not
           the owner of the snippet'''
        snippet_body = {
            "coderId": 3,
            "userId": 2,
            "usertype": "Coder",
            "name": "More revised adasd",
            "code": "def my_revised_function(a):\n\treturn 42",
            "needsReview": True,
            "comments": ''
        }
        
        res = self.client().patch('/snippet/11', json=snippet_body, headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

        '''Confirm that snippet was NOT updated by checking snippet'''
        confirm_res = self.client().get('/snippet/11', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(confirm_data['snippet_name'], 'Revised adasd')

    def test_s3_post_revised_snippet_fail_3(self):
        '''Test the post revised_snippet endpoint with request by mentor who is NOT
           the mentor of the coder who owns the snippet'''
        snippet_body = {
            "coderId": 2,
            "userId": 6,
            "usertype": "Mentor",
            "name": "Reviewed adasd",
            "code": "def my_revised_function(a):\n\treturn 42",
            "needsReview": False,
            "comments": 'Reviewed and approved'
        }
        res = self.client().patch('/snippet/11', json=snippet_body, headers=mentor_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

        '''Confirm that snippet was NOT updated by checking snippet'''
        confirm_res = self.client().get('/snippet/11', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(confirm_data['snippet_name'], 'Revised adasd')

    def test_t_delete_snippet_success(self):
        '''Test the delete snippet endpoint with a proper request/token/RBAC permissions'''
        res = self.client().delete('/snippet/11', json={ 'coderId': 2}, headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        ''' Confirm snippet has been deleted by trying to get snippet'''
        confirm_res = self.client().get('snippet/11', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(confirm_res.status_code, 404)
        self.assertFalse(confirm_data['success'])

    def test_u_delete_snippet_fail(self):
        '''Test the delete snippet endpoint with improper token/RBAC permissions'''
        res = self.client().delete('/snippet/7', json={ 'coderId': 1}, headers=mentor_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

        '''Confirm that snippet was NOT deleted by checking snippet'''
        confirm_res = self.client().get('snippet/7', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(confirm_res.status_code, 200)
        self.assertTrue(confirm_data['success'])
    
    def test_u2_delete_snippet_fail(self):
        '''Test the delete snippet endpoint with request from coder who does not own snippet'''
        res = self.client().delete('/snippet/7', json={'coderId': 3}, headers=coder_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
    
        '''Confirm that snippet was NOT deleted by checking snippet'''
        confirm_res = self.client().get('snippet/7', headers=coder_headers)
        confirm_data = json.loads(confirm_res.data)

        self.assertEqual(confirm_res.status_code, 200)
        self.assertTrue(confirm_data['success'])


"""

    def test_a_get_categories_success(self):
      '''Test /categories GET endpoint with properly formed request '''
      res = self.client().get('/categories')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
    
    def test_b_get_categories_fail(self):
      '''Test /categories GET endpoint with improper request'''
      res = self.client().post('/categories')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 405)
      self.assertFalse(data['success'])

    def test_c_get_questions_success(self):
      ''' Test /questions GET endpoint with properly formed request '''
      res = self.client().get('/questions')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertEqual(len(data['questions']), 10)
      self.assertEqual(data['total_questions'], 19)

    def test_d_get_questions_fail(self):
      ''' Test /questions GET endpoint with improper request ('page' out of bounds) '''
      res = self.client().get('/questions&page=4')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 404)
      self.assertFalse(data['success'])
      self.assertEqual(data['error'], 404)
    
    def test_e_delete_question_success(self):
      ''' Test questions/<id> DELETE endpoint with properly formed request to delete a question '''
      res = self.client().delete('/questions/5')
      data = json.loads(res.data)
      total_questions = len(Question.query.all())
      deleted_question = Question.query.get(5)

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertIsNone(deleted_question)
      self.assertEqual(total_questions, 18)

    def test_f_delete_question_fail(self):
      ''' Test /questions/<id> DELETE endpoint with improper request (id for nonexistent question) '''
      res = self.client().delete('/questions/73')
      data = json.loads(res.data)
      total_questions = len(Question.query.all())

      self.assertEqual(res.status_code, 404)
      self.assertFalse(data['success'])
      self.assertEqual(total_questions, 18)
    
    def test_g_add_question_success(self):
      ''' Test add question functionality of /questions POST endpoint with properly formed request to add a new question '''
      new_question = {
        'question': 'What is the air-speed velocity of an unladen swallow?',
        'answer': 'What do you mean? An African or European swallow?',
        'difficulty': 5,
        'category': 5
      }

      res = self.client().post('/questions', json=new_question, headers={'Content-Type': 'application/json'})
      data = json.loads(res.data)
      total_questions = len(Question.query.all())

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertEqual(total_questions, 19)
    
    def test_h_add_question_fail(self):
      ''' Test add question functionality of /questions POST endpoint with improperly formed request to add a new question (no actual text supplied for new question) '''
      new_question = {
        'question': '',
        'answer': 'What do you mean? An African or European swallow?',
        'difficulty': 5,
        'category': 5
      }

      res = self.client().post('/questions', json=new_question, headers={'Content-Type': 'application/json'})
      data = json.loads(res.data)
      total_questions = len(Question.query.all())

      self.assertEqual(res.status_code, 422)
      self.assertFalse(data['success'])
      self.assertEqual(total_questions, 19)
  
    def test_i_search_success_w_results(self):
      ''' Test search functionality of /questions POST endpoint with property formed search request that should retrieve 2 results '''
      res = self.client().post('/questions', json={'searchTerm': 'sOcCe'}, headers={'Content-Type': 'application/json'})
      data = json.loads(res.data)
      question_ids = sorted([question['id'] for question in data['questions']])

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertEqual(data['total_questions'], 2)
      self.assertEqual(question_ids, [10, 11])

    def test_j_search_success_no_results(self):
      ''' Test search functionality of /questions POST endpoint with properly formed search request for term that should have no results in test database '''
      res = self.client().post('/questions', json={'searchTerm': 'Smashmouth'}, headers={'Content-Type': 'application/json'})
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertEqual(data['total_questions'], 0)
    
    def test_k_search_fail(self):
      ''' Test search functionality of /questions POST endpoint with improper request (no data supplied in json request body) '''
      res = self.client().post('/questions', json={}, headers={'Content-Type': 'application/json'})
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 422)
      self.assertFalse(data['success'])

    def test_l_category_search_success(self):
      ''' Test search functionality of /categories/<id>/questions GET endpoint with properly form search request'''
      res = self.client().get('/categories/3/questions')
      data = json.loads(res.data)
      num_returned_questions = len(data['questions'])
      question_ids = sorted([question['id'] for question in data['questions']])

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertEqual(num_returned_questions, 3)
      self.assertEqual(data['total_questions'], 3)
      self.assertEqual(question_ids, [13, 14, 15])
    
    def test_m_category_search_fail(self):
      ''' Test search functionality of /categories/<id>/questions GET endpoint with improperly form search request'''
      res = self.client().get('/categories/7/questions')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 404)
      self.assertFalse(data['success'])

    def test_n_start_quiz_in_cat_success(self):
      ''' Test /quizzes POST endpoint with properly formatted request for question in specific category'''
      res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'id': 1} })
      data = json.loads(res.data)
      
      question_id = data['question']['id']

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertIn(question_id, [20, 21, 22])

    def test_o_start_quiz_in_all_success(self):
      ''' Test /quizzes POST endpoint with properly formatted request for question with ALL categories selected'''
      res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'id': 0} })
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertTrue(data['question'])
    
    def test_p_start_quiz_in_cat_out_of_questions(self):
      ''' Test /quizzes POST endpoint with properly formatted request for question in category where all questions have been exhausted'''
      res = self.client().post('/quizzes', json={'previous_questions': [13, 14, 15], 'quiz_category': {'id': 3} })
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertNotIn('question', data.keys())

    def test_q_start_quiz_fail(self):
      ''' Test /quizzes POST endpoint with improperly formatted request for question (category does not exist)'''
      res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'id': 9} })
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 404)
      self.assertFalse(data['success'])
"""

# Make the tests conveniently executable
if __name__ == "__main__":
    os.system('dropdb -U udacity funcsterdb_test')
    os.system('createdb -U udacity funcsterdb_test')
    os.system('psql -U udacity funcsterdb_test < funcsterdb_test.psql')

    unittest.main()