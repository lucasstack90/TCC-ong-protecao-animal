from main import app
from flask import render_template

#Rotas, mas você pode adiconar mais rotas conforme as Pgs do site 
@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/Blog")
def Blog():
    return "Bem vindo ao Blog"