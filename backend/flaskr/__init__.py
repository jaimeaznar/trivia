import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# paginate questions following video explanation
def paginate(request,options):
  '''
  https://flask.palletsprojects.com/en/1.1.x/api/#flask.Request.args
  flask.Request.args
  A MultiDict with the parsed contents of the query string. (The part in the URL after the question mark).
  '''
  # get(key, default=None, type=None)
  # request.args['page']
  page = request.args.get('page',1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  # retreive questions with comprehensive list
  questions = [question.format() for question in options]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  # class flask_cors.CORS(app=None, **kwargs)
  # resources (dict, iterable or string)
  # https://flask-cors.corydolphin.com/en/latest/api.html#extension
  CORS(app, resources={'/':{'origins':'*'}})
  
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  # Register a function to be run after each request.
  # after request done we set access control
  # to the response hedeader
  # https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.after_request
  '''
  Your function must take one parameter, an instance of response_class and return a new response object or the same (see process_response()).
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
    
    return response


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  # CATEGORIES
  @app.route('/categories')
  def get_categories():
    # define a dict to store all categories
    dict_of_categories = {}
    # we get all categories from db
    categories = Category.query.all()

    for cat in categories:
      dict_of_categories[cat.id] = cat.type

    # 404 if we dont find any
    # an empty dict evaluates to False
    if (len(dict_of_categories) == 0):
      abort(404)

    # return dictionary successfully
    '''
    The return value from a view function is automatically converted into a response object for you
    '''
    # https://flask.palletsprojects.com/en/1.1.x/api/#flask.json.jsonify
    return jsonify({
      'success': True,
      'categories': dict_of_categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
   

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  # QUESTIONS
  @app.route('/questions')
  def get_questions():
    # get questions from db
    questions = Question.query.all()
    # will need the total num of Qs for pagination
    total_questions = len(questions)
    # display first 10 questions
    current_questions = paginate(request, questions)

    # dictionary to store categories
    dict_of_categories = {}
    # get categories from db
    categories = Category.query.all()
    for cat in categories:
      dict_of_categories[cat.id] = cat.type

    # 404 if there are no categories
    if len(current_questions) == 0:
      abort(404)
    # This endpoint should return a list of questions, 
    # number of total questions, current category, categories. 
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': total_questions,
      'categories': dict_of_categories
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  # DELETE QUESTION
  @app.route('/questions/<int:id>',methods=['DELETE'])
  def delete_question(id):
    # since we dont know if the id exists we must wrap it in a try
    try:
      # filter query by id
      # one_or_none returns at most one result or raise an exception.
      question = Question.query.filter_by(id=id).one_or_none()
      
      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success': True,
        'deleted': id
      })
    except:
      abort(400)  #we return a Bad request
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route("/questions", methods=['POST'])
  def add_question():
      body = request.get_json()

      if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
          abort(422)

      new_question = body.get('question')
      new_answer = body.get('answer')
      new_difficulty = body.get('difficulty')
      new_category = body.get('category')

      try:
          question = Question(question=new_question, answer=new_answer,
                              difficulty=new_difficulty, category=new_category)
          question.insert()

          return jsonify({
              'success': True,
              'created': question.id,
          })

      except:
          abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods = ['POST'])
  def search_questions():
      body = request.get_json()
      search_term = body.get('searchTerm', None)

      if search_term == None:
        abort(404)

  
      search_results = Question.query.filter(
          Question.question.ilike(f'%{search_term}%')).all()

      return jsonify({
          'success': True,
          'questions': [question.format() for question in search_results],
          'total_questions': len(search_results),
          'current_category': None
      })
  

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):

      try:
          questions = Question.query.filter(
              Question.category == str(category_id)).all()

          return jsonify({
              'success': True,
              'questions': [question.format() for question in questions],
              'total_questions': len(questions),
              'current_category': category_id
          })
      except:
          abort(404)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  
  @app.route('/quizzes', methods=['POST'])
  def get_random_quiz_question():
      '''
      Handles POST requests for playing quiz.
      '''

      # load the request body
      body = request.get_json()

      # get the previous questions
      previous = body.get('previous_questions')

      # get the category
      category = body.get('quiz_category')

      # abort 400 if category or previous questions isn't found
      if ((category is None) or (previous is None)):
          abort(400)

      # load questions all questions if "ALL" is selected
      if (category['id'] == 0):
          questions = Question.query.all()
      # load questions for given category
      else:
          questions = Question.query.filter_by(category=category['id']).all()

      # get total number of questions
      total = len(questions)

      # picks a random question
      def get_random_question():
          return questions[random.randrange(0, len(questions), 1)]

      # checks to see if question has already been used
      def check_if_used(question):
          used = False
          for q in previous:
              if (q == question.id):
                  used = True

          return used

      # get random question
      question = get_random_question()

      # check if used, execute until unused question found
      while (check_if_used(question)):
          question = get_random_question()

          # if all questions have been tried, return without question
          # necessary if category has <5 questions
          if (len(previous) == total):
              return jsonify({
                  'success': True
              })

      # return the question
      return jsonify({
          'success': True,
          'question': question.format()
      })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(422)
  def unprocesable_entity(error):
      return jsonify({
          'success': False,
          'error': 422,
          'message': 'Unprocessable entity'
      }), 422
  
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
      }), 404
  
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
      }), 400


  
  return app

    