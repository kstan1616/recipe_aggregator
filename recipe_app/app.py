from flask import Flask, render_template, request, url_for
from recipe_aggregator import get_ingredients
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app)

@app.route('/')
@app.route("/index", methods=["GET", "POST"])
def index():
    url = 'https://image.freepik.com/foto-gratis/vista-aerea-placa-blanca-vacia-sobre-fondo-azul_23-2147865612.jpg'
    if request.method == "POST":
        try:
            recipe_urls = request.form['recipe_urls']
        except:
            recipe_urls = ''
        recipe_urls = recipe_urls + '\n' + request.form['added_recipe']
        return render_template('index.html', url=url, recipe_urls=recipe_urls)
    else:
        recipe_urls = ''
        return render_template('index.html', url=url, recipe_urls=recipe_urls)

@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        ingredient_list = get_ingredients()
        recipe_urls = request.form['recipe_urls'].split('\n')
        print(recipe_urls)
        for recipe_link in recipe_urls:
            if 'epicurious' in recipe_link:
                ingredient_list.scrape_ingredients(recipe_link, 'epi')
            if 'nytimes' in recipe_link:
                ingredient_list.scrape_ingredients(recipe_link, 'nyt')
            if 'allrecipes' in recipe_link:
                ingredient_list.scrape_ingredients(recipe_link, 'all')
        ingredient_list.clean_list()
        recipe = ingredient_list.final_df
        return render_template('add_recipe.html', recipe=recipe.to_html(classes='data', header="true"))
    else:
        url = 'https://media.istockphoto.com/photos/empty-plate-with-knife-and-fork-on-white-kitchen-table-picture-id613022722?k=6&m=613022722&s=612x612&w=0&h=Fr-1qc4a04U0fI0wUlrTu1I-UeGycNNtMlN7pPPXAtc='
        return render_template('index.html', url=url)


@app.route("/recipe_sent", methods=["GET", "POST"])
def recipe_sent():
    email = request.form['recipe_sent']
    # recipe_list = request.form['recipe_list']
    # msg = Message("Recipe List",
    #               sender="kyle.m.stanley16@gmail.com",
    #               recipients=["kyle.m.stanley16@gmail.com"])
    # msg.html = recipe_list
    # mail.send(msg)
    return render_template('recipe_sent.html', email=email)

@app.route("/blog", methods=["GET", "POST"])
def blog():
    return render_template('blog.html')

@app.route("/post", methods=["GET", "POST"])
def post():
    return render_template('post.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
