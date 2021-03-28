import os
import psycopg2
import requests
from flask import Flask, redirect, url_for, render_template, request, session
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func

DATABASE_URL = os.environ['DATABASE_URL']
USER_PASSWORD = os.environ['USER_PASSWORD']
APP_SECRET_KEY = os.environ['APP_SECRET_KEY']
BASE_URL = os.environ['BASE_URL']

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

# argumentos do item a serem editados
item_update_args = reqparse.RequestParser()
item_update_args.add_argument("desc", type=str)
item_update_args.add_argument("link", type=str)
item_update_args.add_argument("pic", type=str)

# parâmetros para o filtro do decorator marshal_with
resource_fields = {"item": fields.String,
                   "desc": fields.String,
                   "link": fields.String,
                   "pic": fields.String,
                   "possui": fields.Boolean}


class Item(Resource):

    @marshal_with(resource_fields)
    def get(self, item): 
        # retorna o item passado como parâmetro
        wishlist_item = Wishlist.query.filter_by(item=item).first()

        if not wishlist_item:
            # checa se o item existe
            abort(404, message="Item not found.")

        return wishlist_item, 200


    @marshal_with(resource_fields)
    def put(self, item): 
        # insere na lista o item passado como parâmetro, aceitando parâmetros opcionais
        args = item_put_args.parse_args()
        wishlist_item = Wishlist.query.filter_by(item=item).first()

        if wishlist_item: 
            # checa se o item já existe na lista
            abort(409, message="O item inserido já existe.")

        # cria o objeto item
        item = Wishlist(item=item, desc=args["desc"], link=args["link"], pic=args["pic"], possui=False)

        # adiciona o item na db
        db.session.add(item)
        db.session.commit()

        return item, 201


    @marshal_with(resource_fields)
    def patch(self, item):
        # edita as características do item passado como parâmetro
        args = item_update_args.parse_args()
        wishlist_item = Wishlist.query.filter_by(item=item).first()

        if not wishlist_item:
            # checa se o item existe
            abort(404, message="Item não encontrado.")

        # atualiza os argumentos caso existam alterações
        if args["desc"]:
            wishlist_item.desc = args["desc"]
        if args["link"]:
            wishlist_item.link = args["link"]
        if args["pic"]:
            wishlist_item.pic = args["pic"]

        db.session.commit()

        return wishlist_item, 200


    @marshal_with(resource_fields)
    def delete(self, item):
        # deleta o item passado como parâmetro
        wishlist_item = Wishlist.query.filter_by(item=item).first()

        if not wishlist_item:
            # checa se o item existe
            abort(404, message="Item não encontrado.")

        db.session.delete(wishlist_item)
        db.session.commit()

        return "", 204


class Owned(Resource):

    def get(self, item):
        # redireciona para o patch
        response = requests.patch(BASE_URL + r"wishlist/" + item + r"/owned/")

    @marshal_with(resource_fields)
    def patch(self, item):
        # altera o status do item para obtido/não obtido
        wishlist_item = Wishlist.query.filter_by(item=item).first()

        if not wishlist_item:
            # checa se o item existe
            abort(404, message="Item não encontrado.")

        wishlist_item.possui = not wishlist_item.possui
        db.session.commit()


class Random(Resource):

    @marshal_with(resource_fields)
    def get(self):
        # retorna um item aleatório da lista (considera apenas os itens não obtidos) 
        wishlist_item = Wishlist.query.filter_by(possui=False).order_by(func.random()).first()

        if not wishlist_item:
            # checa se há itens disponíveis na lista
            abort(404, message="Não há itens disponíveis na lista.")

        return wishlist_item, 200


@app.route("/")
def home():
    # template para a tela inicial
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    # realiza o login
    if request.method == "POST":
        # recebe o password
        password = request.form["pwd"]

        # checa se o password está na lista de senhas
        if password in USER_PASSWORD:
            user = "Admin"

        # adiciona o user a sessão
        session["user"] = user

        # redireciona para a wishlist
        return redirect(url_for("wishlist"))

    else:
        if "user" in session:
            # caso já tenha uma sessão iniciada, redireciona para a wishlist
            return redirect(url_for("wishlist"))
           
        return render_template("login.html") # exibe a página de login 


@app.route("/logout")
def logout():
    session.pop("user", None) # realiza o logout retirando o user da sessão
    return redirect(url_for("home")) # redireciona a página inicial


@app.route("/wishlist", methods=["POST", "GET"])
def wishlist():
    if "user" in session:
        #checa se há sessão iniciada
        user = session["user"]

        if request.method == "POST":

            # recebe os parâmetros
            item = request.form["item"]
            desc = request.form["desc"]
            link = request.form["link"]
            pic = request.form["pic"]

            # cria o item
            data = {item: {"desc": desc,
                           "link": link,
                           "pic": pic}}

            # recebe a ação selecionada
            action = request.form["btnradio"]

            # realiza o método de acordo com a ação
            if action == "edit":
                response = requests.patch(BASE_URL + r"wishlist/" + item, data[item])
            elif action == "delete":
                response = requests.delete(BASE_URL + r"wishlist/" + item)
            elif action == "status":
                response = requests.patch(BASE_URL + r"wishlist/" + item + r"/owned/")
            else:
                response = requests.put(BASE_URL + r"wishlist/" + item, data[item])

        # retorna o template da wishlist, enviando os objetos necessários
        return render_template("wishlist.html",
                               lista_all=enumerate(Wishlist.query.filter_by(possui=False).all()),
                               lista_owned=enumerate(Wishlist.query.filter_by(possui=True).all()),
                               URL_want=[r"/wishlist/" + i.item for i in Wishlist.query.filter_by(possui=False).all()],
                               URL_own=[r"/wishlist/" + i.item for i in Wishlist.query.filter_by(possui=True).all()])
    else:
        return redirect(url_for("login")) # redireciona para login caso não haja sessão

#rotas da api
api.add_resource(Item, r"/wishlist/<string:item>")
api.add_resource(Owned, r"/wishlist/<string:item>/owned/")
api.add_resource(Random, r"/wishlist/random/")

# roda o app
if __name__ == "__main__":
    db.create_all()
    app.run()
