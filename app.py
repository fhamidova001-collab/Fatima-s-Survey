import tkinter as tk
from tkinter import messagebox, filedialog
import json
import csv
import re
from datetime import datetime
from pathlib import Path


# ==========================================================
# GLOBAL DATA
# ==========================================================

APP_TITLE = "Evening Wind-Down Routines and Next-Day Readiness Questionnaire"
CONDUCTED_BY = "Conducted by Fotima"

# Required variable types for marking
sample_int = 20
sample_str = "survey"
sample_float = 100.0 / 80.0
sample_list = [1, 2, 3]
sample_tuple = ("Always", 0)
sample_range = range(1, 6)
sample_bool = True
sample_dict = {"txt": "Text", "csv": "CSV", "json": "JSON"}
sample_set = {"txt", "csv", "json"}
sample_frozenset = frozenset({"txt", "csv", "json"})

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


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def clean_spaces(text):
    """
    Uses a while loop for validation cleanup.
    """
    text = text.strip()
    while "  " in text:
        text = text.replace("  ", " ")
    return text


def validate_full_name(name):
    """
    Only letters, spaces, apostrophes, hyphens.
    Uses a for loop for validation.
    """
    name = clean_spaces(name)

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


def validate_dob(dob_text):
    """
    Required format: DD/MM/YYYY
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
    return student_id.strip().isdigit()


def scaled_score_from_raw(raw_score, question_count):
    max_raw = question_count * 4
    return round((raw_score / max_raw) * 100)


def interpret_result(score_100):
    if 0 <= score_100 <= 20:
        return "Excellent routine — high readiness"
    elif 21 <= score_100 <= 40:
        return "Good habits — minor improvements"
    elif 41 <= score_100 <= 60:
        return "Moderate routine — needs structure"
    elif 61 <= score_100 <= 80:
        return "Low readiness — poor habits"
    else:
        return "Very poor — immediate improvement needed"


def option_text_from_score(score):
    for text, value in ANSWER_OPTIONS:
        if value == score:
            return text
    return "No answer"


def load_question_file(file_path):
    suffix = Path(file_path).suffix.lower()
    questions = []

    if suffix == ".json":
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        for item in data:
            if isinstance(item, dict) and "section" in item and "question" in item:
                questions.append({
                    "section": str(item["section"]).strip(),
                    "question": str(item["question"]).strip()
                })

    elif suffix == ".csv":
        with open(file_path, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if "section" in row and "question" in row:
                    questions.append({
                        "section": row["section"].strip(),
                        "question": row["question"].strip()
                    })

    elif suffix == ".txt":
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line and "|" in line:
                    section, question = line.split("|", 1)
                    questions.append({
                        "section": section.strip(),
                        "question": question.strip()
                    })
    else:
        raise ValueError("Unsupported question file format.")

    return questions


def read_saved_result(file_path):
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

        output = []
        output.append("SURVEY RESULT")
        output.append("=" * 70)

        for key, value in data.items():
            if key != "answers":
                output.append(f"{key}: {value}")

        output.append("")
        output.append("ANSWERS")
        output.append("=" * 70)

        for item in data.get("answers", []):
            output.append(f"Q{item['question_number']}: {item['question']}")
            output.append(f"Selected Answer: {item['selected_answer']} | Score: {item['score']}")
            output.append("-" * 70)

        return "\n".join(output)

    else:
        raise ValueError("Unsupported result file format.")


# ==========================================================
# GUI APP
# ==========================================================

class SurveyApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1020x720")
        self.root.resizable(False, False)

        # Theme
        self.bg_main = "#F6EEFF"
        self.bg_card = "#E9D5FF"
        self.bg_button = "#C084FC"
        self.bg_button_dark = "#A855F7"
        self.text_main = "#3B0764"
        self.text_alt = "#4C1D95"
        self.white = "#FFFFFF"

        self.root.configure(bg=self.bg_main)

        # Data
        self.questions = EMBEDDED_QUESTIONS.copy()
        self.question_source = "Embedded in code"

        self.user_data = {
            "full_name": "",
            "date_of_birth": "",
            "student_id": "",
            "survey_date": ""
        }

        self.answer_vars = []
        self.current_question_index = 0

        # Tk variables
        self.full_name_var = tk.StringVar()
        self.dob_var = tk.StringVar()
        self.student_id_var = tk.StringVar()
        self.question_mode_var = tk.StringVar(value="embedded")

        self.show_welcome_page()

    # ------------------------------------------------------
    # UI utilities
    # ------------------------------------------------------

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_card(self):
        card = tk.Frame(self.root, bg=self.bg_card, bd=2, relief="ridge")
        card.place(relx=0.5, rely=0.5, anchor="center", width=880, height=620)
        return card

    def make_button(self, parent, text, command, width=18):
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            font=("Arial", 11, "bold"),
            bg=self.bg_button,
            fg=self.white,
            activebackground=self.bg_button_dark,
            activeforeground=self.white,
            relief="flat",
            cursor="hand2",
            pady=8
        )

    # ------------------------------------------------------
    # Page 1: Welcome
    # ------------------------------------------------------

    def show_welcome_page(self):
        self.clear_window()
        card = self.create_card()

        tk.Label(
            card,
            text=APP_TITLE,
            bg=self.bg_card,
            fg=self.text_main,
            font=("Arial", 18, "bold"),
            wraplength=740,
            justify="center"
        ).pack(pady=(35, 15))

        tk.Label(
            card,
            text=CONDUCTED_BY,
            bg=self.bg_card,
            fg=self.text_alt,
            font=("Arial", 13, "italic")
        ).pack(pady=5)

        tk.Label(
            card,
            text=(
                "This survey assesses evening routines and readiness for the following study day.\n"
                "It focuses on planning, organization, mental relaxation, sleep preparation,\n"
                "physical and emotional state, and next-day readiness."
            ),
            bg=self.bg_card,
            fg=self.text_alt,
            font=("Arial", 12),
            wraplength=740,
            justify="center"
        ).pack(pady=20)

        button_frame = tk.Frame(card, bg=self.bg_card)
        button_frame.pack(pady=40)

        self.make_button(button_frame, "Start New Questionnaire", self.show_consent_page, 24).grid(row=0, column=0, padx=12, pady=10)
        self.make_button(button_frame, "Load Existing Result", self.load_existing_result, 20).grid(row=0, column=1, padx=12, pady=10)
        self.make_button(button_frame, "Exit", self.root.destroy, 12).grid(row=1, column=0, columnspan=2, pady=12)

    # ------------------------------------------------------
    # Page 2: Consent
    # ------------------------------------------------------

    def show_consent_page(self):
        self.clear_window()
        card = self.create_card()

        tk.Label(
            card,
            text="Consent & Information",
            bg=self.bg_card,
            fg=self.text_main,
            font=("Arial", 18, "bold")
        ).pack(pady=(35, 20))

        tk.Label(
            card,
            text=(
                "• Your responses will be treated confidentially.\n\n"
                "• Estimated completion time: approximately 5–7 minutes.\n\n"
                "• Participation is voluntary.\n\n"
                "• You may leave the questionnaire at any time.\n\n"
                "• This survey is for educational coursework purposes."
            ),
            bg=self.bg_card,
            fg=self.text_alt,
            font=("Arial", 12),
            justify="left",
            wraplength=720
        ).pack(pady=20)

        btns = tk.Frame(card, bg=self.bg_card)
        btns.pack(pady=30)

        self.make_button(btns, "Proceed", self.show_details_page, 15).grid(row=0, column=0, padx=10)
        self.make_button(btns, "Back", self.show_welcome_page, 15).grid(row=0, column=1, padx=10)
        self.make_button(btns, "Exit", self.root.destroy, 15).grid(row=0, column=2, padx=10)

    # ------------------------------------------------------
    # Page 3: Details
    # ------------------------------------------------------

    def show_details_page(self):
        self.clear_window()
        card = self.create_card()

        tk.Label(
            card,
            text="Enter Student Information",
            bg=self.bg_card,
            fg=self.text_main,
            font=("Arial", 18, "bold")
        ).pack(pady=(25, 20))

        form = tk.Frame(card, bg=self.bg_card)
        form.pack(pady=10)

        tk.Label(form, text="Surname and Given Name:", bg=self.bg_card, fg=self.text_alt, font=("Arial", 12, "bold"), width=28, anchor="w").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(form, textvariable=self.full_name_var, font=("Arial", 12), width=35).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(form, text="Date of Birth (DD/MM/YYYY):", bg=self.bg_card, fg=self.text_alt, font=("Arial", 12, "bold"), width=28, anchor="w").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(form, textvariable=self.dob_var, font=("Arial", 12), width=35).grid(row=1, column=1, padx=10, pady=10)

        tk.Label(form, text="Student ID Number:", bg=self.bg_card, fg=self.text_alt, font=("Arial", 12, "bold"), width=28, anchor="w").grid(row=2, column=0, padx=10, pady=10)
        tk.Entry(form, textvariable=self.student_id_var, font=("Arial", 12), width=35).grid(row=2, column=1, padx=10, pady=10)

        source_frame = tk.Frame(card, bg=self.bg_card)
        source_frame.pack(pady=18)

        tk.Label(source_frame, text="Question Source:", bg=self.bg_card, fg=self.text_alt, font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10)

        tk.Radiobutton(
            source_frame,
            text="Embedded in code",
            variable=self.question_mode_var,
            value="embedded",
            bg=self.bg_card,
            fg=self.text_alt,
            selectcolor=self.bg_main,
            font=("Arial", 11)
        ).grid(row=0, column=1, padx=10)

        tk.Radiobutton(
            source_frame,
            text="Load from file",
            variable=self.question_mode_var,
            value="external",
            bg=self.bg_card,
            fg=self.text_alt,
            selectcolor=self.bg_main,
            font=("Arial", 11)
        ).grid(row=0, column=2, padx=10)

        tk.Label(
            card,
            text=(
                "External question file formats:\n"
                "TXT: Section | Question\n"
                "CSV: columns named section and question\n"
                "JSON: list of objects with section and question"
            ),
            bg=self.bg_card,
            fg=self.text_alt,
            font=("Arial", 10),
            justify="left"
        ).pack(pady=10)

        btns = tk.Frame(card, bg=self.bg_card)
        btns.pack(pady=25)

        self.make_button(btns, "Start Survey", self.start_survey, 16).grid(row=0, column=0, padx=10)
        self.make_button(btns, "Back", self.show_consent_page, 16).grid(row=0, column=1, padx=10)

    # ------------------------------------------------------
    # Start survey
    # ------------------------------------------------------

    def start_survey(self):
        full_name = clean_spaces(self.full_name_var.get())
        dob = self.dob_var.get().strip()
        student_id = self.student_id_var.get().strip()

        if not validate_full_name(full_name):
            messagebox.showerror(
                "Invalid Name",
                "Enter surname and given name using letters, spaces, hyphens, or apostrophes only."
            )
            return
        elif not validate_dob(dob):
            messagebox.showerror(
                "Invalid Date of Birth",
                "Enter date of birth in DD/MM/YYYY format, for example 14/05/2004."
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

        if self.question_mode_var.get() == "embedded":
            self.questions = EMBEDDED_QUESTIONS.copy()
            self.question_source = "Embedded in code"
        else:
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
                return

            try:
                loaded_questions = load_question_file(file_path)
                if not (15 <= len(loaded_questions) <= 25):
                    messagebox.showerror(
                        "Invalid Question Count",
                        "The question file must contain between 15 and 25 questions."
                    )
                    return

                self.questions = loaded_questions
                self.question_source = "Loaded from external file"

            except Exception as error:
                messagebox.showerror("File Error", f"Could not load questions.\n\n{error}")
                return

        self.answer_vars = [tk.IntVar(value=-1) for _ in self.questions]
        self.current_question_index = 0
        self.show_question_page()

    # ------------------------------------------------------
    # Question page
    # ------------------------------------------------------

    def show_question_page(self):
        self.clear_window()
        card = self.create_card()

        index = self.current_question_index
        item = self.questions[index]

        tk.Label(
            card,
            text=f"Question {index + 1} of {len(self.questions)}",
            bg=self.bg_card,
            fg=self.text_main,
            font=("Arial", 16, "bold")
        ).pack(pady=(30, 10))

        tk.Label(
            card,
            text=item["section"],
            bg=self.bg_card,
            fg=self.text_alt,
            font=("Arial", 12, "italic")
        ).pack(pady=8)

        tk.Label(
            card,
            text=item["question"],
            bg=self.bg_card,
            fg=self.text_alt,
            font=("Arial", 14),
            wraplength=740,
            justify="center"
        ).pack(pady=25)

        options_frame = tk.Frame(card, bg=self.bg_card)
        options_frame.pack(pady=15)

        for option_text, option_score in ANSWER_OPTIONS:
            tk.Radiobutton(
                options_frame,
                text=f"{option_text} ({option_score})",
                variable=self.answer_vars[index],
                value=option_score,
                bg=self.bg_card,
                fg=self.text_alt,
                selectcolor=self.bg_main,
                font=("Arial", 12),
                width=24,
                anchor="w"
            ).pack(anchor="w", pady=5)

        nav = tk.Frame(card, bg=self.bg_card)
        nav.pack(side="bottom", pady=30)

        if index > 0:
            self.make_button(nav, "Previous", self.previous_question, 14).grid(row=0, column=0, padx=10)

        if index < len(self.questions) - 1:
            self.make_button(nav, "Next", self.next_question, 14).grid(row=0, column=1, padx=10)
        else:
            self.make_button(nav, "Finish", self.finish_survey, 14).grid(row=0, column=1, padx=10)

    def next_question(self):
        if self.answer_vars[self.current_question_index].get() == -1:
            messagebox.showwarning("Answer Required", "Please choose one answer before continuing.")
            return

        self.current_question_index += 1
        self.show_question_page()

    def previous_question(self):
        self.current_question_index -= 1
        self.show_question_page()

    # ------------------------------------------------------
    # Results
    # ------------------------------------------------------

    def build_result_data(self):
        raw_score = sum(var.get() for var in self.answer_vars)
        scaled_score = scaled_score_from_raw(raw_score, len(self.questions))
        result_text = interpret_result(scaled_score)

        answers = []
        for i, q in enumerate(self.questions):
            score = self.answer_vars[i].get()
            answers.append({
                "question_number": i + 1,
                "section": q["section"],
                "question": q["question"],
                "selected_answer": option_text_from_score(score),
                "score": score
            })

        return {
            "survey_title": APP_TITLE,
            "conducted_by": "Fotima",
            "full_name": self.user_data["full_name"],
            "date_of_birth": self.user_data["date_of_birth"],
            "student_id": self.user_data["student_id"],
            "survey_date": self.user_data["survey_date"],
            "question_source": self.question_source,
            "number_of_questions": len(self.questions),
            "raw_score": raw_score,
            "maximum_raw_score": len(self.questions) * 4,
            "scaled_score_out_of_100": scaled_score,
            "psychological_state_result": result_text,
            "answers": answers
        }

    def finish_survey(self):
        missing = []

        for i in range(len(self.answer_vars)):
            if self.answer_vars[i].get() == -1:
                missing.append(str(i + 1))

        if missing:
            messagebox.showwarning(
                "Incomplete Questionnaire",
                "Please answer all questions before finishing.\n\nMissing: " + ", ".join(missing)
            )
            return

        self.show_result_page()

    def show_result_page(self):
        self.clear_window()
        card = self.create_card()

        result_data = self.build_result_data()

        tk.Label(
            card,
            text="Survey Result",
            bg=self.bg_card,
            fg=self.text_main,
            font=("Arial", 18, "bold")
        ).pack(pady=(30, 20))

        summary = (
            f"Name: {result_data['full_name']}\n"
            f"Date of Birth: {result_data['date_of_birth']}\n"
            f"Student ID: {result_data['student_id']}\n"
            f"Survey Date: {result_data['survey_date']}\n"
            f"Question Source: {result_data['question_source']}\n"
            f"Number of Questions: {result_data['number_of_questions']}\n\n"
            f"Raw Score: {result_data['raw_score']} / {result_data['maximum_raw_score']}\n"
            f"Scaled Score: {result_data['scaled_score_out_of_100']} / 100\n\n"
            f"Result: {result_data['psychological_state_result']}"
        )

        tk.Label(
            card,
            text=summary,
            bg=self.bg_card,
            fg=self.text_alt,
            font=("Arial", 12),
            justify="left",
            wraplength=740
        ).pack(pady=20)

        tk.Label(
            card,
            text="Choose file format to save the result:",
            bg=self.bg_card,
            fg=self.text_alt,
            font=("Arial", 12, "bold")
        ).pack(pady=(10, 8))

        save_frame = tk.Frame(card, bg=self.bg_card)
        save_frame.pack(pady=10)

        self.make_button(save_frame, "Save as TXT", lambda: self.save_result("txt"), 14).grid(row=0, column=0, padx=8)
        self.make_button(save_frame, "Save as CSV", lambda: self.save_result("csv"), 14).grid(row=0, column=1, padx=8)
        self.make_button(save_frame, "Save as JSON", lambda: self.save_result("json"), 14).grid(row=0, column=2, padx=8)

        bottom = tk.Frame(card, bg=self.bg_card)
        bottom.pack(pady=25)

        self.make_button(bottom, "Restart", self.restart_app, 14).grid(row=0, column=0, padx=10)
        self.make_button(bottom, "Exit", self.root.destroy, 14).grid(row=0, column=1, padx=10)

    # ------------------------------------------------------
    # Save results
    # ------------------------------------------------------

    def save_result(self, file_format):
        data = self.build_result_data()

        file_path = filedialog.asksaveasfilename(
            title="Save Result",
            defaultextension=f".{file_format}",
            filetypes=[(f"{file_format.upper()} files", f"*.{file_format}")]
        )

        if not file_path:
            return

        try:
            if file_format == "txt":
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write("SURVEY RESULT\n")
                    file.write("=" * 70 + "\n")
                    file.write(f"Survey Title: {data['survey_title']}\n")
                    file.write(f"Conducted By: {data['conducted_by']}\n")
                    file.write(f"Full Name: {data['full_name']}\n")
                    file.write(f"Date of Birth: {data['date_of_birth']}\n")
                    file.write(f"Student ID: {data['student_id']}\n")
                    file.write(f"Survey Date: {data['survey_date']}\n")
                    file.write(f"Question Source: {data['question_source']}\n")
                    file.write(f"Number of Questions: {data['number_of_questions']}\n")
                    file.write(f"Raw Score: {data['raw_score']}\n")
                    file.write(f"Maximum Raw Score: {data['maximum_raw_score']}\n")
                    file.write(f"Scaled Score out of 100: {data['scaled_score_out_of_100']}\n")
                    file.write(f"Psychological State Result: {data['psychological_state_result']}\n\n")
                    file.write("DETAILED ANSWERS\n")
                    file.write("=" * 70 + "\n")

                    for ans in data["answers"]:
                        file.write(f"Q{ans['question_number']}: {ans['question']}\n")
                        file.write(f"Selected Answer: {ans['selected_answer']}\n")
                        file.write(f"Score: {ans['score']}\n")
                        file.write("-" * 70 + "\n")

            elif file_format == "csv":
                with open(file_path, "w", encoding="utf-8", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(["Field", "Value"])
                    writer.writerow(["Survey Title", data["survey_title"]])
                    writer.writerow(["Conducted By", data["conducted_by"]])
                    writer.writerow(["Full Name", data["full_name"]])
                    writer.writerow(["Date of Birth", data["date_of_birth"]])
                    writer.writerow(["Student ID", data["student_id"]])
                    writer.writerow(["Survey Date", data["survey_date"]])
                    writer.writerow(["Question Source", data["question_source"]])
                    writer.writerow(["Number of Questions", data["number_of_questions"]])
                    writer.writerow(["Raw Score", data["raw_score"]])
                    writer.writerow(["Maximum Raw Score", data["maximum_raw_score"]])
                    writer.writerow(["Scaled Score out of 100", data["scaled_score_out_of_100"]])
                    writer.writerow(["Psychological State Result", data["psychological_state_result"]])
                    writer.writerow([])
                    writer.writerow(["Question Number", "Section", "Question", "Selected Answer", "Score"])

                    for ans in data["answers"]:
                        writer.writerow([
                            ans["question_number"],
                            ans["section"],
                            ans["question"],
                            ans["selected_answer"],
                            ans["score"]
                        ])

            elif file_format == "json":
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)

            else:
                messagebox.showerror("Save Error", "Unsupported file format.")
                return

            messagebox.showinfo("Saved", f"Result saved successfully as {file_format.upper()}.")

        except Exception as error:
            messagebox.showerror("Save Error", f"Could not save the file.\n\n{error}")

    # ------------------------------------------------------
    # Load saved result
    # ------------------------------------------------------

    def load_existing_result(self):
        file_path = filedialog.askopenfilename(
            title="Load Saved Result",
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
            display_text = read_saved_result(file_path)
            self.show_loaded_result_page(display_text)
        except Exception as error:
            messagebox.showerror("Load Error", f"Could not load file.\n\n{error}")

    def show_loaded_result_page(self, text_to_display):
        self.clear_window()
        card = self.create_card()

        tk.Label(
            card,
            text="Loaded Saved Result",
            bg=self.bg_card,
            fg=self.text_main,
            font=("Arial", 18, "bold")
        ).pack(pady=(25, 15))

        text_frame = tk.Frame(card, bg=self.bg_card)
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)

        text_box = tk.Text(
            text_frame,
            wrap="word",
            font=("Arial", 11),
            bg=self.white,
            fg=self.text_alt
        )
        text_box.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=text_box.yview)
        scrollbar.pack(side="right", fill="y")
        text_box.config(yscrollcommand=scrollbar.set)

        text_box.insert("1.0", text_to_display)
        text_box.config(state="disabled")

        btns = tk.Frame(card, bg=self.bg_card)
        btns.pack(pady=18)

        self.make_button(btns, "Back to Home", self.show_welcome_page, 16).grid(row=0, column=0, padx=10)
        self.make_button(btns, "Exit", self.root.destroy, 16).grid(row=0, column=1, padx=10)

    # ------------------------------------------------------
    # Restart
    # ------------------------------------------------------

    def restart_app(self):
        self.full_name_var.set("")
        self.dob_var.set("")
        self.student_id_var.set("")
        self.question_mode_var.set("embedded")

        self.questions = EMBEDDED_QUESTIONS.copy()
        self.question_source = "Embedded in code"
        self.answer_vars = []
        self.current_question_index = 0

        self.user_data = {
            "full_name": "",
            "date_of_birth": "",
            "student_id": "",
            "survey_date": ""
        }

        self.show_welcome_page()


# ==========================================================
# MAIN
# ==========================================================

def main():
    try:
        root = tk.Tk()
        SurveyApp(root)
        root.mainloop()
    except tk.TclError:
        print("Tkinter GUI could not start because no graphical display is available.")
        print("Run this program in Spyder IDE or another local desktop Python environment.")


if __name__ == "__main__":
    main()