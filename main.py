import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import tkinter as tk
import cv2
import requests
import os
import json
from tkinter import messagebox
from PIL import Image, ImageTk

class KYCApplication:
    def __init__(self):
        # Initialize speech recognition and text-to-speech engine
        self.listener = sr.Recognizer()
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)

        # API keys and URLs
        self.ipstack_access_key = "58abe40ac8c2748732407189593ef8b4"
        self.ipstack_base_url = "http://api.ipstack.com/"

        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.frame = None

        # Fetch and print current location
        self.current_location = self.get_user_location()
        print("Current location:", self.current_location)

    def talk(self, text):
        print("Ava says:", text)
        self.engine.say(text)
        self.engine.runAndWait()

    def take_command(self):
        try:
            with sr.Microphone() as source:
                print('listening...')
                self.listener.adjust_for_ambient_noise(source, duration=0.5)
                voice = self.listener.listen(source, timeout=5, phrase_time_limit=15)
                command = self.listener.recognize_google(voice)
                command = command.lower()
                print("You said:", command)
                return command
        except Exception as e:
            print("Error taking command:", str(e))
            return ""

    def get_user_location(self):
        try:
            response = requests.get(f"{self.ipstack_base_url}check?access_key={self.ipstack_access_key}")
            data = response.json()
            return f"{data['city']}, {data['region_name']}, {data['country_name']}"
        except Exception as e:
            print("Error fetching location data:", str(e))
            return "Location not found"

    def open_camera(self, video_frame):
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open video device")
            return

        label_for_video = tk.Label(video_frame)
        label_for_video.pack()

        def show_frame():
            ret, self.frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                label_for_video.imgtk = imgtk
                label_for_video.configure(image=imgtk)
                label_for_video.after(10, show_frame)

        show_frame()

    def capture_image(self):
        if self.frame is not None:
            self.captured_image_path = "KYC_photo.jpg"
            cv2.imwrite(self.captured_image_path, self.frame)
            messagebox.showinfo("Image Captured", "The picture has been captured and saved.")

    def save_kyc_data(self, entries, signature_canvas):
        kyc_storage_dir = r"C:\Users\anand\OneDrive\Documents\kyc registration data"
        os.makedirs(kyc_storage_dir, exist_ok=True)

        # Collect data from entries
        kyc_data = {label_text: entry.get() for label_text, entry in entries.items()}
        json_path = os.path.join(kyc_storage_dir, f"{kyc_data['Name'].replace(' ', '_')}_data.json")
        with open(json_path, 'w') as file:
            json.dump(kyc_data, file, indent=4)

        # Move captured image to storage directory
        stored_image_path = os.path.join(kyc_storage_dir, f"{kyc_data['Name'].replace(' ', '_')}_photo.jpg")
        if hasattr(self, 'captured_image_path'):
            os.rename(self.captured_image_path, stored_image_path)

        # Save signature
        signature_path = os.path.join(kyc_storage_dir, f"{kyc_data['Name'].replace(' ', '_')}_signature.eps")
        signature_canvas.postscript(file=signature_path)

        print(f"KYC data stored in {json_path}")
        print(f"Image stored in {stored_image_path}")
        print(f"Signature stored in {signature_path}")

    def open_kyc_registration(self):
        window = tk.Tk()
        window.title("KYC Registration")
        window.geometry('1200x700')

        left_frame = tk.Frame(window)
        left_frame.pack(side=tk.LEFT, padx=10)

        right_frame = tk.Frame(window)
        right_frame.pack(side=tk.RIGHT, padx=10)

        # Form fields
        labels = ["Name", "DOB (dd/mm/yyyy)", "Address", "PAN Card / Aadhaar", "Income Range", "Type of Employment"]
        entries = {}
        for label_text in labels:
            row = tk.Frame(left_frame)
            label = tk.Label(row, text=label_text, anchor='w')
            entry = tk.Entry(row)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            label.pack(side=tk.LEFT)
            entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            entries[label_text] = entry

        # Signature canvas
        signature_label = tk.Label(left_frame, text="Signature", font=("Helvetica", 14))
        signature_label.pack()
        signature_canvas = tk.Canvas(left_frame, width=400, height=200, bg='white')
        signature_canvas.pack()

        signature_canvas.bind("<B1-Motion>", lambda event: self.draw_signature(event, signature_canvas))

        # Video/camera area
        self.open_camera(right_frame)

        # Capture button
        capture_button = tk.Button(right_frame, text="Capture Image", command=self.capture_image)
        capture_button.pack()

        # Submit button
        submit_button = tk.Button(left_frame, text="Submit", command=lambda: self.save_kyc_data(entries, signature_canvas))
        submit_button.pack(pady=20)

        window.mainloop()

    def draw_signature(self, event, signature_canvas):
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        signature_canvas.create_oval(x1, y1, x2, y2, fill='black')

    def run(self):
        while True:
            command = self.take_command()
            if command:
                if 'play' in command:
                    song = command.replace('play', '')
                    self.talk('playing ' + song)
                    pywhatkit.playonyt(song)
                elif 'time' in command:
                    time = datetime.datetime.now().strftime('%I:%M %p')
                    self.talk('current time is ' + time)
                elif 'who is' in command:
                    person = command.replace('who is', '')
                    info = wikipedia.summary(person, 1)
                    self.talk(info)
                elif 'joke' in command:
                    self.talk(pyjokes.get_joke())
                elif 'kyc registration' in command:
                    self.open_kyc_registration()
                else:
                    self.talk("Sorry, I don't understand that command.")

if __name__ == "__main__":
    app = KYCApplication()
    app.run()
