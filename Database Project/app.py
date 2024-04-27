from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from user_manage import login, User, all_users
from init import sys_init
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'


with app.app_context():
    sys_init()

#   BEGIN BASIC FLASK FUNCTIONS   #

# Function to define the root page of the app
@app.route('/')
def index():
    if request.args:
        return render_template('index.html', messages =request.args['messages'])
    else:
        return render_template('index.html', messages = '')

# Function to retrieve a list of all users
@app.route('/users')
def users():
    all = all_users()
    return render_template('users.html', users = all)

# Function like above but is in use for AJAX dynamic loading
@app.route('/users2')
def users2():
    all = all_users()
    return render_template('usersajax.html', users = all)

# Function gets all users and returns usernames and roles into a JSON format
@app.route('/usersajax', methods=['POST'])
def get_users():
    users = all_users()  # Assuming all_users() returns a list of user objects
    user_data = [{'username': user.username, 'role': user.role} for user in users]
    return jsonify(user_data)

# Function to login the user with provided credentials. Then stores details in session
@app.route('/ajaxkeyvalue', methods=['POST'])
def ajax():
    data = request.json  # Assuming the AJAX request sends JSON data
    print(data)
    # Process the data
    username = data['username']
    password = data['password']

    print(username)
    print(password)

    user = login(username, password)
    if not user:
        response_data ={'status' : 'fail'}
    else:
        session['logged_in'] = True
        session['username'] = username
        session['user'] = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role
        }

        response_data = {'status' :'ok', 'user': user.to_json()}

    return jsonify(response_data)

#   END BASIC FLASK FUNCTIONS   #


#   BEGIN LIBRARIAN  FUNCTIONS   #

#   Function for Librarian to ADD new User to database
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'GET':
        # Checks if the logged-in user is a librarian; if not, redirects to the main page with an "Unauthorized Access" message.
        if not session.get('user') or session['user']['role'] != 'Librarian':
            return redirect(url_for('index', messages='Unauthorized Access'))
        # If the user is authorized, render the 'add_user.html' template.
        return render_template('add_user.html')
    # Checks for librarian status, then processes form data to add a new user to the database, encrypts the password using bcrypt
    elif request.method == 'POST':
        if not session.get('user') or session['user']['role'] != 'Librarian':
            return jsonify({'status': 'unauthorized'}), 403
        #  Retrieves the form data submitted with the POST request.
        data = request.form
        # Extract specific fields (username, password, first_name, last_name, role) from the form data.
        username = data['username']
        password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        first_name = data['first_name']
        last_name = data['last_name']
        role = data['role']
        # Establish a connection to the DB named 'users.db'.
        conn = sqlite3.connect('users.db')
        # Create a cursor object for executing SQL queries.
        cursor = conn.cursor()
        # INSERT query to add a new user record to the 'users' table in the database.
        cursor.execute(
            "INSERT INTO users (username, password, first_name, last_name, role) VALUES (?, ?, ?, ?, ?)", # Used parameterized query to prevent SQL injection
            (username, password, first_name, last_name, role))
        # Commits changes to DB.
        conn.commit()
        # Closes connection to DB.
        conn.close()
        # Redirects to the users page.
        return redirect(url_for('users'))

#   Function for Librarian to EDIT User in database
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    # Checks if the logged-in user is a librarian; if not, redirects to the main page with an "Unauthorized Access" message.
    if not session.get('user') or session['user']['role'] != 'Librarian':
        return redirect(url_for('index', messages='Unauthorized Access'))
    #  Fetches user details from the database if the session's role is librarian, then populates and shows an edit form.
    if request.method == 'GET':
        # Establish a connection to the DB named 'users.db'.
        conn = sqlite3.connect('users.db')
        # Create a cursor object for executing SQL queries.
        cursor = conn.cursor()
        # SELECT query to fetch user details based on the provided user_id.
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        # Fetch the user data.
        user = cursor.fetchone()
        # Close the database connection.
        conn.close()
        # If a user with the specified user_id is found in the database.
        if user:
            # It populates a dictionary user_data with the fetched user details.
            user_data = {'id': user[0], 'username': user[1], 'first_name': user[3], 'last_name': user[4], 'role': user[5]}
            # Render the 'edit_user.html' template with this data.
            return render_template('edit_user.html', user=user_data)
        else:
            return redirect(url_for('users', message="User not found"))
    # Checks if the incoming request method is POST.
    elif request.method == 'POST':
        data = request.form
        # Extract specific fields (username, first_name, last_name, role) from the form data submitted via POST.
        username = data['username']
        first_name = data['first_name']
        last_name = data['last_name']
        role = data['role']
        # Establish a connection to the DB named 'users.db'.
        conn = sqlite3.connect('users.db')
        # Create a cursor object for executing SQL queries.
        cursor = conn.cursor()
        # UPDATE query to update the user's details based on user_id.
        cursor.execute(
            "UPDATE users SET username=?, first_name=?, last_name=?, role=? WHERE id=?",  # Used parameterized query to prevent escaping
            (username, first_name, last_name, role, user_id))
        # Commit changes.
        conn.commit()
        # Close connection.
        conn.close()
        # Redirect to the users page.
        return redirect(url_for('users'))

#   Function for Librarian to DELETE User from database
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # Checks if the logged-in user is a librarian; if not, redirects to the main page with an "Unauthorized Access" message.
    if not session.get('user') or session['user']['role'] != 'Librarian':
        return jsonify({'status': 'unauthorized'}), 403
    # Establish a connection to the DB named 'users.db'.
    conn = sqlite3.connect('users.db')
    # Create a cursor object for executing SQL queries.
    cursor = conn.cursor()
    # DELETE query to remove user based on user_id.
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,)) # user_id cannot be tampered with in SQL structure
    # Commit changes.
    conn.commit()
    # Close connection.
    conn.close()
    # Redirect to the users page.
    return redirect(url_for('users'))

#   Function for Librarian to ADD new Item to Library database.
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'GET':
        # Checks if there is no user session or if the user's role is not 'Librarian'.
        if not session.get('user') or session['user']['role'] != 'Librarian':
            return redirect(url_for('index', messages='Unauthorized Access'))
        return render_template('add_item.html')
    # Checks if the incoming request method is POST.
    elif request.method == 'POST':
        # Similar to 'GET' where it checks user in session.
        if not session.get('user') or session['user']['role'] != 'Librarian':
            return jsonify({'status': 'unauthorized'}), 403
        data = request.form
        # Extract specific fields (title, type, author) from the form data submitted via POST.
        title = data['title']
        item_type = data['type']
        author = data['author']
        # Set the availablility to true.
        available = 1
        # Establish a connection to the DB.
        conn = sqlite3.connect('users.db')
        # Create a cursor object for executing SQL queries.
        cursor = conn.cursor()
        #  INSERT query to add a new item to the 'library_items' table with the provided details.
        cursor.execute(
            "INSERT INTO library_items (title, type, author, available) VALUES (?, ?, ?, ?)",
            (title, item_type, author, available))
        # Commit changes.
        conn.commit()
        # Close connection.
        conn.close()
        # Redirect to the profile page.
        return redirect(url_for('profile'))

@app.route('/search_user', methods=['GET', 'POST'])
def search_user():
    # Checks if there is no user session or if the user's role is not 'Librarian'.
    if not session.get('user') or session['user']['role'] != 'Librarian':
        return jsonify({'status': 'unauthorized'}), 403
    # Retrieves user and their checked-out items from the database, and displays them.
    if request.method == 'POST':
        # Retrieve the 'user_id' from the form data submitted via POST.
        user_id = request.form.get('user_id')
        # Establish a connection to the DB.
        conn = sqlite3.connect('users.db')
        # Create a cursor object for executing SQL queries.
        cursor = conn.cursor()
        # SELECT query to fetch user details (id, username, first_name, last_name, role) based on the provided 'user_id'.
        cursor.execute("SELECT id, username, first_name, last_name, role FROM users WHERE id = ?", (user_id,))
        # Fetches the result using fetchone().
        user_info = cursor.fetchone()
        # SELECT query to fetch items checked out by the user identified by 'user_id' by joining the 'library_items' and 'checkout' tables.
        cursor.execute("""
            SELECT library_items.item_id, library_items.title, library_items.type, library_items.author
            FROM library_items
            JOIN checkout ON library_items.item_id = checkout.item_id
            WHERE checkout.user_id = ?
        """, (user_id,))
        # Processes the fetched data into a list of dictionaries representing checked-out items.
        checked_out_items = [{
            'item_id': item[0],
            'title': item[1],
            'type': item[2],
            'author': item[3]
        } for item in cursor.fetchall()]
        # Close connection.
        conn.close()
        # If user is found, render the profile with data.
        if user_info:
            return render_template('profile.html', user_info=dict(zip(['id', 'username', 'first_name', 'last_name', 'role'], user_info)), checked_out_items=checked_out_items)
        else:
            # If the user doesn't exist, it displays an error message.
            return render_template('profile.html', error="No user found with ID: " + str(user_id))
    else:
        # Show the search form if no POST request is made.
        return render_template('search_user.html')

#   END LIBRARIAN  FUNCTIONS   #


#   BEGIN PATRON FUNCTIONS  #

# Function to handle the checkout process of a library item by a patron.
@app.route('/checkout_item/<int:item_id>', methods=['POST'])
def checkout_item(item_id):
    # Checks if the logged-in user is a Patron; if not, redirects to the main page with an "Unauthorized" message.
    if not session.get('user') or session['user']['role'] != 'Patron':
        return jsonify({'status': 'unauthorized'}), 403
    # Retrieve the 'user_id' from the session.
    user_id = session['user']['id']
    # Establish a connection to the DB.
    conn = sqlite3.connect('users.db')
    # Create a cursor object for executing SQL queries.
    cursor = conn.cursor()
    # SELECT query to count how many items the user currently has checked out.
    # Checks if the items are available before counting them
        # By checking if their 'item_id' is not in the set of 'item_id's where 'available' is 1 in the 'library_items' table.
    cursor.execute("""
        SELECT COUNT(*)
        FROM checkout
        WHERE user_id = ? AND item_id NOT IN (
            SELECT item_id
            FROM library_items
            WHERE available = 1
        )
    """, (user_id,))
    item_count = cursor.fetchone()[0]
    # If the user already has 5 or more items checked out.
    if item_count >= 5:
        # Close connection.
        conn.close()
        # Return a JSON response with a status of 'fail' and a message.
        return jsonify({'status': 'fail', 'message': 'Checkout limit reached. You cannot check out more than 5 items.'}), 403
    # Check if the item is available.
    # SELECT query on the 'library_items' table and fetching the result.
    cursor.execute("SELECT available FROM library_items WHERE item_id=?", (item_id,))
    item = cursor.fetchone()
    # If the item is available (item[0] is 1).
    if item and item[0] == 1:  # If available
        # It updates the availability in the 'library_items' table.
        cursor.execute("UPDATE library_items SET available=0 WHERE item_id=?", (item_id,))
        # Inserts a record into the 'checkout' table indicating that the user has checked out the item.
        cursor.execute("INSERT INTO checkout (item_id, user_id) VALUES (?, ?)",
                       (item_id, user_id))
        # Commits the changes.
        conn.commit()
        # Closes the connection.
        conn.close()
        # Returns a JSON response indicating a successful checkout.
        return jsonify({'status': 'success', 'message': 'Checkout successful!'})
    else:
        conn.close()
        return jsonify({'status': 'fail', 'message': 'Item not available'}), 409

# Function to manage the return process of a checked-out library item.
@app.route('/return_item/<int:item_id>', methods=['POST'])
def return_item(item_id):
    # Function is restricted to users identified as 'Patron'.
    if not session.get('user') or session['user']['role'] != 'Patron':
        return jsonify({'status': 'unauthorized'}), 403
    # Connects to the 'users.db' DB.
    conn = sqlite3.connect('users.db')
    # Create cursor to execute queries.
    cursor = conn.cursor()
    # Check if item is actually checked out before attempting to return it.
    # SELECT query on the 'library_items' table and fetching the result.
    cursor.execute("SELECT available FROM library_items WHERE item_id=?", (item_id,))
    availability = cursor.fetchone()
    # If the item is available (availability[0] is 1), it closes the database connection since its been returned.
    if availability and availability[0] == 1:
        # Closes connection.
        conn.close()
        return jsonify({'status': 'fail', 'message': 'Item already returned'}), 400
    # Updates the item's availability in the 'library_items' table to 1 (available).
    cursor.execute("UPDATE library_items SET available=1 WHERE item_id=?", (item_id,))
    #  DELETES the checkout record associated with the item.
    cursor.execute("DELETE FROM checkout WHERE item_id=?", (item_id,))
    # Commits changes to DB.
    conn.commit()
    # Closes connection.
    conn.close()
    return jsonify({'status': 'success', 'message': 'Item returned successfully!'})

#   END PATRON FUNCTIONS    #


#   BEGIN COMBINED FUNCTIONS    #

# Function to view of all items in the library's database.
@app.route('/browse')
def browse():
    # Establish a connection to the SQLite database named 'users.db'.
    conn = sqlite3.connect('users.db')
    # Create a cursor object for executing queries.
    cursor = conn.cursor()
    # Retrieves the value of the 'search' query parameter from the URL.
    # If the 'search' parameter is not provided, it defaults to None.
    search_query = request.args.get('search', None)

    if search_query:
        # SELECT query to retrieve items from the 'library_items' table that match the search term using the LIKE operator.
        cursor.execute("SELECT item_id, title, type, author, available FROM library_items WHERE title LIKE ?", ('%' + search_query + '%',))
    else:
        # If no search query is provided, it fetches all items from the 'library_items' table.
        cursor.execute("SELECT item_id, title, type, author, available FROM library_items")
        # Fetches the results of the executed SQL query using cursor.fetchall()
            # Processes each row into a dictionary format with keys 'item_id', 'title', 'type', 'author', and 'available' representing each item's attributes.
                # It creates a list of such dictionaries called items.
    items = [{'item_id': row[0], 'title': row[1], 'type': row[2], 'author': row[3], 'available': row[4]} for row in cursor.fetchall()]
    # Close the connection.
    conn.close()
    return render_template('browse.html', items=items)


# Function displays profile of current user. If user is patron then shows the checked out items.
@app.route('/profile')
def profile():
    # Retrieve the user data from the session.
    user_data = session.get('user')
    # If there is no user data in the session (i.e., the user is not logged in),
    if not user_data:
        # Redirects the user to the main page (/).
        return redirect('/?messages=Please login again!')
    # Establish a connection to the DB named 'users.db'.
    conn = sqlite3.connect('users.db')
    # Create a cursor for executing queries.
    cursor = conn.cursor()
    # Check the user's role. If the user is identified as a 'Patron',
    if user_data['role'] == 'Patron':
        # SELECT query to fetch items that the patron has checked out (items where 'available' is 0 in the 'library_items' table).
        cursor.execute("""
            SELECT library_items.item_id, library_items.title, library_items.type, library_items.author
            FROM library_items
            JOIN checkout ON library_items.item_id = checkout.item_id
            WHERE checkout.user_id = ? AND library_items.available = 0
        """, (user_data['id'],))
        # Creates a list of dictionaries representing these checked-out items.
        checked_out_items = [{
            'item_id': item[0],
            'title': item[1],
            'type': item[2],
            'author': item[3]
        } for item in cursor.fetchall()]
    else:
        # If the user is not a patron, it sets checked_out_items as an empty list.
        checked_out_items = []
    # Close the connection.
    conn.close()
    return render_template('profile.html', user_info=user_data, checked_out_items=checked_out_items)

# Function logs user out and clears session.
@app.route('/logout')
def logout():
    session.clear()
    # Redirects to root.
    return redirect('/')


#   END COMBINED FUNCTIONS  #

if __name__ == '__main__':
    app.run(debug=True)
