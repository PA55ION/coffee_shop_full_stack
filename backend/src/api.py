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

# db_drop_and_create_all()

## ROUTES
@app.route('/drinks')
def show_drinks():
    try:
        available_drink = Drink.query.all()
        print(available_drink)
        
        drinks = [drink.short() for drink in available_drink]
        print(drinks)

        return jsonify({
            'success': True,
            'status': 200,
            'drinks': drinks,
        })
    except Exception as e:
        print(e)

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def show_drink_detail(token):
    try:
        return json.dumps({
            'success':
            True,
            'drinks': [drink.long() for drink in Drink.query.all()]
        }), 200
    except:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500
    

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
def new_drink(token):
    try:
        data = request.get_json()
        if data is None:
            abort(404)
        
        title = data.get('title', None)
        recipe = data.get('recipe', None)
        
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()
        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        })
    except:
        abort(422)

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
# @app.route('/drinks/<int:drink_id>', methods=['PATCH'])
# @requires_auth('patch:drinks')
# def update_drink(token, drink_id):
#     try:
#         data = request.get_json()



@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, drink_id):
    try:
        drink = Drink.query.get(drink_id)
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink.id
        }), 200
    except:
        abort(404)


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Not Found',
        'error': 404,
    }), 404

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'message': error.status_code,
        'error': error.error
    }), 401
