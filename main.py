from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
from collections import Counter
import math
import re

UPLOAD_FOLDER = 'upload_files'
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <title>Загрузите новый файл(он будет удален после вывода таблицы)</title>
    <h1>Загрузите новый файл(он будет удален после вывода таблицы)</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Загрузить>
    </form>
    '''


def text_to_table(text):
    text = re.sub(r'[^\w\s]', '', text.lower())
    words = text.split()
    tf = Counter(words)
    num_documents = 1
    idf = {word: math.log(num_documents / tf[word]) for word in tf}
    table_data = [(word, tf[word], idf[word]) for word, tf_value in
                  sorted(tf.items(), key=lambda x: x[1], reverse=False)][:50]

    return table_data

@app.route('/upload_files/<filename>')
def uploaded_file(filename):
    with open(f'{os.getcwd()}/upload_files/{filename}', 'r', errors='ignore') as f:
        text = f.read()
    os.remove(f'{os.getcwd()}/upload_files/{filename}')
    return render_template('index.html', table_data=text_to_table(text))


if __name__ == '__main__':
    app.run()