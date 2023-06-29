import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from forms import SignupForm, LoginForm, ProfileEditForm, InternForm

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
            session['user'] = {'id': user[0], 'email': user[1], 'first_name': user[2], 'last_name': user[3]}
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


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = ProfileEditForm()

    if form.validate_on_submit():
        # Retrieve the form data and update the user's profile in the database
        user_id = session['user']['id']

        company_name = form.company_name.data
        company_address = form.company_address.data
        company_city = form.company_city.data
        company_state = form.company_state.data
        company_zipcode = form.company_zipcode.data
        company_phone = form.company_phone.data
        company_email = form.company_email.data
        company_website = form.company_website.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO company (user_id,company_name, company_address, company_city, company_state,"
                    "company_zipcode,"
                    "company_phone_number, company_email, company_website) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        user_id, company_name, company_address, company_city, company_state, company_zipcode,
                        company_phone,
                        company_email, company_website))

        mysql.connection.commit()

        # recently added data in a variable

        cur.close()

        session['company'] = {'company_name': company_name, 'company_address': company_address,
                              'company_city': company_city, 'company_state': company_state,
                              'company_zipcode': company_zipcode,
                              'company_phone': company_phone, 'company_email': company_email,
                              'company_website': company_website}

        return redirect(url_for('profile'))

    # Retrieve the user's existing profile information from the database
    # Pre-fill the form fields with the retrieved data

    return render_template('profile.html', form=form)


@app.route('/intern', methods=['GET', 'POST'])
def intern():
    form = InternForm()

    # Fetch interns data from the database
    cur = mysql.connection.cursor()
    company_id = cur.execute("SELECT id FROM company WHERE user_id = %s", [session['user']['id']])
    cur.execute("SELECT * FROM interns WHERE company_id = %s", [company_id])
    interns = cur.fetchall()
    cur.close()

    if form.validate_on_submit():
        # Retrieve the form data and save the intern details in the database
        first_name = form.first_name.data
        last_name = form.last_name.data
        designation = form.designation.data
        email = form.email.data
        start_date = form.start_date.data
        end_date = form.end_date.data

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO interns (company_id, first_name, last_name, designation, email, start_date, end_date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (company_id, first_name, last_name, designation, email, start_date, end_date))
        mysql.connection.commit()
        cur.close()

        # Refresh the interns data from the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM interns WHERE company_id = %s", [company_id])
        interns = cur.fetchall()
        cur.close()

    return render_template('intern.html', form=form, interns=interns)


@app.route('/employer')
def employee():
    return 'git test'


if __name__ == '__main__':
    app.run(debug=True)
