from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import requests
import config



app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Custom filter to replace newlines with <br> tags
def nl2br(value):
    return value.replace('\n', '<br>\n')

# Register the filter
app.jinja_env.filters['nl2br'] = nl2br

@app.route('/')
def welcome():
    ''' homepage '''
    return render_template('welcome.html')



@app.route('/form', methods=['GET', 'POST'])
def index():
    ''' recipegen form page '''
    if request.method == 'POST':
        # Get form data
        produce = request.form['produce']
        protein = request.form['protein']
        dish_style = request.form['dish_style']
        cuisine_style = request.form['cuisine_style']
        servings = request.form['servings']

        # Save form data in session
        session['produce'] = produce
        session['protein'] = protein
        session['dish_style'] = dish_style
        session['cuisine_style'] = cuisine_style
        session['servings'] = servings

        # Redirect to recipe page
        return redirect(url_for('recipe'))

    # Render the HTML template with the form
    return render_template('index.html')

@app.route('/recipe')
def recipe():
    ''' recipegen recipe output page '''
    # Get form data from session
    produce = session.get('produce', '')
    protein = session.get('protein', '')
    dish_style = session.get('dish_style', '')
    cuisine_style = session.get('cuisine_style', '')
    servings = session.get('servings', '')

    # JSON data to be sent to API endpoint
    payload = {
                "body": {
                    "usr": "default_user",
                    "ingredients": {
                        "produce": produce,
                        "protein": protein,
                        "dish_style": dish_style,
                        "cuisine_style": cuisine_style,
                        "servings": servings
                    }
                }
    }

    # Sending a GET request to API_ENDPOINT with the JSON data
    response = requests.post(config.API_ENDPOINT, json=payload)
    if response.status_code == 200:
        # Extract response body
        recipe_body = response.text

        return render_template('recipe.html',  recipe_body=recipe_body)
    else:
        # Handle error
        return "Error: Unable to fetch recipe from API"


if __name__ == '__main__':
    app.run(debug=True,host=config.HOST, port=config.PORT)
