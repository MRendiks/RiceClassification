import os
from app import app
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import numpy as np
from keras.preprocessing import image
from matplotlib import pyplot as plt
from keras.models import load_model
import tensorflow as tf
import tensorflow.keras.utils
from flask import Flask
from flask_mysqldb import MySQL




UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "sella_ta"

mysql = MySQL(app)


# model = load_model("model-devolepment\pa_rice.h5")
model = load_model("notebook\identifikasi_beras.h5")

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('index.html')

def predict(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = tensorflow.keras.utils.load_img(
        path, target_size=(150, 150))
    x = tf.keras.utils.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    images = np.vstack([x])
    classes = model.predict(images, batch_size=10)
    if classes[0][0] == 1:
        result = "Basmathi"
    elif classes[0][1] == 1:
        result = 'IR 64'
    elif classes[0][2] == 1:
        result = 'Ketan Putih'
    else:
        result = 'Tidak Terdeteksi'
    return result

@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        prediksi = predict(filename)
        keterangan = ""
        ket1 = ""
        ket2 = ""
        ket3 = "" 
        ket4 = "" 
        ket5 = "" 
        
        if prediksi != "Tidak Terdeteksi":
            cur = mysql.connection.cursor()
            cur.execute(f"SELECT * FROM kategori WHERE nama_kategori='{prediksi}'")
            data = cur.fetchall()
            mysql.connection.commit()
            for item in data:
                keterangan = item[2]
                ket1 = item[3]
                ket2 = item[4]
                ket3 = item[5]
                ket4 = item[6]
                ket5 = item[7]
                cur.execute(f"INSERT INTO tabel_gambar VALUES('', '{item[0]}', '{filename}')")
                mysql.connection.commit()
        flash(prediksi)
        cur.close()
        return render_template('index.html', filename=filename, penjelasan=keterangan, prediksi=prediksi, ket1=ket1, ket2=ket2, ket3=ket3, ket4=ket4,ket5=ket5)
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == "__main__":
    app.run()
