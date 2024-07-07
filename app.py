
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import mysql.connector

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database setup
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="test"
)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS Info (
        id INT AUTO_INCREMENT PRIMARY KEY,
        PHY_ID VARCHAR(255),
        PRS_ID VARCHAR(255),
        BOOK_ID VARCHAR(255),
        INSTCD VARCHAR(255),
        image VARCHAR(255),
        image_link VARCHAR(255),
        product_name VARCHAR(255),
        product_quantity INT
    )
''')
conn.commit()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    if username == 'tasnia' and password == '123':
        return redirect(url_for('second_page'))
    else:
        flash("Invalid Credentials")
        return redirect(url_for('login'))

@app.route('/second_page')
def second_page():
    return render_template('second_page.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and file.filename.endswith('.xlsx'):
        df = pd.read_excel(file)
        required_columns = ["PHY_ID", "PRS_ID", "BOOK_ID", "INSTCD", "image", "image_link"]
        if all(column in df.columns for column in required_columns):
            df_required = df[required_columns].fillna('')  # Replace NaN with empty strings
            for _, row in df_required.iterrows():
                c.execute('''
                    INSERT INTO Info (PHY_ID, PRS_ID, BOOK_ID, INSTCD, image, image_link)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (row['PHY_ID'], row['PRS_ID'], row['BOOK_ID'], row['INSTCD'], row['image'], row['image_link']))
            conn.commit()
            flash("Data imported successfully")
        else:
            flash("Required columns are missing in the file")
    else:
        flash("Invalid file format")
    return redirect(url_for('second_page'))

@app.route('/search_page')
def search_page():
    return render_template('third_page.html')

@app.route('/search', methods=['POST'])
def search_records():
    book_id = request.form.get('book_id', '').strip()
    instcd = request.form.get('instcd', '').strip()

    query = "SELECT id, PHY_ID, PRS_ID, BOOK_ID, INSTCD, image, image_link, product_name, product_quantity FROM Info WHERE 1=1"
    params = []

    if book_id:
        query += " AND BOOK_ID=%s"
        params.append(book_id)
    if instcd:
        query += " AND INSTCD=%s"
        params.append(instcd)

    c.execute(query, params)
    records = c.fetchall()

    return render_template('third_page.html', records=records)

@app.route('/entry', methods=['POST'])
def entry():
    record_id = request.form.get('record_id')
    product_name = request.form.get('product_name')
    product_quantity = request.form.get('product_quantity')

    c.execute('''
        UPDATE Info
        SET product_name = %s, product_quantity = %s
        WHERE id = %s
    ''', (product_name, product_quantity, record_id))
    conn.commit()

    flash("Product information saved successfully")
    return redirect(url_for('search_page'))

if __name__ == '__main__':
    app.run(debug=True)
