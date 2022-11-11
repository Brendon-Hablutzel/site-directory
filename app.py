from flask import Flask, request, render_template, redirect
from flask_cors import CORS
import werkzeug
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
db = SQLAlchemy(app)
CORS(app)

class Page(db.Model):
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)
    url = db.Column(db.String(255), unique=True)
    alias = db.Column(db.String(255), unique=True)
    category = db.Column(db.String(255)) # no leading or trailing slash

    def __repr__(self):
        return f"<Page(name={self.name}, url={self.url}, category={self.category})>"

with app.app_context():
    db.create_all()

@app.route('/view', methods=['GET'])
@app.route('/view/<path:category>', methods=['GET'])
def list_view(category=None):
    pages_query = db.session.query(Page)
    if category:
        pages_query = pages_query.filter(Page.category.ilike(category.lower() + "%"))
    pages = pages_query.order_by(Page.category).all()
    return render_template('view.html', pages=pages, category=category)


@app.route('/add', methods=['POST', 'GET'])
@app.route('/add/<name>/<path:url>', methods=['GET'])
def add_page(name=None, url=None):
    if request.method == 'POST':
        data = request.get_json()
        try:
            db.session.add(
                Page(
                    name=data['name'],
                    category=data['category'],
                    alias=data['alias'],
                    url=data['url']
                )
            )
            db.session.commit()
        except:
            return {
                "method": request.method,
                "success": False,
                "message": "Duplicate entry"
            }
        else:
            return {
                "method": request.method,
                "success": True
            }

    elif request.method == 'GET':
        return render_template('add.html', name=name, url=url)


@app.route('/redirect/<alias>', methods=['GET'])
def redirect_to_page(alias):
    page_obj = db.session.query(Page).filter_by(alias=alias).first()
    if not page_obj:
        return 'No page found'
    return redirect(page_obj.url)


@app.route('/pages', methods=['GET'])
def pages_complete():
    pages = db.session.query(Page).all()
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
    page_query = db.session.query(Page).filter_by(id=id)
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
                "category": page_obj.category,
                "alias": page_obj.alias
            }
        }

    elif method == "PATCH":
        data = request.get_json()
        for attr in ["category", "name", "url", "alias"]:
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
        "message": str(err),
        "method": request.method
    }, 404


if __name__ == "__main__":
    app.run(host='0.0.0.0')
