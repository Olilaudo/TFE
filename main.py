import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from function import get_point
import json
import os
from function import recognize_face
from function import clear_window


class UserInterface:
    def __init__(self, window):
        self.root = window
        self.users = []

        # main window
        self.root.geometry("1920x1080")

        # layout
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        self.add_user_button = tk.Button(self.button_frame, text="Add user", command=self.add_user)
        self.add_user_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.delete_user_button = tk.Button(self.button_frame, text="Delete selected user", command=self.delete_user)
        self.delete_user_button.pack(side=tk.LEFT, padx=10, pady=10)

        # list of user
        self.listbox = tk.Listbox(self.root)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.listbox.bind("<Double-1>", self.on_double_click)

        self.load_users()
        self.load_listbox()

    def add_user(self):
        answer = simpledialog.askstring("Input", "Name of the new user:", parent=self.root)
        if answer and answer not in self.users:
            face_data = get_point()
            if face_data is None:
                return
            else:
                with open(f"face_data\\{answer}.json", 'w') as f:
                    json.dump(face_data, f)
                with open(f"password_data\\{answer}.json", 'w') as f:
                    json.dump([], f)
                self.load_users()
                self.load_listbox()

    def delete_user(self):
        try:
            index = self.listbox.curselection()[0]
            user_to_delete = self.users[index]
            face_data_to_delete = f'face_data\\{user_to_delete}.json'
            password_data_to_delete = f'password_data\\{user_to_delete}.json'
            if os.path.exists(face_data_to_delete):
                os.remove(face_data_to_delete)
                os.remove(password_data_to_delete)
                del self.users[index]
                self.load_listbox()
        except IndexError:
            messagebox.showerror("Error", "Please select a user to delete.")

    def load_users(self):
        user_names = []
        for filename in os.listdir("face_data"):
            if filename.endswith('.json'):
                user_name = filename[:-5]
                user_names.append(user_name)
        self.users = user_names

    def load_listbox(self):
        self.listbox.delete(0, tk.END)
        for user in self.users:
            self.listbox.insert(tk.END, user)

    def on_double_click(self, event):
        index = self.listbox.curselection()[0]
        user = self.users[index]
        if recognize_face(user) == 1:
            clear_window(self.root)
            PasswordInterface(self.root, user)
        else:
            return


class PasswordInterface:
    def __init__(self, window, user):
        self.root = window
        self.user = user

        self.root.geometry("1920x1080")

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        self.add_user_button = tk.Button(self.button_frame, text="Add element", command=lambda: self.add_element())
        self.add_user_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.delete_user_button = tk.Button(self.button_frame, text="Delete element",
                                            command=lambda: self.delete_element())
        self.delete_user_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.back_button = tk.Button(self.button_frame, text="Back")
        self.back_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(expand=True, fill=tk.BOTH)

        self.tree = ttk.Treeview(self.tree_frame, columns=("platform", "id", "password"), show="headings")
        self.tree.heading("platform", text="Platform")
        self.tree.heading("id", text="ID")
        self.tree.heading("password", text="Password")
        self.tree.column("platform", width=300, anchor=tk.CENTER)
        self.tree.column("id", width=300, anchor=tk.CENTER)
        self.tree.column("password", width=300, anchor=tk.CENTER)

        self.tree.pack(expand=True, fill=tk.BOTH)
        self.load_elements()

    def add_element(self):
        platform = simpledialog.askstring("Add Element", "Enter platform:", parent=self.root)
        if not platform:
            return
        user_id = simpledialog.askstring("Add Element", "Enter user ID:", parent=self.root)
        if not user_id:
            return
        password = simpledialog.askstring("Add Element", "Enter password:", parent=self.root)
        if not password:
            return

        element = [platform, user_id, password]
        self.save_element(element)
        self.load_elements()

    def save_element(self, element):
        file_path = f'password_data\\{self.user}.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
        else:
            data = []

        data.append(element)
        with open(file_path, 'w') as file:
            json.dump(data, file)

    def load_elements(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        file_path = f'password_data\\{self.user}.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
            for element in data:
                self.tree.insert('', tk.END, values=(element[0], element[1], element[2]))

    def delete_element(self):
        selected_element = self.tree.selection()
        if not selected_element:
            messagebox.showerror("Error", "Please select element to delete.")
            return

        file_path = f'password_data\\{self.user}.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
        else:
            messagebox.showerror("Error", "File not found")
            return

        updated_data = []
        for element in data:
            if not any(self.tree.item(item_id)['values'] == element for item_id in selected_element):
                updated_data.append(element)

            with open(file_path, 'w') as file:
                json.dump(updated_data, file)

        self.load_elements()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("User")
    app = UserInterface(root)
    root.mainloop()
