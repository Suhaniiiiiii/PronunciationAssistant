import tkinter as tk
from tkinter import messagebox
import os
import hashlib #added to encrypt passwords in text file
import random
import speech_recognition as sr
import sounddevice as sd
import wave
from io import BytesIO
from gtts import gTTS
import os
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tempfile
from playsound import playsound
from tkinter.ttk import Progressbar
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from transformers import Wav2Vec2Tokenizer
import torch
import numpy as np


class PronunciationDetector:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("Pronunciation Assistant- Mastering the Spoken Word")
        self.root.geometry("850x650")
        self.root.configure(bg='#e0f7fa')
        
        # Load wav2vec 2.0 model and tokenizer
        self.processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
        self.model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")
        self.tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-large-960h")
        # Initialize user data
        self.current_sentence = ""
        self.logged_in = True
        self.user_data = {"correct_count": 0, "incorrect_count": 0}
        
        # Call UI creation methods
        self.create_main_screen()


    def create_main_screen(self):
        # Header Section
        header_frame = tk.Frame(self.root, bg='#00796b', height=80)  # Teal header
        header_frame.pack(fill=tk.X)

        # Welcome Label in the header
        self.label = tk.Label(header_frame, text=f"Welcome, {self.username}!", font=("Arial", 20, "bold"), bg='#00796b', fg='white')
        self.label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Logout Button in the header
        self.logout_button = tk.Button(header_frame, text="Logout", command=self.logout, font=("Arial", 12, "bold"), bg="#ff5252", fg="white")
        self.logout_button.place(relx=0.93, rely=0.5, anchor=tk.CENTER)

        # Body Frame
        body_frame = tk.Frame(self.root, bg='#e0f7fa')
        body_frame.pack(pady=30)

        # Sentence Input Section (Custom or Random Sentence)
        input_frame = tk.Frame(body_frame, bg='#b2dfdb', padx=20, pady=20)  # Light teal for sentence input area
        input_frame.pack(pady=10)

        sentence_label = tk.Label(input_frame, text="Enter or Get a Random Sentence:", font=("Arial", 14), bg='#b2dfdb')
        sentence_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.custom_sentence_entry = tk.Entry(input_frame, font=("Arial", 14), width=50)
        self.custom_sentence_entry.grid(row=1, column=0, columnspan=2, pady=10)

        self.random_sentence_button = tk.Button(input_frame, text="Get Random Sentence", command=self.get_random_sentence, font=("Arial", 12), bg="#00796b", fg="white")
        self.random_sentence_button.grid(row=2, column=0, padx=10, pady=10)

        self.type_sentence_button = tk.Button(input_frame, text="Type Your Sentence", command=self.type_sentence, font=("Arial", 12), bg="#00796b", fg="white")
        self.type_sentence_button.grid(row=2, column=1, padx=10, pady=10)

        # Pronunciation Recording Section
        record_frame = tk.Frame(body_frame, bg='#b2dfdb', padx=20, pady=20)
        record_frame.pack(pady=10)

        record_label = tk.Label(record_frame, text="Record Your Pronunciation:", font=("Arial", 14), bg='#b2dfdb')
        record_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.record_button = tk.Button(record_frame, text="Record Pronunciation", command=self.record_sentence, font=("Arial", 14), bg="#00796b", fg="white")
        self.record_button.grid(row=1, column=0, padx=10, pady=10)

        self.progress = Progressbar(record_frame, length=200, mode='determinate')
        self.progress.grid(row=1, column=1, padx=10, pady=10)

        # Results Display Section
        result_frame = tk.Frame(body_frame, bg='#b2dfdb', padx=20, pady=20)
        result_frame.pack(pady=10)

        self.result_text = tk.Text(result_frame, height=6, width=65, bg='#ffffff', fg='black', font=("Arial", 12), relief=tk.SUNKEN)
        self.result_text.pack(pady=10)

        # Score Graph Button
        self.graph_button = tk.Button(body_frame, text="Show Score Graph", command=self.show_graph, font=("Arial", 14), bg="#00796b", fg="white")
        self.graph_button.pack(pady=20)

    def get_random_sentence(self):
        try:
            with open("database.txt", "r") as file:
                sentences = file.readlines()
            self.current_sentence = random.choice(sentences).strip()
        except FileNotFoundError:
            messagebox.showwarning("Error", "Sentences file not found.")
            return

        self.label.config(text=f"Random Sentence: {self.current_sentence}")

    def type_sentence(self):
        self.current_sentence = self.custom_sentence_entry.get()
        if not self.current_sentence.strip():
            messagebox.showwarning("Input Error", "Please enter a valid sentence.")
        else:
            self.label.config(text=f"Typed Sentence: {self.current_sentence}")

    def normalize_text(self, text):
        return ''.join(e for e in text.lower() if e.isalnum() or e.isspace()).strip()

    '''def get_phonemes(self, text):
        try:
            phonemes = self.g2p(text)
            return ' '.join(phonemes).strip()  # Convert list to string and strip whitespace
        except Exception as e:
            messagebox.showerror("Phoneme Error", f"Error in generating phonemes: {e}")
            return ""
    '''

    def speak_correct_pronunciation(self):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_path = temp_file.name
            tts = gTTS(self.current_sentence)
            tts.save(temp_path)
            playsound(temp_path)
            os.remove(temp_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not play the sound: {e}")

    def record_sentence(self):
        if not self.logged_in:
            messagebox.showwarning("Login Required", "Please log in to use this feature.")
            return

        if not self.current_sentence:
            messagebox.showwarning("Sentence Required", "Please provide a sentence first.")
            return

        self.label.config(text="Getting ready for listening...")
        fs = 16000  # Sampling rate required for wav2vec 2.0
        duration = 7  # Recording duration
        self.update_progress(duration)
        self.label.config(text=f"Sentence: {self.current_sentence}\nListening...")
        
        # Record the audio
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()

        # Convert the recorded audio to numpy and then to torch tensor
        recording = np.squeeze(recording)
        input_values = self.processor(recording, sampling_rate=fs, return_tensors="pt").input_values

        # Pass audio through the model
        self.label.config(text="Processing...")

        # Inference
        with torch.no_grad():
            logits = self.model(input_values).logits

        # Decode the transcription
        predicted_ids = torch.argmax(logits, dim=-1)
        text = self.tokenizer.batch_decode(predicted_ids)[0]

        # Continue with normalization and comparison logic...
        transcribed_text = self.normalize_text(text)
        expected_text = self.normalize_text(self.current_sentence)

        # Compare texts
        if transcribed_text == expected_text:
            result = "Correct pronunciation!"
            self.user_data["correct_count"] += 1
        else:
            result = "Incorrect pronunciation."
            self.user_data["incorrect_count"] += 1
            self.speak_correct_pronunciation()

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Transcribed Text:\n{text}\n{result}")
        self.show_scoreboard()

    def show_scoreboard(self):
        score = f"Correct: {self.user_data['correct_count']}, Incorrect: {self.user_data['incorrect_count']}"
        self.result_text.insert(tk.END, f"\nYour Score: {score}")

    def update_progress(self, duration):
        for i in range(101):
            self.progress['value'] = i
            self.root.update_idletasks()
            time.sleep(duration / 100)

    def show_graph(self):
        correct = self.user_data["correct_count"]
        incorrect = self.user_data["incorrect_count"]

        if correct == 0 and incorrect == 0:
            messagebox.showinfo("No Data", "No attempts recorded yet.")
            return

        graph_window = tk.Toplevel(self.root)
        graph_window.title("Score Graph")
        graph_window.geometry("600x400")

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(['Correct', 'Incorrect'], [correct, incorrect], color=['green', 'red'])
        ax.set_title('Pronunciation Score')

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        plt.close(fig)

    # Logout function
    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.root.destroy()  # Close the main application window
            login_root = tk.Tk()
            login_app = LoginWindow(login_root, start_main_app)
            login_root.mainloop()
        

class SignupWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success  # Store the callback function
        self.root.title("Sign Up")
        self.root.geometry("400x350")
        self.root.configure(bg='#f0f0f0')
        
        # Title Label
        self.title_label = tk.Label(self.root, text="Create a New Account", font=("Arial", 18, "bold"), bg='#f0f0f0', fg='#333')
        self.title_label.pack(pady=20)

        # Username Label and Entry
        self.username_label = tk.Label(self.root, text="Username", font=("Arial", 12), bg='#f0f0f0')
        self.username_label.pack(pady=(10, 0))
        self.username_entry = tk.Entry(self.root, font=("Arial", 14), bd=2, relief=tk.GROOVE)
        self.username_entry.pack(pady=5, padx=20)

        # Password Label and Entry
        self.password_label = tk.Label(self.root, text="Password", font=("Arial", 12), bg='#f0f0f0')
        self.password_label.pack(pady=(10, 0))
        self.password_entry = tk.Entry(self.root, font=("Arial", 14), bd=2, relief=tk.GROOVE, show="*")
        self.password_entry.pack(pady=5, padx=20)

        # Sign Up Button
        self.signup_button = tk.Button(self.root, text="Sign Up", command=self.signup, font=("Arial", 14), bg='#4CAF50', fg='white', bd=0, width=20)
        self.signup_button.pack(pady=20)

        # Back to Login Button
        self.back_button = tk.Button(self.root, text="Back to Login", command=self.back_to_login, font=("Arial", 12), bg='#f0f0f0', fg='#555', bd=0)
        self.back_button.pack(pady=10)

    def signup(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Sign Up Failed", "Username and password cannot be empty.")
            return

        if len(username) < 3:
            messagebox.showwarning("Sign Up Failed", "Username must be at least 3 characters long.")
            return

        if self.check_if_user_exists(username):
            messagebox.showwarning("Sign Up Failed", "Username already exists.")
            return

        hashed_password = self.hash_password(password)
        self.save_new_user(username, hashed_password)
        messagebox.showinfo("Sign Up Success", "User signed up successfully!")
        self.root.destroy()
        self.on_success(username)  # Call the callback after successful signup

    def back_to_login(self):
        self.root.destroy()
        login_root = tk.Tk()
        login_app = LoginWindow(login_root, start_main_app)
        login_root.mainloop()

    def check_if_user_exists(self, username):
        if os.path.exists("users.txt"):
            with open("users.txt", "r") as file:
                for line in file:
                    existing_username = line.split(":")[0]
                    if existing_username == username:
                        return True
        return False

    def save_new_user(self, username, hashed_password):
        with open("users.txt", "a") as file:
            file.write(f"{username}:{hashed_password}\n")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.root.title("Login")
        self.root.geometry("400x350")
        self.root.configure(bg='#f0f0f0')
        self.on_success = on_success  # Store the callback function for later use

        # Title Label
        self.title_label = tk.Label(self.root, text="Login to Your Account", font=("Arial", 18, "bold"), bg='#f0f0f0', fg='#333')
        self.title_label.pack(pady=20)

        # Username Label and Entry
        self.username_label = tk.Label(self.root, text="Username", font=("Arial", 12), bg='#f0f0f0')
        self.username_label.pack(pady=(10, 0))
        self.username_entry = tk.Entry(self.root, font=("Arial", 14), bd=2, relief=tk.GROOVE)
        self.username_entry.pack(pady=5, padx=20)

        # Password Label and Entry
        self.password_label = tk.Label(self.root, text="Password", font=("Arial", 12), bg='#f0f0f0')
        self.password_label.pack(pady=(10, 0))
        self.password_entry = tk.Entry(self.root, font=("Arial", 14), bd=2, relief=tk.GROOVE, show="*")
        self.password_entry.pack(pady=5, padx=20)

        # Login Button
        self.login_button = tk.Button(self.root, text="Log In", command=self.login, font=("Arial", 14), bg='#4CAF50', fg='white', bd=0, width=20)
        self.login_button.pack(pady=20)

        # Sign Up Button
        self.signup_button = tk.Button(self.root, text="Sign Up", command=self.signup, font=("Arial", 12), bg='#f0f0f0', fg='#555', bd=0)
        self.signup_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        hashed_password = self.hash_password(password)

        if not self.validate_user(username, hashed_password):
            messagebox.showwarning("Login Failed", "Invalid username or password.")
        else:
            self.root.destroy()
            self.on_success(username)  # Use the callback after successful login

    def signup(self):
        self.root.destroy()
        signup_root = tk.Tk()
        signup_app = SignupWindow(signup_root, start_main_app)
        signup_root.mainloop()

    def validate_user(self, username, hashed_password):
        if os.path.exists("users.txt"):
            with open("users.txt", "r") as file:
                for line in file:
                    stored_username, stored_hashed_password = line.strip().split(":")
                    if stored_username == username and stored_hashed_password == hashed_password:
                        return True
        return False

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()


def start_main_app(username):
    root = tk.Tk()
    app = PronunciationDetector(root, username)
    root.mainloop()


if __name__ == "__main__":
    login_root = tk.Tk()
    login_app = LoginWindow(login_root, start_main_app)
    login_root.mainloop()