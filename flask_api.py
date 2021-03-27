from flask import Flask, redirect, url_for, render_template, request, session
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
import psycopg2, os, requests


DATABASE_URL = os.environ['DATABASE_URL']
DATABASE_USER = os.environ['DATABASE_USER']
APP_SECRET_KEY = os.environ['APP_SECRET_KEY']
BASE_URL = r"http://127.0.0.1:5000/"

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

app = Flask(__name__)
api = Api(app)
app.secret_key = APP_SECRET_KEY

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Wishlist(db.Model):
    item = db.Column(db.String(), primary_key=True)
    desc = db.Column(db.String(250))
    link = db.Column(db.String(250))
    pic = db.Column(db.String(250))
    possui = db.Column(db.Boolean)


# argumentos do item
item_put_args = reqparse.RequestParser()
item_put_args.add_argument("desc", type=str)  
item_put_args.add_argument("link", type=str)
item_put_args.add_argument("pic", type=str) 
item_put_args.add_argument("possui", type=bool) 

# argumentos do item a serem editados na lista
item_update_args = reqparse.RequestParser()
item_update_args.add_argument("desc", type=str)  
item_update_args.add_argument("link", type=str)  
item_update_args.add_argument("pic", type=str)


resource_fields = {"item": fields.String,
                   "desc": fields.String,
                   "link": fields.String,
                   "pic": fields.String,
                   "possui":fields.Boolean}


class Item(Resource):

    @marshal_with(resource_fields)
    def get(self, item):
        output = Wishlist.query.filter_by(item=item).first()

        if not output:
            abort(404, message="O item não foi encontrado.")

        return output, 200

    @marshal_with(resource_fields)
    def put(self, item):
        args = item_put_args.parse_args()
        output = Wishlist.query.filter_by(item=item).first()

        if output:
            abort(409, message="O item inserido já existe.")

        item = Wishlist(item=item, desc=args["desc"], link=args["link"], pic=args["pic"], possui=False)
        
        db.session.add(item)
        db.session.commit()
        
        return item, 201

    @marshal_with(resource_fields)
    def patch(self,item):
        args = item_update_args.parse_args()
        output = Wishlist.query.filter_by(item=item).first()

        if not output:
            abort(404, message="Item não encontrado.")

        if args["desc"]:
            output.desc = args["desc"]
        if args["link"]:
            output.link = args["link"]
        if args["pic"]:
            output.pic = args["pic"]

        db.session.commit()

        return output

    @marshal_with(resource_fields)
    def delete(self, item):
        output = Wishlist.query.filter_by(item=item).first()

        if not output:
            abort(404, message="Item não encontrado.")
            
        db.session.delete(output)        
        db.session.commit()

        return "", 204


class Owned(Resource):

    @marshal_with(resource_fields)
    def get(self,item):
        response = requests.patch(BASE_URL + "wishlist/" + item + "/owned/")


    @marshal_with(resource_fields)
    def patch(self,item):
        output = Wishlist.query.filter_by(item=item).first()

        if not output:
            abort(404, message="Item não encontrado.")

        output.possui = not output.possui
        db.session.commit()


class Random(Resource): 

    @marshal_with(resource_fields) 
    def get(self):
        output = Wishlist.query.filter_by(possui=False).order_by(func.random()).first()

        if not output:
            abort(404, message="Não há itens disponíveis na lista.")

        return output, 200



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods =["POST", "GET"])
def login():
    if request.method == "POST":
        password = request.form["pwd"]

        if password in DATABASE_USER:
            user = "Admin"

        session["user"] = user
        return redirect(url_for("wishlist"))
    else:
        if "user" in session:
            return redirect(url_for("wishlist"))
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route("/wishlist", methods =["POST", "GET", "PATCH"])
def wishlist():

    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            item = request.form["item"]
            desc = request.form["desc"]
            link = request.form["link"]
            pic = request.form["pic"]
            
            data = {item: {"desc": desc,
                            "link": link, 
                            "pic": pic}}

            action = request.form["btnradio"]
            
            if action == "edit":
                response = requests.patch(BASE_URL + "wishlist/" + item, data[item])
                # print(BASE_URL + "wishlist/" + item, data[item])     
            elif action == "delete":
                response = requests.delete(BASE_URL + "wishlist/" + item)
            elif action == "status":
                response = requests.patch(BASE_URL + "/wishlist/" + item + "/owned/")
            else:
                response = requests.put(BASE_URL + "wishlist/" + item, data[item])
   
        return render_template("wishlist.html",
                            lista_all=enumerate(Wishlist.query.filter_by(possui=False).all()), 
                            lista_owned=enumerate(Wishlist.query.filter_by(possui=True).all()), 
                            URL_want=[BASE_URL+ "wishlist/" + i.item for i in Wishlist.query.filter_by(possui=False).all()], 
                            URL_own=[BASE_URL+ "wishlist/" + i.item for i in Wishlist.query.filter_by(possui=True).all()])
    else:
        return redirect(url_for("login"))



api.add_resource(Item, r"/wishlist/<string:item>")
api.add_resource(Owned, r"/wishlist/<string:item>/owned/")
api.add_resource(Random, r"/wishlist/random/")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)