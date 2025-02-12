from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=True)

def generate_short_url():
    """Generate a random short URL."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=6))

# Initialize Database
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        custom_short = request.form['custom_short'].strip()  # Get custom short URL
        title = request.form['title']

        if custom_short:  # If the user provides a custom short URL
            existing_custom = URL.query.filter_by(short_url=custom_short).first()
            if existing_custom:
                flash("Custom short URL already taken! Try another one.", "danger")
                return render_template('index.html')

            short_url = custom_short
        else:
            short_url = generate_short_url()

        # Save to the database
        new_url = URL(original_url=original_url, short_url=short_url, title=title)
        db.session.add(new_url)
        db.session.commit()

        return render_template('index.html', short_url=short_url, title=title)

    return render_template('index.html')

@app.route('/<short_url>')
def redirect_url(short_url):
    url_entry = URL.query.filter_by(short_url=short_url).first()
    if url_entry:
        return redirect(url_entry.original_url)
    return "URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)
