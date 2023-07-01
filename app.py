import bcrypt, datetime, qrcode, uuid, os, cv2, fitz, numpy as np
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from flask_mysqldb import MySQL
from forms import SignupForm, LoginForm, ProfileEditForm, InternForm
from werkzeug.utils import secure_filename
from pyzbar.pyzbar import decode
from PIL import Image


app = Flask(__name__)

app.config["SECRET_KEY"] = "23942394820482093"

# MySQL configurations
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "flask"
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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
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

        if user and bcrypt.checkpw(password.encode("utf-8"), user[4].encode("utf-8")):
            session["user"] = {
                "id": user[0],
                "email": user[1],
                "first_name": user[2],
                "last_name": user[3],
            }
            return redirect(url_for("home"))
        else:
            return "Login failed!"

    return render_template("login.html", form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data
        # confirm_password = form.confirm_password.data

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users (email, first_name, last_name, password) VALUES (%s, %s, %s, %s)",
            (email, first_name, last_name, hashed_password),
        )
        mysql.connection.commit()
        cur.close()

        session["user"] = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }
        return redirect(url_for("home"))

    return render_template("signup.html", form=form)


@app.route("/logout")
def logout():
    session.pop("user", None)  # Remove user information from the session
    return redirect(url_for("home"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    form = ProfileEditForm()

    user_id = session["user"]["id"]
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM company WHERE user_id = %s", [user_id])
    company_data = cur.fetchone()
    session["company_data"] = company_data
    cur.close()

    if "company_data" in session:
        company_data = session["company_data"]
    else:
        company_data = None

    if form.validate_on_submit():
        # Retrieve the form data and update the user's profile in the database
        user_id = session["user"]["id"]

        company_name = form.company_name.data
        company_address = form.company_address.data
        company_city = form.company_city.data
        company_state = form.company_state.data
        company_zipcode = form.company_zipcode.data
        company_phone = form.company_phone.data
        company_email = form.company_email.data
        company_website = form.company_website.data

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO company (user_id, company_name, company_address, company_city, company_state,company_zipcode, company_phone_number, company_email, company_website) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"(
                user_id,
                company_name,
                company_address,
                company_city,
                company_state,
                company_zipcode,
                company_phone,
                company_email,
                company_website,
            ),
        )
        mysql.connection.commit()
        cur.close()

        # Fetch the updated company data from the database
        session["company"] = {
            "company_name": company_name,
            "company_address": company_address,
            "company_city": company_city,
            "company_state": company_state,
            "company_zipcode": company_zipcode,
            "company_phone": company_phone,
            "company_email": company_email,
            "company_website": company_website,
        }

        return redirect(url_for("profile"))

    return render_template("profile.html", form=form, company_data=company_data)


def generateQrcode(qrcode_id):
    # Generate QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qrcode_id)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    # Save the QR code image
    qr_img.save(f"static/qr_codes/{qrcode_id}.png")


@app.route("/intern", methods=["GET", "POST"])
def intern():
    form = InternForm()
    user_id = session["user"]["id"]

    # Fetch interns data from the database
    cur = mysql.connection.cursor()

    cur.execute("SELECT id FROM company WHERE user_id = %s", [user_id])
    company_id = cur.fetchone()[0]
    print(company_id)
    cur.execute("SELECT * FROM interns WHERE user_id = %s", [user_id])
    interns = cur.fetchall()
    print(interns)
    cur.close()

    if form.validate_on_submit():
        # Retrieve the form data and save the intern details in the database
        first_name = form.first_name.data
        last_name = form.last_name.data
        designation = form.designation.data
        email = form.email.data
        start_date = form.start_date.data
        end_date = form.end_date.data

        # Generate a unique QR code ID
        qrcode_id = str(uuid.uuid4())

        # Generate QR code and save it
        generateQrcode(qrcode_id)

        cur = mysql.connection.cursor()

        cur.execute(
            "INSERT INTO interns (user_id,company_id, first_name, last_name, designation, email, start_date, end_date, qrcode_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                user_id,
                company_id,
                first_name,
                last_name,
                designation,
                email,
                start_date,
                end_date,
                qrcode_id,
            ),
        )
        mysql.connection.commit()
        cur.close()

        return redirect(url_for("intern"))

    return render_template("intern.html", form=form, interns=interns)


# upload qrcode in index.html
UPLOAD_FOLDER = "static/uploads/qrcode_files"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_qrcode_id_from_file(file_path):
    # Read the PDF file
    if file_path.endswith(".pdf"):
        pdf_file = fitz.open(file_path)
        # Extract the first page as an image
        first_page = pdf_file[0]
        pix = first_page.get_pixmap()

        # Convert Fitz pixmap to PIL image
        pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Convert PIL image to NumPy array
        img_pil_to_np = np.array(pil_image)

        # Convert color space from RGB to BGR
        img = cv2.cvtColor(img_pil_to_np, cv2.COLOR_RGB2BGR)

    else:
        # Read the image file
        img = cv2.imread(file_path)

    # Initialize the cv2 QRCodeDetector
    detector = cv2.QRCodeDetector()
    # Detect the QR code in the image
    data, bbox, straight_qrcode = detector.detectAndDecode(img)
    print(data)
    return data


@app.route("/scan_qr_code", methods=["POST"])
def scan_qr_code():
    if "qr_code_file" not in request.files:
        return jsonify({"error": "No QR code file uploaded"})

    qr_code_file = request.files["qr_code_file"]

    if qr_code_file.filename == "":
        return jsonify({"error": "No selected file"})

    if qr_code_file and allowed_file(qr_code_file.filename):
        filename = secure_filename(qr_code_file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        qr_code_file.save(file_path)

        qrcode_id = get_qrcode_id_from_file(file_path)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM interns WHERE qrcode_id = %s", [qrcode_id])
        intern_data = cur.fetchone()
        print(intern_data)
        cur.close()

        if intern_data:
            # QR code found in the database, return the response
            response = render_template("response.html", intern_data=intern_data)
            return response
        else:
            return jsonify({"error": "QR code not found in the database"})

    return jsonify({"error": "Invalid request"})





if __name__ == "__main__":
    app.run(debug=True)
