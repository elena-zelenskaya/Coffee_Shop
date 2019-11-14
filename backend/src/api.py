import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_all_drinks():
        drinks = Drink.query.all()
        if drinks is None:
            abort(404)
       
        else:
            formated_drinks = [drink.short() for drink in drinks]
            result = {
              "success": True,
              "drinks": formated_drinks,
            }
            return jsonify(result)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    if drinks is None:
            abort(404)
       
    else:
            formated_drinks = [drink.long() for drink in drinks]
            result = {
              "success": True,
              "drinks": formated_drinks,
            }
            return jsonify(result)    

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(jwt):
      if not request.data:
        abort(422)
        
      new_drink_data = json.loads(request.data)        
      new_drink = new_drink_data['title']
      new_recipe = json.dumps(new_drink_data['recipe'])
      if not new_drink or not new_recipe:
        abort(404)

      try:
        added_drink = Drink(title=new_drink, recipe=new_recipe)
        added_drink.insert()

        result = {
            "success": True,
            "drinks": [added_drink.long()]
        }
        return jsonify(result)

      except:
        abort(405)

            


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):
      if not request.data:
        abort(422)
        
      edited_drink_data = json.loads(request.data)         

      try:
        edited_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if edited_drink is None:
            abort(404)

        if 'title' in edited_drink_data:
            setattr(edited_drink, 'title', edited_drink_data['title'])
        if 'recipe' in edited_drink_data:
            setattr(edited_drink, 'recipe', json.dumps(edited_drink_data['recipe']))

        edited_drink.update()

        result = {
            "success": True,
            "drinks": [edited_drink.long()]
        }
        return jsonify(result)

      except:
            abort(405)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
        try:
            drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

            drink.delete()
            result = {
                "success": True,
                "delete": drink_id
             }
            return jsonify(result)

        except:
            abort(404)


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                "success": False, 
                "error": 422,
                "message": "Unprocessable"
            }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
            "success": False, 
            "error": 404,
            "message": "Resource Not Found"
        }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
            "success": False, 
            "error": 401,
            "message": "Unauthorized"
        }), 401



@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
            "success": False, 
            "error": 405,
            "message": "Method Not Allowed"
        }), 405   

@app.errorhandler(500)
def internal_server(error):
    return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500                                            


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify(error.error), error.status_code


