import sqlite3
from datetime import date

DATABASE_NAME = 'test#17'

# Creates the tables required in the database
def create_tables():
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(CREATE_USER_TABLE)
        cursor.execute(CREATE_DECKS_TABLE)
        cursor.execute(CREATE_FLASHCARDS_TABLE)
        cursor.execute(CREATE_REVIEWS_TABLE)
        cursor.execute(CREATE_SPACED_REPETITON_SETTINGS_TABLE)

def signup(username, password):
    try:
        with sqlite3.connect(DATABASE_NAME) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            result = cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password)).fetchone()
            cursor.execute("INSERT INTO spaced_repetition_settings (user_id) VALUES (?)", (result[0],)) # Creates spaced repeptition field
        return result[0] # Returns the id of the user if successfully created
    except sqlite3.IntegrityError:
        return None

def login(username, password):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        # Checks if username and password exist
        result = cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    return result[0] if result else None # Returns the id of the user if successfully found

def create_deck(user_id, deck_name):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        # Checks to see if the user already has a deck with the name they are trying to select
        name_exists = cursor.execute("SELECT EXISTS (SELECT 1 FROM decks WHERE user_id=? AND name=?)", (user_id, deck_name)).fetchone()
        if name_exists[0]:
            return None
        
        cursor.execute("INSERT INTO decks (user_id, name) VALUES (?, ?)", (user_id, deck_name))
        # Return the id of the deck
        return cursor.lastrowid

def rename_deck(user_id, old_deck_name, new_deck_name):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        # Checks to see if the user already has a deck with the new name they are trying to select
        name_exists = cursor.execute("SELECT EXISTS (SELECT 1 FROM decks WHERE user_id=? AND name=?)", (user_id, new_deck_name)).fetchone()
        if name_exists[0]:
            return False
        cursor.execute("UPDATE decks SET name=? WHERE user_id=? AND name=?", (new_deck_name, user_id, old_deck_name))
        return True



def create_flashcard(deck_id, question, answer):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        question_exists = cursor.execute("SELECT EXISTS (SELECT 1 FROM flashcards WHERE deck_id=? AND question=?)", (deck_id, question)).fetchone()
        if question_exists[0]:
            return None

        user_id = cursor.execute("SELECT user_id FROM decks WHERE id=?", (deck_id,)).fetchone()[0]
        ease_factor_setting = cursor.execute("SELECT initial_ease_factor FROM spaced_repetition_settings WHERE user_id=?", (user_id,)).fetchone()
        ease_factor = ease_factor_setting[0] if ease_factor_setting else 2.5 # If exists use the value given else use 2.5

        today = date.today().isoformat()

        cursor.execute("INSERT INTO flashcards (deck_id, question, answer, ease_factor, due_date, last_reviewed_date, repetitions) VALUES (?, ?, ?, ?, ?, NULL, ?)", (deck_id, question, answer, ease_factor, today, 0))

        # Return the id
        return cursor.lastrowid


def edit_flashcard_question(deck_id, old_flashcard_question, new_flashcard_question):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        # Check to see if the deck already has a question with the new question they are trying to select
        question_exists = cursor.execute("SELECT EXISTS (SELECT 1 FROM flashcards WHERE deck_id=? AND question=?)", (deck_id, new_flashcard_question)).fetchone()
        if question_exists[0]:
            return False
        cursor.execute("UPDATE flashcards SET question=? WHERE deck_id=? AND question=?", (new_flashcard_question, deck_id, old_flashcard_question))
        return True

def edit_flashcard_answer(flashcard_id, new_flashcard_answer):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE flashcards SET answer=? WHERE id=?", (new_flashcard_answer, flashcard_id))


# Updates the flashcard table when a flashcard has been reviewed
def update_flashcard(flashcard_id, ease_factor, days_interval, repetitions, due_date, last_reviewed_date):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE flashcards SET ease_factor=?, days_interval=?, repetitions=?, due_date=?, last_reviewed_date=? WHERE id=?", (ease_factor, days_interval, repetitions, due_date, last_reviewed_date, flashcard_id))


# Returns the deck id and name
def retrieve_decks(user_id):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        result = cursor.execute("SELECT id, name FROM decks WHERE user_id=?", (user_id,)).fetchall()
    return result

# Returns every flashcard's information belonging to a deck
def retrieve_flashcards(deck_id):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        result = cursor.execute("SELECT id, question, answer, ease_factor, days_interval, repetitions, due_date, last_reviewed_date FROM flashcards WHERE deck_id=?", (deck_id,)).fetchall()
    return result

def retrieve_one_flashcard(flashcard_id):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        return cursor.execute("SELECT id, deck_id, question, answer, ease_factor, days_interval, repetitions, due_date, last_reviewed_date FROM flashcards WHERE id=?", (flashcard_id,)).fetchone()
    
def count_flashcards_in_deck(deck_id):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        result = cursor.execute("SELECT COUNT(*) FROM flashcards WHERE deck_id=?", (deck_id,)).fetchone()
    return result[0]


def retrieve_spaced_repetition_settings(user_id):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        return cursor.execute("SELECT initial_ease_factor, min_interval, max_interval, ease_factor_change, lapse_penalty FROM spaced_repetition_settings WHERE user_id=?", (user_id,)).fetchone()


# Updates the spaced repetitionn settings table
def save_spaced_repetition_settings(user_id, initial_ease_factor, min_interval, max_interval, ease_factor_change, lapse_penalty):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE spaced_repetition_settings SET initial_ease_factor=?, min_interval=?, max_interval=?, ease_factor_change=?, lapse_penalty=? WHERE user_id=?", (initial_ease_factor, min_interval, max_interval, ease_factor_change, lapse_penalty, user_id))


def create_review(user_id, flashcard_id, duration, time):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO reviews (user_id, flashcard_id, duration_seconds, time_reviewed_at) VALUES (?,?,?,?)", (user_id,flashcard_id, duration, time))
        return cursor.lastrowid


def retrieve_daily_leaderboard():
    today = date.today().isoformat()

    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        results = cursor.execute("""SELECT users.username, COUNT(reviews.id) as review_count FROM reviews JOIN users ON users.id = reviews.user_id WHERE date(reviews.time_reviewed_at) = ? GROUP BY users.id ORDER BY review_count DESC LIMIT 10""", (today,)).fetchall()
    return results


def retrieve_weekly_statistics(user_id):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        results = cursor.execute("""SELECT date(time_reviewed_at) as day, COUNT(id) as flashcard_count, SUM(duration_seconds) as total_time FROM reviews WHERE user_id = ? AND date(time_reviewed_at) >= date('now', '-6 days') GROUP BY day ORDER BY day""", (user_id,)).fetchall()
    return results


#  Below are the commands defining each table

CREATE_USER_TABLE = """CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY,
               username TEXT NOT NULL UNIQUE,
               password TEXT NOT NULL
               )"""

CREATE_DECKS_TABLE = """CREATE TABLE IF NOT EXISTS decks (
               id INTEGER PRIMARY KEY,
               user_id INTEGER NOT NULL,
               name TEXT,
               FOREIGN KEY (user_id) REFERENCES users(id)
               )"""

CREATE_FLASHCARDS_TABLE = """CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY,
                deck_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT,
                ease_factor REAL,
                days_interval INTEGER DEFAULT 0,
                repetitions INTEGER DEFAULT 0,
                due_date TEXT,
                last_reviewed_date TEXT,
                FOREIGN KEY (deck_id) REFERENCES decks(id)
                )"""

CREATE_REVIEWS_TABLE = """ CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                flashcard_id INTEGER NULL,
                duration_seconds INTEGER,
                time_reviewed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (flashcard_id) REFERENCES flashcards(id)
                )"""

CREATE_SPACED_REPETITON_SETTINGS_TABLE= """CREATE TABLE IF NOT EXISTS spaced_repetition_settings (
                user_id INTEGER PRIMARY KEY,
                initial_ease_factor REAL DEFAULT 2.5,
                min_interval INTEGER DEFAULT 1,
                max_interval INTEGER DEFAULT 365,
                ease_factor_change REAL DEFAULT 0.15,
                lapse_penalty REAL DEFAULT 0.2,
                FOREIGN KEY (user_id) REFERENCES users(id)
                )"""