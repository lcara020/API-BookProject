from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, SelectField, validators, StringField, RadioField, BooleanField
import os
from wtforms.validators import NumberRange
import main_functions
import requests

#Creates a random secret key
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


#Creates a book form with all input fields
class BookForm(FlaskForm):
    keyword = StringField("Keyword", [validators.DataRequired()])
    category = SelectField("Popular genres", choices=[("", ""),
                                                  ("Art", "Art"),
                                                  ("Biography & Autobiography", "Biography & Autobiography"),
                                                  ("Business & Economics", "Business & Economics"),
                                                  ("Cooking","Cooking"),
                                                  ("Drama", "Drama"),
                                                  ("Education", "Education"),
                                                  ("Fiction", "Fiction"),
                                                  ("Gardening", "Gardening"),
                                                  ("History", "History"),
                                                  ("Juvenile Fiction", "Juvenile Fiction"),
                                                  ("Medical", "Medical"),
                                                  ("Music","Music"),
                                                  ("Nature", "Nature"),
                                                  ("Philosophy", "Philosophy"),
                                                  ("Psychology", "Psychology"),
                                                  ("Non-fiction", "Non-fiction")

    ])
    amount_results = RadioField("Amount of results", choices=[("3", 3),
                                           ("5", 5),
                                           ("10", 10)
    ])
    submit = SubmitField("Submit")
#Gets the api key
def get_api_key(filename):
    return main_functions.read_from_file(filename)["books_key"]

books_key = get_api_key("api_keys.json")
def get_books(keyword, category, amount_results, api_key):
    url = f"https://www.googleapis.com/books/v1/volumes?q={keyword}+subject:{category}"
    response = requests.get(url).json() #making the request
    main_functions.save_to_file(response,"books_results.json") #saves response to JSON file
    response = main_functions.read_from_file("books_results.json") #reads from file
    found_books = [] #initiating an empty list
    for i in response["items"]:
        if "categories" in i["volumeInfo"].keys():
            print(i["volumeInfo"]["categories"])
            if category in i["volumeInfo"]["categories"] and keyword.lower() in i["volumeInfo"]["title"].lower():
                found_books.append((i["volumeInfo"]["imageLinks"]["smallThumbnail"],
                                    i["volumeInfo"]["title"],
                                    i["volumeInfo"]["authors"][0]))
        else:
            pass
    print(found_books)

#Limit the number of results based on the selected amount
    if amount_results == "3":
        found_books = found_books[:3]
    elif amount_results == "5":
        found_books = found_books[:5]
    elif amount_results == "10":
        found_books = found_books[:10]

    return found_books


#Creates the main page interface for input and return
@app.route('/', methods=["GET", "POST"])
def index():

    my_form = BookForm()

    if request.method == "POST":
        keyword_entered = my_form.keyword.data
        category_entered = my_form.category.data
        amount_results_entered = my_form.amount_results.data
        list_of_books = get_books(keyword_entered, category_entered, amount_results_entered, books_key)
        return render_template("books_results.html", list_of_books=list_of_books, length=len(list_of_books))
    return render_template("books.html", form=my_form)




#Run app
if __name__ == '__main__':
        app.run(port=3030,debug=True)