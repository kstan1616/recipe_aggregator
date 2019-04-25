from flask import Flask, render_template, request
import random

app = Flask(__name__)

# list of cat images

@app.route('/')
@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return render_template("add_recipe.html", recipe=recipe)
    else:
        url = 'https://clutchpoints.com/wp-content/uploads/2019/04/Russell-Westbrook.jpg'
        return render_template('index.html', url=url)

@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    recipe = request.form.get("recipe")
    return render_template('add_recipe.html', recipe=recipe)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
