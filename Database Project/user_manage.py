import sqlite3
import bcrypt


class User:

   def __init__(self, user_id, username, password_hash, first_name, last_name,
                role):
      self.id = user_id
      self.username = username
      self.password_hash = password_hash
      self.first_name = first_name
      self.last_name = last_name
      self.role = role

# Method to convert user data to JSON format.
   def to_json(self):
      user_json = {
          "id": self.id,
          "username": self.username,
          "first_name": self.first_name,
          "last_name": self.last_name,
          "role": self.role
      }
      return user_json

# Function to hash the password using bcrypt.
def hash_password(password):
   return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Function to verify the password using bcrypt.
def verify_password(password, hashed_password):
   return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# Simulating a login functionality with hashed passwords
def login(username, password):
   # Connect to an SQLite database
   conn = sqlite3.connect('users.db')
   cursor = conn.cursor()

   query = "SELECT * FROM users WHERE username = ?"
   cursor.execute(query, (username,))
   user_data = cursor.fetchone()

   if user_data:
      stored_password_hash = user_data[2]
      if verify_password(password, stored_password_hash):
         user = User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4], user_data[5])
      else:
         user = None
   else:
      user = None

   # Close the connection
   conn.close()

   return user

def all_users():
   # Connect to an SQLite database
   conn = sqlite3.connect('users.db')
   cursor = conn.cursor()

   query = "SELECT * FROM users"
   # Passing user input as parameters
   cursor.execute(query)
   # Fetch all rows of the result
   user_data = cursor.fetchall()
   users = []

   if user_data:
      for u in user_data:
          # Create User objects and add to the list
         users.append(User(u[0], u[1], u[2], u[3], u[4], u[5]))
   # Close the connection
   conn.close()
   print(len(users))
   # Return the list of User objects
   return users
