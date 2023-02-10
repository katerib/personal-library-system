import time
import zmq
import requests

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    byte_isbn = socket.recv()

    isbn = byte_isbn.decode('ASCII')
    print(f"Received {isbn}")

    api = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
    response = requests.get(api + str(isbn))

    # destructuring the JSON object from the Google books API
    thumbnail_link = response.json()['items'][0]['volumeInfo']['imageLinks']['thumbnail']
    print(f"Found the following link: {thumbnail_link}")
    print(f"Received request for ISBN: {isbn}")

    time.sleep(1)

    print("Returning resource link to client")
    socket.send_string(thumbnail_link)
