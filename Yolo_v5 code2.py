import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
from tkinter.ttk import Progressbar
from googletrans import Translator,LANGUAGES
from gtts import gTTS
import numpy as np
import tempfile
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, Wav2Vec2Tokenizer
import torch
import sounddevice as sd
import random
import time
from playsound import playsound
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import hashlib
import wavio
from difflib import SequenceMatcher
import soundfile as sf
from deep_translator import GoogleTranslator
from ultralytics import YOLO
import language_tool_python # Import grammar checking library

import nltk
from nltk import pos_tag
from nltk.tokenize import word_tokenize
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

class ObjectDetectionPage:
    def __init__(self, root):      
        self.root = tk.Toplevel(root)
        self.root.title("Object Detection & Feedback")
        self.root.geometry("850x650")

        # Video label for displaying real-time video feed
        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        # Video Capture from webcam
        self.capture = cv2.VideoCapture(0)

        # Initialize detected objects list
        self.detected_objects = []

        # Translator setup (English and Hindi only)
        self.translator = Translator()
        self.language_options = {'English': 'en', 'Hindi': 'hi'}
        
        # Language selection dropdown
        self.selected_lang = tk.StringVar(self.root)
        self.selected_lang.set('English') # Default language

        # Dropdown menu for selecting the language
        self.lang_menu = tk.OptionMenu(self.root, self.selected_lang, *self.language_options.keys())
        self.lang_menu.pack(pady=10)

        # Load YOLOv5 model (ensure you have the YOLOv5 model file)
        self.model = YOLO('yolov5s.pt') # You can change this to a different YOLO model

        # Create buttons for translation and quitting
        self.translation_button = tk.Button(self.root, text="Real-Time Translation", command=self.provide_translation)
        self.translation_button.pack(pady=10)

        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit_program)
        self.quit_button.pack(pady=10)

        # Bind the key press events for quitting and translation
        self.root.bind('<KeyPress-q>', self.quit_program_key)
        self.root.bind('<KeyPress-r>', self.real_time_translation_key)

        # Update the video frame
        self.update_frame()

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
        # Detect objects in the current frame using YOLOv5
            results = self.model(frame) # YOLOv5 inference

        # Initialize an empty list for detected object names
        self.detected_objects = []

        # Draw bounding boxes and extract labels for each detected object
        for box in results[0].boxes: # Access boxes in results
            x1, y1, x2, y2 = map(int, box.xyxy[0]) # Bounding box coordinates
            conf = box.conf[0] # Confidence score
            cls = int(box.cls[0]) # Class index
            label = self.model.names[cls] # Get the label for the detected class

        # Add the label to the list of detected objects
        self.detected_objects.append(label)

        # Draw the bounding box and label on the frame
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Convert the frame to ImageTk format for displaying in the Tkinter window
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        # Update frame every 10 milliseconds
        self.root.after(10, self.update_frame)

    def provide_translation(self):
        """Provide translation via button click."""
        self.real_time_translation()

    def real_time_translation_key(self, event=None):
        """Handle real-time translation when 'r' key is pressed."""
        self.real_time_translation()

    def real_time_translation(self):
        """Real-time translation functionality."""
        target_lang = self.language_options[self.selected_lang.get()]
        for obj in self.detected_objects:
            try:
                translated = GoogleTranslator(source='auto', target=target_lang).translate(obj)
                sentence = f"The word for '{obj}' in {self.selected_lang.get()} is '{translated}'."
                print(sentence)

                # Text-to-speech for translation feedback
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    temp_path = temp_file.name
                    tts = gTTS(sentence)
                    tts.save(temp_path)
                    playsound(temp_path)
                    os.remove(temp_path)
                    break # Translate one object at a time
            except Exception as e:
                    print(f"Error in translation feedback: {e}")

    def quit_program_key(self, event=None):
        """Quit the object detection page when 'q' key is pressed."""
        self.quit_program()

    def quit_program(self, event=None):
        """Quit the object detection page, not the whole application."""
        self.capture.release()
        cv2.destroyAllWindows()
        self.root.destroy() # Close only the object detection window

class PronunciationDetector:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("Pronunciation Assistant - Mastering the Spoken Word")
        self.root.geometry("1000x800")
        self.root.configure(bg='#e0f7fa')

        # Load Wav2Vec 2.0 model and tokenizer
        self.processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
        self.model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")
        self.tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-large-960h")

        
         # Initialize LanguageTool
        self.grammar_tool = language_tool_python.LanguageTool('en-US', remote_server='https://api.languagetool.org')

        # Initialize user data
        self.current_sentence = ""
        self.logged_in = True
        self.user_data = {"correct_count": 0, "incorrect_count": 0}

        # Call method to create the main UI
        self.create_main_screen()

    def create_main_screen(self):
        # Create frame and labels
        self.frame = tk.Frame(self.root, bg='#e0f7fa')
        self.frame.pack(pady=20)

        self.label = tk.Label(self.frame, text=f"Welcome, {self.username}! Enter text for grammar check and POS tagging:", bg='#e0f7fa', font=("Arial", 14))
        self.label.pack(pady=10)

        # Text input
        self.text_input = tk.Text(self.frame, height=10, width=50)
        self.text_input.pack(pady=10)

        # Buttons for grammar check and POS tagging
        self.check_button = tk.Button(self.frame, text="Check Grammar", command=self.check_grammar, bg='#00796b', fg='white', font=("Arial", 12))
        self.check_button.pack(pady=5)

        self.pos_button = tk.Button(self.frame, text="Get POS Tags", command=self.get_pos_tags, bg='#00796b', fg='white', font=("Arial", 12))
        self.pos_button.pack(pady=5)

        # Label to display output
        self.output_label = tk.Label(self.frame, text="", bg='#e0f7fa', font=("Arial", 12))
        self.output_label.pack(pady=10)

        # Pronunciation Section
        self.create_pronunciation_section()

    def create_pronunciation_section(self):
        # Header Section
        header_frame = tk.Frame(self.root, bg='#00796b', height=80)
        header_frame.pack(fill=tk.X)

        self.label = tk.Label(header_frame, text=f"Welcome, {self.username}!", font=("Arial", 20, "bold"), bg='#00796b', fg='white')
        self.label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Logout Button
        self.logout_button = tk.Button(header_frame, text="Logout", command=self.logout, font=("Arial", 12, "bold"), bg="#ff5252", fg="white")
        self.logout_button.place(relx=0.93, rely=0.5, anchor=tk.CENTER)

        # Body Frame
        body_frame = tk.Frame(self.root, bg='#e0f7fa')
        body_frame.pack(pady=30)

        # Sentence Input Section
        input_frame = tk.Frame(body_frame, bg='#b2dfdb', padx=20, pady=20)
        input_frame.pack(pady=10)

        sentence_label = tk.Label(input_frame, text="Enter or Get a Random Sentence:", font=("Arial", 14), bg='#b2dfdb')
        sentence_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.custom_sentence_entry = tk.Entry(input_frame, font=("Arial", 14), width=50)
        self.custom_sentence_entry.grid(row=1, column=0, columnspan=2, pady=10)

        self.random_sentence_button = tk.Button(input_frame, text="Get Random Sentence", command=self.get_random_sentence, font=("Arial", 12), bg="#00796b", fg="white")
        self.random_sentence_button.grid(row=2, column=0, padx=10, pady=10)

        self.type_sentence_button = tk.Button(input_frame, text="Type Your Sentence", command=self.type_sentence, font=("Arial", 12), bg="#00796b", fg="white")
        self.type_sentence_button.grid(row=2, column=1, padx=10, pady=10)

        # Object Detection Button
        button_frame = tk.Frame(body_frame, bg='#e0f7fa')
        button_frame.pack(pady=20)

        self.record_button = tk.Button(button_frame, text="Record Pronunciation", command=self.record_sentence, font=("Arial", 14), bg="#00796b", fg="white")
        self.record_button.grid(row=0, column=0, padx=20)

        self.graph_button = tk.Button(button_frame, text="Show Score Graph", command=self.show_graph, font=("Arial", 14), bg="#00796b", fg="white")
        self.graph_button.grid(row=0, column=1, padx=20)

        # Pronunciation Recording Section
        record_frame = tk.Frame(body_frame, bg='#b2dfdb', padx=20, pady=20)
        record_frame.pack(pady=10)

        self.progress = Progressbar(record_frame, length=200, mode='determinate')
        self.progress.grid(row=1, column=1, padx=10, pady=10)

        # Results Display Section
        result_frame = tk.Frame(body_frame, bg='#b2dfdb', padx=20, pady=20)
        result_frame.pack(pady=10)

        self.result_text = tk.Text(result_frame, height=6, width=65, bg='#ffffff', fg='black', font=("Arial", 12), relief=tk.SUNKEN)
        self.result_text.pack(pady=10)

    def check_grammar(self):
        # Get the text input
        text = self.text_input.get("1.0", tk.END).strip()

        if not text:
            messagebox.showwarning("Input Error", "Please enter some text for grammar checking.")
            return

        # Check grammar using LanguageTool
        matches = self.grammar_tool.check(text)

        if not matches:
            self.output_label.config(text="No grammar issues detected! Great job!")
        else:
            suggestions = []
            for match in matches:
                suggestions.append(f"Issue: {match.message}\nCorrection: {', '.join(match.replacements)}\n")
                self.output_label.config(text="Grammar Issues Found:\n" + "\n".join(suggestions))

    def get_pos_tags(self):
        # Mapping POS short forms to full names
        tag_explanation = {
        'PRP': 'Personal Pronoun',
        'VBZ': 'Verb, 3rd person singular present',
        'DT': 'Determiner',
        'NN': 'Noun, singular',
        'VBD': 'Verb, past tense',
        'JJ': 'Adjective',
        'RB': 'Adverb',
        'IN': 'Preposition',
        'CC': 'Coordinating Conjunction',
        # Add more mappings as needed
        }

        # Get the text input
        text = self.text_input.get("1.0", tk.END).strip()

        if not text:
            messagebox.showwarning("Input Error", "Please enter some text for POS tagging.")
            return

        # Tokenize and get POS tags
        words = word_tokenize(text)
        pos_tags = pos_tag(words)

        # Convert POS short forms to full names
        formatted_tags = []
        for word, tag in pos_tags:
            tag_full = tag_explanation.get(tag, tag) # Use the full form if available, otherwise use the original tag
            formatted_tags.append(f"{word}: {tag_full}")

        # Display POS tags with full names
        self.output_label.config(text="POS Tags:\n" + "\n".join(formatted_tags))
        
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
        fs = 16000 # Sampling rate required for wav2vec 2.0
        duration = 7 # Recording duration
        self.update_progress(duration)
        self.label.config(text=f"Sentence: {self.current_sentence}\nListening...")

        # Record the audio
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()

        self.label.config(text=f"Sentence: {self.current_sentence}\nFinished Recording")

        # Save and process the recorded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_path = temp_audio_file.name
            np.save(temp_audio_path, recording)

        # Preprocess audio and predict transcription
        self.transcribe_audio(temp_audio_path)

        os.remove(temp_audio_path) # Remove temporary file after processing

    def transcribe_audio(self, audio_path):
        # Load and process the recorded audio for transcription
        audio_input, _ = librosa.load(audio_path, sr=16000)
        input_values = self.processor(audio_input, return_tensors="pt", sampling_rate=16000).input_values
        logits = self.model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.decode(predicted_ids[0])

        # Normalize both predicted and actual texts for comparison
        normalized_transcription = self.normalize_text(transcription)
        normalized_sentence = self.normalize_text(self.current_sentence)

        # Display the transcription and result
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Actual Sentence: {self.current_sentence}\n")
        self.result_text.insert(tk.END, f"Predicted Transcription: {transcription}\n")

    # Calculate accuracy
        if normalized_transcription == normalized_sentence:
            self.result_text.insert(tk.END, "Result: Correct Pronunciation!\n")
            self.user_data["correct_count"] += 1
        else:
            self.result_text.insert(tk.END, "Result: Incorrect Pronunciation.\n")
            self.user_data["incorrect_count"] += 1

    def update_progress(self, duration):
        for i in range(100):
            time.sleep(duration / 100)
            self.progress['value'] = i + 1
            self.root.update_idletasks()

    def show_graph(self):
        correct = self.user_data["correct_count"]
        incorrect = self.user_data["incorrect_count"]

        # Create a bar graph
        fig, ax = plt.subplots(figsize=(5, 4))
        categories = ['Correct', 'Incorrect']
        values = [correct, incorrect]

        ax.bar(categories, values, color=['#00796b', '#ff5252'])
        ax.set_title("Pronunciation Results")
        ax.set_ylabel("Count")

        # Display the graph in a Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def logout(self):
        self.logged_in = False
        self.root.quit()

class SignupWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success # Store the callback function
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
        self.on_success(username) # Call the callback after successful signup

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
        self.on_success = on_success # Store the callback function for later use

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
            self.on_success(username) # Use the callback after successful login

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