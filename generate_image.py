import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import mysql.connector
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Replace with your Hugging Face API token
API_TOKEN = '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'
API_URL = 'https://api-inference.huggingface.co/models/ZB-Tech/Text-to-Image'

class ImageGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Generator")
        self.root.geometry("800x600")  # Set window size
        self.root.configure(bg='#106EBE')  # Blue background

        self.generated_image = None
        self.current_user_id = None
        self.selected_style = None  # New variable to store selected style

        self.show_login_page()

    def connect_db(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Karna$200513",
            database="TTI"
        )

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_page(self):
        self.clear_frame()
        frame = tk.Frame(self.root, bg="#106EBE")  # Blue background
        frame.pack(pady=20)

        tk.Label(frame, text="Welcome to Image Generator", font=("Arial", 24, 'bold'), bg="#106EBE", fg="black").pack(pady=(0, 20))

        tk.Label(frame, text="Username", bg="#106EBE", fg="black", font=("Arial", 18, 'bold')).pack(pady=10)
        self.username_entry = tk.Entry(frame, font=("Arial", 16), bg="white")
        self.username_entry.pack(pady=10)

        tk.Label(frame, text="Password", bg="#106EBE", fg="black", font=("Arial", 18, 'bold')).pack(pady=10)
        self.password_entry = tk.Entry(frame, show='*', font=("Arial", 16), bg="white")
        self.password_entry.pack(pady=10)

        tk.Button(frame, text="Login", command=self.login, bg="green", fg="white", font=("Arial", 14, 'bold')).pack(pady=(20, 5))
        tk.Button(frame, text="Register", command=self.show_register_page, bg="orange", fg="black", font=("Arial", 14, 'bold')).pack(pady=(5, 20))

    def show_register_page(self):
        self.clear_frame()
        frame = tk.Frame(self.root, bg="#106EBE")  # Blue background
        frame.pack(pady=20)

        tk.Label(frame, text="Register", font=("Arial", 24, 'bold'), bg="#106EBE", fg="black").pack(pady=(0, 20))

        tk.Label(frame, text="Name", bg="#106EBE", fg="black", font=("Arial", 18, 'bold')).pack(pady=10)
        self.name_entry = tk.Entry(frame, font=("Arial", 16), bg="white")
        self.name_entry.pack(pady=10)

        tk.Label(frame, text="Username", bg="#106EBE", fg="black", font=("Arial", 18, 'bold')).pack(pady=10)
        self.register_username_entry = tk.Entry(frame, font=("Arial", 16), bg="white")
        self.register_username_entry.pack(pady=10)

        tk.Label(frame, text="Password", bg="#106EBE", fg="black", font=("Arial", 18, 'bold')).pack(pady=10)
        self.register_password_entry = tk.Entry(frame, show='*', font=("Arial", 16), bg="white")
        self.register_password_entry.pack(pady=10)

        tk.Button(frame, text="Register", command=self.register, bg="green", fg="white", font=("Arial", 14, 'bold')).pack(pady=(20, 5))

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            connection = self.connect_db()
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, password))
            result = cursor.fetchone()

            if result:
                self.current_user_id = result[0]
                messagebox.showinfo("Success", "Login successful")
                self.show_input_frame()
            else:
                messagebox.showerror("Error", "Invalid username or password")
        finally:
            cursor.close()
            connection.close()

    def register(self):
        name = self.name_entry.get()
        username = self.register_username_entry.get()
        password = self.register_password_entry.get()

        try:
            connection = self.connect_db()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (name, username, password) VALUES (%s, %s, %s)",
                           (name, username, password))
            connection.commit()
            messagebox.showinfo("Success", "Registered successfully, please login")
            self.show_login_page()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close()
            connection.close()

    def generate_image(self, prompt, style):
        headers = {
            'Authorization': f'Bearer {API_TOKEN}',
            'Content-Type': 'application/json'
        }
        payload = {
            'inputs': f"{prompt} in {style} style",
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return response.content
        else:
            messagebox.showerror("Error", "Failed to generate image: " + response.text)
            return None

    def on_generate(self):
        prompt = self.prompt_entry.get("1.0", tk.END).strip()
        self.selected_style = self.style_combobox.get()  # Store selected style
        if not prompt:
            messagebox.showwarning("Input Error", "Please enter a prompt.")
            return

        image_data = self.generate_image(prompt, self.selected_style)

        if image_data:
            self.generated_image = image_data
            self.show_output_frame(image_data)

    def show_output_frame(self, image_data):
        self.clear_frame()
        output_frame = tk.Frame(self.root, bg='#106EBE')
        output_frame.pack(fill='both', expand=True)

        output_heading = tk.Label(output_frame, text="Generated Image", bg='#106EBE', fg='black', font=('Arial', 24, 'bold'))
        output_heading.pack(pady=20)

        image = Image.open(BytesIO(image_data))
        desired_size = (500, 500)
        image = image.resize(desired_size, Image.LANCZOS)

        photo = ImageTk.PhotoImage(image)
        image_label = tk.Label(output_frame, image=photo, bg='#106EBE')
        image_label.image = photo
        image_label.pack(pady=10)

        # Display the style used
        style_label = tk.Label(output_frame, text=f"Style: {self.selected_style}", bg='#106EBE', fg='black', font=('Arial', 18, 'bold'))
        style_label.pack(pady=(10, 20))

        button_frame = tk.Frame(output_frame, bg='#106EBE')
        button_frame.pack(pady=10)

        download_button = tk.Button(button_frame, text="Download Image", command=self.download_image, bg='green', fg='black', font=('Arial', 12, 'bold'))
        download_button.pack(side='left', padx=10)

        regenerate_button = tk.Button(button_frame, text="Regenerate Image", command=self.show_input_frame, bg='orange', fg='black', font=('Arial', 12, 'bold'))
        regenerate_button.pack(side='right', padx=10)

        back_button = tk.Button(output_frame, text="Back to Prompt", command=self.show_input_frame, bg='blue', fg='white', font=('Arial', 12, 'bold'))
        back_button.pack(pady=(20, 10))

    def download_image(self):
        if self.generated_image is None:
            messagebox.showwarning("Download Error", "No image to download.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                  filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"),
                                                             ("All files", "*.*")])

        if file_path:
            with open(file_path, 'wb') as file:
                file.write(self.generated_image)
            messagebox.showinfo("Success", "Image downloaded successfully!")

    def show_input_frame(self):
        self.clear_frame()
        frame = tk.Frame(self.root, bg='#106EBE')
        frame.pack(fill='both', expand=True)

        tk.Label(frame, text="Enter text prompt:", bg='#106EBE', fg='black', font=('Arial', 24, 'bold')).pack(pady=20)
        self.prompt_entry = tk.Text(frame, height=5, width=50, font=('Arial', 16), bg='white', fg='black')
        self.prompt_entry.pack(pady=10)

        tk.Label(frame, text="Select art style:", bg='#106EBE', fg='black', font=('Arial', 24, 'bold')).pack(pady=20)
        styles = [ 'realistic', 'cartoon', 'sketch', 'digital art', 'oil painting']
        self.style_combobox = ttk.Combobox(frame, values=styles, font=('Arial', 16))
        self.style_combobox.pack(pady=10)
        self.style_combobox.current(0)  # Set default selection

        generate_button = tk.Button(frame, text="Generate Image", command=self.on_generate, bg='green', fg='black', font=('Arial', 14, 'bold'))
        generate_button.pack(pady=20)

root = tk.Tk()
app = ImageGeneratorApp(root)
root.mainloop()
