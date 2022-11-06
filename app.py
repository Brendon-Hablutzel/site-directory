from flask import Flask, request, render_template, redirect
from flask_cors import CORS
import database as db
import werkzeug


app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
@app.route('/<path:category>', methods=['GET'])
def list_view(category=None):
    pages_query = db.session.query(db.Page)
    if category:
        pages_query = pages_query.filter_by(category=category)
    pages = pages_query.order_by(db.Page.category).all()
    return render_template('index.html', pages=pages, category=category)


@app.route('/redirect/<id>', methods=['GET'])
def redirect_to_page(id):
    page_obj = db.session.query(db.Page).filter_by(id=id).first()
    if not page_obj:
        return 'No page found'
    return redirect(page_obj.url)


@app.route('/pages', methods=['GET'])
def pages_complete():
    pages = db.session.query(db.Page).all()
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


@app.route('/page', methods=['POST'])
@app.route('/page/<id>', methods=['GET', 'PATCH', 'DELETE'])
def page(id=None):
    method = request.method
    if method == "POST":
        data = request.get_json()
        db.session.add(
            db.Page(
                name=data['name'],
                category=data['category'],
                url=data['url']
            )
        )
        db.session.commit()
        return {
            "method": method,
            "success": True
        }
    else:
        page_query = db.session.query(db.Page).filter_by(id=id)
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
            db.session.commit()
            return {
                "method": method,
                "success": True
            }

        elif method == "DELETE":
            page_query.delete()
            db.session.commit()
            return {
                "method": method,
                "success": True
            }


@app.errorhandler(werkzeug.exceptions.NotFound)
def handle_not_found(err):
    return {
        "success": False,
        "message": "Not found",
        "method": request.method
    }, 404


if __name__ == "__main__":
    app.run()