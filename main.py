import os
import json
import secrets
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, Response
from sqlalchemy.orm.exc import NoResultFound
from blogger import create_paste, update_paste, delete_paste


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Paste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    routes = [
        {"GET": "/"},
        {"GET": "/api"},
        {"POST": "/api"}
    ]
    return Response(json.dumps(routes), status=200, mimetype='application/json')


@app.route('/api/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def main():
    if request.method == 'GET':
        return "There's nothing to see here 👀"

    elif request.method == 'POST':
        data = request.get_json()
        key = secrets.token_urlsafe(8)

        if data['title'] and data['body'] is not None:
            paste_id, paste_url = create_paste(
                data['title'], data['body'], data['label']
            )
            row = Paste(id=paste_id, key=key)
            db.session.add(row)
            db.session.commit()
            response = Response(
                json.dumps({'url': paste_url, 'key': key, 'id': paste_id}),
                status=200,
                mimetype='application/json'
            )
            return response
        return Response(status=400)

    elif request.method == 'PUT':
        data = request.get_json()
        post_id = int(data['id'])
        key = data['key']

        query = db.session.execute(
            db.select(Paste).filter_by(key=key)
        )
        try:
            query = query.one()
        except NoResultFound:
            return Response('Permission denied', status=403)
        else:
            if query[0].id == post_id:
                if data['title'] and data['body'] is not None:
                    paste_url = update_paste(post_id, data['title'], data['body'], data['label'])
                    response = Response(
                        json.dumps(
                            {'url': paste_url, 'key': key, 'id': post_id}),
                        status=200,
                        mimetype='application/json'
                    )
                    return response
                return Response(status=400)

    elif request.method == 'DELETE':
        data = request.get_json()
        post_id = int(data['id'])
        key = data['key']
        query = db.session.execute(
            db.select(Paste).filter_by(key=key)
        )
        try:
            query = query.one()
        except NoResultFound:
            return Response('Permission denied', status=403)
        else:
            if query[0].id == post_id:
                delete_paste(post_id)
                db.session.delete(query[0])
                db.session.commit()
                return Response(status=200)
    else:
        return Response(status=405)


if __name__ == "__main__":
    app.run(debug=True)
