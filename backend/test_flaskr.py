import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_pagination(self):
        '''
        By using client().get() we can send an HTTP GET request to the application with the given path. The return value will be a response_class object. We can now use the data attribute to inspect the return value (as string) from the application.
        '''
        response = self.client().get('/questions')

        # retreive the data from the response
        # The json.loads() is used to convert the JSON String document into the Python dictionary
        data = json.loads(response.data)
        
        # make sure the response is 200 (ok) and that the success' key
        # value is True
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # make sure following keys exist
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])

    
    # Test delete question
    def test_delete(self):
        # create Qs object
        question = Question(question="test question", answer="answer question", difficulty=1,category="1")

        # insert Qs in db
        question.insert()
        question_id = question.id

        # delete response
        response = self.client().delete(f'/questions/{question_id}')
        data = json.loads(response.data)

        # check if Qs is in db

        question = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],question_id)
        self.assertEqual(question, None)

    def test_add(self):
        # create mock data
        mock_question = {
            'question': 'test question',
            'answer': 'test answer',
            'difficulty':1,
            'category':1
        }

        response = self.client().post('/questions', json=mock_question)
        data = json.loads(response.data)

        #ensure successful request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)



    def test_search_questions(self):
        new_search = {'searchTerm': 'www'}
        response = self.client().post('/questions/search', json=new_search)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_get_questions_per_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
    
    def test_play_quiz(self):
        new_quiz_round = {'previous_questions': [],
                          'quiz_category': {'type': 'Science', 'id': '1'}}

        res = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    # test 4XX errors

    # page limit exceeded
    def test_404_valid_page(self):
        response = self.client().get('/questions?page=300')
        data = json.loads(response.data)

        # status 404 and false
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    # category non existent
    def test_404_no_category(self):
        response = self.client().get('/categories/10')
        data = json.loads(response.data)

        # 404 and False
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    # delete error
    def test_404_delete_question(self):
        response = self.client().delete('/questions/wwwww')
        data = json.loads(response.data)

        # 400 and False
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # add error 500
    def test_422_add_question(self):
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable entity")

    # error search Qs
    def test_404_search(self):
        search_term = {
            'searchTearm': '',
        }

        response = self.client().post('/questions/search', json=search_term)
        data = json.loads(response.data)

        # 404 and False
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    # error Qs per category
    def test_400_search_question_category(self):
        response = self.client().get('/categories/www/questions')
        data = json.loads(response.data)

        # 404 and False
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    # quizz error
    def test_500_quiz(self):
        mock_quiz_data = {
            'previous_question':[]
        }

        response = self.client().post('/quizzes', json=mock_quiz_data)
        data = json.loads(response.data)

        # 500 and False
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()