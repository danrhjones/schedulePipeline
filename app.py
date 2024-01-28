import os
from flask import Flask

from api.pipelines import pipelines
from waitress import serve

# from flask_cors import CORS
# from api.product import product_route
# from api.user import user_route
# from mongoengine import connect

app = Flask(__name__)
app.register_blueprint(pipelines)
# app.register_blueprint(product_route)

# CORS(app)

# connect(host=os.environ.get('MONGO_URI'))

if __name__ == "__main__":
    # app.debug = True
    serve(app, port="8080")
