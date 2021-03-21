from flask import Flask, redirect, url_for
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from dotenv import load_dotenv
import urllib.parse as up
import psycopg2, os

load_dotenv()

up.uses_netloc.append("postgres")
url = up.urlparse(os.environ['DATABASE_URL'])
conn = psycopg2.connect(database=url.path[1:],
                        user=url.username,
                        password=url.password,
                        host=url.hostname,
                        port=url.port)

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)

@app.route("/")
def home():
    return "<h1> HOME PAGE <h1>"


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


class Lista(Resource):

    @marshal_with(resource_fields) 
    def get(self):
        args = item_put_args.parse_args()
        output = Wishlist.query.all()

        if not output:
            abort(404, message="Não há itens na lista.")

        return output, 200


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


class Obtido(Resource):

    @marshal_with(resource_fields)
    def patch(self,item):
        output = Wishlist.query.filter_by(item=item).first()

        if not output:
            abort(404, message="Item não encontrado.")

        output.possui = not output.possui
        db.session.commit()

        return output, 200


class Random(Resource): 

    @marshal_with(resource_fields) 
    def get(self):
        output = Wishlist.query.filter_by(possui=False).order_by(func.random()).first()

        if not output:
            abort(404, message="Não há itens disponíveis na lista.")

        return output, 200


api.add_resource(Lista, r"/itens/")
api.add_resource(Item, r"/itens/<string:item>/")
api.add_resource(Obtido, r"/itens/<string:item>/obtido/")
api.add_resource(Random, r"/itens/random/")

if __name__ == "__main__":
    app.run()
