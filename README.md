# Library-Database
(351 Intro to Database Project) Basic Flask Application for Library Management

CS 351: Term Project

Overview
In this project I implemented a database named ‘users.db’ which has three tables:
1.‘users’ which holds information regarding the registered users
2.‘library_items’ which holds books, DVDs, CDs along with their respective authors and the items availability.
3.‘checkout’ which holds information on the checkout_id, item_id, and user_id.
In each function for the Librarian, I implemented a role check to decide whether the session user has the correct role to begin the database operations. Because of this, there cannot be an attempt of unauthorized access to the data since it will redirect the user to an unauthorized page which would make them login again. I also implemented password hashing on the dummy accounts and all newly created accounts. Some functions as you will see have a double role checking where I used it to prevent any attempt to change the URL.
Templates
In this folder I have included all redirectable webpages for adding, editing, removing and searching users, adding items to the library, showing the session profile, the login page, a checkout items page, browse library page and a base page.
The base page allows other pages to implement the base navigation, so they do not have to go back and repeatedly click different links. This was something I included on my own which really felt like a necessity after countless times testing and editing the project.
The base.html file shows the Library Dashboard with navigation links to the following pages, Home, Browse, and implements a role check on a Librarian to give the navigation options of listing Users, Adding Library Items and Searching Users. Then for all roles, a Logout button is added.

init.py
In my ‘init.py’ file, which holds the tables, I created some dummy data for the library, this includes:
1.Two default users with hashed passwords using ‘bcrypt’.
  a.Librarian: (Username: Librarian Password: lib)
  b.Patron: (Username: Patron Password: pat)
2.Six default library items.

app.py
In my ‘app.py’ file, which holds the websites code, I broke it down into four sections.

1. Basic Flask Functions
In this section, I define the root page of the app being (‘/’) which renders the index.html template. I also have a route for ‘/users’ that retrieves a list of all the users. Then the standard ‘/users2’, '/usersajax' and '/ajaxkeyvalue' which came with the flask app in vLab. With the basic implementation using ‘phone’ and ‘email’ as a piece of data for the user, I switched them out for a basic ‘role’ which is used for my role checking in other functions.

3. Librarian Functions
I began with the function to ADD a new user to the database. This function implements a role check to decide if the session user has clearance. If the session user is Librarian, it redirects them to the ‘add_user.html’ page where it then checks again if they are a Librarian after a POST. This is so you cannot type in the add_user to the end of the URL. It encrypts the password of the user created and stores all relevant information into the ‘users’ table.
I then added a function to EDIT a user which also implements a role check and redirects if not allowed. It connects to the ‘users.db’ database and proceeds to SELECT all users WHERE id=?. If a user is found with the specified ‘user_id’, it renders the ‘edit_user.html’ page to begin editing the user. After the edit is made via a form, it connects to the ‘users.db’ and UPDATES the ‘users’ table with the new data.

I added a function to DELETE a user, which again, implements a role check. It connects the ‘users.db’ and calls a DELETE query to remove the user based on the specified ‘user_id’
I added an add_item function that checks the role, redirects to ‘add_item.html’ and checks role again. Displays a form and saves the submitted data fields into the ‘library_items’ table. Then redirects the user to the profile page.
I implemented a function to search for a user, this checks the session role, retrieves the user based on the submitted ‘user_id’, connects the database, and preforms a SELECT on the ‘users’ table based on the ‘user_id’. Then begins a SELECT query by joining the ‘library_items’ and ‘checkout’ tables which is used to display the items a Patron has currently checked out. Then displays all items checked out by the searched user with the help of the profile template.

3. Patron Functions
In this section, I implemented a checkout_item function that checks the role of the user in session which must be Patron, since I do not want a librarian to check out items from the library. I begin by retrieving the ‘user_id’ from the session and connect to the database and execute a SELECT query to count the number of items the Patron has currently checked out by checking if the item they checked out has an availability of 1. If the user has >= 5 items checked out, it closes the connection and gives a JSON response of “Checkout limit reached” which informs the Patron that a maximum of 5 items may be checked out at once. If the Patron has less than 5 items checked out, it runs a SELECT query on the ‘library_items’ table to find the items that have an availability of 1 (which means they are available) if it is, it runs an UPDATE query on the ‘library_items’ table and sets the availability to 0 (not available) and runs an INSERT INTO the ‘checkout’ table to indicate what ‘item_id’ was checked out by which ‘user_id’. If successful, gives a JSON notification that the checkout was successful.
I then implemented a return_item function that allows the Patron to return an item. It first checks the role to make sure it is only a Patron. Then connects to the database and runs a SELECT query on ‘library_items’ to check if the item is available to see if the item has already been returned. If it has not been returned, it runs an UPDATE query on ‘library_items’ and sets the ‘item_id’ to 1 (available) and runs a DELETE query on ‘checkout’ table to remove the checkout from the associated ‘item_id’.

5. Combined Functions
In this section I decided to put three functions that I believe were to be used by either role. There is a browse function which connects the database, which allows the user to search for an item. This function takes a search parameter if provided or defaults back to None to show all items. If there is a search query, it runs a SELECT query on ‘library_items’ table WHERE ‘search_query’. If no search query is provided, it just selects all from the ‘library_items’ table. Then returns a list of items with the Title, Type, Author and Availability.
I then created the profile function. It retrieves data from the session, connects to the database, checks the role, this role check is for Patrons so there is not risk of unauthorized data leakage. The role check is for Patrons to see what is checked out by them without having to go to another page. It runs a JOIN on ‘library_items’ and ‘checkout’ to SELECT where items are not available using the ‘user_id’ to see if there are any items checked out by the session user. If the role check shows the user is not a Patron, it shows an empty list.
Then finally there is the logout function which clears the session and redirects back to the root.
