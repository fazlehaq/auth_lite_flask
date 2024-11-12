# auth_lite_flask

**auth_lite_flask** is a lightweight authentication and session management system built using Flask and SQLite. Designed with simplicity and efficiency in mind, it includes features for secure login, session management, and protection of resources. All functionality, including session handling, is implemented manually without using ORMs or other libraries, ensuring low overhead and direct control over data flow.

## Features

- **Custom Authentication and Authorization**: Secure login, session creation, and protected resources.
- **Manual Session Management**: Sessions are created, validated, and cleared entirely within the codebase, backed by SQLite.
- **Session Expiration and Cleanup**: Uses `APScheduler` to periodically clear expired sessions.
- **Configurable Settings**: Session duration, cleanup intervals, and cache limits are configurable in `flask_app.config`.
- **Planned LRU Cache**: (Upcoming) LRU cache for sessions to improve efficiency.
- **Minimal Dependencies**: Built using Flask without ORMs or other frameworks that add overhead.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/fazlehaq/auth_lite_flask.git
   cd auth_lite_flask
   ```

2. **Set Up a Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Requirements**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Database Initialization**: Ensure the SQLite database is set up with required tables.

   ```bash
   python init_db.py
   ```

## Configuration

All configuration settings are managed in `flask_app.config`:

- **SESSION_DURATION**: Duration of each session in minutes.
- **SESSION_CLEANUP_INTERVAL**: Frequency of session cleanup, in minutes.
- **SESSION_CACHE_LIMIT**: Limit for session cache (for planned LRU cache functionality).

## Usage

### Running the Application

1. **Start the Server**:

   ```bash
   flask run
   ```

   The server will run at `http://127.0.0.1:5000`.

2. **APScheduler** is configured to clear expired sessions automatically based on the interval set in `SESSION_CLEANUP_INTERVAL`.

### API Endpoints

- **/login**:
  - `POST`: Login to create a session. Requires form data with `email` and `password`.
  - `GET`: Returns the login page.
- **/register**:

  - `POST`: Register a new user. Requires form data with `email`, `username`, and `password`.
  - `GET`: Returns the registration page.

- **/logout**:

  - `GET`: Log out the current session, clear the session cookie, and remove the session from the database.

- **/protected**:
  - `GET`: Access a protected resource, accessible only to authenticated users.

### Middleware

The application includes middleware that checks session validity for each request. If a session is expired or invalid, it clears the session cookie and prevents access to protected resources.

### Example Usage

1. **Register**:

   - Navigate to `/register` to register a new user or send a `POST` request with `email`, `username`, and `password`.

2. **Login**:

   - Navigate to `/login` or send a `POST` request with `email` and `password`. If successful, a session ID is generated and stored in cookies.

3. **Access Protected Resource**:

   - After logging in, access `/protected` to view a protected message. This route is only accessible with a valid session.

4. **Logout**:
   - Call `/logout` to clear the session cookie and remove the session from the database.

## Implementation Details

- **Session Management**: Sessions are created with a unique session ID, stored in SQLite with an expiration timestamp. Sessions are validated on each request and removed after expiration.
- **Password Hashing**: Passwords are securely hashed with bcrypt before storage.
- **Session Cleanup**: Expired sessions are removed from the database by a background job using `APScheduler`.
- **Authentication Decorator**: `ensureAuthenticated` is a decorator that checks session validity and protects sensitive routes.
- **Session Cache** (In Development): A planned LRU cache to optimize session handling.

## Future Improvements

- **Implementing LRU Cache**: To further improve performance by reducing database reads for active sessions.
