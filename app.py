import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)
from pymongo import MongoClient
from bson import ObjectId

# Conectar con MongoDB
client = MongoClient('mongodb+srv://{MONGO_USER}:{MONGO_PASS}@cluster0.{MONGO_CLUSTER}.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
                     .format(**os.environ))
db = client["bookstore"]
collection = db["books"]

# Crear una instancia de Flask
app = Flask(__name__)


@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


# Ruta para obtener todos los libros
@app.route("/books", methods=["GET"])
def get_books():
    books = []
    for book in collection.find():
        book["_id"] = str(book["_id"])
        books.append(book)
    return jsonify({'books':books})

# Ruta para obtener un libro por su ID
@app.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    book = collection.find_one({"_id": ObjectId(book_id)})
    if book:
        book["_id"] = str(book["_id"])
        return jsonify(book)
    else:
        return jsonify({"error": "Libro no encontrado"}), 404

# Ruta para agregar un nuevo libro
@app.route("/books/", methods=["POST"])
def create_book():
    book_data = request.json
    result = collection.insert_one(book_data)
    return jsonify({"id": str(result.inserted_id)}), 201

# Ruta para actualizar un libro por su ID
@app.route("/books/<book_id>", methods=["PUT"])
def update_book(book_id):
    book_data = request.json
    result = collection.update_one({"_id": ObjectId(book_id)}, {"$set": book_data})
    if result.modified_count == 1:
        return jsonify({"message": "Libro actualizado exitosamente"})
    else:
        return jsonify({"error": "Libro no encontrado"}), 404

# Ruta para eliminar un libro por su ID
@app.route("/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    result = collection.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Libro eliminado exitosamente"})
    else:
        return jsonify({"error": "Libro no encontrado"}), 404


if __name__ == '__main__':
   app.run()
