from datetime import date, timedelta
import database
from tkinter import messagebox


class User():
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        self.decks = []
        
        # Retrieves the name and id of all decks associated with the user, and stores them as the Deck class within the decks list
        deck_information = database.retrieve_decks(self.id)
        for deck_id, deck_name in deck_information:
            self.decks.append(Deck(deck_id, self.id, deck_name))
        
    def add_deck(self, deck_name):       
        deck_id = database.create_deck(self.id, deck_name)
        if deck_id == None:
            messagebox.showwarning(title="Warning", message=f"Deck name '{deck_name}' already exists")
            return
        self.decks.append(Deck(deck_id, self.id, deck_name))
    
    def retrieve_spaced_repetition_settings(self):
        return database.retrieve_spaced_repetition_settings(self.id)

    def save_spaced_repetition_settings(self, initial_ease_factor, min_interval, max_interval, ease_factor_change, lapse_penalty):
        database.save_spaced_repetition_settings(self.id, initial_ease_factor, min_interval, max_interval, ease_factor_change, lapse_penalty)


class Deck():
    def __init__(self, id, user_id, name):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.flashcard_count = database.count_flashcards_in_deck(self.id)
        self.flashcards = []

        flashcard_information = database.retrieve_flashcards(self.id)
        for flashcard_id, question, answer, ease_factor, days_interval, repetitions, due_date, last_reviewed_date in flashcard_information:
            self.flashcards.append(Flashcard(flashcard_id, self.id, question, answer, ease_factor, days_interval, repetitions, due_date, last_reviewed_date, self.user_id))
    
    def rename(self, new_deck_name):
        successful = database.rename_deck(self.user_id, self.name, new_deck_name)
        if not successful:
            messagebox.showwarning(title="Warning", message=f"Deck name '{new_deck_name}' already exists")
            return
        self.name = new_deck_name
    
    def add_flashcard(self, question, answer):
        flashcard_id = database.create_flashcard(self.id, question, answer)
        if flashcard_id == None: # Could not create the flashcard
            messagebox.showwarning(title="Warning", message=f"Question already exists")
            return
        
        flashcard_info = database.retrieve_one_flashcard(flashcard_id) # Retrieves all information from the row in the flashcard table
        self.flashcards.append(Flashcard(*flashcard_info, self.user_id)) # Unpacks the information and stores in a flashcard object
        self.flashcard_count += 1
    
    def study(self):
        flashcards_to_study = []
        for flashcard in self.flashcards:
            due = date.fromisoformat(flashcard.due_date) # Converts due date from string to datetime object so they can be compared
            if due <= date.today(): # If the due date is now or overdue
                flashcards_to_study.append(flashcard)
        return flashcards_to_study


class Flashcard():
    def __init__(self, id, deck_id, question, answer, ease_factor, days_interval, repetitions, due_date, last_reviewed_date, user_id):
        self.id = id
        self.deck_id = deck_id
        self.question = question
        self.answer = answer
        self.ease_factor = ease_factor
        self.days_interval = days_interval
        self.repetitions = repetitions
        self.due_date = due_date
        self.last_reviewed_date = last_reviewed_date
        self.user_id = user_id
    
    def edit_question(self, new_flashcard_question):
        successful = database.edit_flashcard_question(self.deck_id, self.question, new_flashcard_question)
        if not successful:
            messagebox.showwarning(title="Warning", message=f"Question already exists")
            return False
        self.question = new_flashcard_question
        return True
    
    def edit_answer(self, new_flashcard_answer):
        database.edit_flashcard_answer(self.id, new_flashcard_answer)
        self.answer = new_flashcard_answer

    def flashcard_reviewed(self, correct, time_taken_seconds):
        #print(f"\nOriginal due date: {self.due_date}")
        MINIMUM_EASE_FACTOR = 1.3
        initial_ease_factor, min_interval, max_interval, ease_factor_change, lapse_penalty = database.retrieve_spaced_repetition_settings(self.user_id)

        self.last_reviewed_date = date.today().isoformat()

        if not correct:
            self.repetitions = 0
            self.days_interval = min_interval
            self.ease_factor = max(MINIMUM_EASE_FACTOR, self.ease_factor - lapse_penalty) # Returns the bigger value
        else:
            self.repetitions += 1
            if self.repetitions == 1: # If first time getting it correct
                self.days_interval = min_interval
            elif self.repetitions == 2: # If second time getting it correct
                self.days_interval = min_interval * 2
            else:
                self.days_interval = 2
                self.days_interval = int(self.days_interval * self.ease_factor)
            
            self.ease_factor += ease_factor_change
            self.ease_factor = max(MINIMUM_EASE_FACTOR, self.ease_factor)
        
        self.days_interval = min(self.days_interval, max_interval) # Returns the smaller value
        self.due_date = (date.today() + timedelta(days=self.days_interval)).isoformat()
        #print(f"Next due date: {self.due_date}\n")
        database.update_flashcard(self.id, self.ease_factor, self.days_interval, self.repetitions, self.due_date, self.last_reviewed_date) # Stores new information in database
        database.create_review(self.user_id, self.id, time_taken_seconds, self.last_reviewed_date)
