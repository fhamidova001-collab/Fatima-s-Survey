import streamlit as st
import json
import csv
import io
import re
import datetime

# ─────────────────────────────────────────────
# Variable types (marking criteria)
# int, str, float, list, tuple, range, bool, dict, set, frozenset
# ─────────────────────────────────────────────

TOTAL_QUESTIONS: int = 20
MAX_SCORE: int = 80
APP_TITLE: str = "Evening Wind-Down Routines and Next-Day Readiness Questionnaire"
APP_SUBTITLE: str = "Assessing evening habits and study-day preparedness"
CONDUCTOR: str = "Conducted by Fotima"
ESTIMATED_TIME: float = 7.0  # float type

ALLOWED_CHARS: frozenset = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'"
)

# Billie Eilish - wildflower (official audio upload on YouTube)
MUSIC_YOUTUBE_ID: str = "oFEHmvJ-JkA"

SCORE_STATES: tuple = (
    (0,  20, "🌟 Excellent Routine",
     "You have outstanding evening habits and very high next-day readiness. "
     "Keep up your disciplined routine — it is clearly working for you."),
    (21, 40, "✅ Good Habits",
     "Your evening routine is solid with only minor areas to improve. "
     "Small adjustments could push you to excellent readiness."),
    (41, 60, "⚠️ Moderate Routine",
     "Your routine needs more structure. Consider adding a consistent "
     "wind-down checklist and set fixed sleep/wake times."),
    (61, 80, "🔴 Low Readiness",
     "Your evening habits are significantly affecting your next-day performance. "
     "Creating a calming nightly routine is strongly recommended."),
    (81, 100, "🆘 Very Poor Routine",
     "Immediate improvement is needed. Your current habits are likely causing "
     "fatigue, low focus, and poor study performance. Please seek support."),
)

SECTIONS: list = [
    "📋 Section 1: Planning & Organization",
    "🧘 Section 2: Mental Relaxation",
    "😴 Section 3: Sleep Preparation",
    "💛 Section 4: Physical & Emotional State",
    "🌅 Section 5: Next-Day Readiness",
]

ANSWER_OPTIONS: list = [
    ("Always", 0),
    ("Often", 1),
    ("Sometimes", 2),
    ("Rarely", 3),
    ("Never", 4),
]

QUESTIONS: list = [
    # Section 1
    {"section": 0, "text": "How often do you organise your study materials before going to bed?"},
    {"section": 0, "text": "How regularly do you set goals for the next day?"},
    {"section": 0, "text": "Do you create a to-do list for upcoming tasks?"},
    {"section": 0, "text": "How often do you review your schedule before sleeping?"},
    # Section 2
    {"section": 1, "text": "How often do you engage in calming activities (reading, meditation)?"},
    {"section": 1, "text": "Do you feel mentally relaxed before going to sleep?"},
    {"section": 1, "text": "How often do you avoid stressful thinking at night?"},
    {"section": 1, "text": "How frequently do you feel calm and peaceful before bed?"},
    # Section 3
    {"section": 2, "text": "How consistent is your sleep schedule?"},
    {"section": 2, "text": "Do you avoid using electronic devices before bedtime?"},
    {"section": 2, "text": "How often do you sleep without interruptions?"},
    {"section": 2, "text": "How comfortable is your sleeping environment?"},
    # Section 4
    {"section": 3, "text": "How often do you feel physically relaxed before sleep?"},
    {"section": 3, "text": "Do you feel emotionally stable at night?"},
    {"section": 3, "text": "How often do you feel tired in a healthy way (not exhausted)?"},
    # Section 5
    {"section": 4, "text": "How energised do you feel when you wake up?"},
    {"section": 4, "text": "How ready are you to start your daily tasks?"},
    {"section": 4, "text": "How confident do you feel about managing your schedule?"},
    {"section": 4, "text": "How focused are you in the morning?"},
    {"section": 4, "text": "How motivated are you to begin studying?"},
]

USED_IDS: set = set()

# ─────────────────────────────────────────────
# VALIDATION FUNCTIONS
# ─────────────────────────────────────────────

def validate_name(name: str) -> bool:
    if not name or not name.strip():
        return False
    valid: bool = True
    for ch in name:           # for loop for input validation
        if ch not in ALLOWED_CHARS:
            valid = False
            break
    return valid


def validate_dob(dob_str: str) -> bool:
    pattern: str = r"^\d{2}/\d{2}/\d{4}$"
    if not re.match(pattern, dob_str):
        return False
    try:
        day, month, year = dob_str.split("/")
        birth: datetime.date = datetime.date(int(year), int(month), int(day))
        today: datetime.date = datetime.date.today()
        age: int = today.year - birth.year
        if birth > today or age > 120:
            return False
        return True
    except ValueError:
        return False


def validate_student_id(sid: str) -> bool:
    if not sid:
        return False
    is_valid: bool = True
    while is_valid:           # while loop for input validation
        for ch in sid:
            if not ch.isdigit():
                is_valid = False
                break
        break
    return is_valid


def get_psychological_state(score: int) -> dict:
    result: dict = {}
    for low, high, label, description in SCORE_STATES:
        if low <= score <= high:
            result = {"label": label, "description": description}
            break
    return result


def compute_score(answers: dict) -> int:
    total: int = 0
    for q_idx in range(TOTAL_QUESTIONS):
        if q_idx in answers:
            total += answers[q_idx]
    return total


def build_results_dict(user_info: dict, answers: dict, score: int, state: dict) -> dict:
    answered: list = []
    for i, q in enumerate(QUESTIONS):
        if i in answers:
            sc: int = answers[i]
            label: str = next((lbl for lbl, val in ANSWER_OPTIONS if val == sc), "")
            answered.append({"question": q["text"], "answer": label, "score": sc})
    return {
        "surname_name": user_info.get("name", ""),
        "date_of_birth": user_info.get("dob", ""),
        "student_id": user_info.get("sid", ""),
        "total_score": score,
        "result": state.get("label", ""),
        "description": state.get("description", ""),
        "answers": answered,
    }


def results_to_txt(data: dict) -> str:
    lines: list = [
        "=" * 60,
        f"  {APP_TITLE}",
        f"  {CONDUCTOR}",
        "=" * 60,
        f"Name          : {data['surname_name']}",
        f"Date of Birth : {data['date_of_birth']}",
        f"Student ID    : {data['student_id']}",
        f"Total Score   : {data['total_score']} / {MAX_SCORE}",
        f"Result        : {data['result']}",
        f"Assessment    : {data['description']}",
        "-" * 60,
        "DETAILED ANSWERS:",
        "-" * 60,
    ]
    for item in data["answers"]:
        lines.append(f"  {item['question']}")
        lines.append(f"  -> {item['answer']}  [score: {item['score']}]")
        lines.append("")
    return "\n".join(lines)


def results_to_csv(data: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Field", "Value"])
    writer.writerow(["Name", data["surname_name"]])
    writer.writerow(["Date of Birth", data["date_of_birth"]])
    writer.writerow(["Student ID", data["student_id"]])
    writer.writerow(["Total Score", data["total_score"]])
    writer.writerow(["Result", data["result"]])
    writer.writerow(["Description", data["description"]])
    writer.writerow([])
    writer.writerow(["#", "Question", "Answer", "Score"])
    for idx, item in enumerate(data["answers"], 1):
        writer.writerow([idx, item["question"], item["answer"], item["score"]])
    return output.getvalue()


def results_to_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def load_results_from_file(content: str, file_ext: str) -> dict:
    loaded: dict = {}
    if file_ext == "json":
        loaded = json.loads(content)
    elif file_ext == "csv":
        reader = csv.reader(io.StringIO(content))
        rows: list = list(reader)
        for row in rows:
            if len(row) == 2:
                key, val = row[0].strip(), row[1].strip()
                if key == "Name":
                    loaded["surname_name"] = val
                elif key == "Date of Birth":
                    loaded["date_of_birth"] = val
                elif key == "Student ID":
                    loaded["student_id"] = val
                elif key == "Total Score":
                    loaded["total_score"] = int(val)
                elif key == "Result":
                    loaded["result"] = val
                elif key == "Description":
                    loaded["description"] = val
    elif file_ext == "txt":
        for line in content.splitlines():
            if line.startswith("Name"):
                loaded["surname_name"] = line.split(":", 1)[-1].strip()
            elif line.startswith("Date of Birth"):
                loaded["date_of_birth"] = line.split(":", 1)[-1].strip()
            elif line.startswith("Student ID"):
                loaded["student_id"] = line.split(":", 1)[-1].strip()
            elif line.startswith("Total Score"):
                part = line.split(":", 1)[-1].strip().split("/")[0].strip()
                loaded["total_score"] = int(part)
            elif line.startswith("Result"):
                loaded["result"] = line.split(":", 1)[-1].strip()
            elif line.startswith("Assessment"):
                loaded["description"] = line.split(":", 1)[-1].strip()
    return loaded


# ─────────────────────────────────────────────
# MUSIC COMPONENT
# ─────────────────────────────────────────────

def render_music_player() -> None:
    """Embed Billie Eilish - wildflower as autoplay background player."""
    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,0.55);
            border-radius: 16px;
            padding: 0.7rem 1.1rem;
            border: 1px solid #c9b3e8;
            margin: 0.4rem 0 0.8rem 0;
            display: flex;
            align-items: center;
            gap: 0.7rem;
        ">
            <span style="font-size:1.4rem;">🌸</span>
            <div style="flex:1;">
                <p style="margin:0;font-weight:700;color:#5b2d8e;font-size:0.88rem;">
                    Now Playing: wildflower
                </p>
                <p style="margin:0;color:#8458b3;font-size:0.78rem;">Billie Eilish</p>
            </div>
            <span style="font-size:0.72rem;color:#b07fd4;font-weight:700;">♫ PLAYING</span>
        </div>
        <iframe
            width="100%" height="80"
            src="https://www.youtube.com/embed/{MUSIC_YOUTUBE_ID}?autoplay=1&mute=0&controls=1&loop=1&playlist={MUSIC_YOUTUBE_ID}"
            frameborder="0"
            allow="autoplay; encrypted-media"
            allowfullscreen
            style="border-radius:10px; display:block; margin-bottom:0.4rem;"
        ></iframe>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────

def apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Playfair+Display:wght@600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        .stApp {
            background: linear-gradient(140deg, #f3eaff 0%, #e8d8f8 35%, #dcc8f5 70%, #cdb6ef 100%);
            min-height: 100vh;
        }

        h1, h2, h3 {
            font-family: 'Playfair Display', serif;
            color: #3d1a6e;
        }

        .card {
            background: rgba(255,255,255,0.72);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 1.8rem 2.2rem;
            box-shadow: 0 8px 30px rgba(100,50,180,0.10);
            border: 1px solid rgba(180,140,230,0.35);
            margin-bottom: 1.4rem;
        }

        .title-hero {
            text-align: center;
            padding: 2.5rem 1rem 0.8rem;
        }

        .title-hero h1 {
            font-size: 2rem;
            color: #3d1a6e;
            line-height: 1.25;
        }

        .title-hero p {
            color: #7048a8;
            font-size: 1rem;
        }

        .badge {
            display: inline-block;
            background: linear-gradient(90deg, #7b3fbf, #b07fd4);
            color: white;
            border-radius: 50px;
            padding: 0.28rem 1.1rem;
            font-size: 0.88rem;
            font-weight: 700;
            margin-top: 0.5rem;
        }

        .section-tag {
            display: inline-block;
            background: rgba(176, 127, 212, 0.18);
            color: #6b2fa0;
            border: 1px solid #c9a8e8;
            border-radius: 50px;
            padding: 0.2rem 0.9rem;
            font-size: 0.82rem;
            font-weight: 600;
            margin-bottom: 0.6rem;
        }

        .stButton > button {
            background: linear-gradient(90deg, #7b3fbf, #b07fd4) !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 0.55rem 2rem !important;
            font-weight: 700 !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 1rem !important;
            box-shadow: 0 4px 14px rgba(123,63,191,0.25) !important;
            transition: transform 0.15s, box-shadow 0.15s !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 22px rgba(123,63,191,0.35) !important;
        }

        .progress-label {
            font-size: 0.83rem;
            color: #7048a8;
            font-weight: 600;
            margin-bottom: 0.15rem;
        }

        .score-chip {
            display: inline-block;
            background: linear-gradient(90deg, #7b3fbf, #b07fd4);
            color: white;
            border-radius: 50px;
            padding: 0.4rem 1.5rem;
            font-size: 1.5rem;
            font-weight: 800;
        }

        .stProgress > div > div {
            background: linear-gradient(90deg, #7b3fbf, #d4a8f5) !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label {
            background: rgba(243,234,255,0.7);
            border: 1px solid #d4b8f0;
            border-radius: 10px;
            padding: 0.4rem 0.8rem;
            margin: 0.2rem 0;
            display: block;
            transition: background 0.2s;
            color: #3d1a6e;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background: rgba(200,168,240,0.4);
        }

        .stTextInput > div > div > input {
            border: 1.5px solid #c9a8e8 !important;
            border-radius: 10px !important;
            background: rgba(255,255,255,0.8) !important;
        }

        .stSelectbox > div > div {
            border: 1.5px solid #c9a8e8 !important;
            border-radius: 10px !important;
            background: rgba(255,255,255,0.8) !important;
        }

        /* Decorative sticker pulse */
        @keyframes float {
            0%   { transform: translateY(0px) rotate(-3deg); }
            50%  { transform: translateY(-8px) rotate(3deg); }
            100% { transform: translateY(0px) rotate(-3deg); }
        }
        .sticker {
            animation: float 4s ease-in-out infinite;
            display: inline-block;
            font-size: 3.5rem;
            filter: drop-shadow(0 4px 8px rgba(100,50,180,0.18));
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────

def page_welcome() -> None:
    st.markdown(
        f"""
        <div class="title-hero">
            <div class="sticker">🌙</div>
            <h1>{APP_TITLE}</h1>
            <p>{APP_SUBTITLE}</p>
            <span class="badge">{CONDUCTOR}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="card">
            <h3>📖 About This Survey</h3>
            <p>
                This questionnaire examines how well your <strong>evening wind-down routine</strong>
                prepares you for the next study day. It covers five key areas:
                planning & organisation, mental relaxation, sleep preparation,
                physical & emotional state, and next-day readiness.
            </p>
            <p>
                Based on your responses you will receive a personalised readiness score and
                actionable feedback to help you improve your nightly routine.
            </p>
            <table style="width:100%;border-collapse:collapse;margin-top:0.8rem;">
                <tr>
                    <td style="padding:0.35rem 0.5rem;color:#6b2fa0;">📋 Questions</td>
                    <td style="padding:0.35rem 0.5rem;font-weight:700;color:#3d1a6e;">20 questions across 5 sections</td>
                </tr>
                <tr style="background:rgba(180,130,230,0.07);">
                    <td style="padding:0.35rem 0.5rem;color:#6b2fa0;">⏱️ Time</td>
                    <td style="padding:0.35rem 0.5rem;font-weight:700;color:#3d1a6e;">~{ESTIMATED_TIME:.0f} minutes</td>
                </tr>
                <tr>
                    <td style="padding:0.35rem 0.5rem;color:#6b2fa0;">🎯 Purpose</td>
                    <td style="padding:0.35rem 0.5rem;font-weight:700;color:#3d1a6e;">Evaluate evening habits & study readiness</td>
                </tr>
                <tr style="background:rgba(180,130,230,0.07);">
                    <td style="padding:0.35rem 0.5rem;color:#6b2fa0;">🎵 Music</td>
                    <td style="padding:0.35rem 0.5rem;font-weight:700;color:#3d1a6e;">Billie Eilish — wildflower plays during the survey</td>
                </tr>
                <tr>
                    <td style="padding:0.35rem 0.5rem;color:#6b2fa0;">🔒 Privacy</td>
                    <td style="padding:0.35rem 0.5rem;font-weight:700;color:#3d1a6e;">All responses are strictly confidential</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ Start Survey", use_container_width=True):
            st.session_state.page = "consent"
            st.rerun()
    with col2:
        if st.button("📂 Load Existing Results", use_container_width=True):
            st.session_state.page = "load"
            st.rerun()


def page_consent() -> None:
    st.markdown(
        '<div class="title-hero"><div class="sticker">🕯️</div><h1>Consent & Information</h1></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="card">
            <h3>🔒 Privacy & Confidentiality</h3>
            <p>All data you provide is kept strictly confidential and used solely for the
            purpose of this academic assessment. No personal information will be shared
            with third parties.</p>

            <h3>⏱️ Time Required</h3>
            <p>The survey contains <strong>20 questions</strong> and takes approximately
            <strong>{ESTIMATED_TIME:.0f} minutes</strong> to complete.</p>

            <h3>🤝 Voluntary Participation</h3>
            <p>Your participation is entirely voluntary. You may withdraw at any time.
            Proceeding past this page implies your informed consent.</p>

            <h3>🎵 Background Music</h3>
            <p><em>wildflower</em> by Billie Eilish will play softly in the background
            while you complete the survey. You can pause it at any time using the
            player that appears on each question page.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ I Agree — Continue", use_container_width=True):
            st.session_state.page = "user_info"
            st.rerun()
    with col2:
        if st.button("← Go Back", use_container_width=True):
            st.session_state.page = "welcome"
            st.rerun()


def page_user_info() -> None:
    st.markdown(
        '<div class="title-hero"><div class="sticker">🪷</div><h1>Your Details</h1></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)

    name = st.text_input(
        "Full Name (Surname and Given Name)",
        value=st.session_state.get("user_name", ""),
        placeholder="e.g. Karimova Fotima",
    )
    dob = st.text_input(
        "Date of Birth (DD/MM/YYYY)",
        value=st.session_state.get("user_dob", ""),
        placeholder="e.g. 22/09/2003",
    )
    sid = st.text_input(
        "Student ID (digits only)",
        value=st.session_state.get("user_sid", ""),
        placeholder="e.g. 20230042",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Begin Survey →", use_container_width=True):
        error_set: set = set()

        if not validate_name(name):
            error_set.add("Name may only contain letters, spaces, hyphens (-) and apostrophes (').")
        if not validate_dob(dob):
            error_set.add("Date of birth must be in DD/MM/YYYY format with realistic values.")
        if not validate_student_id(sid):
            error_set.add("Student ID must contain digits only.")

        if error_set:
            for err in error_set:
                st.error(err)
        else:
            st.session_state.user_name = name.strip()
            st.session_state.user_dob = dob.strip()
            st.session_state.user_sid = sid.strip()
            st.session_state.page = "survey"
            st.session_state.current_q = 0
            if "answers" not in st.session_state:
                st.session_state.answers = {}
            st.rerun()

    if st.button("← Back"):
        st.session_state.page = "consent"
        st.rerun()


def page_survey() -> None:
    q_idx: int = st.session_state.get("current_q", 0)
    answers: dict = st.session_state.get("answers", {})

    # Progress
    progress: float = q_idx / TOTAL_QUESTIONS
    st.markdown(
        f'<p class="progress-label">Question {q_idx + 1} of {TOTAL_QUESTIONS}</p>',
        unsafe_allow_html=True,
    )
    st.progress(progress)

    # Music player (autoplay)
    st.markdown("---")
    render_music_player()
    st.markdown("---")

    question: dict = QUESTIONS[q_idx]
    section_name: str = SECTIONS[question["section"]]
    option_labels: list = [opt[0] for opt in ANSWER_OPTIONS]
    option_scores: list = [opt[1] for opt in ANSWER_OPTIONS]

    default_idx: int = 0
    if q_idx in answers:
        saved: int = answers[q_idx]
        for i, sc in enumerate(option_scores):
            if sc == saved:
                default_idx = i
                break

    st.markdown(
        f'<div class="card">'
        f'<span class="section-tag">{section_name}</span>'
        f'<h3 style="margin-top:0.5rem;">{question["text"]}</h3>',
        unsafe_allow_html=True,
    )

    chosen_label = st.radio(
        "Select your answer:",
        option_labels,
        index=default_idx,
        key=f"q_{q_idx}",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    chosen_score_val: int = option_scores[option_labels.index(chosen_label)]
    answers[q_idx] = chosen_score_val
    st.session_state.answers = answers

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if q_idx > 0:
            if st.button("← Previous"):
                st.session_state.current_q = q_idx - 1
                st.rerun()
    with col3:
        if q_idx < TOTAL_QUESTIONS - 1:
            if st.button("Next →"):
                st.session_state.current_q = q_idx + 1
                st.rerun()
        else:
            if st.button("✅ Submit"):
                st.session_state.page = "results"
                st.rerun()


def page_results() -> None:
    answers: dict = st.session_state.get("answers", {})
    user_info: dict = {
        "name": st.session_state.get("user_name", ""),
        "dob":  st.session_state.get("user_dob", ""),
        "sid":  st.session_state.get("user_sid", ""),
    }

    score: int = compute_score(answers)
    state: dict = get_psychological_state(score)

    st.markdown(
        '<div class="title-hero"><div class="sticker">🌠</div><h1>Your Results</h1></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="card">
            <p><strong>Name:</strong> {user_info['name']}</p>
            <p><strong>Date of Birth:</strong> {user_info['dob']}</p>
            <p><strong>Student ID:</strong> {user_info['sid']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="card" style="text-align:center;background:linear-gradient(135deg,rgba(240,225,255,0.9),rgba(220,196,252,0.9));">
            <p style="color:#7048a8;font-weight:600;margin-bottom:0.4rem;">Total Score</p>
            <span class="score-chip">{score} / {MAX_SCORE}</span>
            <h2 style="margin-top:1rem;">{state.get('label','')}</h2>
            <p style="color:#3d1a6e;">{state.get('description','')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Score scale
    with st.expander("📊 Full Scoring Scale"):
        scale_data: list = [
            ("0–20",  "🌟 Excellent Routine",   "Outstanding evening habits and very high next-day readiness."),
            ("21–40", "✅ Good Habits",          "Solid routine with minor areas to improve."),
            ("41–60", "⚠️ Moderate Routine",    "Needs more structure — add a wind-down checklist."),
            ("61–80", "🔴 Low Readiness",        "Poor evening habits affecting daily performance."),
            ("81–100","🆘 Very Poor Routine",    "Immediate improvement needed — consider professional support."),
        ]
        for rng, lbl, desc in scale_data:
            here: str = "  ◀ You are here" if lbl == state.get("label", "") else ""
            st.markdown(f"**{rng} — {lbl}**{here}")
            st.caption(desc)

    # Section breakdown
    with st.expander("📋 Score Breakdown by Section"):
        section_scores: dict = {}
        for i, q in enumerate(QUESTIONS):
            sec: int = q["section"]
            if sec not in section_scores:
                section_scores[sec] = 0
            if i in answers:
                section_scores[sec] += answers[i]
        for sec_idx, sec_name in enumerate(SECTIONS):
            sec_score: int = section_scores.get(sec_idx, 0)
            st.markdown(f"**{sec_name}** — {sec_score} pts")

    # Save
    st.markdown("---")
    st.subheader("💾 Save Your Results")

    save_format: str = st.selectbox(
        "Choose file format:",
        ["JSON", "CSV", "TXT"],
        key="save_format",
    )

    results_data: dict = build_results_dict(user_info, answers, score, state)

    if save_format == "JSON":
        file_content: str = results_to_json(results_data)
        mime: str = "application/json"
        filename: str = f"winddown_results_{user_info['sid']}.json"
    elif save_format == "CSV":
        file_content = results_to_csv(results_data)
        mime = "text/csv"
        filename = f"winddown_results_{user_info['sid']}.csv"
    else:
        file_content = results_to_txt(results_data)
        mime = "text/plain"
        filename = f"winddown_results_{user_info['sid']}.txt"

    st.download_button(
        label=f"⬇️ Download as {save_format}",
        data=file_content,
        file_name=filename,
        mime=mime,
        use_container_width=True,
    )

    if st.button("🔄 Start New Survey", use_container_width=True):
        for key in ["answers", "user_name", "user_dob", "user_sid", "current_q"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.page = "welcome"
        st.rerun()


def page_load() -> None:
    st.markdown(
        '<div class="title-hero"><div class="sticker">📁</div><h1>Load Existing Results</h1></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card"><p>Upload a previously saved results file (JSON, CSV, or TXT) to review your results.</p></div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Upload results file",
        type=["json", "csv", "txt"],
        key="upload_file",
    )

    if uploaded is not None:
        ext: str = uploaded.name.rsplit(".", 1)[-1].lower()
        content: str = uploaded.read().decode("utf-8")

        try:
            loaded: dict = load_results_from_file(content, ext)
        except Exception as e:
            st.error(f"Could not parse file: {e}")
            loaded = {}

        if loaded:
            st.success("File loaded successfully!")
            st.markdown(
                f"""
                <div class="card">
                    <p><strong>Name:</strong> {loaded.get('surname_name','—')}</p>
                    <p><strong>Date of Birth:</strong> {loaded.get('date_of_birth','—')}</p>
                    <p><strong>Student ID:</strong> {loaded.get('student_id','—')}</p>
                    <p><strong>Total Score:</strong> {loaded.get('total_score','—')} / {MAX_SCORE}</p>
                    <p><strong>Result:</strong> {loaded.get('result','—')}</p>
                    <p><strong>Assessment:</strong> {loaded.get('description','—')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.warning("File could not be read or has an unexpected format.")

    if st.button("← Back to Home"):
        st.session_state.page = "welcome"
        st.rerun()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🌙",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    apply_styles()

    if "page" not in st.session_state:
        st.session_state.page = "welcome"
    if "answers" not in st.session_state:
        st.session_state.answers = {}

    page: str = st.session_state.page

    if page == "welcome":
        page_welcome()
    elif page == "consent":
        page_consent()
    elif page == "user_info":
        page_user_info()
    elif page == "survey":
        page_survey()
    elif page == "results":
        page_results()
    elif page == "load":
        page_load()
    else:
        st.session_state.page = "welcome"
        st.rerun()


if __name__ == "__main__":
    main()
