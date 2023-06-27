import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
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

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", [email])
        user = cur.fetchone()
        # print(user) = (1, 'admin@website.com', 'admin', '', '$2b$12$9.xkOBOu8gvYWDrWzcj56er/j029XsGBfWzvJLQIJXiajic53LKaK')
        # the data user return is a tuple
        cur.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')):
            session['user'] = user, {'first_name': user[2], 'last_name': user[3]}
            return redirect(url_for('home'))
        else:
            return 'Login failed!'

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users (email, first_name, last_name, password) VALUES (%s, %s, %s, %s)",
            (email, first_name, last_name, hashed_password)
        )
        mysql.connection.commit()
        cur.close()

        session['user'] = {'email': email, 'first_name': first_name, 'last_name': last_name}
        return redirect(url_for('home'))

    return render_template('signup.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user information from the session
    return redirect(url_for('home'))


@app.route('/employer')
def employee():
    return 'Employee Page'


if __name__ == '__main__':
    app.run(debug=True)
