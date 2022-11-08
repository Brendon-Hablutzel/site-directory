from flask import Flask, request, render_template, redirect
from flask_cors import CORS
import database as db
import werkzeug
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
CORS(app)


@app.route('/view', methods=['GET'])
@app.route('/view/<path:category>', methods=['GET'])
def list_view(category=None):
    db_session = scoped_session(sessionmaker(bind=db.engine))
    pages_query = db_session.query(db.Page)
    if category:
        pages_query = pages_query.filter(db.Page.category.ilike(category.lower() + "%"))
    pages = pages_query.order_by(db.Page.category).all()
    return render_template('view.html', pages=pages, category=category)


@app.route('/add', methods=['POST', 'GET'])
@app.route('/add/<name>/<path:url>', methods=['GET'])
def add_page(name=None, url=None):
    if request.method == 'POST':
        data = request.get_json()
        db_session = scoped_session(sessionmaker(bind=db.engine))
        db_session.add(
            db.Page(
                name=data['name'],
                category=data['category'],
                url=data['url']
            )
        )
        db_session.commit()
        return {
            "method": request.method,
            "success": True
        }

    elif request.method == 'GET':
        return render_template('add.html', name=name, url=url)


@app.route('/redirect/<id>', methods=['GET'])
def redirect_to_page(id):
    db_session = scoped_session(sessionmaker(bind=db.engine))
    page_obj = db_session.query(db.Page).filter_by(id=id).first()
    if not page_obj:
        return 'No page found'
    return redirect(page_obj.url)


@app.route('/pages', methods=['GET'])
def pages_complete():
    db_session = scoped_session(sessionmaker(bind=db.engine))
    pages = db_session.query(db.Page).all()
    return {
        "success": True,
        "pages": [
            {
                "id": page.id,
                "name": page.name,
                "category": page.category,
                "url": page.url
            } for page in pages
        ]
    }


@app.route('/page/<id>', methods=['GET', 'PATCH', 'DELETE'])
def page(id=None):
    method = request.method
    db_session = scoped_session(sessionmaker(bind=db.engine))
    page_query = db_session.query(db.Page).filter_by(id=id)
    page_obj = page_query.first()

    if not page_obj:
        return {
            "success": False,
            "method": method,
            "message": f"No page found with id {id}"
        }

    if method == "GET":
        return {
            "method": method,
            "success": True,
            "page": {
                "id": page_obj.id,
                "name": page_obj.name,
                "url": page_obj.url,
                "category": page_obj.category
            }
        }

    elif method == "PATCH":
        data = request.get_json()
        for attr in ["category", "name", "url"]:
            val = data.get(attr)
            if val:
                setattr(page_obj, attr, val)
        db_session.commit()
        return {
            "method": method,
            "success": True
        }

    elif method == "DELETE":
        page_query.delete()
        db_session.commit()
        return {
            "method": method,
            "success": True
        }


@app.errorhandler(werkzeug.exceptions.NotFound)
def handle_not_found(err):
    return {
        "success": False,
        "message": str(err),
        "method": request.method
    }, 404


if __name__ == "__main__":
    app.run(host='0.0.0.0')
