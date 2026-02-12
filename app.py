from flask import Flask, request, render_template, redirect, url_for
from google.cloud import storage
from datetime import datetime
import re

app = Flask(__name__)

BUCKET_NAME = "user-form-data-bucket-123"
FILE_NAME = "users.csv"
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@(gmail\.com|highspringindia\.com)$"

def validate_input(contact, email):
    if not contact.isdigit() or len(contact) != 10:
        return False, "Contact must be exactly 10 digits"
    if not re.match(EMAIL_REGEX, email):
        return False, "Invalid email domain"
    return True, ""

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]
        contact = request.form["contact"]
        email = request.form["email"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        valid, message = validate_input(contact, email)
        if not valid:
            return message, 400

        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(FILE_NAME)

        if not blob.exists():
            blob.upload_from_string(
                "timestamp,name,role,contact,email\n"
            )

        existing_data = blob.download_as_text()
        new_row = f"{timestamp},{name},{role},{contact},{email}\n"
        blob.upload_from_string(existing_data + new_row)

        # Redirect with success parameter
        return redirect(url_for("form", success="true"))
    return render_template("form.html")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
