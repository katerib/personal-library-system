# BookNook

_Welcome to BookNook, the virtual bookshelf that keeps track of your favorite reads._

## Description

BookNook is a virtual bookshelf and personal library, designed for avid readers who want to keep track of their favorite reads. With BookNook, users can easily add and rate the books they've read, and build a collection of all their favorite titles in one place. This platform provides over 50,000 pre-imported books, but users can also search for specific titles to add to their personal shelf. BookNook helps readers consolidate their reading history on one site and allows them to discover new titles to grow their list!

### How it Works

The app connects to the server (microservice.py) and sends the ISBN as a message. The server listens for and receives the message, then calls the Google Books API to find the book ID associated with that ISBN, and passes back the relevant information to the client (app.py). For more information on this microservice architecture, view the ReadMe for my [MicroserviceGUID project](https://github.com/katerib/microserviceGUID).

### Tech Stack

* Python
* Flask
* HTML
* CSS
* Jinja2
* ZeroMQ (microservice architecture)
* SQLite (database persistence)

## Usage

Start the virtual environment, then run the Flask app with `py -m flask run`

In another terminal within a virtual environment, start the microservice with `py -m microservice.py`

### Requirements

View [requirements.txt](https://github.com/katerib/personal-library-system/blob/master/requirements.txt) for all necessary packages.

## Features

* **MY SHELF** stores information about the books the user has read. Users can add a book to My Shelf using one of the following methods:
  * **ADD TO SHELF** allows users to add a book by manually inputting the book data. 
  * **IMPORT** allows users to add a book by uploading a CSV file. This is recommended for users who have a large quantity of books to add. The CSV should be formatted with the following header row: title, author, rating, pages.
* **LIBRARY** contains over 50,000 imported books. This allows the user to view potential books to read next or remember a book they may have already read. Each page displays five book results for simplicity.
* **SEARCH** allows a user to search for a book with the option to display results with images of the cover or without. 
  * The Search feature calls the Google Books API via a microservice that relies on [ZeroMQ](https://zeromq.org/) to carry messages via sockets connected by a [request-reply pattern](https://zeromq.org/).
  * **VIEW BOOK DETAILS** opens the book in a more detailed view and displays the description, genres, ISBNs, cover image, and ratings to the user. All of this information is provided by the Google Books API.
    * Additionally, users are given the option to Preview the book. Clicking this link will take the user to the Google Books preview for that exact copy.

### Future Improvements

* In the future, I hope to add a Book Recommendation system to BookNook so readers can get personalized recommendations for what to read next based on the titles they've liked or disliked.
* I also hope to further develop the user-interface. The main focus on this project was with the backend, so I look forward to the opportunity to bringing more exciting features to the front-end components.


## Demo

Images of the site and its features can be found in the [Demo folder](https://github.com/katerib/personal-library-system/tree/master/demo). 

