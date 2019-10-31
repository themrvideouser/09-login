from flask import Flask, render_template, request, redirect, url_for, make_response
from model import User, db
import hashlib
import uuid

app = Flask(__name__)
# erstellt neue datenbank Tabelle
db.create_all()


@app.route("/")
def index():
    session_token = request.cookies.get("session_token")
    # email_address = request.cookies.get("email")
    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
        # user = db.query(User).filter_by(email=email_address).first()
    else:
        user = None
        # print(user.name)
    return render_template("index.html", user=user)


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password_clear = request.form.get("user-password")
    password_hashed = hashlib.sha256(password_clear.encode()).hexdigest()

    # Neues Objekt vom Type User (Model)
    user = db.query(User).filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email, password=password_hashed)
        db.add(user)
        db.commit()
    if password_hashed != user.password:
        return "Falsches Passwort eingegeben"
    elif password_hashed == user.password:
        session_token = str(uuid.uuid4())
        user.session_token = session_token
        db.add(user)
        db.commit()

    # Cookie
    response = make_response(redirect(url_for('index')))
    response.set_cookie("session_token", session_token, httponly=True, samesite="Strict")
    return response


if __name__ == "__main__":
    app.run()
