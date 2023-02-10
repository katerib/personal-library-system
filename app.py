import csv
import os
import requests
import zmq
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for

load_dotenv()

UPLOAD_FOLDER = 'static/files'
ALLOWED_EXTENSIONS = {'csv', 'csv'}
BOOK_KEY = os.environ.get("api-key")

app = Flask(__name__, instance_relative_config=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"F4Q8z23r]/'

context = zmq.Context()
print("Connecting to microservice...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")


@app.route('/')
def root():
    return render_template('homepage.html')


def get_all_data():
    from functions.sqlquery import sql_query
    return sql_query(''' SELECT * FROM data_table''')


@app.route('/shelf')
def sql_database():
    results = get_all_data()
    return render_template('shelfDB.html', results=results)


@app.route('/create', methods=['POST', 'GET'])
def sql_create():
    return render_template('shelfDB.html')


def request_form(form):
    author = form['author']
    title = form['title']
    rating = form['rating']
    pages = form['pages']
    return author, title, rating, pages


def insert_db(form):
    from functions.sqlquery import sql_edit_insert
    author, title, rating, pages = request_form(form)
    sql_edit_insert(''' INSERT INTO data_table (title,author,rating,pages) VALUES (?,?,?,?) ''',
                    (title, author, rating, pages))


@app.route('/insert', methods=['POST', 'GET'])
def sql_data_insert():
    if request.method == 'POST':
        insert_db(request.form)
    results = get_all_data()
    return render_template('shelfDB.html', results=results)


def delete(args):
    from functions.sqlquery import sql_delete
    author = args.get('author')
    title = args.get('title')
    sql_delete(''' DELETE FROM data_table where title = ? and author = ?''', (title, author))


@app.route('/delete', methods=['POST', 'GET'])
def sql_data_delete():
    if request.method == 'GET':
        delete(request.args)
        return redirect('/shelf')
    results = get_all_data()
    return render_template('shelfDB.html', results=results)


@app.route('/query_edit', methods=['POST', 'GET'])
def sql_edit_link():
    from functions.sqlquery import sql_query2
    if request.method == 'GET':
        eAuthor, eTitle = request.args.get('eAuthor'), request.args.get('eTitle')
        eResults = sql_query2(''' SELECT * FROM data_table where title = ? and author = ?''', (eTitle, eAuthor))
    results = get_all_data()
    return render_template('shelfDB.html', eResults=eResults, results=results)


def get_old_info(form):
    old_author = form['old_author']
    old_title = form['old_title']
    return old_author, old_title


def edit_insert(form):
    from functions.sqlquery import sql_edit_insert
    old_author, old_title = get_old_info(form)
    author, title, rating, pages = request_form(form)
    sql_edit_insert(''' UPDATE data_table set title=?,author=?,rating=?,pages=? WHERE title=? and author=? ''',
                    (title, author, rating, pages, old_title, old_author))


@app.route('/edit', methods=['POST', 'GET'])
def sql_data_edit():
    if request.method == 'POST':
        edit_insert(request.form)
        redirect('/shelf')
    results = get_all_data()
    return render_template('shelfDB.html', results=results)


def allowed(file_check):
    return '.' in file_check and file_check.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/err')
def error_pg():
    error_msg = request.args.get('error_msg')
    if error_msg is None or error_msg == '':
        error_msg = 'An error occurred.'
    return render_template('error.html', error_msg=error_msg)


@app.route('/import', methods=['GET'])
def import_csv():
    return render_template('import.html')


def insert_from_csv(file):
    from functions.sqlquery import sql_csv_insert
    file.save(file.filename)
    with open(file.filename) as in_file:
        reader = csv.reader(in_file)
        next(reader)
        sql_csv_insert(''' INSERT INTO data_table (title,author,rating,pages) VALUES (?,?,?,?) ''', reader)


@app.route('/import', methods=['POST'])
def upload_csv():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            error_msg = 'No file specified for upload. Please select a file and try again.'
            return render_template('error.html', error_msg=error_msg)
        if uploaded_file and allowed(uploaded_file.filename):
            insert_from_csv(uploaded_file)
        return redirect(url_for('sql_database'))


def pagination_calculations(page, data):
    displayQuant = 5
    start_index = 0
    for index in range(int(page) - 1):
        start_index += displayQuant
    end_index = start_index + displayQuant
    return ((int(len(data)) // displayQuant) + 1), start_index, end_index


def get_current_page(args):
    if args.get('page') is None:  # pagination
        page = 0
    else:
        page = args.get('page')
    return page


@app.route('/library', methods=['GET', 'POST'])
def render():
    with open('data/books.csv') as file:
        data = [dict(item) for item in csv.DictReader(file)]
        page = get_current_page(request.args)
        totalPages, start_index, end_index = pagination_calculations(page, data)
        return render_template('library.html', data=data[start_index:end_index], totalPages=totalPages, page=int(page),
                               show=int(5))


def get_isbn_list(results):
    """
    note: industryIdentifiers not static order, sometimes returns isbn10 first, sometimes isbn13
    :param results:
    :return:
    """
    results_isbn = []
    for item in results["items"]:       # only append isbn13
        if item["volumeInfo"]["industryIdentifiers"][0]["type"] != "OTHER":
            results_isbn.append(item["volumeInfo"]["industryIdentifiers"][0]["identifier"])
        else:
            results_isbn.append("NULL")
    return results_isbn


def call_microservice(results, index):
    socket.send_string(results[index])
    byte_link = socket.recv()
    return str(byte_link.decode('ASCII'))


def check_items(check, results, index):
    if "items" in check:
        if "imageLinks" in check["items"][0]["volumeInfo"]:
            return str(call_microservice(results, index))
        else:
            return "NULL"
    else:
        return "invalid"


def compile_image_links(results):
    image_links = []
    for index in range(len(results)):
        if results[index] != "NULL":
            check = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{results[index]}").json()
            image_links.append(check_items(check, results, index))
        else:
            image_links.append("invalid")
    return image_links


def get_img_src(results):
    results_isbn = get_isbn_list(results)
    img_links = compile_image_links(results_isbn)
    return img_links


@app.route('/search', methods=['GET'])
def search_page():
    if request.method == "GET":
        return render_template('search.html')


def assign_img_links(form, results):
    if form.get("showImages"):
        img_links = get_img_src(results)
    else:
        img_links = False
    return img_links


@app.route('/search', methods=['POST'])
def search():
    if request.form.get("lookup"):
        results = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={request.form.get("lookup")}').json()
        img_links = assign_img_links(request.form, results)
        return render_template('results.html', bookResults=results, thumbnails=img_links)


@app.route('/details')
def details():
    book_id = request.args.get('book_id')
    book = requests.get(f'https://www.googleapis.com/books/v1/volumes/{book_id}').json()
    return render_template('book-details.html', book=book)


@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')


if __name__ == '__main__':
    app.run(debug=True)
