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

db_drop_and_create_all()

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
def drink_detail(token):
    try:
        available_drink = Drink.query.all()

        drinks = [drink.long() for drink in available_drink]
        print(drinks)
        return jsonify({
            'success': True,
            'drinks': [drinks]
        }), 200
    except:
        abort(404)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def new_drink(token):
    try:
        data = request.get_json()
        
        title = data.get('title', None)
        recipe = data.get('recipe', None)
        
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()
        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        }), 200
    except:
        abort(401)

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink:
        try:
            data = request.get_json()
            update_title = data.get('title', None)
            update_recipe = data.get('recipe', None)
            if update_title:
                drink.title = update_title
            if update_recipe:
                drink_recipe = update_recipe
            drink.update()
            return json.dumps({
                'success': True,
                'drinks': [drink.long()]
            })
        except:
            abort(422)
    else:
        abort(404)

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
def auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
