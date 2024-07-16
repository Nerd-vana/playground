import tkinter as tk

def say_hello():
    print("Hello, World!")

# Create the main window
root = tk.Tk()
root.title("Hello Tkinter")

# Create a button widget
hello_button = tk.Button(root, text="Say Hello", command=say_hello)
hello_button.pack()

# Run the application
root.mainloop()
