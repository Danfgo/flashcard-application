import database
import classes
import UI
from tkinter import messagebox


def login_button_clicked(login_window, username, password, logging_in):
    # Validation
    if len(username) == 0 and len(password) == 0:
        messagebox.showwarning(title="Warning", message="No username and password entered")
        return
    elif len(username) == 0:
        messagebox.showwarning(title="Warning", message="No username entered")
        return
    elif len(password) < 8 or not any(char.isdigit() for char in password):
        messagebox.showwarning(title="Warning", message="Password must be at least 8 characters in length and have at least one number")
        return

    # Logging in or signing up
    user_id = None
    if logging_in.get():
        user_id = database.login(username, password)
        if user_id == None:
            messagebox.showwarning(title="Warning", message="Incorrect username or password")
            return
    else:
        user_id = database.signup(username, password)
        if user_id == None:
            messagebox.showwarning(title="Warning", message="Username already exists")
            return
    
    # Instantiates user class
    user = classes.User(user_id, username, password)

    # Creates the main menu window, then destroys the login window
    login_window.destroy()
    UI.create_main_menu_window(user)


if __name__ == "__main__":
    database.create_tables()
    UI.create_login_window(login_button_clicked)
