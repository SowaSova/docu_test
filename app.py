import json
from http import HTTPStatus

from bson import json_util
from flask import Flask, request
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError


MONGO_URI = "mongodb://db:27017/myDatabase"
COLLECTION_NAME = "collection"
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080

app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)

collection = mongo.db[COLLECTION_NAME]
collection.create_index("key", unique=True)


@app.route("/", methods=["GET", "POST", "PUT"])
def index():
    if request.method == "POST":
        key = str(request.json["key"])
        value = request.json["value"]
        try:
            mongo.db.collection.insert_one({"key": key, "value": value})
            return {"result": "Объект создан"}, HTTPStatus.CREATED
        except DuplicateKeyError:
            return {
                "error": f"Ключ {key} уже существует"
            }, HTTPStatus.BAD_REQUEST

    elif request.method == "PUT":
        key = request.args.get("key")
        new_value = request.json["new_value"]
        doc = mongo.db.collection.find_one({"key": key})
        if doc is None:
            return {
                "error": f"Ключа {key} не существует"
            }, HTTPStatus.NOT_FOUND
        mongo.db.collection.update_one(
            {"key": key}, {"$set": {"value": new_value}}
        )
        return {
            "result": f"Новое значение ключа {key} успешно обновлено на {new_value}"
        }, HTTPStatus.OK

    elif request.method == "GET":
        key = request.args.get("key")
        doc = mongo.db.collection.find_one({"key": key})
        if doc is None:
            return {
                "error": f"Ключа {key} не существует"
            }, HTTPStatus.NOT_FOUND
        return json.loads(json_util.dumps(doc))


@app.route("/all/", methods=["GET"])
def get_all():
    docs = mongo.db.collection.find()
    return json.loads(json_util.dumps(docs))


if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)
