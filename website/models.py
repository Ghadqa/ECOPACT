import sqlite3
from flask_login import UserMixin


        
     



def admin(email,username,password) :
        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()
        



        emaile = email
        usernamee = username
        passworde = password
        role = 'user'

        # Insert data into the users table
        cursor.execute("INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)", (email, username, password, role))

        conn.commit()

        # Close the connection
        conn.close() ;
def authenticate_user(email, password) :
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()
    



    # Execute a SELECT query to find a user with the provided email and password
    cursor.execute("SELECT email,password,role,last_login FROM users WHERE email=? AND password=?", (email, password))

    # Fetch the first row from the result set
    user = cursor.fetchone()

    # Close the database connection
    conn.close()

    # Return the user if found, otherwise return None
    return user
def users() :
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT  email, username,password, role, last_login FROM users")
    users = cursor.fetchall()

    # Close the database connection
    conn.close()
    return users
def UserComponents(user_id) :
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()
    select_user_components_query = '''
    SELECT component,value,date
    FROM user_components,users
    WHERE users.email=user_components.user_id AND
    users.email= ?
    '''

    # Specify the email of the user you want to retrieve components for
    user_email = user_id 

    # Execute the query to retrieve the user's components
    cursor.execute(select_user_components_query, (user_email,))
    #cursor.execute(select_user_components_query)
    components = cursor.fetchall()

    # Close the database connection
    conn.close()
    return components   

def insert_data(email, components, date, value):
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_components (user_id, component, value, date) VALUES (?, ?, ?, ?)",
                   (email, components, value, date))
    conn.commit()
    conn.close()















