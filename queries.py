import sqlite3
import time,json
from typing import Dict , Callable 

queries_sql = {
    "user" : {
        "create_table" : """CREATE TABLE user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )"""
        ,
        #sql statement with parameter placeholder
        "create_new_user" : "INSERT INTO user (name,email,password) VALUES (?,?,?)"
        ,
        "all_user" : "SELECT id,name,email,password FROM user"
        ,
        "update_password" : "UPDATE user SET password=? WHERE id=?"
        ,
        "get_user_by_email" : "SELECT * FROM user WHERE email= ? "
    },
    "session" : {
        "create_table" : """CREATE TABLE IF NOT EXISTS session(
            id TEXT PRIMARY KEY,
            data TEXT,
            expires_at TIMESTAMP
        )"""
        ,
        "create_new_session" : "INSERT INTO session (id,data,expires_at) VALUES (?,?,?)"
        ,
        "get_session" : "SELECT * FROM session WHERE id=?"
        ,
        "update_session_data" : "UPDATE session set data=? WHERE id=?"
        ,
        "delete_session" : "DELETE FROM session WHERE id=?"
    }   
}

# Functions For Testing and development only
def all_user():
    cursor=db.cursor()
    cursor.execute(queries_sql["user"]["all_user"])
    users = cursor.fetchall()
    for user in users :
        print(dict(user))
    
def clear_sessions():
    db.execute("DELETE FROM session;")

def all_sessions():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM session;")
    sessions = cursor.fetchall()
    cursor.close()
    for session in sessions :
        print(dict(session))


# Actual Fuctions 
def get_user_by_email(get_db,email_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(queries_sql["user"]["get_user_by_email"],(email_id,))
    user = cursor.fetchone()
    cursor.close()
    return dict(user) if user else None

def create_new_user(get_db,email:str,username:str,password:str) -> bool :
    db = get_db()
    cursor = db.cursor()
    try :
        out = cursor.execute(queries_sql["user"]["create_new_user"],(username,email,password))
        print(out)
        out = db.commit()
        print(out)
        cursor.close()
        db.close()
        return True
    except sqlite3.IntegrityError :
        cursor.close()
        db.close()
        return False
    
def create_new_session(get_db,data,expires_at,session_id) -> bool :
    db = get_db()  
    cursor = db.cursor()
    try :
        cursor.execute(queries_sql["session"]["create_new_session"],(session_id,data,expires_at))
        cursor.close()
        db.commit()
        return True
    except sqlite3.IntegrityError :
        cursor.close()
        db.commit()
        return False
    finally:
        cursor.close()
        db.commit()
        
def get_session(get_db,session_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(queries_sql["session"]["get_session"], (session_id,))
    session = cursor.fetchone()
    cursor.close()
    # Check if session exists
    if session is None:
        print("No session found.")
        return None
    # Convert session to dictionary for easy access
    session_data = dict(session)
    session_data["data"] = json.loads(session_data["data"])
    return session_data

def delete_expired_sessions(get_db):  
    current_time = time.time()
    # Connect to your SQLite database
    db = get_db()
    cursor = db.cursor()
    # Delete sessions where expires_at is less than the current time
    cursor.execute("DELETE FROM session WHERE expires_at < ?", (current_time,))
    db.commit()
    db.close()
    
def delete_session(get_db,session_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(queries_sql["session"]["delete_session"],(session_id,))
    cursor.close()


queries_functions : Dict[str,Callable] = {
    "get_user_by_email": get_user_by_email,
    "create_new_user" : create_new_user,
    "create_new_session" : create_new_session,
    "get_session" : get_session,
    "delete_expired_sessions" : delete_expired_sessions,
    "delete_session" : delete_session,
    
}

if __name__ == "__main__" :
    db = sqlite3.connect("./db.sqlite")
    db.row_factory = sqlite3.Row
    # all_user()
    # clear_sessions()
    all_sessions()
    db.commit()
    db.close()