from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__, instance_relative_config=True)
app.config["MONGO_URI"] = "mongodb://localhost:27017/smartroster"
mongo = PyMongo(app)


if __name__ == "__main__":
    app.run()