from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'ooo'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

class Book(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    isbn = db.Column(db.String(100), unique=True)
    price = db.Column(db.Float(100))
    quantity = db.Column(db.Integer)

    def __init__(self,title,author,isbn,price,quantity):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.price = price
        self.quantity = quantity

class BookSchema(ma.Schema):
    class Meta:
        fields = ('id','title','author','isbn','price','quantity')
Book_schema = BookSchema()
Books_schema = BookSchema(many=True)
app.app_context().push()

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username=='admin' and password=='balaji':
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token),200
    else:
        return jsonify({"message":"Invalid username or password"}), 401

@app.route('/book',methods=['POST'])
@jwt_required()
def add_books():
    title = request.json['title']
    author = request.json['author']
    isbn = request.json['isbn']
    price = request.json['price']
    quantity = request.json['quantity']
    new_Book = Book(title, author, isbn, price, quantity)
    db.session.add(new_Book)
    db.session.commit()
    return Book_schema.jsonify(new_Book)

@app.route('/book',methods=['GET'])
@jwt_required()
def show_all_book():
    all_Books = Book.query.all()
    result = Books_schema.dump(all_Books)
    return jsonify(result)

@app.route('/book/<id>', methods=['GET'])
@jwt_required()
def getBookByid(id):
    book = Book.query.get(id)
    result = Book_schema.dump(book)
    return jsonify(result)

@app.route('/book/<author>',methods=['PUT'])
@jwt_required()
def updateUserByauthor(author):
    book = Book.query.filter_by(author=author).first()
    if book:
        title = request.json.get('title')
        price = request.json.get('price')
        quantity = request.json.get('quantity')
        if title is not None:
            book.title = title
        if price is not None:
            book.price = price
        if quantity is not None:
            book.quantity = quantity
    db.session.commit()
    return Book_schema.jsonify(book)

@app.route('/book/<id>', methods=['DELETE'])
@jwt_required()
def delete_book(id):
    book = Book.query.get(id)
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Book deleted successfully"}), 200
    else:
        return jsonify({"error": "Book not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=2002)