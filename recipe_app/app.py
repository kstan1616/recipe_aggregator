from flask import Flask, render_template, request
import random
from recipe_aggregator import get_ingredients

app = Flask(__name__)

# list of cat images

@app.route('/')
@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "POST":
    	add_recipe()
    else:
        url = 'https://media.istockphoto.com/photos/empty-plate-with-knife-and-fork-on-white-kitchen-table-picture-id613022722?k=6&m=613022722&s=612x612&w=0&h=Fr-1qc4a04U0fI0wUlrTu1I-UeGycNNtMlN7pPPXAtc='
        return render_template('index.html', url=url)

@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    try:
        recipe_link = request.form['added_recipe_nyt']
        recipe = get_ingredients(recipe_link, 'nyt')
    except:
        try:
            recipe_link = request.form['added_recipe_epi']
            recipe = get_ingredients(recipe_link, 'epi')
        except:
            try:
                recipe_link = request.form['added_recipe_all']
                recipe = get_ingredients(recipe_link, 'all')
            except:
                url = 'https://media.istockphoto.com/photos/empty-plate-with-knife-and-fork-on-white-kitchen-table-picture-id613022722?k=6&m=613022722&s=612x612&w=0&h=Fr-1qc4a04U0fI0wUlrTu1I-UeGycNNtMlN7pPPXAtc='
                return render_template('index.html', url=url)
    return render_template('add_recipe.html', recipe=recipe.to_html(classes='data', header="true"))

@app.route("/recipe_sent", methods=["GET", "POST"])
def recipe_sent():
    email = request.form['recipe_sent']
    return render_template('recipe_sent.html', email=email)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
