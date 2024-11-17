from flask import Flask, g, request, jsonify, render_template , make_response
import sqlite3
import bcrypt
import hashlib 
import time,json
from queries import queries_functions
from apscheduler.schedulers.background import BackgroundScheduler
from functools import wraps
from cache import SessionCache

# setting up app
flask_app = Flask(__name__,template_folder="templates")
flask_app.config['DATABASE'] = './db.sqlite'
flask_app.config['SESSION_DURATION'] = 2
flask_app.config["SESSION_CLEANUP_INTERVAL"] = 3
flask_app.config["IS_DEBUGGING"] = True
flask_app.config["SESSION_CACHE_LIMIT"] = 30


#db functions
def get_db():
    if 'db' not in g :
        g.db = sqlite3.connect(flask_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

#helper functions 
def hash_password(password:str) -> str :
    return bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())

def verify_password(actual_password:bytes,entered_password:str) -> bool : 
    return bcrypt.checkpw(
        password=entered_password.encode('utf-8'),
        hashed_password=actual_password
    )
    
def generate_session_id(data:str) -> str:
    return hashlib.sha256((data+str(time.time())).encode()).hexdigest()


# decorators
def ensureAuthenticated(f):
    @wraps(f)
    def decorated_fn(*args,**kwargs):
        print("running ensure auth")
        print(g.is_authenticated)
        if not g.get('is_authenticated') :
            return jsonify({"message" : "Authentication required"})
        return f(*args,*kwargs)
    return decorated_fn


# middlewares
# Extracts session id from request and populate g object with session if exists
@flask_app.before_request
def extract_session_data():
    print("*************REQUEST STARTED*************")
    session_id = request.cookies.get("session_id")
    
    # No session cookie found
    if not session_id : 
        print("No session cookie")
        g.session = None
        g.is_authenticated = False
    
    # Session cookie exists in request
    else : 
        session = queries_functions["get_session"](get_db,session_id)
        # expired session might have been deleted
        if not session :
            print("Expired and Deleted Session")
            g.clear_session_cookie = True 
            g.session = None
            g.is_authenticated = False
            
        else :
            # check if session is expired or not
            print(session)
            if session["expires_at"] < time.time() :
                print("Expired Session")
                g.clear_session_cookie = True 
                g.session = None
                g.is_authenticated = False
            else :
                print("Session found")
                g.session = session
                g.is_authenticated = True    

@flask_app.after_request
def clear_session_cookie(response):
    if getattr(g,'clear_session_cookie',False) :
        response.set_cookie("session_id","",expires=0)
        response.status_code = 401
    return response
    

# routes
@flask_app.route('/')
def home():
    if not g.is_authenticated : 
        return jsonify({"message" : "Not logged in" })
    return jsonify({"message" : f"Authenticated {g.session['data']['username']}"})

@flask_app.route('/login',methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    # Grabbing users payload from form
    email = request.form.get("email")
    password = request.form.get("password")
    
    # fecthing user data from db
    user = queries_functions["get_user_by_email"](get_db,str(email))    
    
    # Checking if user exists
    if user is None :
        return jsonify({"message" : f"No user exists with emailId {email}"}) , 404
    
    # verifying password
    actual_password = user["password"]
    if not verify_password(entered_password=password,actual_password=actual_password) :
        return jsonify({"message" : f"Incorrect Password "}) , 401
    
    # create new session 
    session_id = generate_session_id(data=email)
    data = {
        "email" : email,
        "username" : user["name"],
        "id" : user["id"]
    }
    data = json.dumps(data)
    expires_at = time.time() + (60 * flask_app.config["SESSION_DURATION"])
    
    is_session_created = queries_functions["create_new_session"](get_db=get_db,session_id=session_id,data=data,expires_at=expires_at)
    
    if not is_session_created :
        print("could not create session")
        return jsonify({"message" : "Could not login"})
        
    #setting up response
    response = make_response(jsonify({"message" : "Login Successful"}))
    response.set_cookie("session_id", session_id, secure=True,httponly=True, samesite="Lax")
    return response

@flask_app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "GET" :
        return render_template("register.html")
    
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    
    if email is None :
        return jsonify({"message" : "Email-id is required!"}) , 400
    if username is None : 
        return jsonify({"message" : "username is required!"}) , 400
    if password is None :
        return jsonify({"message" : "password is required!"}) , 400
    
    hashed_password = hash_password(password)
    is_user_registered = queries_functions["create_new_user"](get_db=get_db,email=email,username=username,password=hashed_password)
    
    if not is_user_registered :
        return jsonify({"message" : f"User already exists with email id {email}"}) 
    
    return jsonify({"message" : "User registered sucessfully"}) , 201

@ensureAuthenticated
@flask_app.route("/logout")
def logout():
    session_id = g.session.session_id
    g.clear_session_cookie = True
    queries_functions["delete_session"](get_db,session_id)
    return jsonify({"message" : "Logged out"})


@flask_app.route("/protected")
@ensureAuthenticated
def protected() :
    return "protected"

# running app
if __name__ == '__main__' :
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(lambda : queries_functions["delete_expired_sessions"](get_db), 'interval', minutes=60*flask_app.config["SESSION_CLEANUP_INTERVAL"])
    scheduler.start()
    flask_app.run(host="0.0.0.0",debug=True,use_reloader=True)