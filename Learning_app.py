import os
import subprocess
from gtts import gTTS
import customtkinter as ctk
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import threading

# Recording settings
fs = 44100
seconds = 5

# Color palette
PALETTE = [
    ("#ef5350", "#c62828"),  # red
    ("#ec407a", "#ad1457"),  # pink
    ("#ab47bc", "#6a1b9a"),  # purple
    ("#5c6bc0", "#283593"),  # indigo
    ("#29b6f6", "#0277bd"),  # light blue
    ("#26a69a", "#00695c"),  # teal
    ("#66bb6a", "#2e7d32"),  # green
    ("#ffa726", "#ef6c00"),  # orange
    ("#ff7043", "#d84315"),  # deep orange
    ("#8d6e63", "#4e342e"),  # brown
]

# --- UI ---
app = ctk.CTk()
app.title("Learning app for kids")
app.geometry("900x600")
app.configure(fg_color="#b3e5fc")

# Global variables
current_screen = "s2t"  # "s2t" or "t2s"
content_frame = None
sentence = ""
picture_status_label = None

# --- Speech: each click spawns its own short-lived PowerShell SAPI process ---
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

def _speak_async(word):
    safe = str(word).replace("'", "''")
    try:
        subprocess.Popen(
            [
                "powershell", "-NoProfile", "-Command",
                "Add-Type -AssemblyName System.Speech; "
                f"(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe}')"
            ],
            creationflags=_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"[speech] launched: {word}")
    except Exception as e:
        print(f"[speech] error: {e}")

# --- Functions ---
def transcribe_audio():
    r = sr.Recognizer()
    with sr.AudioFile("output.wav") as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio)
        transcription_label.configure(text="You said: " + text)
        status_label.configure(text="Status: Ready to record")
    except sr.UnknownValueError:
        transcription_label.configure(text="Could not understand audio")
        status_label.configure(text="Status: Ready to record")
    except sr.RequestError as e:
        transcription_label.configure(text="Error: " + str(e))
        status_label.configure(text="Status: Ready to record")

def record_audio():
    status_label.configure(text="Status: Recording...")
    recording = sd.rec(int(seconds * fs),
                       samplerate=fs,
                       channels=1,
                       dtype='int16')
    sd.wait()
    write("output.wav", fs, recording)
    status_label.configure(text="Status: Processing...")
    transcribe_audio()

def start_recording():
    threading.Thread(target=record_audio).start()

def clear_transcription():
    transcription_label.configure(text="Transcription will appear here")
    status_label.configure(text="Status: Ready to record")

def convert_text_to_speech():
    text = text_entry.get()
    if text:
        tts = gTTS(text=text, lang='en')
        tts.save("output.mp3")
        os.system("start output.mp3")

def clear_text():
    text_entry.delete(0, ctk.END)

def speak(word):
    global sentence, picture_status_label
    sentence += word + " "
    try:
        if picture_status_label:
            picture_status_label.configure(text=sentence)
    except:
        pass  # Widget might be destroyed, that's okay

    _speak_async(word)

def clear_content():
    global content_frame, picture_status_label
    if content_frame:
        content_frame.destroy()
        content_frame = None
    picture_status_label = None

def add_home_icon(parent, color="#ec407a", hover="#ad1457"):
    home_icon_btn = ctk.CTkButton(
        parent,
        text="🏠",
        width=50,
        height=50,
        font=("Arial", 22, "bold"),
        fg_color=color,
        text_color="white",
        hover_color=hover,
        border_color="white",
        border_width=3,
        corner_radius=25,
        command=show_home
    )
    home_icon_btn.place(relx=1.0, x=-15, y=10, anchor="ne")

def show_home():
    global content_frame, current_screen
    current_screen = "home"
    clear_content()

    content_frame = ctk.CTkFrame(app, fg_color="#e4f1fe", corner_radius=10)
    content_frame.pack(pady=20, padx=20, fill="both", expand=True)

    scroll_area = ctk.CTkScrollableFrame(content_frame, fg_color="#e4f1fe", corner_radius=0)
    scroll_area.pack(fill="both", expand=True, padx=5, pady=5)

    title_home = ctk.CTkLabel(
        scroll_area,
        text="🌟 Welcome to Learning App 🌟",
        font=("Arial", 32, "bold"),
        fg_color="#e4f1fe",
        text_color="#6a1b9a"
    )
    title_home.pack(pady=20)

    description = ctk.CTkLabel(
        scroll_area,
        text="Choose a learning mode below:",
        font=("Arial", 18, "bold"),
        fg_color="#e4f1fe",
        text_color="#ad1457"
    )
    description.pack(pady=10)

    button_frame = ctk.CTkFrame(scroll_area, fg_color="#e4f1fe")
    button_frame.pack(pady=20, padx=10, fill="both", expand=True)

    menu_buttons = [
        ("🎙️ Speech to Text", show_speech_to_text, "#ef5350", "#c62828"),
        ("🔊 Text to Speech", show_text_to_speech, "#66bb6a", "#2e7d32"),
        ("🖼️ Picture Talk", show_picture_communication, "#ab47bc", "#6a1b9a"),
        ("➕ Math Learning", math_part, "#ffa726", "#ef6c00"),
        ("💖 Emotion Friendly UI", show_emotion_ui, "#29b6f6", "#0277bd"),
    ]

    for label, command, color, hover in menu_buttons:
        btn = ctk.CTkButton(
            button_frame,
            text=label,
            width=600,
            height=70,
            font=("Arial", 18, "bold"),
            fg_color=color,
            hover_color=hover,
            text_color="white",
            corner_radius=15,
            command=command
        )
        btn.pack(pady=10, padx=20, fill="x")

    emotion_section = ctk.CTkFrame(scroll_area, fg_color="#ffefdb", corner_radius=10)
    emotion_section.pack(pady=20, padx=20, fill="x")

    emotion_title = ctk.CTkLabel(
        emotion_section,
        text="You are doing great! 💖",
        font=("Arial", 20, "bold"),
        fg_color="#ffefdb"
    )
    emotion_title.pack(pady=(15, 10))

    emotions = ["😊 Happy", "🌟 Confident", "👍 Great Job", "🌈 Keep Going"]
    for em in emotions:
        em_label = ctk.CTkLabel(
            emotion_section,
            text=em,
            font=("Arial", 18, "bold"),
            fg_color="#ffefdb"
        )
        em_label.pack(pady=5)
    ctk.CTkLabel(emotion_section, text="", fg_color="#ffefdb").pack(pady=5)


def show_emotion_ui():
    global content_frame, current_screen
    current_screen = "emotion"
    clear_content()

    content_frame = ctk.CTkFrame(app, fg_color="#ffefdb", corner_radius=10)
    content_frame.pack(pady=20, padx=20, fill="both", expand=True)

    add_home_icon(content_frame, "#ec407a", "#ad1457")

    title_emotion = ctk.CTkLabel(
        content_frame,
        text="💖 Emotion Friendly UI 💖",
        font=("Arial", 32, "bold"),
        fg_color="#ffefdb",
        text_color="#ad1457"
    )
    title_emotion.pack(pady=20)

    message = ctk.CTkLabel(
        content_frame,
        text="You are doing great! Choose a mode or relax with a friendly message.",
        font=("Arial", 18, "bold"),
        fg_color="#ffefdb",
        wraplength=600,
        text_color="#6a1b9a"
    )
    message.pack(pady=10)

    emotion_frame = ctk.CTkFrame(content_frame, fg_color="#ffefdb")
    emotion_frame.pack(pady=20, padx=20, fill="both", expand=True)

    emotions = [
        ("😊 Happy", "#fff176", "#5d4037"),
        ("🌟 Confident", "#ffb74d", "#3e2723"),
        ("👍 Great Job", "#81c784", "#1b5e20"),
        ("🌈 Keep Going", "#64b5f6", "#0d47a1"),
        ("💖 Loved", "#f48fb1", "#880e4f"),
        ("✨ Calm", "#ce93d8", "#4a148c"),
    ]

    for em, bg, fg in emotions:
        label = ctk.CTkLabel(
            emotion_frame,
            text=em,
            font=("Arial", 22, "bold"),
            fg_color=bg,
            text_color=fg,
            corner_radius=20,
            width=320,
            height=50
        )
        label.pack(pady=8)

    go_home_button = ctk.CTkButton(
        content_frame,
        text="🏠 Back to Home",
        width=200,
        height=50,
        font=("Arial", 16, "bold"),
        fg_color="#ec407a",
        hover_color="#ad1457",
        text_color="white",
        corner_radius=15,
        command=show_home
    )
    go_home_button.pack(pady=20)


def show_speech_to_text():
    global content_frame, current_screen
    current_screen = "s2t"
    clear_content()
    
    content_frame = ctk.CTkFrame(app, fg_color="lightyellow", corner_radius=10)
    content_frame.pack(pady=20, padx=20, fill="both", expand=True)

    add_home_icon(content_frame, "#ef5350", "#c62828")

    title_s2t = ctk.CTkLabel(
        content_frame,
        text="🎙️ Speech To Text",
        font=("Arial", 28, "bold"),
        fg_color="lightyellow",
        text_color="#c62828"
    )
    title_s2t.pack(pady=20)

    global status_label, transcription_label
    status_label = ctk.CTkLabel(
        content_frame,
        text="Status: Ready to record",
        font=("Arial", 16, "bold"),
        text_color="#0277bd"
    )
    status_label.pack(pady=10)

    transcription_label = ctk.CTkLabel(
        content_frame,
        text="Transcription will appear here",
        font=("Arial", 14, "bold"),
        wraplength=400,
        text_color="#2e7d32"
    )
    transcription_label.pack(pady=15)

    button_frame = ctk.CTkFrame(content_frame, fg_color="lightyellow")
    button_frame.pack(pady=20)

    record_button = ctk.CTkButton(
        button_frame,
        text="🔴 Record",
        width=150,
        height=50,
        font=("Arial", 16, "bold"),
        fg_color="#ef5350",
        hover_color="#c62828",
        text_color="white",
        corner_radius=15,
        command=start_recording
    )
    record_button.pack(side="left", padx=10)

    clear_s2t_button = ctk.CTkButton(
        button_frame,
        text="🧹 Clear",
        width=150,
        height=50,
        font=("Arial", 16, "bold"),
        fg_color="#ffa726",
        hover_color="#ef6c00",
        text_color="white",
        corner_radius=15,
        command=clear_transcription
    )
    clear_s2t_button.pack(side="left", padx=10)

def show_text_to_speech():
    global content_frame, current_screen, text_entry
    current_screen = "t2s"
    clear_content()
    
    content_frame = ctk.CTkFrame(app, fg_color="lightgreen", corner_radius=10)
    content_frame.pack(pady=20, padx=20, fill="both", expand=True)

    add_home_icon(content_frame, "#ab47bc", "#6a1b9a")

    title_t2s = ctk.CTkLabel(
        content_frame,
        text="🔊 Text To Speech",
        font=("Arial", 28, "bold"),
        fg_color="lightgreen",
        text_color="#2e7d32"
    )
    title_t2s.pack(pady=20)

    text_entry = ctk.CTkEntry(
        content_frame,
        width=400,
        height=50,
        font=ctk.CTkFont(size=16),
        placeholder_text="Enter text here...",
        border_color="#2e7d32",
        border_width=2
    )
    text_entry.pack(pady=20)

    button_frame = ctk.CTkFrame(content_frame, fg_color="lightgreen")
    button_frame.pack(pady=20)

    convert_button = ctk.CTkButton(
        button_frame,
        text="🔊 Convert to Speech",
        width=180,
        height=50,
        font=("Arial", 16, "bold"),
        fg_color="#ab47bc",
        text_color="white",
        hover_color="#6a1b9a",
        corner_radius=15,
        command=convert_text_to_speech
    )
    convert_button.pack(side="left", padx=10)

    clear_button = ctk.CTkButton(
        button_frame,
        text="🧹 Clear Text",
        width=150,
        height=50,
        font=("Arial", 16, "bold"),
        fg_color="#ffa726",
        text_color="white",
        hover_color="#ef6c00",
        corner_radius=15,
        command=clear_text
    )
    clear_button.pack(side="left", padx=10)

def show_picture_communication():
    global content_frame, current_screen, sentence, picture_status_label
    current_screen = "picture"
    clear_content()
    sentence = ""

    content_frame = ctk.CTkFrame(app, fg_color="#f9f3c9", corner_radius=10)
    content_frame.pack(pady=20, padx=20, fill="both", expand=True)

    add_home_icon(content_frame, "#29b6f6", "#0277bd")

    title_pic = ctk.CTkLabel(
        content_frame,
        text="🖼️ Picture Communication",
        font=("Arial", 28, "bold"),
        fg_color="#f9f3c9",
        text_color="#6a1b9a"
    )
    title_pic.pack(pady=20)

    picture_status_label = ctk.CTkLabel(
        content_frame,
        text="Tap a picture to speak",
        font=("Arial", 16, "bold"),
        wraplength=500,
        text_color="#ad1457"
    )
    picture_status_label.pack(pady=10)

    picture_frame = ctk.CTkScrollableFrame(content_frame, fg_color="#f9f3c9")
    picture_frame.pack(pady=10, fill="both", expand=True)

    for col in range(5):
        picture_frame.grid_columnconfigure(col, weight=1, uniform="col")

    buttons1 = [
        ("💧", "Water", "water"),
        ("🍎", "Apple", "apple"),
        ("🍌", "Banana", "banana"),
        ("🍕", "Pizza", "pizza"),
        ("🙏", "Please", "please"),

        ("🚪", "Door", "door"),
        ("🛏️", "Sleep", "sleep"),
        ("🎵", "Music", "music"),
        ("😊", "Happy", "happy"),
        ("😢", "Sad", "sad"),

        ("🚗", "Car", "car"),
        ("⚽", "Play", "play"),
        ("🐶", "Dog", "dog"),
        ("🐱", "Cat", "cat"),
        ("📚", "Book", "book"),

        ("💡", "Light", "light"),
        ("📱", "Phone", "phone"),
        ("🧸", "Toy", "toy"),
        ("👕", "Clothes", "clothes"),
        ("🧼", "Soap", "soap"),

        ("🚽", "Bathroom", "bathroom"),
        ("🍪", "Cookie", "cookie"),
        ("🎂", "Cake", "cake"),
        ("🍦", "Ice Cream", "ice cream"),
        ("🧁", "Cupcake", "cupcake"),
    ]

    def make_card_click(w):
        return lambda _: speak(w)

    PICTURE_BG = [
        "#fff9c4", "#ffe0b2", "#ffccbc", "#f8bbd0", "#e1bee7",
        "#d1c4e9", "#c5cae9", "#bbdefb", "#b3e5fc", "#b2ebf2",
        "#b2dfdb", "#c8e6c9", "#dcedc8", "#f0f4c3", "#fff59d",
    ]

    for i, (emoji, label, word) in enumerate(buttons1):
        color, hover = PALETTE[i % len(PALETTE)]
        pic_bg = PICTURE_BG[i % len(PICTURE_BG)]

        card = ctk.CTkFrame(
            picture_frame,
            width=170,
            height=140,
            fg_color=color,
            corner_radius=6,
            border_color="white",
            border_width=3,
        )
        card.grid(row=i//5, column=i%5, padx=10, pady=10)
        card.grid_propagate(False)

        picture_area = ctk.CTkFrame(
            card,
            fg_color=pic_bg,
            corner_radius=4,
            border_color="white",
            border_width=2,
        )
        picture_area.pack(padx=6, pady=(6, 2), fill="both", expand=True)

        emoji_label = ctk.CTkLabel(
            picture_area,
            text=emoji,
            font=("Arial", 42),
            fg_color=pic_bg,
        )
        emoji_label.pack(expand=True)

        word_label = ctk.CTkLabel(
            card,
            text=label,
            font=("Arial", 14, "bold"),
            fg_color=color,
            text_color="white",
        )
        word_label.pack(pady=(0, 6))

        click = make_card_click(word)
        for widget in (card, picture_area, emoji_label, word_label):
            widget.bind("<Button-1>", click)
            widget.configure(cursor="hand2")

        def on_enter(_, c=card, w=word_label, h=hover):
            c.configure(fg_color=h)
            w.configure(fg_color=h)
        def on_leave(_, c=card, w=word_label, col=color):
            c.configure(fg_color=col)
            w.configure(fg_color=col)
        for widget in (card, picture_area, emoji_label, word_label):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    sentence = ""

    def clear_speech():
        global sentence, picture_status_label
        sentence = ""
        try:
            if picture_status_label:
                picture_status_label.configure(text="Tap a picture to speak")
        except:
            pass

    clear_pic_button = ctk.CTkButton(
        content_frame,
        text="🧹 Clear Speech",
        width=180,
        height=50,
        font=("Arial", 16, "bold"),
        fg_color="#ef5350",
        hover_color="#c62828",
        text_color="white",
        corner_radius=15,
        command=clear_speech
    )
    clear_pic_button.pack(pady=10)

def show_math_exercises(operation):
    global content_frame
    clear_content()
    math_frame = ctk.CTkFrame(app, fg_color="lightcoral", corner_radius=10)
    content_frame = math_frame
    math_frame.pack(pady=20, padx=20, fill="both", expand=True)

    add_home_icon(math_frame, "#66bb6a", "#2e7d32")

    title_math = ctk.CTkLabel(
        math_frame,
        text=f"➕ {operation.capitalize()} Practice",
        font=("Arial", 28, "bold"),
        fg_color="lightcoral",
        text_color="#6a1b9a"
    )
    title_math.pack(pady=20)

    instruction = ctk.CTkLabel(
        math_frame,
        text=f"Enter a {operation} expression, or tap a sample below.",
        font=("Arial", 18, "bold"),
        text_color="#0277bd"
    )
    instruction.pack(pady=10)

    entry = ctk.CTkEntry(
        math_frame,
        width=350,
        height=45,
        font=ctk.CTkFont(size=16),
        placeholder_text="Enter math expression, e.g. 2+3*4",
        border_color="#6a1b9a",
        border_width=2
    )
    entry.pack(pady=10)

    def set_expression(value):
        entry.delete(0, ctk.END)
        entry.insert(0, value)

    sample_frame = ctk.CTkFrame(math_frame, fg_color="lightcoral")
    sample_frame.pack(pady=10, fill="x")

    examples = {
        "addition": ["1+1", "2+1", "3+1", "4+1", "5+1","6+1","7+1","8+1","9+1"],
        "subtraction": ["5-1", "6-2", "7-3", "8-4", "9-5","10-6","11-7","12-8","13-9"],
        "multiplication": ["1*1", "2*2", "3*3", "4*4", "5*5","6*6","7*7","8*8","9*9"],
        "division": ["10/2", "20/4", "30/5", "40/8", "50/10","60/12","70/14","80/16","90/18"],
    }

    for i, expr in enumerate(examples.get(operation, [])):
        color, hover = PALETTE[i % len(PALETTE)]
        sample_btn = ctk.CTkButton(
            sample_frame,
            text=expr,
            width=100,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color=color,
            hover_color=hover,
            text_color="white",
            corner_radius=12,
            command=lambda expr=expr: set_expression(expr)
        )
        sample_btn.grid(row=0, column=i, padx=5, pady=5)

    result_label = ctk.CTkLabel(
        math_frame,
        text="Result will appear here",
        font=("Arial", 18, "bold"),
        text_color="#2e7d32"
    )
    result_label.pack(pady=20)

    def calculate():
        try:
            expression = entry.get()
            result = eval(expression)
            result_label.configure(text=f"Result: {result}")
        except Exception:
            result_label.configure(text="Invalid Expression")

    calc_button = ctk.CTkButton(
        math_frame,
        text="✅ Calculate",
        width=160,
        height=45,
        font=("Arial", 16, "bold"),
        fg_color="#66bb6a",
        hover_color="#2e7d32",
        text_color="white",
        corner_radius=15,
        command=calculate
    )
    calc_button.pack(pady=10)

    back_button = ctk.CTkButton(
        math_frame,
        text="↩️ Back to Operations",
        width=200,
        height=45,
        font=("Arial", 16, "bold"),
        fg_color="#ffa726",
        hover_color="#ef6c00",
        text_color="white",
        corner_radius=15,
        command=math_part
    )
    back_button.pack(pady=10)


def math_part():
    global content_frame
    clear_content()
    math_frame = ctk.CTkFrame(app, fg_color="lightcoral", corner_radius=10)
    content_frame = math_frame
    math_frame.pack(pady=20, padx=20, fill="both", expand=True)

    add_home_icon(math_frame, "#66bb6a", "#2e7d32")

    scroll_area = ctk.CTkScrollableFrame(math_frame, fg_color="lightcoral", corner_radius=0)
    scroll_area.pack(fill="both", expand=True, padx=5, pady=(60, 5))

    title_math = ctk.CTkLabel(
        scroll_area,
        text="➕ Math Learning",
        font=("Arial", 28, "bold"),
        fg_color="lightcoral",
        text_color="#6a1b9a"
    )
    title_math.pack(pady=20)

    instruction = ctk.CTkLabel(
        scroll_area,
        text="Choose an operation to continue.",
        font=("Arial", 18, "bold"),
        text_color="#0277bd"
    )
    instruction.pack(pady=10)

    operation_frame = ctk.CTkFrame(scroll_area, fg_color="lightcoral")
    operation_frame.pack(pady=10, fill="x")

    operations = [
        ("➕ Addition", "addition", "#ef5350", "#c62828"),
        ("➖ Subtraction", "subtraction", "#29b6f6", "#0277bd"),
        ("✖️ Multiplication", "multiplication", "#66bb6a", "#2e7d32"),
        ("➗ Division", "division", "#ab47bc", "#6a1b9a"),
    ]

    for i, (label, op, color, hover) in enumerate(operations):
        op_button = ctk.CTkButton(
            operation_frame,
            text=label,
            width=140,
            height=60,
            font=("Arial", 14, "bold"),
            fg_color=color,
            hover_color=hover,
            text_color="white",
            corner_radius=15,
            command=lambda op=op: show_math_exercises(op)
        )
        op_button.grid(row=0, column=i, padx=5, pady=5)
        operation_frame.grid_columnconfigure(i, weight=1)

    calc_title = ctk.CTkLabel(
        scroll_area,
        text="🧮 Quick Calculator",
        font=("Arial", 22, "bold"),
        fg_color="lightcoral",
        text_color="#6a1b9a"
    )
    calc_title.pack(pady=(20, 5))

    display = ctk.CTkEntry(
        scroll_area,
        width=320,
        height=50,
        font=ctk.CTkFont(size=22, weight="bold"),
        justify="right",
        border_color="#6a1b9a",
        border_width=2,
    )
    display.pack(pady=8)

    def press(char):
        display.insert(ctk.END, char)

    def clear_calc():
        display.delete(0, ctk.END)

    def backspace():
        current = display.get()
        display.delete(0, ctk.END)
        display.insert(0, current[:-1])

    def equals():
        try:
            result = eval(display.get())
            display.delete(0, ctk.END)
            display.insert(0, str(result))
        except Exception:
            display.delete(0, ctk.END)
            display.insert(0, "Error")

    calc_grid = ctk.CTkFrame(scroll_area, fg_color="lightcoral")
    calc_grid.pack(pady=5)

    NUM_COLOR, NUM_HOVER = "#5c6bc0", "#283593"
    OP_COLOR, OP_HOVER = "#ffa726", "#ef6c00"
    EQ_COLOR, EQ_HOVER = "#66bb6a", "#2e7d32"
    CLR_COLOR, CLR_HOVER = "#ef5350", "#c62828"

    calc_buttons = [
        ("7", 0, 0, NUM_COLOR, NUM_HOVER, lambda: press("7")),
        ("8", 0, 1, NUM_COLOR, NUM_HOVER, lambda: press("8")),
        ("9", 0, 2, NUM_COLOR, NUM_HOVER, lambda: press("9")),
        ("➗", 0, 3, OP_COLOR, OP_HOVER, lambda: press("/")),
        ("4", 1, 0, NUM_COLOR, NUM_HOVER, lambda: press("4")),
        ("5", 1, 1, NUM_COLOR, NUM_HOVER, lambda: press("5")),
        ("6", 1, 2, NUM_COLOR, NUM_HOVER, lambda: press("6")),
        ("✖️", 1, 3, OP_COLOR, OP_HOVER, lambda: press("*")),
        ("1", 2, 0, NUM_COLOR, NUM_HOVER, lambda: press("1")),
        ("2", 2, 1, NUM_COLOR, NUM_HOVER, lambda: press("2")),
        ("3", 2, 2, NUM_COLOR, NUM_HOVER, lambda: press("3")),
        ("➖", 2, 3, OP_COLOR, OP_HOVER, lambda: press("-")),
        ("0", 3, 0, NUM_COLOR, NUM_HOVER, lambda: press("0")),
        (".", 3, 1, NUM_COLOR, NUM_HOVER, lambda: press(".")),
        ("⌫", 3, 2, CLR_COLOR, CLR_HOVER, backspace),
        ("➕", 3, 3, OP_COLOR, OP_HOVER, lambda: press("+")),
        ("C", 4, 0, CLR_COLOR, CLR_HOVER, clear_calc),
        ("(", 4, 1, NUM_COLOR, NUM_HOVER, lambda: press("(")),
        (")", 4, 2, NUM_COLOR, NUM_HOVER, lambda: press(")")),
        ("=", 4, 3, EQ_COLOR, EQ_HOVER, equals),
    ]

    for label, row, col, color, hover, cmd in calc_buttons:
        btn = ctk.CTkButton(
            calc_grid,
            text=label,
            width=70,
            height=55,
            font=("Arial", 18, "bold"),
            fg_color=color,
            hover_color=hover,
            text_color="white",
            corner_radius=12,
            command=cmd
        )
        btn.grid(row=row, column=col, padx=4, pady=4)

# Initialize with Home page
show_home()
app.mainloop()