from flask import Flask, jsonify, render_template, request, redirect, url_for, abort, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Text, Column, ForeignKey
from flask_bootstrap import Bootstrap5
from forms import RegistrationForm, LoginForm, AddCafeForm
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os


datetime = datetime

app = Flask(__name__)
# TopSecretAPIKey = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SECRET_KEY'] = os.environ.get("FlaskConfigKey", "dev")

Bootstrap5(app)

# Configure Flask-Login's Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE USER TABLE IN DB with the UserMixin
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()


# # CREATE CAFE TABLE IN DB
class Cafe(db.Model):
    __tablename__ = "cafe"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)
    # author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    # author = relationship("User", back_populates="cafe")

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    year = datetime.now().year
    return render_template("index.html", year=year)


@app.route("/places", methods=["GET"])
def places():
    year = datetime.now().year
    with app.app_context():
        result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
        all_cafes = result.scalars().all()
        cafes = [cafe.to_dict() for cafe in all_cafes]
        num_cafes = len(cafes)
    return render_template("places.html", cafes=cafes, num_cafes=num_cafes, year=year)


@app.route("/join", methods=["GET", "POST"])
def join():
    year = datetime.now().year
    form = LoginForm()
    if form.validate_on_submit():
        email = request.form.get("email")
        password = request.form.get("password")
        # Find user by email entered.
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('register'))
        # Check stored password hash against entered password hashed.
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again")
            return redirect(url_for('join'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("join.html", form=form, current_user=current_user, year=year)


@app.route("/register", methods=["GET", "POST"])
def register():
    year = datetime.now().year
    form = RegistrationForm()
    if form.validate_on_submit():
        email = request.form.get("email")
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            # User already exists
            flash("This email already exist, login instead!")
            return redirect(url_for('join'))
        hash_and_salted_password = generate_password_hash(request.form.get("password"), method="pbkdf2", salt_length=5)

        with app.app_context():
            new_user = User(name=request.form.get("name"),
                            email=request.form.get("email"),
                            password=hash_and_salted_password

                            )
            db.session.add(new_user)
            db.session.commit()
            # Log in and authenticate user after adding details to database.
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template("register.html", form=form, current_user=current_user, year=year)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# Create the add_cafe route
@app.route('/add_cafe', methods=['GET', 'POST'])
def add_cafe():
    year = datetime.now().year
    form = AddCafeForm()
    if form.validate_on_submit():
        with app.app_context():
            new_cafe = Cafe(name=request.form.get("name"),
                            map_url=request.form.get("map_url"),
                            img_url=request.form.get("img_url"),
                            location=request.form.get("location"),
                            seats=request.form.get("seats"),
                            has_toilet=bool(request.form.get("has_toilet")),
                            has_wifi=bool(request.form.get("has_wifi")),
                            has_sockets=bool(request.form.get("has_sockets")),
                            can_take_calls=bool(request.form.get("can_take_calls")),
                            coffee_price=request.form.get("coffee_price"),

                            )
            db.session.add(new_cafe)
            db.session.commit()
            return redirect(url_for('places'))

    return render_template("add_place.html", form=form, year=year)


@app.route('/cafe/<int:cafe_id>', methods=['GET', 'POST'])
def show_cafe(cafe_id):
    requested_cafe = db.get_or_404(Cafe, cafe_id)

    return render_template("cafe.html", cafe=requested_cafe)


if __name__ == '__main__':
    app.run(debug=True)
