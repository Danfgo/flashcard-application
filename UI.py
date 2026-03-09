import tkinter as tk
from tkinter import simpledialog, ttk, colorchooser, messagebox
import json
import time
from datetime import datetime, timedelta
from database import retrieve_daily_leaderboard, retrieve_weekly_statistics
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator


def create_login_window(login_button_clicked):
    login_window = tk.Tk()
    login_window.geometry("640x480")
    login_window.title("Login")
    login_window.resizable(False, False)

    # A boolean is created to keep track of which state the user is in, logging in or signing up. A button is created to switch between the states.
    logging_in = tk.BooleanVar(value=True)
    login_signup_toggle = tk.Button(login_window, text="Switch to Sign Up", width=20, font=("Arial", 11), bg="gray90", command=lambda:toggle_mode(login_button, logging_in, login_signup_toggle))

    tk.Label(login_window, text="Ikna", font=("Arial", 24, "bold")).pack(pady=(30, 40))

    entry_frame = tk.Frame()
    entry_frame.pack()

    # Username
    username_entry_box = tk.Entry(entry_frame, font=("Arial", 14), width=30, bg="gray90")
    username_entry_box.insert(0, "Username")
    username_entry_box.pack(pady=10)
    username_entry_box.bind("<FocusIn>", lambda event: on_entry_clicked(event, username_entry_box, "username"))

    # Password
    password_entry_box = tk.Entry(entry_frame, font=("Arial", 14), width=30, bg="gray90")
    password_entry_box.insert(0, "Password")
    password_entry_box.pack(pady=10)
    password_entry_box.bind("<FocusIn>", lambda event: on_entry_clicked(event, password_entry_box, "password"))

    login_button_frame = tk.Frame(width=600)
    login_button_frame.pack(pady=10, fill="x")
    # When pressed, the login button will run the login_button_clicked function in the main module. It passes the login window and contents of the entry boxes as arguments
    login_button = tk.Button(login_button_frame, text="Login", width=10, font=("Arial", 12), bg="gray90", command=lambda:login_button_clicked(login_window, username_entry_box.get().strip(), password_entry_box.get().strip(), logging_in))
    login_button.pack(anchor="e", padx=150)

    login_signup_toggle.pack(pady=(100,0))


    login_window.mainloop()


# When either the username or password entry box is clicked, this function is called.
def on_entry_clicked(event, entry, type):
    if type == "password" and entry.get() == "Password":
        entry.config(show="*")
        entry.delete(0, "end")
    elif type == "username" and entry.get() == "Username":
        entry.delete(0, "end")


# Toggles between logging in and signing up
def toggle_mode(login_button, logging_in, login_signup_toggle):
    logging_in.set(not logging_in.get()) # Flip the value of the logging in boolean
    if logging_in.get(): # If true
        login_button.config(text="Login")
        login_signup_toggle.config(text="Switch to Sign Up")
    else: # If false
        login_button.config(text="Sign Up")
        login_signup_toggle.config(text="Switch to Login")


def create_main_menu_window(user_class):
    main_menu_window = tk.Tk()
    main_menu_window.geometry("640x480")
    main_menu_window.title("Main Menu")
    main_menu_window.resizable(False, False)

    side_frame = tk.Frame(main_menu_window, width=180, bg="gray60", relief="solid", borderwidth=1)
    side_frame.pack(side="left", fill="y")

    tk.Label(side_frame, text="Leaderboard", bg="gray60", font=("Arial", 12, "bold")).pack(pady=20)
    leaderboard_display = tk.Frame(side_frame, width=140, height=250, bg="gray60", relief="solid", borderwidth=1)
    leaderboard_display.pack(pady=(5, 20), padx=10)
    leaderboard_display.pack_propagate(False)
    leaderboard_display.grid_propagate(False)
    display_leaderboard(leaderboard_display)

    tk.Button(side_frame, text="Statistics", font=("Arial", 11), bg="gray60", borderwidth=0, command=lambda:statistics_pressed(main_menu_window, user_class)).pack(pady=15)
    tk.Button(side_frame, text="Settings", font=("Arial", 11), bg="gray60", borderwidth=0, command=lambda:settings_pressed(main_menu_window, user_class)).pack(pady=15)

    main_frame = tk.Frame(main_menu_window, bg="white")
    main_frame.pack(fill="both", expand=True)

    tk.Label(main_frame, text="Decks", bg="white", font=("Arial", 18, "bold")).pack(pady=20)

    deck_container = tk.Frame(main_frame, width=350, height=250, relief="solid", borderwidth=1)
    deck_container.pack(pady=10)
    deck_container.pack_propagate(False)

    # Creates a canvas which can be vertically scrolled using the mouse wheel
    canvas = tk.Canvas(deck_container, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    inner_deck_frame = tk.Frame(canvas)
    canvas_window = canvas.create_window((0, 0), window=inner_deck_frame, anchor="nw")
    inner_deck_frame.bind("<Configure>", lambda event:canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda event: canvas.itemconfig(canvas_window, width=event.width))
    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda ev: canvas.yview_scroll(-1*(ev.delta//120), "units")))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    tk.Button(main_frame, text="Create Deck", font=("Arial", 11), bg="white", borderwidth=0, command=lambda:create_deck_pressed(inner_deck_frame, user_class)).pack(pady=(5, 15))
    tk.Button(main_frame, text="Create Flashcards", font=("Arial", 11), bg="white", borderwidth=0, command=lambda:create_flashcard_menu(main_menu_window, inner_deck_frame, user_class)).pack(pady=15)

    show_decks(inner_deck_frame, user_class)

    main_menu_window.mainloop()


def display_leaderboard(display):
    leaderboard_data = retrieve_daily_leaderboard()

    for widget in display.winfo_children():
        widget.destroy()

    # Scrolling
    canvas = tk.Canvas(display, bg="gray60", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    content = tk.Frame(canvas, bg="gray60")
    canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")
    content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda ev: canvas.yview_scroll(-1*(ev.delta//120), "units")))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    header = tk.Frame(content, bg="gray60")
    header.pack(fill="x", padx=5, pady=(5, 2))
    tk.Label(header, text="User", font=("Arial", 10, "bold"), bg="gray60", anchor="w").pack(side="left", fill="x", expand=True)
    tk.Label(header, text="Score", font=("Arial", 10, "bold"), bg="gray60", width=4, anchor="e").pack(side="right")

    # Populating the leaderboard
    for i, (username, score) in enumerate(leaderboard_data, start=1):
        row = tk.Frame(content, bg="gray60")
        row.pack(fill="x", padx=5, pady=2)
        tk.Label(row, text=f"{i}. {username}", bg="gray60", wraplength=95, justify="left", anchor="w").pack(side="left", fill="x", expand=True)
        tk.Label(row, text=str(score), bg="gray60", width=4, anchor="e").pack(side="right")


def statistics_pressed(main_menu_window, user_class):
    statistics_window = tk.Toplevel(main_menu_window)
    statistics_window.title("Statistics")
    statistics_window.geometry("480x320")
    statistics_window.resizable(False, False)

    raw_stats = retrieve_weekly_statistics(user_class.id)
    if not raw_stats: # If raw_stats is empty
        tk.Label(statistics_window, text="You have not yet studied this week!", font=("Arial", 12)).pack(expand=True)
        return

    # Sets up the number of reviews and time spent for each day
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    number_of_reviews = [0] * 7
    time_spent = [0] * 7

    today = datetime.today().date()
    monday = today - timedelta(days=today.weekday())

    date_to_index = {(monday + timedelta(days=i)).isoformat(): i for i in range(7)}

    # Fill data from database
    for day, count, total_time in raw_stats:
        if day in date_to_index:
            index = date_to_index[day]
            number_of_reviews[index] = count
            time_spent[index] = (total_time or 0) / 60  # Converts seconds to minutes

    # Create matplotlib figure
    figure = Figure(figsize=(6, 3), dpi=80)
    reviews_axes, time_axes = figure.subplots(1, 2)

    reviews_axes.bar(weekdays, time_spent, color="#bfbfbf")
    reviews_axes.set_title("Time Spent Studying (min)")

    time_axes.bar(weekdays, number_of_reviews, color="#5f93ad")
    time_axes.set_title("Flashcards Studied")
    time_axes.yaxis.set_major_locator(MaxNLocator(integer=True))

    figure.suptitle("Weekly Statistics")

    canvas = FigureCanvasTkAgg(figure, master=statistics_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


# ----Decks----

def show_decks(inner_deck_frame, user_class):
    # Destroys all UI within the inner deck frame
    for widget in inner_deck_frame.winfo_children():
        widget.destroy()
    
    for deck in user_class.decks:
        deck_frame = tk.Frame(inner_deck_frame, bd=1, relief="solid", padx=10, pady=8)

        deck_name = tk.StringVar(value=deck.name)
        card_count = tk.IntVar(value=deck.flashcard_count)

        name_label = tk.Label(deck_frame, textvariable=deck_name, font=("Arial", 14), anchor="center")
        name_label.pack(fill="x", expand=True) # Deck name
        name_label.bind("<Button-1>", lambda event, d=deck: create_study_ui(inner_deck_frame.winfo_toplevel(), d))

        bottom_frame = tk.Frame(deck_frame)
        bottom_frame.pack(pady=(6, 0))

        tk.Label(bottom_frame, text=f"{card_count.get()} Flashcards").pack(side="left", padx=10) # Flashcard count
        tk.Button(bottom_frame, text="Browse", width=8, borderwidth=0, command=lambda d=deck: create_browse_menu(inner_deck_frame.winfo_toplevel(), d)).pack(side="left", padx=5) # Browse Button
        tk.Button(bottom_frame, text="Rename", width=8, borderwidth=0, command=lambda d=deck: rename_deck_pressed(inner_deck_frame, d, user_class)).pack(side="left", padx=5) # Rename button
            
        deck_frame.pack(fill="x", pady=5)


def create_deck_pressed(inner_deck_frame, user_class):
    deck_name = simpledialog.askstring("Create Deck", "New deck name:")
        
    if deck_name and (deck_name := deck_name.strip()): # Checks to see if name is None or empty
        user_class.add_deck(deck_name)
        show_decks(inner_deck_frame, user_class)


def rename_deck_pressed(inner_deck_frame, deck, user_class): # Checks to see if name is None or empty
    new_deck_name = simpledialog.askstring("Rename Deck", "New deck name:")

    if new_deck_name and (new_deck_name := new_deck_name.strip()):
        deck.rename(new_deck_name)
        show_decks(inner_deck_frame, user_class)
 


# ----Settings----

def settings_pressed(main_menu_window, user_class):
    settings_window = tk.Toplevel(main_menu_window)
    settings_window.title("Settings")
    settings_window.geometry("480x320")
    settings_window.resizable(False, False)
    settings_window.protocol("WM_DELETE_WINDOW", lambda: on_closing_settings(settings_window, user_class, entries))

    tk.Label(settings_window, text="Settings", font=("Arial", 12)).pack(pady=10)

    fields_container = tk.Frame(settings_window, padx=20, pady=20) # Creates a container which holds all of the labels and entry boxes
    fields_container.place(relx=0.5, rely=0.5, anchor="center")
    fields_container.columnconfigure(0, weight=1)
    fields_container.columnconfigure(1, weight=1)

    description_var = tk.StringVar() # Contains the description for the field being hovered over by the mouse

    tk.Label(settings_window, textvariable=description_var, relief="sunken", anchor="w").pack(side="bottom", fill="x") # Displays description

    # Settings fields
    fields = {"Initial Ease Factor": "The starting ease value for new flashcards",
              "Minimum Interval": "The shortest number of days a flaschard can be scheduled for",
              "Maximum Interval": "The largest number of days a flaschard can be scheduled for",
              "Lapse Penalty": "How much the ease of a flashcard is deducted by per incorrect review",
              "Ease Factor Change": "How much the ease of a flaschard is changed per correct review"}
    
    entries = {} # Stores the values of the entry boxes

    for i, field in enumerate(fields):
        label = tk.Label(fields_container, text=field, font=("Arial", 10))
        label.grid(row=i, column=0, sticky="e", pady=5, padx=(0, 10))
        label.bind("<Enter>", lambda e, f=field: show_setting_description(description_var, fields[f]))
        label.bind("<Leave>", lambda e: clear_setting_description(description_var))

        entry = tk.Entry(fields_container, width=10, justify="center")
        entry.insert(0, user_class.retrieve_spaced_repetition_settings()[i])
        entry.grid(row=i, column=1, sticky="w", pady=5)

        entries[field] = entry


def show_setting_description(description_var, text):
    description_var.set(text)


def clear_setting_description(description_var):
    description_var.set("")


def on_closing_settings(settings_window, user_class, entries):
    save = messagebox.askyesno(title="Save", message="Save the changes?")
    if save:
        initial_ease_factor, min_interval, max_interval, ease_factor_change, lapse_penalty = [entry.get() for entry in entries.values()]

        try: # Ensures all values are the correct data type
            initial_ease_factor = float(initial_ease_factor)
            min_interval = int(min_interval)
            max_interval = int(max_interval)
            ease_factor_change = float(ease_factor_change)
            lapse_penalty = float(lapse_penalty)
        except ValueError:
            messagebox.showwarning(title="Warning", message="Invalid inputs entered")
            return

        if initial_ease_factor <= 0 or min_interval <= 0 or max_interval <= 0 or ease_factor_change <= 0 or lapse_penalty <= 0: # Ensures that values cannot be <= 0
            messagebox.showwarning(title="Warning", message="No values must be 0 or negative numbers")
            return
            
        if min_interval > max_interval: # Ensures that min interval can never be greater
            messagebox.showwarning(title="Warning", message="Minimum interval cannot be greater than maximum interval")
            return
        
        user_class.save_spaced_repetition_settings(initial_ease_factor, min_interval, max_interval, ease_factor_change, lapse_penalty)
        settings_window.destroy()
    else:
        settings_window.destroy()
    


# ----Editing Text----

def toggle_tag(text_widget, tag_name, **tag_config):
    if not isinstance(text_widget, tk.Text): # Checks if text_widget is a text object
        return

    if tag_name not in text_widget.tag_names(): # Check if the style (tag name) is already applied
        text_widget.tag_configure(tag_name, **tag_config) # Creates a new tag if not

    try:
        start = text_widget.index("sel.first")
        end = text_widget.index("sel.last")
        # If tag is applied to the first character of the selection, remove the tag. Else, add it.
        if tag_name in text_widget.tag_names("sel.first"):
            text_widget.tag_remove(tag_name, start, end)
        else:
            text_widget.tag_add(tag_name, start, end)
    except tk.TclError:
        pass  # No text selected


def add_bullets(text_widget):
    if not isinstance(text_widget, tk.Text): # Checks if text_widget is a text object
        return

    try:
        start = text_widget.index("sel.first linestart")
        end = text_widget.index("sel.last lineend")
    except tk.TclError:
        return # No text selected

    current_line = start
    while text_widget.compare(current_line, "<=", end): # While current line <= end line
        text_widget.insert(current_line, "• ")
        current_line = text_widget.index(f"{current_line} +1line") # Increments the line


def change_text_colour(text_widget):
    if not isinstance(text_widget, tk.Text): # Checks if text_widget is a text object
        return

    parent = text_widget.winfo_toplevel() # Select flashcard creation window

    colour = colorchooser.askcolor(parent=parent)[1]
    parent.deiconify()
    parent.lift()
    parent.focus_force()

    if not colour:
        return

    tag_name = f"color_{colour}"
    if tag_name not in text_widget.tag_names(): # Check if the tag name is already applied
        text_widget.tag_configure(tag_name, foreground=colour) # Creates a new tag if not

    try:
        text_widget.tag_add(tag_name, "sel.first", "sel.last") # Apply tag to selected text
    except tk.TclError:
        pass # No text selected


def get_active_text_widget(flashcard_creation_window):
    widget = flashcard_creation_window.focus_get() # Selects the widget that the user is currently focused on
    return widget if isinstance(widget, tk.Text) else None # Returns the widget if it is a text widget


# ----Studying Flashcards----


def create_study_ui(main_menu_window, deck):
    question_window = tk.Toplevel(main_menu_window)
    question_window.title("Question")
    question_window.geometry("480x320")
    question_window.resizable(False, False)
    question_window.configure(bg="white")

    main_frame = tk.Frame(question_window, bg="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    main_frame.pack_propagate(False)

    question_answer_text = tk.Text(main_frame, font=("Arial", 14), wrap="word", bg="white", relief="flat", height=4) # Text object which will display the question and answer
    question_answer_text.pack(expand=True, fill="both")
    question_answer_text.config(state="disabled")
    question_answer_text.tag_configure("center", justify="center") # Creates a new tag to centre the text

    button_frame = tk.Frame(main_frame, bg="white")
    button_frame.pack(side="bottom", pady=30, fill="x")

    show_answer_button = tk.Button(button_frame, text="Show Answer", font=("Arial", 11), width=18, height=2, relief="flat", command=lambda: show_flashcard_answer(deck, question_answer_text, incorrect_button, correct_button, button_frame))
    incorrect_button = tk.Button(button_frame, text="Incorrect", font=("Arial", 11), width=14, height=2, relief="flat", command=lambda: next_flashcard(deck, question_answer_text, show_answer_button, button_frame, False))
    correct_button = tk.Button(button_frame, text="Correct", font=("Arial", 11), width=14, height=2, relief="flat", command=lambda: next_flashcard(deck, question_answer_text, show_answer_button, button_frame, True))

    show_flashcard_question(deck, question_answer_text, show_answer_button, button_frame)


def show_flashcard_question(deck, question_answer_text, show_ans_button, button_frame):
    flashcard_list = deck.study()

    # Validation to ensure that the flashcard list is not empty
    if not len(flashcard_list):
        clear_study_buttons(button_frame)
        text = "This deck is complete"
        question_answer_text.config(state="normal")
        question_answer_text.delete("1.0", "end")
        question_answer_text.insert("1.0", text)
        question_answer_text.tag_add("center", "1.0", "end") # Centre the text
        question_answer_text.config(state="disabled")
        return

    current_flaschard = flashcard_list[0] # Retrieves the first flashcard 

    question_answer_text.start_time = time.perf_counter() # Creates the time attribute and sets it to the current time

    question_answer_text.config(state="normal")
    deserialize_text_widget(question_answer_text, current_flaschard.question)
    question_answer_text.tag_add("center", "1.0", "end") # Centre the text
    question_answer_text.config(state="disabled")

    clear_study_buttons(button_frame)
    show_ans_button.pack()


def show_flashcard_answer(deck, question_answer_text, incorrect_button, correct_button, button_frame):
    flashcard_list = deck.study()
    current_flaschard = flashcard_list[0]
    question_answer_text.config(state="normal")
    deserialize_text_widget(question_answer_text, current_flaschard.answer)
    question_answer_text.tag_add("center", "1.0", "end") # Centre the text
    question_answer_text.config(state="disabled")

    clear_study_buttons(button_frame)
    incorrect_button.pack(side="left", padx=20)
    correct_button.pack(side="right", padx=20)


def next_flashcard(deck, question_answer_text, show_ans_button, button_frame, correct):
    flashcard_list = deck.study()
    current_flaschard = flashcard_list[0]

    #Calculate time taken
    end_time = time.perf_counter()
    time_taken = end_time - question_answer_text.start_time

    if correct:
        current_flaschard.flashcard_reviewed(correct, time_taken)
    else:
        current_flaschard.flashcard_reviewed(correct, time_taken)
    show_flashcard_question(deck, question_answer_text, show_ans_button, button_frame)
    

def clear_study_buttons(button_frame):
    for widget in button_frame.winfo_children():
        widget.pack_forget()


# ----Flashcard Browsing----

def create_browse_menu(main_menu_window, deck):
    # Validation to ensure there are flashcards in the deck
    if not deck.flashcards:
        messagebox.showwarning(title="Warning", message=f"No flashcards in {deck.name}")
        return

    browse_window = tk.Toplevel(main_menu_window)
    browse_window.title("Browse Flashcards")
    browse_window.geometry("900x500")

    browse_window.columnconfigure(0, weight=1)
    browse_window.columnconfigure(1, weight=3)
    browse_window.rowconfigure(1, weight=1)

    # Title
    tk.Label(browse_window, text=deck.name, font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)


    # Left Panel (Questions)
    left_frame = tk.Frame(browse_window, bd=1, relief="solid", padx=10, pady=10)
    left_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)

    tk.Label(left_frame, text="Questions", font=("Arial", 12)).pack(anchor="w")

    # Scrolling area
    canvas = tk.Canvas(left_frame, highlightthickness=0)
    canvas.pack(fill="both", expand=True, pady=(5, 0))
    inner_frame = tk.Frame(canvas)
    canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
    inner_frame.bind("<Configure>", lambda event:canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda event: canvas.itemconfig(canvas_window, width=event.width))
    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda ev: canvas.yview_scroll(-1*(ev.delta//120), "units")))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
    
    question_widgets = [] # Stores the text widgets for the flashcards
    selected_flashcard_index = tk.IntVar(value=-1)
    
    # Right Panel (Flashcard)
    right_frame = tk.Frame(browse_window, bd=1, relief="solid", padx=10, pady=10)
    right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)

    tk.Label(right_frame, text="Flashcard", font=("Arial", 12)).pack(anchor="w")

    # Toolbar
    toolbar = tk.Frame(right_frame)
    toolbar.pack(anchor="w", pady=(5, 10))

    default_font = ("Arial", 11)
    bold_font = ("Arial", 11, "bold")
    underline_font = ("Arial", 11, "underline")

    tk.Button(toolbar, text="B", width=3, borderwidth=0, command=lambda: toggle_tag(get_active_text_widget(browse_window), "bold", font=bold_font)).pack(side="left", padx=3)
    tk.Button(toolbar, text="U", width=3, borderwidth=0, command=lambda: toggle_tag(get_active_text_widget(browse_window), "underline", font=underline_font)).pack(side="left", padx=3)
    tk.Button(toolbar, text="Bullet Points", borderwidth=0, command=lambda: add_bullets(get_active_text_widget(browse_window))).pack(side="left", padx=3)
    tk.Button(toolbar, text="Change Text Colour", borderwidth=0, command=lambda: change_text_colour(get_active_text_widget(browse_window))).pack(side="left", padx=10)

    question_entry = tk.Text(right_frame, height=3, wrap="none", font=default_font, bd=1, relief="solid", padx=10, pady=8)
    question_entry.pack(fill="x", pady=(0, 10))
    question_entry.insert("1.0", "Select a question")
    question_entry.config(state="disabled")
    original_question_entry_text = tk.StringVar(value="")

    answer_entry = tk.Text(right_frame, font=default_font, wrap="word", bd=1, relief="solid", padx=10, pady=10, height=5)
    answer_entry.pack(fill="both", expand=True)
    answer_entry.config(state="disabled")
    
    # Edit and delete buttons
    button_frame = tk.Frame(right_frame)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Edit", width=10, command=lambda:edit_flashcard(browse_window, question_entry, answer_entry, deck, selected_flashcard_index.get(), original_question_entry_text.get())).pack(side="left", padx=10)
    tk.Button(button_frame, text="Delete", width=10).pack(side="left", padx=10)

    # Creating Question List
    for i, flashcard_json in enumerate(deck.flashcards):
        text_widget = tk.Text(inner_frame, height=1, wrap="none", font=("Arial", 10), bd=0, padx=5, pady=6, bg="white", cursor="hand2") # Creates the text widget that the question will be stored in

        deserialize_text_widget(text_widget, flashcard_json.question) # Enters the formatted question into the text widget

        text_widget.update_idletasks()

        max_lines = 3
        line_count = min(int(text_widget.index("end-1c").split(".")[0]), max_lines) # Calculates how many lines each question should use in the left frame, capping it at 3

        text_widget.config(height=line_count)
        text_widget.config(state="disabled", highlightthickness=0)
        text_widget.pack(fill="x")
        text_widget.bind("<Button-1>", lambda e, index=i: load_browse_flashcard(index, question_widgets, deck, question_entry, answer_entry, selected_flashcard_index, original_question_entry_text)) # When the text is clicked, executes the function

        question_widgets.append(text_widget)


def load_browse_flashcard(index, question_widgets, deck, question_entry, answer_entry, selected_flashcard_index, original_question_entry_text):
    selected_flashcard_index.set(index)

    for widget in question_widgets:
        widget.config(bg="white") # By default, all widgets have a white background

    question_widgets[index].config(bg="gray90") # The selected widget has a grey background

    # Loads the question and answer data into the right frame
    flashcard = deck.flashcards[index]

    question_entry.config(state="normal")
    question_entry.delete("1.0", "end")
    deserialize_text_widget(question_entry, flashcard.question)
    original_question_entry_text.set(question_entry.get("1.0", "end-1c").strip())

    answer_entry.config(state="normal")
    answer_entry.delete("1.0", "end")
    deserialize_text_widget(answer_entry, flashcard.answer)


def edit_flashcard(browse_window, question_entry, answer_entry, deck, selected_flashcard_index, original_question_entry_text):
    # Validation to ensure a flashcard was selected
    if selected_flashcard_index == -1:
        browse_window.destroy()
        messagebox.showwarning(title="Warning", message=f"No flashcard selected")
        return

    selected_flashcard = deck.flashcards[selected_flashcard_index]

    # Validation to ensure question is not empty
    question_text = question_entry.get("1.0", "end-1c").strip()
    if not question_text:
        browse_window.destroy()
        messagebox.showwarning(title="Warning", message=f"No question entered")
        return
    
    question_data = serialize_text_widget(question_entry) # Turns text into json
    answer_data = serialize_text_widget(answer_entry)
    
    # Checks to see if the question was changed
    if question_text == original_question_entry_text: # Only answer / neither were changed
        selected_flashcard.edit_answer(answer_data)
    else: # Question / both were changed
        changed_question = selected_flashcard.edit_question(question_data)
        if changed_question:
            selected_flashcard.edit_answer(answer_data)


    browse_window.destroy()



# ----Flashcard Creation----

def create_flashcard_menu(main_menu_window, inner_deck_frame, user_class):
    if not len(user_class.decks):
        messagebox.showwarning(title="Warning", message=f"No decks in existence")
        return

    flashcard_creation_window = tk.Toplevel(main_menu_window)
    flashcard_creation_window.title("Create Flashcard")
    flashcard_creation_window.geometry("480x320")
    flashcard_creation_window.resizable(False, False)

    toolbar = tk.Frame(flashcard_creation_window)
    toolbar.pack(padx=10, pady=5, fill="x")
    
    # Combobox drop down
    deck_var = tk.StringVar(value=user_class.decks[0].name if len(user_class.decks) else None)
    style = ttk.Style(flashcard_creation_window)
    style.theme_use("default")
    style.configure("Gray.TCombobox", fieldbackground="gray90", background="gray90")

    deck_map = {deck.name: deck for deck in user_class.decks} # Maps each deck name to its deck object within the decks list
    ttk.Combobox(toolbar, textvariable=deck_var, values= list(deck_map.keys()) if len(user_class.decks) else [], width=10, state="readonly", style="Gray.TCombobox").pack(side="right")

    default_font = ("Arial", 11)
    bold_font = ("Arial", 11, "bold")
    underline_font = ("Arial", 11, "underline")

    tk.Label(flashcard_creation_window, text="Question", font=("Arial", 11)).pack(anchor="w", padx=10)
    question_entry = tk.Text(flashcard_creation_window, font=default_font, height=3, wrap="word")
    question_entry.pack(padx=10, fill="x")

    tk.Label(flashcard_creation_window, text="Answer", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(10, 0))
    answer_entry = tk.Text(flashcard_creation_window, font=default_font, height=3, wrap="word")
    answer_entry.pack(padx=10, fill="x")

    tk.Button(flashcard_creation_window, text="Create", width=15, bg="gray90", command=lambda:create_flashcard(flashcard_creation_window, question_entry, answer_entry, deck_map[deck_var.get()], inner_deck_frame, user_class)).pack(pady=15)

    tk.Button(toolbar, text="B", width=3, borderwidth=0, command=lambda: toggle_tag(get_active_text_widget(flashcard_creation_window), "bold", font=bold_font)).pack(side="left", padx=2)
    tk.Button(toolbar, text="U", width=3, borderwidth=0, command=lambda: toggle_tag(get_active_text_widget(flashcard_creation_window), "underline", font=underline_font)).pack(side="left", padx=2)
    tk.Button(toolbar, text="Bullet Points", borderwidth=0, command=lambda: add_bullets(get_active_text_widget(flashcard_creation_window))).pack(side="left", padx=5)
    tk.Button(toolbar, text="Change Text Colour", borderwidth=0, command=lambda: change_text_colour(get_active_text_widget(flashcard_creation_window))).pack(side="left", padx=5)


def create_flashcard(flashcard_creation_window, question_entry, answer_entry, selected_deck, inner_deck_frame, user_class):
    # Validation to ensure question is not empty
    question_text = question_entry.get("1.0", "end-1c").strip()
    if not question_text:
        flashcard_creation_window.destroy()
        messagebox.showwarning(title="Warning", message=f"No question entered")
        return
    
    question_data = serialize_text_widget(question_entry) # Turns text into json
    answer_data = serialize_text_widget(answer_entry)
    selected_deck.add_flashcard(question_data, answer_data)
    show_decks(inner_deck_frame, user_class)
    question_entry.delete("1.0", "end") # Deletes contents of textboxes
    answer_entry.delete("1.0", "end")


def serialize_text_widget(text_widget):
    data = {"text": text_widget.get("1.0", "end-1c"), "tags": {}} # Stores the plain text and all tags applied to that text
    
    for tag in text_widget.tag_names(): # Loop through all tags in the text widget
        if tag == "sel":
            continue
        ranges = text_widget.tag_ranges(tag) # Retrieves where the tag is applied
        data["tags"][tag] = {"ranges":[(str(ranges[i]), str(ranges[i+1])) for i in range(0, len(ranges), 2)], "config": {"foreground": text_widget.tag_cget(tag, "foreground"), "font": text_widget.tag_cget(tag, "font")}} # Stores where the tag is applied and the visual styling of the text
    
    return json.dumps(data)


def deserialize_text_widget(text_widget, json_data):
    data = json.loads(json_data)

    text_widget.delete("1.0", "end")
    text_widget.insert("1.0", data["text"]) # Inserts plain text into the widget

    # Loops over each tag and applies it to the text
    for tag, info in data["tags"].items():
        text_widget.tag_configure(tag, **info["config"])
        for start, end in info["ranges"]:
            text_widget.tag_add(tag, start, end)


