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
@TODO uncomment the following line to initialize the datbase [DONE]
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
https://test-alanoud.us.auth0.com/authorize?audience=drinks&response_type=token&client_id=3Hd4Of7KRQq5biFW1y3glQ8A5WhZ4Rn2&redirect_uri=https://127.0.0.1:8080/login-results


https://127.0.0.1:8080/login-results#access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkpBWTU0cndkcDZxUDg3Z1ZNLUlMZiJ9.eyJpc3MiOiJodHRwczovL3Rlc3QtYWxhbm91ZC51cy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDg5NTUwNDU4MTAyODkxOTIyNzAiLCJhdWQiOlsiZHJpbmtzIiwiaHR0cHM6Ly90ZXN0LWFsYW5vdWQudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTU5NjY3MjAyMSwiZXhwIjoxNTk2Njc5MjIxLCJhenAiOiIzSGQ0T2Y3S1JRcTViaUZXMXkzZ2xROEE1V2haNFJuMiIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6W119.Jd9l_w0lM65Aw05pIdzQjk7YEPJ_U_fgD24Hq5HDpC1g1hqrbiZRkcD_EQYx-8ZO_uLMCFMBdKuXuo_5yR3iimPqWK3LamcxNG0OhKXtN3b6xZyWF903rmblTeyCRE1uEIBOQkVJyq9_MD6HcSACHcxXeZm4nsYWzBaTivQ9kiW9Eku7dNcC48esVG1zCyOP8-d1d6dqaGWiYTZ79qcPa98aM01CSo_u9wKKMy6LDvptINFDPshpUPCGbVZW83anmteKdXIZGb-JFiR0KTai_1_EswPDdaHZvA7uKOyerXCNqUYR4lOPHTWvR7LeIVnKSA9_M4mxdNdCO26bla9wOQ&scope=openid%20profile%20email&expires_in=7200&token_type=Bearer&state=g6Fo2SAtMHVjQ0poSjRVRTdEVmljM3Y5eUppRW43R3dMbVpnNqN0aWTZIGlqbVlFczhwdUppUFhUbG4zMnNCeDYtdUFpY1k0aUhLo2NpZNkgM0hkNE9mN0tSUXE1YmlGVzF5M2dsUThBNVdoWjRSbjI
'''
#uncommented next line
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint [DONE]
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET']) 
def get_drinks():
    #Get all drinks
    drinks = Drink.query.all()

    return jsonify({
        'success': True
        #Return only short drinks from "Drinks" var
        'drinks': [drink.short() for drink in drinks]
    }), 200

'''
@TODO implement endpoint [DONE]
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    #Get all drinks
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        #Return only long drinks from "Drinks" var
        'drinks': [drink.long() for drink in drinks]
    }), 200

'''
@TODO implement endpoint [DONE]
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST']) 
@requires_auth('post:drinks')
def create_drink(payload):
    # get the request body data
    body = request.get_json()

    if 'title' and 'recipe' not in body:
        abort(422)

    # get title from body
    title = body['title']
    # Get recipe + convert to json string instead of an object
    recipe = json.dumps(body['recipe'])

    #create a new drink object
    new_drink = Drink(title=title, recipe=recipe)

    try:
        #insert the new drink to the db
        new_drink.insert()

    except BaseException:
        abort(400)
    
    return jsonify(
        {'success': True, 
        'drinks': [drink.long()]
        })

'''
@TODO implement endpoint [DONE]
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):

    #get drink by id
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    # get the request body data
    body = request.get_json()

    if not drink:
        abort(404)

    #check if title is in the body then update the drink title
    if 'title' in body:
        drink.title = body['title']

    #check if recipe is in the body then update the drink recipe
    if 'recipe' in body:
        drink.recipe = json.dumps(body['recipe'])

    #Update the drink
    drink.update()
    
    #Return the updated drink in long format
   return jsonify({
    'success': True,
    'drinks': [drink.long()]
    }), 200

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
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    #get drink by id
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    #if id is not found abort
    if not drink:
        abort(404)

    #Try to delete the drink 
    try:
        drink.delete()

    #Abort 400 when there is an exception 
    except BaseException:
        abort(400)
    #RETRUN THE ID OF the deleted drink and return status code.
    return jsonify({
        'success': True, 
        'delete': id}
    ), 200


## Error Handling
'''
Example error handling for unprocessable entity
'''
#return 422 for unprocessable entity
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
            "success": False, 
            "error": 422,
            "message": "unprocessable"
            }), 422

'''
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@DONE implement error handler for 404
    error handler should conform to general task above 
'''
#return 404 for resource not found

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'Error': 404,
        'Message':'not found'
    }),404

'''
@DONE implement error handler for AuthError
    error handler should conform to general task above 
'''
#retrun error for any authorization errors
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code

# anoud-0 Barista
# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkpBWTU0cndkcDZxUDg3Z1ZNLUlMZiJ9.eyJpc3MiOiJodHRwczovL3Rlc3QtYWxhbm91ZC51cy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDg5NTUwNDU4MTAyODkxOTIyNzAiLCJhdWQiOlsiZHJpbmtzIiwiaHR0cHM6Ly90ZXN0LWFsYW5vdWQudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTU5NjY3Mjg1MCwiZXhwIjoxNTk2NjgwMDUwLCJhenAiOiIzSGQ0T2Y3S1JRcTViaUZXMXkzZ2xROEE1V2haNFJuMiIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6ZHJpbmtzLWRldGFpbCJdfQ.EyI91XVUXd_l7j1ED_aJSpKFsXhKRIAu2FQcAZAtMbr7Zdc-s6DiLw8deNVjg90KUhmfhr8B4KU0LjG2NEj80s3ZnuQVzLz16JzG6ZCvUh2GJDlyJfkUJ54QNvZBPWYJAQTou8Pou42fPUSwpecJ827K_cxLnItRc2Vr_KIDZBx6ShDSPXZJXLPdND8BBjbW5yR7jkBOpoxVy_B8ShdCtVjZ7RpbmZrXJglF3jQJC9980GObQQrTl3YZo0xV6DqPgiJoiBTYV5u0M_B1f9nGS1p_elze_AOxg-iu2qSwQf0Yh6dFVwXnF141xO-p64D4AU-_dWxNVbS2DiznosB9XQ

#rayesanoud Manager
#eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkpBWTU0cndkcDZxUDg3Z1ZNLUlMZiJ9.eyJpc3MiOiJodHRwczovL3Rlc3QtYWxhbm91ZC51cy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDExNjE3MjQ1ODcyODgzNDM1MDciLCJhdWQiOlsiZHJpbmtzIiwiaHR0cHM6Ly90ZXN0LWFsYW5vdWQudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTU5NjY3MzMwNiwiZXhwIjoxNTk2NjgwNTA2LCJhenAiOiIzSGQ0T2Y3S1JRcTViaUZXMXkzZ2xROEE1V2haNFJuMiIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6ZHJpbmtzIiwiZ2V0OmRyaW5rcy1kZXRhaWwiLCJwYXRjaDpkcmlua3MiLCJwb3N0OmRyaW5rcyJdfQ.WenJ4Pv35ed47pw9JMh__l8XMFE_TN_hcwVnFMVG_fve2cl8ivt9OgXzPlLfi7Fj_SGyCjiVLtOExn9pxuRl32UIxozKpjIag7DEJ7VWMMJtV7NuK6y8fPirQY2Atgk5LLiKnG_H2m4n1cCxQijoTWivSZkCuXeyLpGBhuzyZV21jPO5ZS7eAMLLcOdxvOEp-rREQZRIDoxKqCtOoL4-hIylPMDKG8VCnFrwZLRvM0JtkwPmY7O9rNu54GXaDPjX8HCq-Wgip1a6BOhpGjqPUhs6zrolCrEhgHRS_9kRYXbgMxclTsGxx7TkWc4_WH0W8IxF1YA5qyOO6-vLcjb2pg&scope=openid%20profile%20email&expires_in=7200&token_type=Bearer&state=g6Fo2SB1QWlNTUY5bjBfQ2pqTzloemxTV3R2dl9QSE5nQ3kzd6N0aWTZIFhqRjdub2hscGJYRUFrZGpaZExKbGMzaVU0WDZIZXZCo2NpZNkgM0hkNE9mN0tSUXE1YmlGVzF5M2dsUThBNVdoWjRSbjI