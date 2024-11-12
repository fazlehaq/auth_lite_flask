import sqlite3
import os
from dotenv import load_dotenv
from queries import queries

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # Get the database path from environment variables
    db_path = os.getenv("DB_PATH")

    try:
        # Connect to the database using a context manager
        with sqlite3.connect(db_path) as db:
            # Create a cursor using the context manager
            cursor = db.cursor()

            # Execute the queries to create tables
            cursor.execute(queries["user"]["create_table"])
            cursor.execute(queries["session"]["create_table"])

            # Commit the transaction (this happens automatically when using 'with' in sqlite3)
            db.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
