import mysql.connector
from mysql.connector import Error
import hashlib

#USING DATABASE SQL OPERATIONS THROUGHOUT
def create_connection():
    """Create a database connection to MySQL server"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Hunny67mustv3!10'
        )
        return connection
    except Error as e: #error handling
        print(f"Error connecting to MySQL: {e}") #Using f-strings
        return None

def init_database():
    """Initialize the database and users table"""
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS user_auth")
            cursor.execute("USE user_auth")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(64) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("Database initialized successfully")
        except Error as e:
            print(f"Error initializing database: {e}")
        finally:
            cursor.close()
            conn.close()

def hash_password(password):
    #Hash password using SHA-256
    return hashlib.sha256(password.encode()).hexdigest() #increased database security

def signup_user(username, password):
    #Add a new user to the database
    conn = create_connection()
    if not conn:
        return False, "Database connection failed"
    
    cursor = conn.cursor()
    try:
        cursor.execute("USE user_auth")
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
        return True, "Signup successful!"
    except mysql.connector.IntegrityError:
        return False, "Username already exists"
    except Error as e:
        return False, f"Error: {e}"
    finally:
        cursor.close()
        conn.close()

def login_user(username, password):
    """Verify user credentials"""
    conn = create_connection()
    if not conn:
        return False, "Database connection failed"
    
    cursor = conn.cursor()
    try:
        cursor.execute("USE user_auth")
        password_hash = hash_password(password)
        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = %s AND password_hash = %s",
            (username, password_hash)
        )
        result = cursor.fetchone()
        
        if result:
            id_value = result[0]
            return True, "Login successful!", id_value
            
        else:
            return False, "Incorrect password", 0
    except Error as e:
        return False, f"Error: {e}"
    finally:
        cursor.close()
        conn.close()

def save_time(user_id, time_to_save, level):
    conn = create_connection()
    #print("GOT HERE")

    if not conn:
        #print("Conn failed")
        return False, "Connection failed"

    cursor = conn.cursor()
    try:
        cursor.execute("USE user_auth")
        cursor.execute("INSERT INTO leaderboard (user_id, time, level) VALUES (%s, %s, %s)",
        (user_id, time_to_save, level))
        conn.commit()
        #print("SUCCESSFUL")
        return True, "Saved successfully!"
    except mysql.connector.IntegrityError:
        print(e)
        return False, "Time ID already exists"
    except Error as e:
        print(e)
        return False, f"Error: {e}"
    finally:
        cursor.close()
        conn.close()

def get_leaderboard(level):
    conn = create_connection()

    if not conn:
        return False, "COnnection failed"

    cursor = conn.cursor()
    try:
        cursor.execute("USE user_auth")
        cursor.execute("SELECT user_id, time FROM leaderboard WHERE level = %s ORDER BY time ASC LIMIT 10", (level))
        scores = []

        for row in cursor.fetchall():
            scores.append(row)

        # row[0] user_id
        # row[1] time

        return scores

    except mysql.connector.IntegrityError:
        print(e)
        return False, "Time ID already exists"
    except Error as e:
        print(e)
        return False, f"Error: {e}"
    finally:
        cursor.close()
        conn.close()