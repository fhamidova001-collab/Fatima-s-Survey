try:
    import tkinter as tk
    from tkinter import messagebox, filedialog
except ImportError:
    tk = None
    messagebox = None
    filedialog = None
import json
import csv
import re
from datetime import datetime
from pathlib import Path


# ============================================================
# CONFIGURATION / DATA
# ============================================================

APP_TITLE = "Evening Wind-Down Routines and Next-Day Readiness Questionnaire"
CONDUCTED_BY = "Conducted by Fotima"

# Required variable types for marking:
EXAMPLE_INT = 80
EXAMPLE_STR = "Psychological survey"
EXAMPLE_FLOAT = 100.0 / 80.0
EXAMPLE_LIST = [1, 2, 3]
EXAMPLE_TUPLE = ("Always", 0)
EXAMPLE_RANGE = range(1, 6)
EXAMPLE_BOOL = True
EXAMPLE_DICT = {"txt": "Text", "csv": "CSV", "json": "JSON"}
EXAMPLE_SET = {"txt", "csv", "json"}
EXAMPLE_FROZENSET = frozenset({"txt", "csv", "json"})

ANSWER_OPTIONS = [
    ("Always", 0),
    ("Often", 1),
    ("Sometimes", 2),
    ("Rarely", 3),
    ("Never", 4)
]

EMBEDDED_QUESTIONS = [
    {"section": "Section 1: Planning & Organization", "question": "How often do you organize your study materials before going to bed?"},
    {"section": "Section 1: Planning & Organization", "question": "How regularly do you set goals for the next day?"},
    {"section": "Section 1: Planning & Organization", "question": "Do you create a to-do list for upcoming tasks?"},
    {"section": "Section 1: Planning & Organization", "question": "How often do you review your schedule before sleeping?"},

    {"section": "Section 2: Mental Relaxation", "question": "How often do you engage in calming activities (reading, meditation)?"},
    {"section": "Section 2: Mental Relaxation", "question": "Do you feel mentally relaxed before going to sleep?"},
    {"section": "Section 2: Mental Relaxation", "question": "How often do you avoid stressful thinking at night?"},
    {"section": "Section 2: Mental Relaxation", "question": "How frequently do you feel calm and peaceful before bed?"},

    {"section": "Section 3: Sleep Preparation", "question": "How consistent is your sleep schedule?"},
    {"section": "Section 3: Sleep Preparation", "question": "Do you avoid using electronic devices before bedtime?"},
    {"section": "Section 3: Sleep Preparation", "question": "How often do you sleep without interruptions?"},
    {"section": "Section 3: Sleep Preparation", "question": "How comfortable is your sleeping environment?"},

    {"section": "Section 4: Physical & Emotional State", "question": "How often do you feel physically relaxed before sleep?"},
    {"section": "Section 4: Physical & Emotional State", "question": "Do you feel emotionally stable at night?"},
    {"section": "Section 4: Physical & Emotional State", "question": "How often do you feel tired in a healthy way (not exhausted)?"},

    {"section": "Section 5: Next-Day Readiness", "question": "How energized do you feel when you wake up?"},
    {"section": "Section 5: Next-Day Readiness", "question": "How ready are you to start your daily tasks?"},
    {"section": "Section 5: Next-Day Readiness", "question": "How confident do you feel about managing your schedule?"},
    {"section": "Section 5: Next-Day Readiness", "question": "How focused are you in the morning?"},
    {"section": "Section 5: Next-Day Readiness", "question": "How motivated are you to begin studying?"}
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_extra_spaces(text):
    """
    Uses while loop for validation-related cleanup.
    """
    text = text.strip()
    while "  " in text:
        text = text.replace("  ", " ")
    return text


def validate_full_name(name):
    """
    Validate surname and given name.
    Allowed: letters, spaces, hyphens, apostrophes.
    Uses a for loop for validation.
    """
    name = clean_extra_spaces(name)

    if name == "":
        return False

    allowed_special = {" ", "-", "'"}

    has_letter = False
    for ch in name:
        if ch.isalpha():
            has_letter = True
        elif ch not in allowed_special:
            return False

    if not has_letter:
        return False

    if name[0] in "-'" or name[-1] in "-'":
        return False

    return True


def validate_date_of_birth(dob_text):
    """
    Accept DD/MM/YYYY.
    Validates both format and calendar values.
    """
    dob_text = dob_text.strip()

    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", dob_text):
        return False

    try:
        dob_obj = datetime.strptime(dob_text, "%d/%m/%Y")
        if dob_obj > datetime.now():
            return False
        return True
    except ValueError:
        return False


def validate_student_id(student_id):
    """
    Only digits allowed.
    """
    student_id = student_id.strip()
    return student_id.isdigit() and len(student_id) > 0


def calculate_scaled_score(raw_score, max_raw_score):
    """
    Convert raw score to 0-100 so your exact scoring table stays usable.
    """
    return round((raw_score / max_raw_score) * 100)


def classify_state(scaled_score):
    """
    5 psychological states based on scaled score.
    """
    if 0 <= scaled_score <= 20:
        return "Excellent routine — high readiness"
    elif 21 <= scaled_score <= 40:
        return "Good habits — minor improvements"
    elif 41 <= scaled_score <= 60:
        return "Moderate routine — needs structure"
    elif 61 <= scaled_score <= 80:
        return "Low readiness — poor habits"
    else:
        return "Very poor — immediate improvement needed"


def load_questions_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    questions = []
    for item in data:
        if isinstance(item, dict) and "section" in item and "question" in item:
            questions.append({
                "section": str(item["section"]).strip(),
                "question": str(item["question"]).strip()
            })
    return questions


def load_questions_from_csv(file_path):
    questions = []
    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if "section" in row and "question" in row:
                questions.append({
                    "section": row["section"].strip(),
                    "question": row["question"].strip()
                })
    return questions


def load_questions_from_txt(file_path):
    """
    TXT format:
    Section Name | Question text
    """
    questions = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line and "|" in line:
                section, question = line.split("|", 1)
                questions.append({
                    "section": section.strip(),
                    "question": question.strip()
                })
    return questions


def load_saved_result_as_text(file_path):
    suffix = Path(file_path).suffix.lower()

    if suffix == ".txt":
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    elif suffix == ".csv":
        lines = []
        with open(file_path, "r", encoding="utf-8", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                lines.append(" | ".join(row))
        return "\n".join(lines)

    elif suffix == ".json":
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        lines = []
        lines.append("LOADED RESULT")
        lines.append("=" * 60)
        for key, value in data.items():
            if key != "answers":
                lines.append(f"{key}: {value}")

        if "answers" in data:
            lines.append("")
            lines.append("ANSWERS")
            lines.append("=" * 60)
            for item in data["answers"]:
                lines.append(f"Q{item['question_number']}: {item['question']}")
                lines.append(f"Answer: {item['selected_answer']} | Score: {item['score']}")
                lines.append("-" * 60)
        return "\n".join(lines)

    else:
        raise ValueError("Unsupported file format.")


# ============================================================
# MAIN APPLICATION
# ============================================================

class SurveyApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1000x700")
        self.root.resizable(False, False)

        # Light purple theme
        self.bg_main = "#F5EDFF"
        self.bg_card = "#EBD9FF"
        self.bg_button = "#C084FC"
        self.bg_button_alt = "#A855F7"
        self.text_main = "#3B0764"
        self.text_dark = "#2E1065"
        self.white = "#FFFFFF"

        self.root.configure(bg=self.bg_main)

        self.questions = EMBEDDED_QUESTIONS.copy()
        self.question_source = "Embedded in code"

        self.user_data = {
            "full_name": "",
            "date_of_birth": "",
            "student_id": "",
            "survey_date": ""
        }

        self.question_vars = []
        self.current_question_index = 0

        self.name_var = tk.StringVar()
        self.dob_var = tk.StringVar()
        self.student_id_var = tk.StringVar()
        self.question_source_var = tk.StringVar(value="embedded")

        self.show_welcome_page()

    # --------------------------------------------------------
    # Common UI helpers
    # --------------------------------------------------------

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_card(self, width=860, height=590):
        card = tk.Frame(
            self.root,
            bg=self.bg_card,
            bd=2,
            relief="ridge"
        )
        card.place(relx=0.5, rely=0.5, anchor="center", width=width, height=height)
        return card

    def make_button(self, parent, text, command, width=18):
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            bg=self.bg_button,
            fg=self.white,
            activebackground=self.bg_button_alt,
            activeforeground=self.white,
            relief="flat",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            pady=8
        )

    # --------------------------------------------------------
    # Slide 1
    # --------------------------------------------------------

    def show_welcome_page(self):
        self.clear_window()
        card = self.create_card()

        tk.Label(
            card,
            text=APP_TITLE,
            bg=self.bg_card,
            fg=self.text_main,
            font=("Arial", 18, "bold"),
            wraplength=720,
            justify="center"
        ).pack(pady=(35, 15))

        tk.Label(
            card,
            text=CONDUCTED_BY,
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Arial", 13, "italic")
        ).pack(pady=8)

        tk.Label(
            card,
            text=(
                "This survey assesses evening routines and readiness for the following study day.\n"
                "It focuses on planning, relaxation, sleep preparation, emotional balance,\n"
                "and morning readiness."
            ),
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Arial", 12),
            justify="center",
            wraplength=720
        ).pack(pady=20)

        button_frame = tk.Frame(card, bg=self.bg_card)
        button_frame.pack(pady=35)

        self.make_button(button_frame, "Start New Questionnaire", self.show_consent_page, 24).grid(row=0, column=0, padx=12, pady=10)
        self.make_button(button_frame, "Load Existing Result", self.load_existing_result, 20).grid(row=0, column=1, padx=12, pady=10)
        self.make_button(button_frame, "Exit", self.root.destroy, 12).grid(row=1, column=0, columnspan=2, pady=15)

    # --------------------------------------------------------
    # Slide 2
    # --------------------------------------------------------

    def show_consent_page(self):
        self.clear_window()
        card = self.create_card()

        tk.Label(
            card,
            text="Consent & Information",
            bg=self.bg_card,
            fg=self.text_main,
            font=("Arial", 18, "bold")
        ).pack(pady=(30, 20))

        consent_text = (
            "• Your personal data and responses will be kept confidential.\n\n"
            "• Estimated completion time: about 5 to 7 minutes.\n\n"
            "• Participation is voluntary.\n\n"
            "• You may exit the survey at any time before submission.\n\n"
            "• This questionnaire is used for educational and survey purposes."
        )

        tk.Label(
            card,
            text=consent_text,
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Arial", 12),
            justify="left",
            wraplength=720
        ).pack(pady=20)

        frame = tk.Frame(card, bg=self.bg_card)
        frame.pack(pady=30)

        self.make_button(frame, "Proceed", self.show_details_page, 15).grid(row=0, column=0, padx=10)
        self.make_button(frame, "Back", self.show_welcome_page, 15).grid(row=0, column=1, padx=10)
        self.make_button(frame, "Exit", self.root.destroy, 15).grid(row=0, column=2, padx=10)

    # --------------------------------------------------------
    # Student details page
    # --------------------------------------------------------

    def show_details_page(self):
        self.clear_window()
        card = self.create_card()

        tk.Label(
            card,
            text="Student Details",
            bg=self.bg_card,
            fg=self.text_main,
            font=("Arial", 18, "bold")
        ).pack(pady=(25, 20))

        form = tk.Frame(card, bg=self.bg_card)
        form.pack(pady=10)

        tk.Label(form, text="Surname and Given Name:", bg=self.bg_card, fg=self.text_dark, font=("Arial", 12, "bold"), width=26, anchor="w").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(form, textvariable=self.name_var, font=("Arial", 12), width=35).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(form, text="Date of Birth (DD/MM/YYYY):", bg=self.bg_card, fg=self.text_dark, font=("Arial", 12, "bold"), width=26, anchor="w").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(form, textvariable=self.dob_var, font=("Arial", 12), width=35).grid(row=1, column=1, padx=10, pady=10)

        tk.Label(form, text="Student ID Number:", bg=self.bg_card, fg=self.text_dark, font=("Arial", 12, "bold"), width=26, anchor="w").grid(row=2, column=0, padx=10, pady=10)
        tk.Entry(form, textvariable=self.student_id_var, font=("Arial", 12), width=35).grid(row=2, column=1, padx=10, pady=10)

        source_frame = tk.Frame(card, bg=self.bg_card)
        source_frame.pack(pady=15)

        tk.Label(source_frame, text="Question Source:", bg=self.bg_card, fg=self.text_dark, font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10)

        tk.Radiobutton(
            source_frame,
            text="Embedded in program",
            variable=self.question_source_var,
            value="embedded",
            bg=self.bg_card,
            fg=self.text_dark,
            selectcolor=self.bg_main,
            font=("Arial", 11)
        ).grid(row=0, column=1, padx=10)

        tk.Radiobutton(
            source_frame,
            text="Load from external file",
            variable=self.question_source_var,
            value="external",
            bg=self.bg_card,
            fg=self.text_dark,
            selectcolor=self.bg_main,
            font=("Arial", 11)
        ).grid(row=0, column=2, padx=10)

        tk.Label(
            card,
            text=(
                "External file formats for questions:\n"
                "TXT: Section | Question\n"
                "CSV: columns named section, question\n"
                "JSON: list of objects with section and question"
            ),
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Arial", 10),
            justify="left"
        ).pack(pady=10)

        buttons = tk.Frame(card, bg=self.bg_card)
        buttons.pack(pady=25)

        self.make_button(buttons, "Start Survey", self.start_survey, 16).grid(row=0, column=0, padx=10)
        self.make_button(buttons, "Back", self.show_consent_page, 16).grid(row=0, column=1, padx=10)

    # --------------------------------------------------------
    # Start survey
    # --------------------------------------------------------

    def start_survey(self):
        full_name = clean_extra_spaces(self.name_var.get())
        dob = self.dob_var.get().strip()
        student_id = self.student_id_var.get().strip()

        # at least 3 conditionals
        if not validate_full_name(full_name):
            messagebox.showerror(
                "Invalid Name",
                "Name must contain only letters, spaces, hyphens (-), and apostrophes (')."
            )
            return
        elif not validate_date_of_birth(dob):
            messagebox.showerror(
                "Invalid Date of Birth",
                "Date of birth must be in DD/MM/YYYY format and be a real valid date."
            )
            return
        elif not validate_student_id(student_id):
            messagebox.showerror(
                "Invalid Student ID",
                "Student ID must contain digits only."
            )
            return

        self.user_data["full_name"] = full_name
        self.user_data["date_of_birth"] = dob
        self.user_data["student_id"] = student_id
        self.user_data["survey_date"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if self.question_source_var.get() == "embedded":
            self.questions = EMBEDDED_QUESTIONS.copy()
            self.question_source = "Embedded in code"
        else:
            loaded = self.load_external_questions()
            if not loaded:
                return
            self.question_source = "Loaded from external file"

        if not (15 <= len(self.questions) <= 25):
            messagebox.showerror(
                "Question Count Error",
                "The questionnaire must contain between 15 and 25 questions."
            )
            return

        self.question_vars = [tk.IntVar(value=-1) for _ in self.questions]
        self.current_question_index = 0
        self.show_question_page()

    # --------------------------------------------------------
    # Load external questions
    # --------------------------------------------------------

    def load_external_questions(self):
        file_path = filedialog.askopenfilename(
            title="Select Question File",
            filetypes=[
                ("All Supported Files", "*.txt *.csv *.json"),
                ("Text Files", "*.txt"),
                ("CSV Files", "*.csv"),
                ("JSON Files", "*.json")
            ]
        )

        if not file_path:
            return False

        try:
            suffix = Path(file_path).suffix.lower()

            if suffix == ".txt":
                loaded_questions = load_questions_from_txt(file_path)
            elif suffix == ".csv":
                loaded_questions = load_questions_from_csv(file_path)
            elif suffix == ".json":
                loaded_questions = load_questions_from_json(file_path)
            else:
                messagebox.showerror("File Error", "Unsupported file format.")
                return False

            if not (15 <= len(loaded_questions) <= 25):
                messagebox.showerror(
                    "Question Count Error",
                    "External question file must contain between 15 and 25 questions."
                )
                return False

            self.questions = loaded_questions
            return True

        except Exception as error:
            messagebox.showerror("File Error", f"Could not load questions.\n\n{error}")
            return False

    # --------------------------------------------------------
    # Question slides
    # --------------------------------------------------------

    def show_question_page(self):
        self.clear_window()
        card = self.create_card()

        index = self.current_question_index
        q_data = self.questions[index]

        tk.Label(
            card,
            text=f"Question {index + 1} of {len(self.questions)}",
            bg=self.bg_card,
            fg=self.text_main,
            font=("Arial", 16, "bold")
        ).pack(pady=(25, 10))

        tk.Label(
            card,
            text=q_data["section"],
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Arial", 12, "italic")
        ).pack(pady=5)

        tk.Label(
            card,
            text=q_data["question"],
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Arial", 14),
            wraplength=720,
            justify="center"
        ).pack(pady=25)

        options_frame = tk.Frame(card, bg=self.bg_card)
        options_frame.pack(pady=20)

        for option_text, option_score in ANSWER_OPTIONS:
            tk.Radiobutton(
                options_frame,
                text=f"{option_text} ({option_score})",
                variable=self.question_vars[index],
                value=option_score,
                bg=self.bg_card,
                fg=self.text_dark,
                selectcolor=self.bg_main,
                font=("Arial", 12),
                anchor="w",
                width=24
            ).pack(anchor="w", pady=5)

        nav = tk.Frame(card, bg=self.bg_card)
        nav.pack(side="bottom", pady=30)

        if index > 0:
            self.make_button(nav, "Previous", self.previous_question, 14).grid(row=0, column=0, padx=12)

        if index < len(self.questions) - 1:
            self.make_button(nav, "Next", self.next_question, 14).grid(row=0, column=1, padx=12)
        else:
            self.make_button(nav, "Finish", self.finish_survey, 14).grid(row=0, column=1, padx=12)

    def next_question(self):
        if self.question_vars[self.current_question_index].get() == -1:
            messagebox.showwarning("Answer Required", "Please choose one answer before moving to the next question.")
            return
        self.current_question_index += 1
        self.show_question_page()

    def previous_question(self):
        self.current_question_index -= 1
        self.show_question_page()

    # --------------------------------------------------------
    # Finish / Results
    # --------------------------------------------------------

    def finish_survey(self):
        unanswered = []
        for i in range(len(self.question_vars)):
            if self.question_vars[i].get() == -1:
                unanswered.append(str(i + 1))

        if unanswered:
            messagebox.showwarning(
                "Incomplete Survey",
                "Please answer all questions before finishing.\n\nUnanswered questions: " + ", ".join(unanswered)
            )
            return

        self.show_results_page()

    def build_result_data(self):
        raw_score = sum(var.get() for var in self.question_vars)
        max_raw_score = len(self.questions) * 4
        scaled_score = calculate_scaled_score(raw_score, max_raw_score)
        result_text = classify_state(scaled_score)

        answers_data = []
        for i in range(len(self.questions)):
            selected_score = self.question_vars[i].get()
            selected_answer = ""

            for answer_text, answer_score in ANSWER_OPTIONS:
                if answer_score == selected_score:
                    selected_answer = answer_text
                    break

            answers_data.append({
                "question_number": i + 1,
                "section": self.questions[i]["section"],
                "question": self.questions[i]["question"],
                "selected_answer": selected_answer,
                "score": selected_score
            })

        result_data = {
            "survey_title": APP_TITLE,
            "conducted_by": "Fotima",
            "full_name": self.user_data["full_name"],
            "date_of_birth": self.user_data["date_of_birth"],
            "student_id": self.user_data["student_id"],
            "survey_date": self.user_data["survey_date"],
            "question_source": self.question_source,
            "number_of_questions": len(self.questions),
            "raw_score_out_of_80": raw_score,
            "scaled_score_out_of_100": scaled_score,
            "psychological_state_result": result_text,
            "answers": answers_data
        }
        return result_data

    def show_results_page(self):
        self.clear_window()
        card = self.create_card()

        result_data = self.build_result_data()

        tk.Label(
            card,
            text="Survey Result",
            bg=self.bg_card,
            fg=self.text_main,
            font=("Arial", 18, "bold")
        ).pack(pady=(25, 20))

        result_text = (
            f"Name: {result_data['full_name']}\n"
            f"Date of Birth: {result_data['date_of_birth']}\n"
            f"Student ID: {result_data['student_id']}\n"
            f"Survey Date: {result_data['survey_date']}\n"
            f"Question Source: {result_data['question_source']}\n"
            f"Number of Questions: {result_data['number_of_questions']}\n\n"
            f"Raw Score: {result_data['raw_score_out_of_80']} / 80\n"
            f"Scaled Score: {result_data['scaled_score_out_of_100']} / 100\n\n"
            f"Result: {result_data['psychological_state_result']}"
        )

        tk.Label(
            card,
            text=result_text,
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Arial", 12),
            justify="left",
            wraplength=720
        ).pack(pady=20)

        tk.Label(
            card,
            text="Choose a file format to save the survey result:",
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Arial", 12, "bold")
        ).pack(pady=(10, 10))

        save_frame = tk.Frame(card, bg=self.bg_card)
        save_frame.pack(pady=10)

        self.make_button(save_frame, "Save as TXT", lambda: self.save_result("txt"), 14).grid(row=0, column=0, padx=8)
        self.make_button(save_frame, "Save as CSV", lambda: self.save_result("csv"), 14).grid(row=0, column=1, padx=8)
        self.make_button(save_frame, "Save as JSON", lambda: self.save_result("json"), 14).grid(row=0, column=2, padx=8)

        bottom = tk.Frame(card, bg=self.bg_card)
        bottom.pack(pady=30)

        self.make_button(bottom, "Restart", self.restart_app, 14).grid(row=0, column=0, padx=10)
        self.make_button(bottom, "Exit", self.root.destroy, 14).grid(row=0, column=1, padx=10)

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    def save_result(self, file_format):
        result_data = self.build_result_data()

        file_path = filedialog.asksaveasfilename(
            title="Save Survey Result",
            defaultextension=f".{file_format}",
            filetypes=[(f"{file_format.upper()} files", f"*.{file_format}")]
        )

        if not file_path:
            return

        try:
            if file_format == "txt":
                self.save_as_txt(file_path, result_data)
            elif file_format == "csv":
                self.save_as_csv(file_path, result_data)
            elif file_format == "json":
                self.save_as_json(file_path, result_data)
            else:
                messagebox.showerror("Save Error", "Unsupported file format.")
                return

            messagebox.showinfo("Saved", f"Result saved successfully as {file_format.upper()}.")

        except Exception as error:
            messagebox.showerror("Save Error", f"Could not save file.\n\n{error}")

    def save_as_txt(self, file_path, result_data):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("SURVEY RESULT\n")
            file.write("=" * 70 + "\n")
            file.write(f"Survey Title: {result_data['survey_title']}\n")
            file.write(f"Conducted By: {result_data['conducted_by']}\n")
            file.write(f"Full Name: {result_data['full_name']}\n")
            file.write(f"Date of Birth: {result_data['date_of_birth']}\n")
            file.write(f"Student ID: {result_data['student_id']}\n")
            file.write(f"Survey Date: {result_data['survey_date']}\n")
            file.write(f"Question Source: {result_data['question_source']}\n")
            file.write(f"Number of Questions: {result_data['number_of_questions']}\n")
            file.write(f"Raw Score (out of 80): {result_data['raw_score_out_of_80']}\n")
            file.write(f"Scaled Score (out of 100): {result_data['scaled_score_out_of_100']}\n")
            file.write(f"Psychological State Result: {result_data['psychological_state_result']}\n")
            file.write("\n")
            file.write("DETAILED ANSWERS\n")
            file.write("=" * 70 + "\n")

            for answer in result_data["answers"]:
                file.write(f"Q{answer['question_number']}: {answer['question']}\n")
                file.write(f"Selected Answer: {answer['selected_answer']}\n")
                file.write(f"Score: {answer['score']}\n")
                file.write("-" * 70 + "\n")

    def save_as_csv(self, file_path, result_data):
        with open(file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)

            writer.writerow(["Field", "Value"])
            writer.writerow(["Survey Title", result_data["survey_title"]])
            writer.writerow(["Conducted By", result_data["conducted_by"]])
            writer.writerow(["Full Name", result_data["full_name"]])
            writer.writerow(["Date of Birth", result_data["date_of_birth"]])
            writer.writerow(["Student ID", result_data["student_id"]])
            writer.writerow(["Survey Date", result_data["survey_date"]])
            writer.writerow(["Question Source", result_data["question_source"]])
            writer.writerow(["Number of Questions", result_data["number_of_questions"]])
            writer.writerow(["Raw Score (out of 80)", result_data["raw_score_out_of_80"]])
            writer.writerow(["Scaled Score (out of 100)", result_data["scaled_score_out_of_100"]])
            writer.writerow(["Psychological State Result", result_data["psychological_state_result"]])

            writer.writerow([])
            writer.writerow(["Question Number", "Section", "Question", "Selected Answer", "Score"])

            for answer in result_data["answers"]:
                writer.writerow([
                    answer["question_number"],
                    answer["section"],
                    answer["question"],
                    answer["selected_answer"],
                    answer["score"]
                ])

    def save_as_json(self, file_path, result_data):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(result_data, file, ensure_ascii=False, indent=4)

    # --------------------------------------------------------
    # Load existing saved result
    # --------------------------------------------------------

    def load_existing_result(self):
        file_path = filedialog.askopenfilename(
            title="Load Existing Result",
            filetypes=[
                ("All Supported Files", "*.txt *.csv *.json"),
                ("Text Files", "*.txt"),
                ("CSV Files", "*.csv"),
                ("JSON Files", "*.json")
            ]
        )

        if not file_path:
            return

        try:
            display_text = load_saved_result_as_text(file_path)
            self.show_loaded_result_page(display_text)
        except Exception as error:
            messagebox.showerror("Load Error", f"Could not load the file.\n\n{error}")

    def show_loaded_result_page(self, text_to_display):
        self.clear_window()
        card = self.create_card()

        tk.Label(
            card,
            text="Loaded Saved Result",
            bg=self.bg_card,
            fg=self.text_main,
            font=("Arial", 18, "bold")
        ).pack(pady=(20, 15))

        text_frame = tk.Frame(card, bg=self.bg_card)
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)

        text_box = tk.Text(
            text_frame,
            wrap="word",
            font=("Arial", 11),
            bg=self.white,
            fg=self.text_dark
        )
        text_box.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=text_box.yview)
        scrollbar.pack(side="right", fill="y")
        text_box.config(yscrollcommand=scrollbar.set)

        text_box.insert("1.0", text_to_display)
        text_box.config(state="disabled")

        bottom = tk.Frame(card, bg=self.bg_card)
        bottom.pack(pady=20)

        self.make_button(bottom, "Back to Home", self.show_welcome_page, 16).grid(row=0, column=0, padx=10)
        self.make_button(bottom, "Exit", self.root.destroy, 16).grid(row=0, column=1, padx=10)

    # --------------------------------------------------------
    # Restart
    # --------------------------------------------------------

    def restart_app(self):
        self.name_var.set("")
        self.dob_var.set("")
        self.student_id_var.set("")
        self.question_source_var.set("embedded")

        self.questions = EMBEDDED_QUESTIONS.copy()
        self.question_source = "Embedded in code"
        self.question_vars = []
        self.current_question_index = 0

        self.user_data = {
            "full_name": "",
            "date_of_birth": "",
            "student_id": "",
            "survey_date": ""
        }

        self.show_welcome_page()


# ============================================================
# MAIN
# ============================================================

def main():
    """
    This program is intended for Spyder IDE / normal desktop Python.
    Tkinter GUI needs a graphical desktop environment.
    """
    try:
        root = tk.Tk()
        app = SurveyApp(root)
        root.mainloop()
    except tk.TclError:
        print("Tkinter GUI could not start because no graphical display is available.")
        print("Run this program in Spyder IDE or a local Python environment with desktop support.")


if __name__ == "__main__":
    if tk is None:
        print("Tkinter GUI cannot run in this environment (like Streamlit Cloud).")
        print("Please run this program locally on your computer.")
    else:
        root = tk.Tk()
        app = SurveyApp(root)
        root.mainloop()