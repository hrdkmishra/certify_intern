from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_mysqldb import MySQL
from forms import SignupForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '2394239482048209fdsfew3hh'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
mysql = MySQL(app)

# with app.app_context():
#     try:
#         connection = mysql.connection
#         if connection is not None:
#             print("MySQL connection successful!")
#         else:
#             print("MySQL connection failed.")
#     except Exception as e:
#         print("An error occurred while connecting to MySQL:", e)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Perform validation and authentication logic here
        if email == 'example@example.com' and password == 'password':
            # Successful login
            return 'Login successful!'
        else:
            # Invalid credentials
            return 'Invalid email or password'

    return render_template('login.html', form=form)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users (email, first_name, last_name, password) VALUES (%s, %s, %s, %s, %s)",
            (email, password)
        )
        mysql.connection.commit()
        cur.close()

        return 'Signup successful!'

    return render_template('signup.html', form=form)


@app.route('/employer')
def employee():
    return 'Employee Page'


if __name__ == '__main__':
    app.run(debug=True)
