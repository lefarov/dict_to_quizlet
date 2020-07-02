
import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS

from leo import search
from docs import list_docs, get_creds, get_folder_id, append_transalation


BOOKS = [
    {
        "id": uuid.uuid4().hex,
        'title': 'On the Road',
        'author': 'Jack Kerouac',
        'read': True
    },
    {
        "id": uuid.uuid4().hex,
        'title': 'Harry Potter and the Philosopher\'s Stone',
        'author': 'J. K. Rowling',
        'read': False
    },
    {
        "id": uuid.uuid4().hex,
        'title': 'Green Eggs and Ham',
        'author': 'Dr. Seuss',
        'read': True
    }
]

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


def get_book_index(book_id):
    for i, book in enumerate(BOOKS):
        if book["id"] == book_id:
            return i

    raise ValueError("trying to access unexisting book.")


# Sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@app.route("/translate/<query>", methods=["GET"])
def translate(query):
    response_object = {"status": "success"}
    results = search(query, "https://dict.leo.org/german-english/")
    response_object["translation"] = results
    return jsonify(response_object)


@app.route('/docs/<folder>', methods=['GET', 'POST'])
def docs(folder):
    response_object = {"status": "success"}
    creds = get_creds()

    if request.method == "POST":
        return  # create folder here    
    elif request.method == "GET":
        folder_id = get_folder_id('leo2quizlet', creds)
        response_object["docs"] = list_docs(folder_id, creds)
    return jsonify(response_object)


@app.route('/append_translation/<doc_id>', methods=["POST"])
def append_translation(doc_id):
    response_object = {"status": "success"}
    creds = get_creds()
    
    payload = request.get_json()
    append_transalation(
        payload.get('term', ''),
        payload.get('translation', ''), 
        doc_id, creds)

    response_object["message"] = f"Translation is appended to {doc_id}"
    return jsonify(response_object)


@app.route('/books', methods=['GET', 'POST'])
def all_books():
    response_object = {"status": "success"}
    
    if request.method == "POST":
        BOOKS.append({"id": uuid.uuid4().hex, **request.get_json()})
        response_object["message"] = "Book is added!"
    else:
        response_object["books"]  = BOOKS 

    return jsonify(response_object)


@app.route("/books/<book_id>", methods=["PUT", "DELETE"])
def single_book(book_id):
    response_object = {"status": "success"}
    
    if request.method == "PUT":
        BOOKS[get_book_index(book_id)].update(request.get_json())
        response_object["message"] = "Book is updated!"
    else:
        BOOKS[:] = [book for book in BOOKS if book["id"] != book_id]
        response_object["message"] = "Book is removed!"

    return jsonify(response_object)


if __name__ == '__main__':
    app.run()
