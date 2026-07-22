# -*- coding: utf-8 -*-
from __future__ import annotations

import base64
import csv
import html
import json
import random
import re
import time
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image
from openai import OpenAI
import streamlit as st

_logo_raw = Image.open(Path(__file__).resolve().parent / "logoCropped.png").convert("RGBA")
_pad = 8
_favicon = Image.new("RGBA", (_logo_raw.width + _pad * 2, _logo_raw.height + _pad * 2), (0, 0, 0, 0))
_favicon.paste(_logo_raw, (_pad, _pad))
st.set_page_config(page_title="PhishGap", page_icon=_favicon, layout="wide")

GLOBAL_CSS = """
<style>
/* Force sidebar to LEFT side ALWAYS — overrides RTL on .stApp */
.stApp {
    direction: ltr !important;
}
section[data-testid="stSidebar"] {
    direction: ltr !important;
    left: 0 !important;
    right: auto !important;
}
section[data-testid="stSidebar"] > div {
    direction: ltr !important;
}
[data-testid="stSidebarCollapsedControl"] {
    left: 0.5rem !important;
    right: auto !important;
}
/* Only apply RTL to the main content block, not the whole app */
.block-container {
    direction: inherit;
}

/* Hide Streamlit default elements */
#MainMenu {visibility: visible;}
footer {visibility: hidden;}
header {visibility: visible;}

/* Primary Button Styling (targets standard st.button) */
.stButton > button {
    background-color: #0ea5e9 !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 12px 32px !important;
    border: none !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 4px rgba(14, 165, 233, 0.2) !important;
}

.stButton > button:hover {
    background-color: #0284c7 !important;
    box-shadow: 0 4px 6px rgba(14, 165, 233, 0.3) !important;
    transform: translateY(-1px) !important;
}

/* --- Premium Simulation Button Styling --- */
/* Phishing Button: Vibrant Red-Orange Gradient */
[data-testid="column"] button[aria-label*="Phishing"],
[data-testid="column"] button[aria-label*="تصيد"],
[data-testid="column"] button[aria-label*="פישינג"] {
    background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%) !important;
    color: white !important;
    font-weight: 800 !important;
    font-size: 1.15rem !important;
    border-radius: 14px !important;
    padding: 12px 24px !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(255, 65, 108, 0.35) !important;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    height: 60px !important;
    width: 100% !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

[data-testid="column"] button[aria-label*="Phishing"]:hover,
[data-testid="column"] button[aria-label*="تصيد"]:hover,
[data-testid="column"] button[aria-label*="פישינג"]:hover {
    transform: translateY(-5px) scale(1.02) !important;
    box-shadow: 0 12px 30px rgba(255, 65, 108, 0.5) !important;
    background: linear-gradient(135deg, #ff527b 0%, #ff5e41 100%) !important;
}

/* Legitimate Button: Vibrant Teal-Blue Gradient */
[data-testid="column"] button[aria-label*="Legitimate"],
[data-testid="column"] button[aria-label*="شرعي"],
[data-testid="column"] button[aria-label*="לגיטימי"] {
    background: linear-gradient(135deg, #00b09b 0%, #00d2ff 100%) !important;
    color: white !important;
    font-weight: 800 !important;
    font-size: 1.15rem !important;
    border-radius: 14px !important;
    padding: 12px 24px !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(0, 176, 155, 0.35) !important;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    height: 60px !important;
    width: 100% !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

[data-testid="column"] button[aria-label*="Legitimate"]:hover,
[data-testid="column"] button[aria-label*="شرعي"]:hover,
[data-testid="column"] button[aria-label*="לגיטימי"]:hover {
    transform: translateY(-5px) scale(1.02) !important;
    box-shadow: 0 12px 30px rgba(0, 176, 155, 0.5) !important;
    background: linear-gradient(135deg, #12c2ae 0%, #29e2ff 100%) !important;
}

[data-testid="column"] button:active {
    transform: scale(0.94) translateY(-1px) !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2) !important;
}

/* Force text styles for Streamlit inner elements */
[data-testid="column"] button[aria-label*="Phishing"] p,
[data-testid="column"] button[aria-label*="تصيد"] p,
[data-testid="column"] button[aria-label*="פישינג"] p,
[data-testid="column"] button[aria-label*="Legitimate"] p,
[data-testid="column"] button[aria-label*="شرعي"] p,
[data-testid="column"] button[aria-label*="לגיטימי"] p {
    font-weight: 800 !important;
    color: white !important;
    font-size: 1.15rem !important;
}

/* Card Styling */
.custom-card {
    background-color: white;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
}

/* Fade-in animation for simulation cards */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
    animation: fadeIn 0.4s ease-out forwards;
}

/* Recommendation card left border */
.rec-card {
    border-left: 4px solid #0ea5e9;
}

/* Placeholder always left-aligned (RTL pages shift it right otherwise) */
input::placeholder {
    text-align: left !important;
    direction: ltr !important;
}
textarea::placeholder {
    text-align: left !important;
    direction: ltr !important;
}

/* Hide "Press Enter to apply" label on all text inputs */
div[data-testid="InputInstructions"] {
    display: none !important;
}

/* Force Arial font for Hebrew text */
*:lang(he),
[dir="rtl"] {
    font-family: Arial, sans-serif !important;
}
</style>
"""

def render_progress_bar(current_step: int):
    steps = [
        t("step_registration"), t("step_questionnaire"), t("step_simulation"),
        t("step_results"), t("step_recommendations"), t("step_final_test"), t("step_report"),
    ]

    is_rtl = st.session_state.get("lang", "en") in ("ar", "he")
    stepper_dir = "rtl" if is_rtl else "ltr"
    # In RTL the connector line must go leftward (right: 50%), in LTR rightward (left: 50%)
    connector_pos = "right: 50%; left: auto;" if is_rtl else "left: 50%; right: auto;"
    gradient_dir = "270deg" if is_rtl else "90deg"

    html_out = f"""
    <style>
    .stepper-outer {{
        background: white;
        padding: 30px 20px 36px 20px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 40px;
        overflow-x: auto;
        overflow-y: clip;
        scrollbar-width: thin;
        direction: {stepper_dir} !important;
    }}
    .stepper-inner {{
        display: flex;
        flex-direction: row !important;
        direction: {stepper_dir} !important;
        justify-content: space-between;
        width: 100%;
        position: relative;
        padding: 0 10px;
    }}
    @media (max-width: 850px) {{
        .stepper-inner {{
            min-width: 800px;
        }}
    }}
    .step-item {{
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
    }}
    /* Horizontal connector line */
    .step-item:not(:last-child)::after {{
        content: '';
        position: absolute;
        top: 19px;
        {connector_pos}
        width: 100%;
        height: 3px;
        background: #f1f5f9;
        z-index: 1;
    }}
    .step-item.completed:not(:last-child)::after {{
        background: #dcfce7;
    }}
    .step-item.active-line:not(:last-child)::after {{
        background: linear-gradient({gradient_dir}, #16a34a, #e2e8f0);
    }}
    .step-circle {{
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #f8fafc;
        color: #94a3b8;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 14px;
        border: 3px solid white;
        box-shadow: 0 0 0 1px #e2e8f0;
        z-index: 2;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }}
    .step-item.active .step-circle {{
        background: #0ea5e9;
        color: white;
        box-shadow: 0 0 0 1px #0ea5e9, 0 0 15px rgba(14, 165, 233, 0.3);
        transform: scale(1.1);
    }}
    .step-item.completed .step-circle {{
        background: #16a34a;
        color: white;
        box-shadow: 0 0 0 1px #16a34a;
    }}
    .step-label {{
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
        text-align: center;
        white-space: nowrap;
        transition: all 0.3s ease;
    }}
    .step-item.active .step-label {{
        color: #0ea5e9;
        font-weight: 800;
        font-size: 14px;
    }}
    .step-item.completed .step-label {{
        color: #16a34a;
    }}
    </style>
    <div class="stepper-outer">
        <div class="stepper-inner">
    """

    for i, name in enumerate(steps):
        step_num = i + 1
        status_class = ""
        icon = str(step_num)

        if step_num < current_step:
            status_class = "completed"
            icon = "✓"
        elif step_num == current_step:
            status_class = "active"

        if step_num < current_step:
            status_class += " completed"

        html_out += f'<div class="step-item {status_class}">'
        html_out += f'<div class="step-circle">{icon}</div>'
        html_out += f'<div class="step-label">{name}</div>'
        html_out += '</div>'

    html_out += '</div></div>'
    st.markdown(html_out, unsafe_allow_html=True)


QUESTIONS = {
    "DB": [
        {
            "id": "DB1",
            "en": "I constantly switch between email and platforms like Moodle and WhatsApp, which reduces my focus when handling messages.",
            "ar": "أتنقل باستمرار بين البريد الإلكتروني ومنصات مثل Moodle والواتساب، مما يقلّل من تركيزي أثناء التعامل مع الرسائل",
            "he": "אני עובר/ת כל הזמן בין הדואר האלקטרוני ופלטפורמות כגון מודל והוואטסאפ, מה שמפחית את הריכוז שלי בעת טיפול בהודעות",
        },
        {
            "id": "DB4",
            "en": "I click on links in messages that carry the university logo without checking the sender's address.",
            "ar": "أضغط على الروابط في الرسائل التي تحمل شعار الجامعة دون التحقق من عنوان المرسل",
            "he": "אני לוחץ/ת על קישורים בהודעות הנושאות את סמל האוניברסיטה מבלי לבדוק את כתובת השולח",
        },
        {
            "id": "DB6",
            "en": "During academic pressure, I read messages quickly without checking the details.",
            "ar": "وقت الضغط الدراسي، أقرأ الرسائل بسرعة بدون أن أدقق في التفاصيل",
            "he": "בזמן לחץ לימודי, אני קורא/ת הודעות במהירות מבלי לבדוק את הפרטים",
        },
        {
            "id": "DB7",
            "en": "I don't check messages that arrive in my inbox because I rely on the spam filter.",
            "ar": "لا أتحقق من الرسائل التي تصل لصندوق الوارد لأنني أعتمد على فلتر البريد المزعج (spam)",
            "he": "אני לא בודק/ת הודעות שמגיעות לתיבת הדואר הנכנס כי אני סומך/ת על מסנן הספאם",
        },
    ],
    "AW": [
        {
            "id": "AW1",
            "en": "I can easily distinguish between real university messages and fake ones, because it's impossible to convincingly imitate the university's style.",
            "ar": "أستطيع بسهولة التمييز بين رسائل الجامعة الحقيقية وأي رسالة مزيّفة، فمن المستحيل تقليد أسلوب الجامعة بشكل مُقنع",
            "he": "אני יכול/ה להבחין בקלות בין הודעות אמיתיות של האוניברסיטה לבין הודעות מזויפות, כי אי אפשר לחקות את הסגנון של האוניברסיטה בצורה משכנעת",
        },
        {
            "id": "AW5",
            "en": "As long as I have good knowledge of digital security, I am completely protected from falling for any phishing attempt.",
            "ar": "ما دمتُ أمتلك معرفة جيدة بالأمن الرقمي، فأنا محصّن تماماً من الوقوع في أي محاولة تصيّد",
            "he": "כל עוד יש לי ידע טוב באבטחה דיגיטלית, אני מוגן/ת לחלוטין מנפילה בכל ניסיון פישינג",
        },
        {
            "id": "AW6",
            "en": "I can always detect phishing messages through spelling and language errors, because no fake message is free of errors.",
            "ar": "أستطيع دائماً اكتشاف رسائل التصيّد من خلال الأخطاء الإملائية واللغوية فيها، فلا توجد رسالة مزيفة خالية من الأخطاء",
            "he": "אני תמיד יכול/ה לזהות הודעות פישינג דרך שגיאות כתיב ושפה, כי אין הודעה מזויפת שהיא ללא שגיאות",
        },
        {
            "id": "AW10",
            "en": "I don't think students are specifically targeted by cyber attackers; there are other groups that are much more exposed.",
            "ar": "لا أعتقد أن الطلاب مستهدفون بشكل خاص من قبل المهاجمين الإلكترونيين، فهناك فئات أخرى أكثر عُرضة منهم بكثير",
            "he": "אני לא חושב/ת שסטודנטים מוּכּוָנִים במיוחד על ידי תוקפי סייבר, יש קבוצות אחרות שהרבה יותר חשופות מהם",
        },
    ],
    "SV": [
        {
            "id": "SV2",
            "en": "When I receive a message mentioning an academic 'penalty' or 'fine', I feel fear and act quickly without thinking.",
            "ar": "عندما تصلني رسالة تذكر 'عقوبة' أو 'غرامة' أكاديمية، أشعر بالخوف وأتصرف بسرعة دون تفكير",
            "he": "כשמגיעה לי הודעה המזכירה 'עונש' או 'קנס' אקדמי, אני מרגיש/ה פחד ופועל/ת במהירות ללא חשיבה",
        },
        {
            "id": "SV6",
            "en": "I act much faster when the message contains my name or personal information about me.",
            "ar": "أتصرف بسرعة أكبر عندما تحتوي الرسالة على اسمي أو معلومات شخصية عني",
            "he": "אני פועל/ת במהירות רבה יותר כאשר ההודעה מכילה את שמי או מידע אישי עלי",
        },
        {
            "id": "SV8",
            "en": "When I am very happy, my caution decreases when opening messages.",
            "ar": "عندما أكون سعيداً/سعيدة جداً، يقلّ حذري عند فتح الرسائل",
            "he": "כשאני שמח/ה מאוד, הזהירות שלי פוחתת בעת פתיחת הודעות",
        },
        {
            "id": "SV9",
            "en": "When I am sad or worried, my judgment about suspicious messages becomes less accurate.",
            "ar": "عندما أكون حزيناً/حزينة أو قلقاً/قلقة، يصبح حكمي على الرسائل المشبوهة أقل دقة",
            "he": "כשאני עצוב/ה או מודאג/ת, השיפוט שלי לגבי הודעות חשודות הופך פחות מדויק",
        },
    ],
}


# Three sets of emails — Sim 1 randomly picks Set A or Set C each session; Sim 2 always uses Set B.
_SIM1_SET_A = ["AW_01", "AW_04", "DB_01", "DB_04", "SV_01", "SV_04"]
_SIM1_SET_C = ["AW_03", "AW_06", "DB_03", "DB_06", "SV_03", "SV_06"]
_SIM2_IDS = ["AW_02", "AW_05", "DB_02", "DB_05", "SV_02", "SV_05"]

GPT_SYSTEM_PROMPT_SIM1 = """You are an educational recommendation system that helps
students improve resilience against phishing.
Write in simple, clear language.
Do not invent results that are not in the data.
Use these rules:
1. Error type decides what to teach.
2. Gap type decides how to teach.
3. The timer is only a supporting behavioral indicator.
4. If the gap is large, use direct but respectful confrontation.
5. If the gap is medium, use gentle warning.
6. If aligned, use support and targeted practice.
7. If better than expected, reinforce confidence.

Write a Markdown report with:
- Personal diagnosis (2-3 sentences, address student by name)
- Why the errors happened (reference specific messages)
- Three practical recommendations
  (content from error type, tone from gap type)
- One actionable tip per recommendation
- Short encouraging closing

IMPORTANT LANGUAGE RULES:
- NEVER use technical codes like AW, DB, SV, AW_04, DB_01, etc.
- Instead of 'AW' say 'security awareness deficit' or 'ability to recognize fake emails'
- Instead of 'DB' say 'risky digital behavior' or 'how carefully you handle emails'
- Instead of 'SV' say 'emotional & situational vulnerability' or 'how pressure affects your decisions'
- Instead of any message ID, describe the email by its subject line or content
- Write as if you are talking to a friend — simple, warm, practical
- Do NOT use any internal system terminology
- The student should understand everything without any technical background

CRITICAL — FORBIDDEN TERMS (never use these):
- NEVER write 'AW', 'DB', 'SV' anywhere in your response
- NEVER write message IDs like 'AW_01', 'DB_03', 'SV_04'
- NEVER write 'gap type: large' or 'gap type: medium'
- NEVER write 'aligned', 'better than expected' as labels
- NEVER use the word 'dimension' or 'ממד'

USE INSTEAD:
- Instead of 'AW' write: 'זיהוי הודעות מזויפות' (HE) / 'التعرف على الرسائل المزيفة' (AR) / 'security awareness deficit' (EN)
- Instead of 'DB' write: 'התנהגות דיגיטלית זהירה' (HE) / 'السلوك الرقمي الحذر' (AR) / 'risky digital behavior' (EN)
- Instead of 'SV' write: 'עמידות בפני לחץ רגשי' (HE) / 'مقاومة الضغط العاطفي' (AR) / 'emotional & situational vulnerability' (EN)
- Instead of message IDs, describe the email: 'the overdue library book email' / 'the Zoom meeting email' / 'the scholarship email'
- Instead of 'large gap', say: 'there is a significant difference between your confidence and your actual performance'
- Instead of 'medium gap', say: 'your performance was slightly different from what you expected'

This is MANDATORY — if you use ANY technical code, the response is considered FAILED.
"""

_URL_RE = re.compile(r"https?://[^\s<>]+")


def _md_to_html(text: str) -> str:
    """Convert basic GPT markdown to HTML for rendering inside an HTML div."""
    lines = text.split('\n')
    result = []
    in_ul = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('### '):
            if in_ul: result.append('</ul>'); in_ul = False
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped[4:])
            result.append(f'<h3>{content}</h3>')
        elif stripped.startswith('## '):
            if in_ul: result.append('</ul>'); in_ul = False
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped[3:])
            result.append(f'<h2>{content}</h2>')
        elif stripped.startswith('# '):
            if in_ul: result.append('</ul>'); in_ul = False
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped[2:])
            result.append(f'<h1>{content}</h1>')
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_ul: result.append('<ul>'); in_ul = True
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped[2:])
            result.append(f'<li>{content}</li>')
        elif stripped == '':
            if in_ul: result.append('</ul>'); in_ul = False
        else:
            if in_ul: result.append('</ul>'); in_ul = False
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            result.append(f'<p>{content}</p>')
    if in_ul:
        result.append('</ul>')
    return '\n'.join(result)


def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def _load_messages_json() -> list[dict]:
    path = Path(__file__).resolve().parent / "messages.json"
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    
    lang = st.session_state.get("lang", "en")
    localized_data = []
    for msg in data:
        loc_msg = {k: v for k, v in msg.items() if k not in ("en", "ar", "he")}
        lang_data = msg.get(lang, msg.get("en", {}))
        loc_msg.update(lang_data)
        localized_data.append(loc_msg)
    return localized_data


def select_sim1_version1_messages(all_messages: list[dict]) -> list[dict]:
    import random
    by_id = {m["id"]: m for m in all_messages}
    chosen_set = random.choice([_SIM1_SET_A, _SIM1_SET_C])
    missing = [i for i in chosen_set if i not in by_id]
    if missing:
        raise KeyError(f"messages.json missing required ids: {missing}")
    msgs = [by_id[i] for i in chosen_set]
    random.shuffle(msgs)
    return msgs


def select_sim2_version2_messages(all_messages: list[dict]) -> list[dict]:
    import random
    by_id = {m["id"]: m for m in all_messages}
    missing = [i for i in _SIM2_IDS if i not in by_id]
    if missing:
        raise KeyError(f"messages.json missing required ids: {missing}")
    msgs = [by_id[i] for i in _SIM2_IDS]
    random.shuffle(msgs)
    return msgs


def compute_sim_score(trials: list[dict]) -> int:
    """Count correct answers in a simulation's trials."""
    return sum(1 for t in trials if not t["incorrect"])


def extract_display_urls(body: str) -> list[str]:
    urls = list(dict.fromkeys(_URL_RE.findall(body)))
    if not urls:
        for m in re.finditer(r"\b(?:https?://)?(?:[\w.-]+\.)*university\.ac\.il(?:/[\w\-./]*)?", body, re.I):
            s = m.group(0).strip(",.;)")
            if s and s not in urls:
                urls.append(s)
    return urls


def timer_penalty_for_response(seconds: float, wrong: bool) -> float:
    if not wrong:
        return 0.0
    if seconds < 5:
        return 0.20
    if seconds <= 15:
        return 0.10
    return 0.0


def gap_type_section_63(gap: float) -> str:
    """Section 6.3 thresholds (matches design-doc Python pseudocode)."""
    if gap >= 0.50:
        return "large"
    if gap >= 0.25:
        return "medium"
    if gap >= -0.24:
        return "aligned"
    if gap >= -0.49:
        return "better"
    return "much_better"


def aggregate_sim1_dimension_metrics(
    trials: list[dict],
    self_report_risk: dict[str, float],
) -> tuple[
    dict[str, float],
    dict[str, float],
    dict[str, float],
    dict[str, float],
    dict[str, str],
]:
    error_rates: dict[str, float] = {}
    avg_timer_penalties: dict[str, float] = {}
    actual_risks: dict[str, float] = {}
    gaps: dict[str, float] = {}
    gap_types: dict[str, str] = {}

    for dim in ("AW", "DB", "SV"):
        trials_d = [t for t in trials if t["dimension"] == dim]
        n = len(trials_d)
        errors = sum(1 for t in trials_d if t["incorrect"])
        error_rate = errors / n if n else 0.0

        penalties_wrong_only = [t["timer_penalty"] for t in trials_d if t["incorrect"]]
        avg_pen = (
            sum(penalties_wrong_only) / len(penalties_wrong_only) if penalties_wrong_only else 0.0
        )

        actual = min(1.0, error_rate + avg_pen)
        sr = float(self_report_risk.get(dim, 0.0))
        gap = round(actual - sr, 2)

        error_rates[dim] = round(error_rate, 4)
        avg_timer_penalties[dim] = round(avg_pen, 4)
        actual_risks[dim] = round(actual, 4)
        gaps[dim] = gap
        gap_types[dim] = gap_type_section_63(gap)

    return error_rates, avg_timer_penalties, actual_risks, gaps, gap_types


def _build_sim1_errors_for_gpt(
    trials: list[dict], messages_by_id: dict[str, dict]
) -> list[dict]:
    out: list[dict] = []
    for t in trials:
        if not t.get("incorrect"):
            continue
        mid = str(t.get("email_id", ""))
        meta = messages_by_id.get(mid, {})
        out.append(
            {
                "message_id": mid,
                "dimension": t.get("dimension", ""),
                "tactic": t.get("tactic", ""),
                "subject": meta.get("subject", ""),
                "student_answer": t.get("user_answer"),
                "correct_answer": t.get("correct"),
                "response_time_seconds": t.get("elapsed_seconds"),
                "timer_penalty_added": t.get("timer_penalty"),
                "teach": meta.get("teach", ""),
            }
        )
    return out


def _build_sim1_gpt_user_content() -> str:
    """JSON payload for GPT; all numbers from session_state (Python-computed)."""
    name = st.session_state.get("student_name", "")
    trials = st.session_state.get("sim1_trials") or []
    messages_by_id = {m["id"]: m for m in _load_messages_json()}

    payload = {
        "student_name": name,
        "questionnaire_scores": {
            "AW": float(st.session_state["scores"]["AW"]),
            "DB": float(st.session_state["scores"]["DB"]),
            "SV": float(st.session_state["scores"]["SV"]),
        },
        "self_report_risk": {
            k: float(st.session_state["self_report_risk"][k])
            for k in ("AW", "DB", "SV")
        },
        "actual_risk_simulation1": {
            k: float(st.session_state["sim1_actual_risk"][k]) for k in ("AW", "DB", "SV")
        },
        "gap": {k: float(st.session_state["sim1_gap"][k]) for k in ("AW", "DB", "SV")},
        "gap_type": {k: st.session_state["sim1_gap_type"][k] for k in ("AW", "DB", "SV")},
        "error_rate_simulation1": {
            k: float(st.session_state["sim1_error_rate"][k]) for k in ("AW", "DB", "SV")
        },
        "avg_timer_penalty_when_wrong_simulation1": {
            k: float(st.session_state["sim1_avg_timer_penalty"][k]) for k in ("AW", "DB", "SV")
        },
        "errors_detail": _build_sim1_errors_for_gpt(trials, messages_by_id),
    }
    intro = (
        "Use only the structured data below. Actual risk includes timer penalties as shown. "
        "If errors_detail is empty, the student had no classification errors.\n"
        "REMINDER: Do NOT use codes like AW, DB, SV, AW_04, DB_01, etc. "
        "Describe everything in plain human language.\n"
    )
    return intro + json.dumps(payload, indent=2, ensure_ascii=False)


# ── Avatar background palette (soft pastels keyed by first letter) ─────────
_AVATAR_COLORS = {
    "A": ("#dbeafe", "#1e40af"), "B": ("#fce7f3", "#9d174d"),
    "C": ("#d1fae5", "#065f46"), "D": ("#fef3c7", "#92400e"),
    "E": ("#ede9fe", "#5b21b6"), "F": ("#fee2e2", "#991b1b"),
    "G": ("#ccfbf1", "#134e4a"), "H": ("#fce7f3", "#831843"),
    "I": ("#e0e7ff", "#3730a3"), "J": ("#dbeafe", "#1e3a8a"),
    "K": ("#fef9c3", "#713f12"), "L": ("#d1fae5", "#064e3b"),
    "M": ("#ede9fe", "#4c1d95"), "N": ("#fff7ed", "#9a3412"),
    "O": ("#f0fdf4", "#166534"), "P": ("#fdf2f8", "#9d174d"),
    "Q": ("#ecfdf5", "#047857"), "R": ("#fef2f2", "#b91c1c"),
    "S": ("#dbeafe", "#1e40af"), "T": ("#f5f3ff", "#6d28d9"),
    "U": ("#e0f2fe", "#0369a1"), "V": ("#fce7f3", "#be185d"),
    "W": ("#ecfeff", "#155e75"), "X": ("#fef3c7", "#b45309"),
    "Y": ("#fefce8", "#854d0e"), "Z": ("#f0fdfa", "#115e59"),
}
_DEFAULT_AVATAR = ("#e5e7eb", "#374151")


def _random_time_stamp(seed: str) -> str:
    """Deterministic-per-email random morning/afternoon timestamp."""
    rng = random.Random(seed)
    hour = rng.choice([7, 8, 9, 10, 11, 12, 1, 2, 3, 4])
    minute = rng.randint(0, 59)
    ampm = "AM" if hour >= 7 and seed.__hash__() % 2 == 0 else "PM"
    if hour >= 7 and hour <= 11:
        ampm = "AM"
    else:
        ampm = "PM"
    return f"{hour}:{minute:02d} {ampm}"


def _format_email_address(addr: str) -> str:
    """Return escaped HTML for the email address — identical styling for all."""
    return html.escape(addr)


def _linkify_body(body_text: str) -> str:
    """Escape body and turn raw URLs into styled (non-clickable) blue links.
    Matches both https:// URLs and bare domain URLs (e.g. library.university.ac.il/path)
    so that phishing and legitimate emails look identical."""
    safe = html.escape(body_text)
    # First: style full https:// URLs as blue underlined spans
    safe = re.sub(
        r"(https?://[^\s<>]+)",
        r'<span style="color:#2563eb; text-decoration:underline; '
        r'cursor:default; word-break:break-all;">\1</span>',
        safe,
    )
    # Second: style bare domain URLs (not already inside a span) — e.g. library.university.ac.il/path
    safe = re.sub(
        r'(?<![">])\b([a-zA-Z][\w.-]*\.[a-zA-Z]{2,}(?:/[^\s<>]*))',
        r'<span style="color:#2563eb; text-decoration:underline; '
        r'cursor:default; word-break:break-all;">\1</span>',
        safe,
    )
    return safe.replace("\n", "<br>")


def render_email(msg: dict) -> str:
    """Return an HTML string that looks like a real webmail message card."""
    from_name = msg["from_name"]
    from_addr = msg["from_email"]
    subject = msg["subject"]
    body = msg["body"]

    # Avatar
    initial = from_name[0].upper() if from_name else "?"
    bg, fg = _AVATAR_COLORS.get(initial, _DEFAULT_AVATAR)

    # Timestamp (deterministic per email id so it doesn't change on rerun)
    ts = _random_time_stamp(msg.get("id", from_addr))

    # Email address — identical styling for all emails
    addr_html = _format_email_address(from_addr)

    # Body with styled links
    body_html = _linkify_body(body)

    # Signature / footer — extract last line if it looks like a sign-off
    lines = body.strip().split("\n")
    footer_html = ""
    if len(lines) >= 2:
        last = lines[-1].strip()
        # Heuristic: short line at the end is likely a sign-off
        if len(last) < 80 and not last.startswith("http"):
            # Separate footer visually
            body_without_footer = "\n".join(lines[:-1])
            body_html = _linkify_body(body_without_footer)
            footer_html = (
                f'<div style="margin-top:14px; padding-top:10px; '
                f'border-top:1px solid #eee; font-size:11px; color:#999; '
                f'line-height:1.5;">{html.escape(last)}</div>'
            )

    # Font selection based on language
    email_font = "Arial, sans-serif" if st.session_state.get("lang") == "he" else "'Segoe UI', Roboto, Arial, sans-serif"

    return f"""
<div style="max-width:520px; margin:0 auto 16px; background:#fff;
     border:1px solid #e0e0e0; border-radius:8px; overflow:hidden;
     font-family:{email_font};
     box-shadow:0 1px 3px rgba(0,0,0,0.08);">
  <!-- ── header ── -->
  <div style="padding:12px 16px; border-bottom:1px solid #eee;
       background:#f8f9fa;">
    <div style="display:flex; align-items:center; gap:10px;">
      <div style="width:36px; height:36px; border-radius:50%;
           background:{bg}; display:flex; align-items:center;
           justify-content:center; font-weight:600;
           font-size:15px; color:{fg}; flex-shrink:0;">{initial}</div>
      <div style="flex:1; min-width:0;">
        <div style="font-size:13px; font-weight:600; color:#202124;
             white-space:nowrap; overflow:hidden;
             text-overflow:ellipsis;">{html.escape(from_name)}</div>
        <div style="font-size:11px; color:#5f6368;
             white-space:nowrap; overflow:hidden;
             text-overflow:ellipsis;">{addr_html}</div>
      </div>
      <div style="font-size:11px; color:#999; white-space:nowrap;
           flex-shrink:0;">{ts}</div>
    </div>
  </div>
  <!-- ── body ── -->
  <div style="padding:16px;">
    <div style="font-size:14px; font-weight:600; color:#202124;
         margin-bottom:12px;">{html.escape(subject)}</div>
    <div style="font-size:13px; color:#3c4043;
         line-height:1.8;">{body_html}</div>
    {footer_html}
  </div>
</div>
"""


# ── Translations scaffolding ────────────────────────────────────────────────
TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # Hero
        "hero_subtitle": "Use AI to build unbreakable resilience against dangerous messages",
        "hero_desc": "Discover the gap between what you think you know about phishing and how you actually perform. Get personalized AI recommendations to strengthen your defenses.",
        "btn_start": "Start Phishing Assessment",
        "hero_info": "Takes only 20 minutes • 100% anonymous • Free",
        # How It Works
        "how_title": "How It Works",
        "how1_title": "📋 Self-Assessment",
        "how1_desc": "Answer 12 questions about your security awareness, digital behavior, and emotional vulnerability.",
        "how2_title": "📧 Phishing Simulation",
        "how2_desc": "Face 6 realistic email scenarios and try to identify which ones are phishing attacks.",
        "how3_title": "🤖 AI Analysis",
        "how3_desc": "Get a personalized report showing exactly where your blind spots are and how to fix them.",
        # Stats
        "stats_title": "Platform Statistics",
        "stat_scenarios": "Realistic scenarios",
        "stat_recommendations": "AI recommendations",
        "stat_resilience": "To improve resilience",
        # Discover
        "discover_title": "What You'll Discover",
        "discover1": "Your real awareness level vs what you think",
        "discover2": "How fast decisions affect your vulnerability",
        "discover3": "Which phishing tactics fool you most",
        "discover4": "Personalized strategies to protect yourself",
        # CTA / Footer
        "cta_title": "Ready to find out how phishing-proof you really are?",
        "btn_begin": "Begin Now",
        "footer_text": "Built as a graduation project at Azrieli College of Engineering - Jerusalem",
        # Registration (Step 1)
        "reg_title": "🛡️ Phishing Resilience Assessment",
        "reg_subtitle": "Test and improve your ability to detect phishing attacks",
        "reg_card_title": "Registration",
        "reg_name": "Full Name *",
        "reg_email": "Email Address *",
        "reg_major": "Major/Department",
        "reg_year": "Year of Study",
        "reg_major_industrial": "Industrial Engineering",
        "reg_major_software": "Software Engineering",
        "reg_major_electrical": "Electrical Engineering",
        "reg_major_civil": "Civil Engineering",
        "reg_major_mechanical": "Mechanical Engineering",
        "reg_major_other": "Other",
        "reg_year_1": "1st Year",
        "reg_year_2": "2nd Year",
        "reg_year_3": "3rd Year",
        "reg_year_4": "4th Year",
        "btn_begin_assessment": "Begin Assessment",
        "reg_note": "This assessment takes approximately 20 minutes",
        "reg_warning": "Please provide both your name and email address to continue.",
        "reg_name_missing": "Please enter your full name.",
        "reg_email_missing": "Please enter your email address.",
        "reg_email_no_at": "Email address must contain @ (e.g. name@gmail.com).",
        "reg_email_multi_at": "Email address can only contain one @.",
        "reg_email_no_user": "Please enter something before @ (e.g. yourname@gmail.com).",
        "reg_email_no_domain": "Please enter a domain after @ (e.g. name@gmail.com).",
        "reg_email_domain_invalid": "Email domain is not valid — please use a proper domain (e.g. gmail.com, outlook.com, hotmail.com, yahoo.com, icloud.com).",
        # Questionnaire (Step 2)
        "q_title": "Questionnaire",
        "q_subtitle": "Rate each statement according to what you think about yourself.",
        "dim_AW": "Security Awareness",
        "dim_DB": "Digital Behavior",
        "dim_SV": "Situational Vulnerability",
        "slider_1": "1 - Strongly Disagree",
        "slider_2": "2",
        "slider_3": "3",
        "slider_4": "4",
        "slider_5": "5",
        "slider_6": "6 - Strongly Agree",
        "btn_submit_q": "Submit Questionnaire",
        # Progress bar step names
        "step_registration": "Registration",
        "step_questionnaire": "Questionnaire",
        "step_simulation": "Simulation",
        "step_results": "Results",
        "step_recommendations": "Recommendations",
        "step_final_test": "Final Test",
        "step_report": "Report",
        # Simulation (Step 3 & 6)
        "sim1_title": "Simulation",
        "sim1_subtitle": "Classify each email. Your response time is measured in the background.",
        "sim2_title": "Simulation 2",
        "sim2_subtitle": "Apply what you learned. Different messages, same tactics. Timer runs in the background.",
        "sim_scenario": "Scenario {n} of {total}",
        "sim_question": "Is this message phishing or legitimate?",
        "btn_phishing": "🎣 Phishing",
        "btn_legitimate": "✅ Legitimate",
        # Results (Step 4)
        "res_title": "Results Dashboard",
        "res_error_incomplete": "Complete Simulation 1 first.",
        "res_score_summary": "Score summary",
        "res_your_score": "Your Score",
        "res_correct": "Correct",
        "res_mistakes": "Mistakes",
        "res_breakdown_expander": "📋 Message-by-message breakdown",
        "res_tactic": "Tactic",
        "res_badge_wrong": "Wrong",
        "res_badge_correct": "Correct",
        "res_your_answer": "Your answer",
        "res_correct_label": "Correct",
        "res_why_was": "Why this was {answer}:",
        "res_tip": "💡 Tip:",
        "res_gap_analysis": "Gap analysis",
        "dim_label_AW": "Security Awareness Deficit",
        "dim_label_DB": "Risky Digital Behavior",
        "dim_label_SV": "Emotional & Situational Vulnerability",
        "res_self_report_risk": "Self-report risk",
        "res_actual_risk": "Actual risk",
        "res_gap": "Gap",
        "gap_large_label": "Large gap",
        "gap_large_desc": "You thought you were safe, but your performance shows otherwise.",
        "gap_medium_label": "Medium gap",
        "gap_medium_desc": "There is a noticeable gap between your perception and actual behavior.",
        "gap_aligned_label": "Aligned",
        "gap_aligned_desc": "Your self-assessment matches your actual behavior.",
        "gap_better_label": "Better than expected",
        "gap_better_desc": "You performed better than you expected!",
        "gap_much_better_label": "Much better",
        "gap_much_better_desc": "You significantly outperformed your self-assessment.",
        "res_behavioral_insights": "Behavioral insights",
        "res_avg_response_time": "Average response time",
        "res_fastest_response": "Fastest response",
        "res_message_prefix": "Message",
        "res_quick_wrong_warning": "⚡ You made quick decisions (under 5 seconds) on some messages you got wrong — slowing down could help you catch important details.",
        "res_btn_recommendations": "Get Personalized Recommendations →",
        "res_answer_phishing": "phishing",
        "res_answer_legitimate": "legitimate",
        # Recommendations (Step 5)
        "rec_title": "Personalized recommendation",
        "rec_error_incomplete": "Complete Simulation 1 first to unlock recommendations.",
        "rec_error_api_key": "Add **OPENAI_API_KEY** to `.streamlit/secrets.toml`.",
        "rec_btn_retry": "Retry recommendation request",
        "rec_spinner": "Generating your recommendation...",
        "rec_btn_continue": "Continue to Simulation 2",
        # Final Report (Step 7)
        "rep_title": "Final Report",
        "rep_error_incomplete": "Complete Simulation 2 first.",
        "rep_great_job": "Great job, {name}!",
        "rep_completed": "You have completed all sections of the Phishing Resilience System.",
        "rep_performance": "Performance comparison",
        "rep_sim1": "Simulation 1",
        "rep_sim2": "Simulation 2",
        "rep_per_dim": "Per-dimension gap analysis",
        "rep_satisfaction": "Satisfaction survey",
        "sat_q_0": "Were the recommendations clear and understandable?",
        "sat_q_1": "Did you feel the recommendations were personalized to you?",
        "sat_q_2": "Did you learn something new you didn't know before?",
        "sat_q_3": "Would you recommend this system to other students?",
        "sat_open_label": "Any additional comments or suggestions? (optional)",
        "sat_open_placeholder": "Share your thoughts here...",
        "sat_slider_1": "1 - Not at all",
        "sat_slider_2": "2",
        "sat_slider_3": "3",
        "sat_slider_4": "4",
        "sat_slider_5": "5 - Very much",
        "btn_submit_save": "Submit & save results",
        "rep_success": "Results saved successfully!",
    },
    "ar": {
        # Hero
        "hero_subtitle": "استخدم الذكاء الاصطناعي لبناء مرونة لا تُكسر ضد الرسائل الخطرة",
        "hero_desc": "اكتشف الفجوة بين ما تعتقد أنك تعرفه عن التصيد الاحتيالي وأدائك الفعلي. احصل على توصيات مخصصة بالذكاء الاصطناعي لتعزيز دفاعاتك.",
        "btn_start": "ابدأ تقييم التصيد الاحتيالي",
        "hero_info": "يستغرق 20 دقيقة فقط • مجهول 100% • مجاني",
        # How It Works
        "how_title": "كيف يعمل",
        "how1_title": "📋 التقييم الذاتي",
        "how1_desc": "أجب عن 12 سؤالاً حول وعيك الأمني وسلوكك الرقمي وقابليتك العاطفية.",
        "how2_title": "📧 محاكاة التصيد",
        "how2_desc": "واجه 6 سيناريوهات بريد إلكتروني واقعية وحاول تحديد أيها هجمات تصيد.",
        "how3_title": "🤖 تحليل الذكاء الاصطناعي",
        "how3_desc": "احصل على تقرير مخصص يوضح بالضبط أين نقاط ضعفك وكيفية إصلاحها.",
        # Stats
        "stats_title": "إحصائيات المنصة",
        "stat_scenarios": "سيناريوهات واقعية",
        "stat_recommendations": "توصيات الذكاء الاصطناعي",
        "stat_resilience": "لتحسين المرونة",
        # Discover
        "discover_title": "ما ستكتشفه",
        "discover1": "مستوى وعيك الحقيقي مقارنة بما تعتقد",
        "discover2": "كيف تؤثر القرارات السريعة على قابليتك للاختراق",
        "discover3": "أي أساليب التصيد تخدعك أكثر",
        "discover4": "استراتيجيات مخصصة لحماية نفسك",
        # CTA / Footer
        "cta_title": "هل أنت مستعد لمعرفة مدى مقاومتك للتصيد الاحتيالي؟",
        "btn_begin": "ابدأ الآن",
        "footer_text": "تم بناؤه كمشروع تخرج في كلية عزرائيلي للهندسة - القدس",
        # Registration (Step 1)
        "reg_title": "🛡️ تقييم المرونة ضد التصيد الاحتيالي",
        "reg_subtitle": "اختبر وحسّن قدرتك على اكتشاف هجمات التصيد الاحتيالي",
        "reg_card_title": "التسجيل",
        "reg_name": "الاسم الكامل *",
        "reg_email": "عنوان البريد الإلكتروني *",
        "reg_major": "التخصص/القسم",
        "reg_year": "سنة الدراسة",
        "reg_major_industrial": "هندسة صناعية",
        "reg_major_software": "هندسة البرمجيات",
        "reg_major_electrical": "هندسة كهربائية",
        "reg_major_civil": "هندسة مدنية",
        "reg_major_mechanical": "هندسة ميكانيكية",
        "reg_major_other": "أخرى",
        "reg_year_1": "السنة الأولى",
        "reg_year_2": "السنة الثانية",
        "reg_year_3": "السنة الثالثة",
        "reg_year_4": "السنة الرابعة",
        "btn_begin_assessment": "ابدأ التقييم",
        "reg_note": "يستغرق هذا التقييم حوالي 20 دقيقة",
        "reg_warning": "يرجى تقديم اسمك وعنوان بريدك الإلكتروني للمتابعة.",
        "reg_name_missing": "يرجى إدخال اسمك الكامل.",
        "reg_email_missing": "يرجى إدخال عنوان بريدك الإلكتروني.",
        "reg_email_no_at": "يجب أن يحتوي البريد الإلكتروني على @ (مثال: name@gmail.com).",
        "reg_email_multi_at": "يمكن أن يحتوي البريد الإلكتروني على رمز @ واحد فقط.",
        "reg_email_no_user": "يرجى إدخال اسم المستخدم قبل @ (مثال: yourname@gmail.com).",
        "reg_email_no_domain": "يرجى إدخال النطاق بعد @ (مثال: name@gmail.com).",
        "reg_email_domain_invalid": "النطاق غير صحيح — يرجى استخدام نطاق معروف (مثل: gmail.com أو outlook.com أو hotmail.com أو yahoo.com أو icloud.com).",
        # Questionnaire (Step 2)
        "q_title": "الاستبيان",
        "q_subtitle": "قيّم كل عبارة حسب ما تعتقده عن نفسك.",
        "dim_AW": "الوعي الأمني",
        "dim_DB": "السلوك الرقمي",
        "dim_SV": "القابلية الظرفية",
        "slider_1": "1 - أرفض بشدة",
        "slider_2": "2",
        "slider_3": "3",
        "slider_4": "4",
        "slider_5": "5",
        "slider_6": "6 - أوافق بشدة",
        "btn_submit_q": "إرسال الاستبيان",
        # Progress bar step names
        "step_registration": "التسجيل",
        "step_questionnaire": "الاستبيان",
        "step_simulation": "المحاكاة",
        "step_results": "النتائج",
        "step_recommendations": "التوصيات",
        "step_final_test": "الاختبار النهائي",
        "step_report": "التقرير",
        # Simulation (Step 3 & 6)
        "sim1_title": "المحاكاة",
        "sim1_subtitle": "صنّف كل بريد إلكتروني. يتم قياس وقت استجابتك في الخلفية.",
        "sim2_title": "المحاكاة 2",
        "sim2_subtitle": "طبّق ما تعلمته. رسائل مختلفة، نفس الأساليب. يعمل المؤقت في الخلفية.",
        "sim_scenario": "السيناريو {n} من {total}",
        "sim_question": "هل هذه الرسالة تصيد احتيالي أم شرعية؟",
        "btn_phishing": "🎣 تصيد احتيالي",
        "btn_legitimate": "✅ شرعي",
        # Results (Step 4)
        "res_title": "لوحة النتائج",
        "res_error_incomplete": "أكمل المحاكاة الأولى أولاً.",
        "res_score_summary": "ملخص النتيجة",
        "res_your_score": "نتيجتك",
        "res_correct": "صحيح",
        "res_mistakes": "أخطاء",
        "res_breakdown_expander": "📋 تفصيل رسالة بعد رسالة",
        "res_tactic": "الأسلوب",
        "res_badge_wrong": "خطأ",
        "res_badge_correct": "صحيح",
        "res_your_answer": "إجابتك",
        "res_correct_label": "الصحيح",
        "res_why_was": "لماذا كانت هذه الرسالة {answer}:",
        "res_tip": "💡 نصيحة:",
        "res_gap_analysis": "تحليل الفجوة",
        "dim_label_AW": "التعرف على الرسائل المزيفة",
        "dim_label_DB": "السلوك الرقمي الحذر",
        "dim_label_SV": "مقاومة الضغط العاطفي",
        "res_self_report_risk": "خطر الإبلاغ الذاتي",
        "res_actual_risk": "الخطر الفعلي",
        "res_gap": "الفجوة",
        "gap_large_label": "فجوة كبيرة",
        "gap_large_desc": "اعتقدت أنك بأمان، لكن أداءك يظهر خلاف ذلك.",
        "gap_medium_label": "فجوة متوسطة",
        "gap_medium_desc": "هناك فجوة ملحوظة بين تصورك وسلوكك الفعلي.",
        "gap_aligned_label": "متوافق",
        "gap_aligned_desc": "تقييمك الذاتي يتطابق مع سلوكك الفعلي.",
        "gap_better_label": "أفضل مما توقعت",
        "gap_better_desc": "لقد أديت أداءً أفضل مما كنت تتوقع!",
        "gap_much_better_label": "أفضل بكثير",
        "gap_much_better_desc": "لقد تجاوزت توقعاتك الذاتية بشكل كبير.",
        "res_behavioral_insights": "رؤى سلوكية",
        "res_avg_response_time": "متوسط وقت الاستجابة",
        "res_fastest_response": "أسرع استجابة",
        "res_message_prefix": "الرسالة",
        "res_quick_wrong_warning": "⚡ اتخذت قرارات سريعة (أقل من 5 ثوانٍ) في بعض الرسائل التي أخطأت فيها — التمهل يساعدك على ملاحظة التفاصيل المهمة.",
        "res_btn_recommendations": "احصل على توصيات مخصصة →",
        "res_answer_phishing": "تصيد احتيالي",
        "res_answer_legitimate": "شرعي",
        # Recommendations (Step 5)
        "rec_title": "التوصية الشخصية",
        "rec_error_incomplete": "أكمل المحاكاة الأولى لفتح التوصيات.",
        "rec_error_api_key": "أضف **OPENAI_API_KEY** إلى `.streamlit/secrets.toml`.",
        "rec_btn_retry": "إعادة طلب التوصية",
        "rec_spinner": "جارٍ إنشاء توصيتك...",
        "rec_btn_continue": "متابعة إلى المحاكاة 2",
        # Final Report (Step 7)
        "rep_title": "التقرير النهائي",
        "rep_error_incomplete": "أكمل المحاكاة الثانية أولاً.",
        "rep_great_job": "عمل رائع، {name}!",
        "rep_completed": "لقد أكملت جميع أقسام نظام المرونة ضد التصيد الاحتيالي.",
        "rep_performance": "مقارنة الأداء",
        "rep_sim1": "المحاكاة 1",
        "rep_sim2": "المحاكاة 2",
        "rep_per_dim": "تحليل الفجوة لكل بُعد",
        "rep_satisfaction": "استبيان الرضا",
        "sat_q_0": "هل كانت التوصيات واضحة ومفهومة؟",
        "sat_q_1": "هل شعرت بأن التوصيات كانت مخصصة لك؟",
        "sat_q_2": "هل تعلمت شيئاً جديداً لم تكن تعرفه من قبل؟",
        "sat_q_3": "هل توصي بهذا النظام لطلاب آخرين؟",
        "sat_open_label": "هل لديك تعليقات أو اقتراحات إضافية؟ (اختياري)",
        "sat_open_placeholder": "شاركنا رأيك هنا...",
        "sat_slider_1": "1 - إطلاقاً",
        "sat_slider_2": "2",
        "sat_slider_3": "3",
        "sat_slider_4": "4",
        "sat_slider_5": "5 - جداً",
        "btn_submit_save": "إرسال وحفظ النتائج",
        "rep_success": "تم حفظ النتائج بنجاح!",
    },
    "he": {
        # Hero
        "hero_subtitle": "השתמש בבינה מלאכותית לבניית חוסן בלתי ניתן לשבירה נגד הודעות מסוכנות",
        "hero_desc": "גלה את הפער בין מה שאתה חושב שאתה יודע על פישינג לבין הביצועים שלך בפועל. קבל המלצות מותאמות אישית מבוססות AI לחיזוק ההגנות שלך.",
        "btn_start": "התחל הערכת פישינג",
        "hero_info": "לוקח רק 20 דקות • 100% אנונימי • חינם",
        # How It Works
        "how_title": "איך זה עובד",
        "how1_title": "📋 הערכה עצמית",
        "how1_desc": "ענה על 12 שאלות על המודעות האבטחתית שלך, ההתנהגות הדיגיטלית והפגיעות הרגשית.",
        "how2_title": "📧 סימולציית פישינג",
        "how2_desc": "התמודד עם 6 תרחישי אימייל מציאותיים ונסה לזהות אילו מהם הם מתקפות פישינג.",
        "how3_title": "🤖 ניתוח AI",
        "how3_desc": "קבל דוח מותאם אישית שמראה בדיוק היכן הנקודות העיוורות שלך וכיצד לתקן אותן.",
        # Stats
        "stats_title": "סטטיסטיקות הפלטפורמה",
        "stat_scenarios": "תרחישים מציאותיים",
        "stat_recommendations": "המלצות AI",
        "stat_resilience": "לשיפור החוסן",
        # Discover
        "discover_title": "מה תגלה",
        "discover1": "רמת המודעות האמיתית שלך לעומת מה שאתה חושב",
        "discover2": "איך החלטות מהירות משפיעות על הפגיעות שלך",
        "discover3": "אילו טקטיקות פישינג מרמות אותך ביותר",
        "discover4": "אסטרטגיות מותאמות אישית להגנה על עצמך",
        # CTA / Footer
        "cta_title": "מוכן לגלות כמה אתה עמיד בפני פישינג?",
        "btn_begin": "התחל עכשיו",
        "footer_text": "נבנה כפרויקט גמר במכללת עזריאלי להנדסה - ירושלים",
        # Registration (Step 1)
        "reg_title": "🛡️ הערכת חוסן מפני פישינג",
        "reg_subtitle": "בדוק ושפר את יכולתך לזהות התקפות פישינג",
        "reg_card_title": "הרשמה",
        "reg_name": "שם מלא *",
        "reg_email": "כתובת אימייל *",
        "reg_major": "חוג/מחלקה",
        "reg_year": "שנת לימודים",
        "reg_major_industrial": "הנדסת תעשייה",
        "reg_major_software": "הנדסת תוכנה",
        "reg_major_electrical": "הנדסת חשמל",
        "reg_major_civil": "הנדסה אזרחית",
        "reg_major_mechanical": "הנדסה מכנית",
        "reg_major_other": "אחר",
        "reg_year_1": "שנה א'",
        "reg_year_2": "שנה ב'",
        "reg_year_3": "שנה ג'",
        "reg_year_4": "שנה ד'",
        "btn_begin_assessment": "התחל הערכה",
        "reg_note": "הערכה זו אורכת כ-20 דקות",
        "reg_warning": "אנא הזן את שמך וכתובת האימייל שלך כדי להמשיך.",
        "reg_name_missing": "אנא הזן את שמך המלא.",
        "reg_email_missing": "אנא הזן את כתובת האימייל שלך.",
        "reg_email_no_at": "כתובת האימייל חייבת להכיל @ (לדוגמה: name@gmail.com).",
        "reg_email_multi_at": "כתובת האימייל יכולה להכיל @ אחד בלבד.",
        "reg_email_no_user": "אנא הזן שם משתמש לפני @ (לדוגמה: yourname@gmail.com).",
        "reg_email_no_domain": "אנא הזן דומיין אחרי @ (לדוגמה: name@gmail.com).",
        "reg_email_domain_invalid": "הדומיין אינו תקין — אנא השתמש בדומיין מוכר (לדוגמה: gmail.com, outlook.com, hotmail.com, yahoo.com, icloud.com).",
        # Questionnaire (Step 2)
        "q_title": "שאלון",
        "q_subtitle": "דרג כל משפט לפי מה אתה חושב על עצמך.",
        "dim_AW": "מודעות אבטחה",
        "dim_DB": "התנהגות דיגיטלית",
        "dim_SV": "פגיעות מצבית",
        "slider_1": "1 - לא מסכים בכלל",
        "slider_2": "2",
        "slider_3": "3",
        "slider_4": "4",
        "slider_5": "5",
        "slider_6": "6 - מסכים מאוד",
        "btn_submit_q": "שלח שאלון",
        # Progress bar step names
        "step_registration": "הרשמה",
        "step_questionnaire": "שאלון",
        "step_simulation": "סימולציה",
        "step_results": "תוצאות",
        "step_recommendations": "המלצות",
        "step_final_test": "מבחן סופי",
        "step_report": "דוח",
        # Simulation (Step 3 & 6)
        "sim1_title": "סימולציה",
        "sim1_subtitle": "סווג כל מייל. זמן התגובה שלך נמדד ברקע.",
        "sim2_title": "סימולציה 2",
        "sim2_subtitle": "יישם את מה שלמדת. הודעות שונות, אותן טקטיקות. הטיימר רץ ברקע.",
        "sim_scenario": "תרחיש {n} מתוך {total}",
        "sim_question": "האם הודעה זו היא פישינג או לגיטימית?",
        "btn_phishing": "🎣 פישינג",
        "btn_legitimate": "✅ לגיטימי",
        # Results (Step 4)
        "res_title": "לוח תוצאות",
        "res_error_incomplete": "השלם את הסימולציה הראשונה תחילה.",
        "res_score_summary": "סיכום ציון",
        "res_your_score": "הציון שלך",
        "res_correct": "נכון",
        "res_mistakes": "טעויות",
        "res_breakdown_expander": "📋 פירוט הודעה אחר הודעה",
        "res_tactic": "טקטיקה",
        "res_badge_wrong": "שגוי",
        "res_badge_correct": "נכון",
        "res_your_answer": "תשובתך",
        "res_correct_label": "נכון",
        "res_why_was": "מדוע הודעה זו הייתה {answer}:",
        "res_tip": "💡 טיפ:",
        "res_gap_analysis": "ניתוח פערים",
        "dim_label_AW": "זיהוי הודעות מזויפות",
        "dim_label_DB": "התנהגות דיגיטלית זהירה",
        "dim_label_SV": "עמידות בפני לחץ רגשי",
        "res_self_report_risk": "סיכון לפי דיווח עצמי",
        "res_actual_risk": "סיכון בפועל",
        "res_gap": "פער",
        "gap_large_label": "פער גדול",
        "gap_large_desc": "חשבת שאתה בטוח, אך הביצועים שלך מראים אחרת.",
        "gap_medium_label": "פער בינוני",
        "gap_medium_desc": "קיים פער ניכר בין תפיסתך לבין ההתנהגות בפועל.",
        "gap_aligned_label": "מיושר",
        "gap_aligned_desc": "ההערכה העצמית שלך תואמת את ההתנהגות בפועל.",
        "gap_better_label": "טוב מהצפוי",
        "gap_better_desc": "ביצעת טוב יותר ממה שציפית!",
        "gap_much_better_label": "הרבה יותר טוב",
        "gap_much_better_desc": "עקפת משמעותית את ההערכה העצמית שלך.",
        "res_behavioral_insights": "תובנות התנהגותיות",
        "res_avg_response_time": "זמן תגובה ממוצע",
        "res_fastest_response": "התגובה המהירה ביותר",
        "res_message_prefix": "הודעה",
        "res_quick_wrong_warning": "⚡ קיבלת החלטות מהירות (פחות מ-5 שניות) על חלק מההודעות שטעית בהן — האטה תעזור לך לזהות פרטים חשובים.",
        "res_btn_recommendations": "קבל המלצות מותאמות אישית →",
        "res_answer_phishing": "פישינג",
        "res_answer_legitimate": "לגיטימי",
        # Recommendations (Step 5)
        "rec_title": "המלצה מותאמת אישית",
        "rec_error_incomplete": "השלם את הסימולציה הראשונה כדי לפתוח את ההמלצות.",
        "rec_error_api_key": "הוסף **OPENAI_API_KEY** לקובץ `.streamlit/secrets.toml`.",
        "rec_btn_retry": "נסה שוב את בקשת ההמלצה",
        "rec_spinner": "מייצר את ההמלצה שלך...",
        "rec_btn_continue": "המשך לסימולציה 2",
        # Final Report (Step 7)
        "rep_title": "דוח סופי",
        "rep_error_incomplete": "השלם את הסימולציה השנייה תחילה.",
        "rep_great_job": "כל הכבוד, {name}!",
        "rep_completed": "השלמת את כל חלקי מערכת החוסן מפני פישינג.",
        "rep_performance": "השוואת ביצועים",
        "rep_sim1": "סימולציה 1",
        "rep_sim2": "סימולציה 2",
        "rep_per_dim": "ניתוח פערים לפי ממד",
        "rep_satisfaction": "סקר שביעות רצון",
        "sat_q_0": "האם ההמלצות היו ברורות ומובנות?",
        "sat_q_1": "האם הרגשת שההמלצות היו מותאמות אישית עבורך?",
        "sat_q_2": "האם למדת משהו חדש שלא ידעת לפני כן?",
        "sat_q_3": "האם תמליץ על המערכת הזו לסטודנטים אחרים?",
        "sat_open_label": "יש לך הערות או הצעות נוספות? (אופציונלי)",
        "sat_open_placeholder": "שתף/י את דעתך כאן...",
        "sat_slider_1": "1 - בכלל לא",
        "sat_slider_2": "2",
        "sat_slider_3": "3",
        "sat_slider_4": "4",
        "sat_slider_5": "5 - מאוד",
        "btn_submit_save": "שלח ושמור תוצאות",
        "rep_success": "התוצאות נשמרו בהצלחה!",
    },
}

_LANG_OPTIONS = {"en": "English", "ar": "العربية", "he": "עברית"}
_LANG_NAMES = {"en": "English", "ar": "Arabic", "he": "Hebrew"}
_LANG_CODES = list(_LANG_OPTIONS.keys())
_LANG_LABELS = list(_LANG_OPTIONS.values())
_LANG_FLAG_URLS = {
    "en": "https://flagcdn.com/24x18/us.png",
    "ar": "https://flagcdn.com/24x18/sa.png",
    "he": "https://flagcdn.com/24x18/il.png",
}


def t(key: str) -> str:
    """Return the translated string for *key* in the active language."""
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


def _rtl() -> str:
    return ' dir="rtl"' if st.session_state.get("lang", "en") in ("ar", "he") else ""


def _init_session_state() -> None:
    if "step" not in st.session_state:
        st.session_state.step = 0
    if "lang" not in st.session_state:
        # Read language from query param set by the flag selector
        qp_lang = st.query_params.get("_lang", "en")
        st.session_state.lang = qp_lang if qp_lang in _LANG_CODES else "en"
    if "student_name" not in st.session_state:
        st.session_state.student_name = ""
    if "student_email" not in st.session_state:
        st.session_state.student_email = ""
    if "student_major" not in st.session_state:
        st.session_state.student_major = "Software Engineering"
    if "student_year" not in st.session_state:
        st.session_state.student_year = "1st Year"


_init_session_state()

# ── Handle nav query param (from sidebar HTML links) ──────────────────────
_nav_target = st.query_params.get("nav", "")
if _nav_target == "about":
    st.query_params.clear()
    st.switch_page("pages/1_About_Us.py")

# ── Sidebar: visible on landing page only ─────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

if st.session_state.get("step", 0) == 0:
    _lang = st.session_state.get("lang", "en")

    def _pill(code: str, label: str) -> str:
        if _lang == code:
            style = "background:#0ea5e9;color:white;"
        else:
            style = "background:white;color:#64748b;border:1px solid #cbd5e1;"
        return (
            f'<a href="/?_lang={code}" target="_self" style="text-decoration:none;">'
            f'<span style="display:inline-block;padding:5px 14px;border-radius:20px;'
            f'font-size:13px;font-weight:600;{style}">{label}</span></a>'
        )

    _nav_labels = {
        "en": {"home": "Home", "about": "About Us"},
        "ar": {"home": "الرئيسية", "about": "من نحن"},
        "he": {"home": "דף הבית", "about": "אודותינו"},
    }
    _nl = _nav_labels.get(_lang, _nav_labels["en"])

    st.sidebar.markdown(f"""
<style>
section[data-testid="stSidebar"] > div:first-child {{
    background-color: #dde4ec !important;
    padding: 20px 14px !important;
}}
</style>
<div style="text-align:center;padding:12px 0 18px 0;">
    <span style="font-size:38px;display:block;margin-bottom:14px;">🌐</span>
    <div style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap;">
        {_pill("en","EN")}
        {_pill("ar","ع")}
        {_pill("he","עב")}
    </div>
</div>
<div style="background:white;border-radius:14px;padding:8px;
            box-shadow:0 2px 8px rgba(0,0,0,0.07);">
    <a href="/?_lang={_lang}" target="_self" style="text-decoration:none;">
        <div style="display:flex;align-items:center;gap:10px;padding:10px 14px;
                    border-radius:10px;background:#dbeafe;color:#1d4ed8;
                    font-weight:600;font-size:14px;margin-bottom:4px;">
            <span style="font-size:18px;">🏠</span>
            <span>{_nl["home"]}</span>
        </div>
    </a>
    <a href="/?nav=about&_lang={_lang}" target="_self" style="text-decoration:none;">
        <div style="display:flex;align-items:center;gap:10px;padding:10px 14px;
                    border-radius:10px;color:#475569;font-weight:500;font-size:14px;">
            <span style="font-size:18px;">👥</span>
            <span>{_nl["about"]}</span>
        </div>
    </a>
</div>
""", unsafe_allow_html=True)

else:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

total_steps = 8
step = st.session_state.step

# ── RTL support for Arabic and Hebrew ──────────────────────────────────────
if st.session_state.get("lang", "en") in ("ar", "he"):
    lang = st.session_state.get("lang", "en")
    he_font = "font-family: Arial, sans-serif !important;" if lang == "he" else ""
    
    st.markdown(f"""
    <style>
    .block-container, div[data-testid="stMarkdownContainer"] {{
        direction: rtl !important;
        text-align: right !important;
        {he_font}
    }}
    /* RTL for How It Works step cards */
    .step-card, .step-num, .step-title, .step-desc {{
        direction: rtl !important;
        text-align: right !important;
    }}
    /* Apply font to inputs and buttons too for Hebrew */
    {"button, input, select, textarea { " + he_font + " }" if lang == "he" else ""}

    /* Fix select_slider and slider widgets: keep track LTR so the thumb stays inside */
    div[data-testid="stSlider"],
    div[data-testid="stSlider"] > div,
    div[data-testid="stSlider"] input[type="range"] {{
        direction: ltr !important;
    }}
    /* Keep slider min/max labels readable in RTL */
    div[data-testid="stSlider"] [data-testid="stTickBarMin"],
    div[data-testid="stSlider"] [data-testid="stTickBarMax"] {{
        direction: rtl !important;
        text-align: center !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    if lang == "he":
        st.markdown("""
        <style>
        /* Hebrew font - Arial for ALL text */
        body, p, span, div, label, h1, h2, h3, h4, h5, h6,
        button, input, select, textarea, li, td, th, a,
        [data-testid="stMarkdownContainer"],
        [data-testid="stChatMessage"],
        .stSelectbox, .stTextInput input,
        .stButton > button {
            font-family: Arial, sans-serif !important;
        }

        /* RESTORE icon fonts everywhere - not just sidebar */
        .material-icons,
        .material-symbols-rounded,
        .material-symbols-outlined,
        [data-testid="stSidebarCollapsedControl"] *,
        [data-testid="collapsedControl"] *,
        [class*="icon"],
        [class*="Icon"],
        [data-testid*="Icon"],
        [data-testid="stExpanderToggleIcon"] *,
        [data-testid="stChatMessageAvatarCustom"],
        button[kind="headerNoPadding"] *,
        span[class*="material"],
        i[class*="material"] {
            font-family: "Material Symbols Rounded", "Material Icons",
                         "Material Symbols Outlined", sans-serif !important;
        }
        </style>
        """, unsafe_allow_html=True)

if step > 0:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if step == 0:
    lang = st.session_state.get("lang", "en")
    hero_font = "Arial, sans-serif" if lang == "he" else "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif"
    # Preferred hero font stack (Poppins for LTR, Noto fonts for RTL when available)
    hero_face = "'Poppins', 'Noto Sans Arabic', 'Noto Sans Hebrew', " + hero_font
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Noto+Sans+Arabic:wght@500;700&family=Noto+Sans+Hebrew:wght@500;700&display=swap');
    /* Global font and light background */
    .stApp {{ 
        background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 50%, #edf2f7 100%) !important; 
        font-family: {hero_font} !important;
    }}
    
    /* Remove Top Gap */
    .block-container {{ padding-top: 6rem !important; padding-bottom: 0 !important; max-width: 100% !important; }}
    .stApp > header {{ display: none !important; }}
    div[data-testid="stAppViewContainer"] > div:first-child {{ padding-top: 0 !important; }}
    .element-container {{ margin-top: 0 !important; }}
    
    section[data-testid="stSidebar"] {{ }}
    footer {{ visibility: hidden !important; }}
    #MainMenu, header {{ visibility: visible !important; }}
    
    /* Force Streamlit markdown text colors to avoid conflicts */
    div[data-testid="stMarkdownContainer"] p, div[data-testid="stMarkdownContainer"] span {{ color: #4a5568 !important; font-family: {hero_font} !important; }}
    
    .hero {{ text-align: center; padding: 20px 20px 100px; min-height: 80vh; display: flex; flex-direction: column; justify-content: center; align-items: center; }}
    .hero h1 {{ 
        font-size: 56px !important; 
        font-weight: 800 !important; 
        letter-spacing: -2px !important;
        line-height: 1.1 !important;
        margin: 0 !important; 
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2px;
    }}
    .phish-text {{
        background: linear-gradient(90deg, #0ea5e9, #8b5cf6, #0ea5e9) !important; 
        background-size: 200% auto !important;
        -webkit-background-clip: text !important; 
        -webkit-text-fill-color: transparent !important; 
        animation: textSweep 4s linear infinite;
    }}
    @keyframes textSweep {{
        to {{ background-position: 200% center; }}
    }}
    .gap-text {{
        color: #1a202c !important; 
    }}
    .hero p.sub {{
        font-size: {"26px" if lang in ("ar", "he") else "22px"} !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: {"0" if lang in ("ar", "he") else "0.5px"} !important;
        text-transform: none !important;
        margin-bottom: 18px !important;
        margin-top: 12px !important;
        font-family: {hero_face} !important;
        background: linear-gradient(90deg, #0ea5e9, #8b5cf6, #06b6d4) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-size: 200% auto !important;
        animation: textSweep 6s linear infinite !important;
    }}
    .hero p.desc {{ 
        font-size: 17px !important; 
        line-height: 1.8 !important; 
        color: #4a5568 !important; 
        max-width: 600px; 
        width: 100%;
        margin: 0 auto 24px auto !important; 
        font-weight: 400 !important; 
        word-wrap: break-word;
    }}
    
    .brand-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        animation: floatPulse 5s ease-in-out infinite;
        margin-bottom: 8px;
    }}
    @keyframes floatPulse {{
        0%, 100% {{ transform: translateY(0) scale(1); }}
        50% {{ transform: translateY(-12px) scale(1.02); }}
    }}
    
    .logo-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto 0 auto;
        width: 100%;
        transition: all 0.4s ease;
    }}
    .custom-logo {{
        width: 450px;
        height: auto;
        max-width: 90%;
        animation: subtleGlow 5s ease-in-out infinite;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 10;
    }}
    .custom-logo:hover {{
        transform: translateY(-8px) scale(1.05);
        filter: drop-shadow(0 15px 45px rgba(139, 92, 246, 0.8)) !important;
    }}
    @keyframes subtleGlow {{
        0%, 100% {{ filter: drop-shadow(0 8px 15px rgba(14, 165, 233, 0.4)); }}
        50% {{ filter: drop-shadow(0 15px 40px rgba(139, 92, 246, 0.6)); }}
    }}
    
    /* Primary CTA Button Styling for Hero */
    div[data-testid="stButton"] {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin-top: 0 !important;
        margin-bottom: 30px !important;
    }}
    div[data-testid="stButton"] button {{
        width: 100% !important;
        max-width: 420px !important;
        height: 60px !important;
        background: linear-gradient(135deg, #0ea5e9, #8b5cf6) !important;
        color: white !important;
        border-radius: 18px !important;
        border: none !important;
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    div[data-testid="stButton"] button:hover {{
        transform: translateY(-4px) !important;
        box-shadow: 0 14px 32px rgba(14, 165, 233, 0.6) !important;
        background: linear-gradient(135deg, #38bdf8, #a78bfa) !important;
    }}
    div[data-testid="stButton"] button:active {{
        transform: scale(0.97) translateY(0) !important;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4) !important;
    }}
    div[data-testid="stButton"] button p {{
        font-size: 20px !important;
        font-weight: 700 !important;
        margin: 0 !important;
        color: white !important;
    }}
    [data-testid="stAppViewContainer"] div[data-testid="stButton"] button p::after {{
        content: '→';
        display: inline-block;
        margin-left: 12px;
        transition: transform 0.3s ease !important;
    }}
    [data-testid="stAppViewContainer"] div[data-testid="stButton"] button:hover p::after {{
        transform: translateX(6px) !important;
    }}
    
    .how-it-works {{ padding: 80px 40px; }}
    .how-it-works h2, .learn-section h2 {{ 
        text-align: center; 
        color: #1a202c !important; 
        font-size: 32px !important; 
        font-weight: 700 !important; 
        margin-bottom: 40px !important; 
    }}
    
    .step-card {{ 
        background: white !important; 
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1) !important; 
        border-radius: 16px !important; 
        padding: 32px !important; 
        text-align: left; 
        height: 100%; 
        border: 1px solid rgba(0,0,0,0.02) !important; 
    }}
    .step-num {{ font-size: 48px !important; font-weight: 800 !important; background: linear-gradient(90deg, #3182ce, #38b2ac) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; margin-bottom: 16px !important; line-height: 1 !important; }}
    .step-title {{ font-size: 18px !important; color: #1a202c !important; font-weight: 600 !important; margin-bottom: 12px !important; }}
    .step-desc {{ color: #4a5568 !important; font-size: 14px !important; line-height: 1.7 !important; }}
    
    .stats-section {{ padding: 80px 20px; text-align: center; }}
    .stats-title {{ font-size: 32px !important; font-weight: 700 !important; color: #1a202c !important; letter-spacing: 0 !important; text-transform: none !important; margin-bottom: 40px !important; opacity: 1; }}
    .stats-grid {{ 
        display: grid; 
        grid-template-columns: repeat(3, minmax(240px, 320px)); 
        gap: 30px; 
        justify-content: center;
        max-width: 1100px; 
        margin: 0 auto; 
    }}
    .stat-card {{ 
        background: white !important; 
        padding: 40px 24px !important; 
        border-radius: 20px !important; 
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important; 
        border: 1px solid rgba(0,0,0,0.02) !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 180px;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    .stat-card:hover {{ transform: translateY(-6px); }}
    .stat-val {{ font-size: 46px !important; font-weight: 800 !important; background: linear-gradient(135deg, #0ea5e9, #8b5cf6) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; margin-bottom: 12px !important; }}
    .stat-desc {{ color: #1e293b !important; font-size: 16px !important; font-weight: 600 !important; line-height: 1.3 !important; }}
    @media (max-width: 900px) {{
        .stats-grid {{ 
            grid-template-columns: 1fr;
            max-width: 320px;
            gap: 20px;
        }}
        .stat-card {{ min-height: 160px; }}
    }}
    
    .learn-section {{ padding: 60px 20px; }}
    .learn-grid {{ 
        display: grid; 
        grid-template-columns: repeat(2, minmax(280px, 360px)); 
        gap: 24px; 
        justify-content: center;
        max-width: 900px; 
        margin: 0 auto; 
    }}
    .learn-item {{ 
        background: white !important; 
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important; 
        padding: 32px 24px !important; 
        border-radius: 16px !important; 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: center;
        text-align: center;
        gap: 12px; 
        color: #1e293b !important; 
        font-size: 15px !important; 
        font-weight: 600 !important; 
        transition: all 0.3s ease !important;
        border: 1px solid rgba(0,0,0,0.03) !important;
        min-height: 200px;
        height: 100%;
    }}
    .learn-item:hover {{
        transform: translateY(-6px) !important;
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08) !important;
        border-color: rgba(14, 165, 233, 0.15) !important;
    }}
    .learn-item span {{
        font-size: 40px !important;
        display: block;
        margin-bottom: 4px;
    }}
    @media (max-width: 650px) {{
        .learn-grid {{ 
            grid-template-columns: 1fr;
            max-width: 320px;
            gap: 20px;
        }}
        .learn-item {{ 
            min-height: 180px;
        }}
    }}
    
    .cta-footer {{ 
        padding: 60px 20px 0px 20px !important; 
        text-align: center; 
    }}
    .cta-footer h2 {{
        font-size: 38px !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important; /* Further reduced from 20px */
        color: #1a202c !important;
    }}
    @media (max-width: 768px) {{
        .cta-footer h2 {{
            font-size: 26px !important;
        }}
    }}
    .footer-text {{ color: #718096 !important; font-size: 14px !important; margin-top: 20px !important; }}
    </style>
    """, unsafe_allow_html=True)

    # RTL-aware arrow CSS override (separate block to avoid escaping all CSS braces above)
    _is_rtl_home = st.session_state.get("lang", "en") in ("ar", "he")
    _arrow_char   = "\\2190" if _is_rtl_home else "\\2192"
    _arrow_margin = "margin-right:12px;margin-left:0;" if _is_rtl_home else "margin-left:12px;margin-right:0;"
    _arrow_move   = "translateX(-6px)" if _is_rtl_home else "translateX(6px)"
    st.markdown(f"""<style>
    [data-testid="stAppViewContainer"] div[data-testid="stButton"] button p::after {{
        content: '{_arrow_char}' !important;
        {_arrow_margin}
    }}
    [data-testid="stAppViewContainer"] div[data-testid="stButton"] button:hover p::after {{
        transform: {_arrow_move} !important;
    }}
    </style>""", unsafe_allow_html=True)

    # Get base64 logo
    logo_path = Path(__file__).resolve().parent / "logo.png"
    logo_base64 = ""
    if logo_path.exists():
        logo_base64 = get_base64_of_bin_file(str(logo_path))
    
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="custom-logo" style="display:block; margin:0 auto; position:relative; left:12px;">' if logo_base64 else "<!-- logo.png missing -->"

    st.markdown(f"""
<div class="hero"{_rtl()}>
<div class="brand-container"{_rtl()}>
<div class="logo-container"{_rtl()}>
{logo_html}
</div>
</div>
<p class="sub">{t("hero_subtitle")}</p>
<p class="desc">{t("hero_desc")}</p>
</div>
    """, unsafe_allow_html=True)
    
    start = st.button(t("btn_start"), use_container_width=True)
    
    st.markdown(f"""
    <style>
    .hero-info-text {{
        color: #475569 !important;
        font-size: clamp(10px, 2vw, 16px) !important;
        font-weight: 800 !important;
        text-align: center;
        margin: 4px auto 60px auto !important;
        letter-spacing: 0.5px !important;
    }}
    </style>
    <div style="display: flex; justify-content: center;"{_rtl()}>
        <p class="hero-info-text">{t("hero_info")}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if start:
        st.session_state.step = 1
        st.rerun()

    st.markdown(f"""
    <div class="how-it-works"{_rtl()}>
        <h2>{t("how_title")}</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px; max-width: 1000px; margin: 0 auto;"{_rtl()}>
            <div class="step-card"><div class="step-num">01</div><div class="step-title">{t("how1_title")}</div><div class="step-desc">{t("how1_desc")}</div></div>
            <div class="step-card"><div class="step-num">02</div><div class="step-title">{t("how2_title")}</div><div class="step-desc">{t("how2_desc")}</div></div>
            <div class="step-card"><div class="step-num">03</div><div class="step-title">{t("how3_title")}</div><div class="step-desc">{t("how3_desc")}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stats-section"{_rtl()}>
        <p class="stats-title">{t("stats_title")}</p>
        <div class="stats-grid"{_rtl()}>
            <div class="stat-card"><div class="stat-val">6</div><div class="stat-desc">{t("stat_scenarios")}</div></div>
            <div class="stat-card"><div class="stat-val">3</div><div class="stat-desc">{t("stat_recommendations")}</div></div>
            <div class="stat-card"><div class="stat-val">20m</div><div class="stat-desc">{t("stat_resilience")}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="learn-section"{_rtl()}>
        <h2>{t("discover_title")}</h2>
        <div class="learn-grid"{_rtl()}>
            <div class="learn-item"><span>🔍</span><div>{t("discover1")}</div></div>
            <div class="learn-item"><span>⚡</span><div>{t("discover2")}</div></div>
            <div class="learn-item"><span>🎯</span><div>{t("discover3")}</div></div>
            <div class="learn-item"><span>🛡️</span><div>{t("discover4")}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="cta-footer"{_rtl()}><h2>{t("cta_title")}</h2></div>', unsafe_allow_html=True)
    cols = st.columns([1, 1, 1])
    with cols[1]:
        start2 = st.button(t("btn_begin"), use_container_width=True, key="start2")
    st.markdown(f'<div style="text-align: center;"{_rtl()}><p class="footer-text">{t("footer_text")}</p></div>', unsafe_allow_html=True)

    if start2:
        st.session_state.step = 1
        st.rerun()

elif step == 1:
    st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .block-container { max-width: 900px !important; padding-top: 3rem !important; }
    </style>
    """, unsafe_allow_html=True)
    render_progress_bar(1)
    st.markdown(f"<h1 style='text-align: center; margin-bottom: 8px; font-size: 2.5rem;'>{t('reg_title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center; color: #64748b; font-weight: 400; margin-bottom: 40px;'>{t('reg_subtitle')}</h4>", unsafe_allow_html=True)

    _major_options = {
        "en": [
            "Engineering (Electrical, Mechanical, Civil, Chemical, Materials)",
            "Software & Computer Science",
            "Industrial Engineering, Management or Economics",
            "Social Sciences & Humanities",
            "Medicine & Health Professions",
            "Education & Teaching",
            "Exact Sciences",
            "Other",
        ],
        "ar": [
            "الهندسة (كهرباء، ميكانيكا، مدنية، كيميائية، مواد)",
            "البرمجيات وعلوم الحاسوب",
            "إدارة والصناعة أو اقتصاد",
            "علوم اجتماعية وإنسانية",
            "طب ومهن صحية",
            "تربية وتعليم",
            "العلوم الدقيقة",
            "تخصص آخر",
        ],
        "he": [
            "הנדסה (חשמל, מכונות, אזרחית, כימית, חומרים)",
            "תוכנה ומדעי המחשב",
            "תעשייה וניהול או כלכלה",
            "מדעי החברה והרוח",
            "רפואה ומקצועות הבריאות",
            "חינוך והוראה",
            "מדעים מדויקים",
            "תחום אחר",
        ],
    }
    _major_lang = st.session_state.get("lang", "en")
    _major_opts = _major_options.get(_major_lang, _major_options["en"])
    _year_options = {
        "en": [
            "Preparatory Year",
            "1st Year",
            "2nd Year",
            "3rd Year",
            "4th Year and above",
            "Graduate Studies",
        ],
        "ar": [
            "سنة تحضيرية",
            "سنة أولى",
            "سنة ثانية",
            "سنة ثالثة",
            "سنة رابعة فما فوق",
            "دراسات عليا",
        ],
        "he": [
            "שנת מכינה",
            "שנה ראשונה",
            "שנה שנייה",
            "שנה שלישית",
            "שנה רביעית ומעלה",
            "לימודי תואר שני",
        ],
    }
    _year_lang = st.session_state.get("lang", "en")
    _year_opts = _year_options.get(_year_lang, _year_options["en"])

    cols = st.columns([1, 2, 1])
    with cols[1]:
        with st.container(border=True):
            st.markdown(f"<h3 style='margin-top: 0; margin-bottom: 16px;'>{t('reg_card_title')}</h3>", unsafe_allow_html=True)

            name = st.text_input(t("reg_name"), value=st.session_state.student_name)
            email = st.text_input(t("reg_email"), value=st.session_state.student_email)

            major = st.selectbox(
                t("reg_major"),
                options=_major_opts,
                index=_major_opts.index(st.session_state.student_major) if st.session_state.student_major in _major_opts else 0
            )

            year = st.selectbox(
                t("reg_year"),
                options=_year_opts,
                index=_year_opts.index(st.session_state.student_year) if st.session_state.student_year in _year_opts else 0
            )

            st.markdown("<br>", unsafe_allow_html=True)
            start = st.button(t("btn_begin_assessment"), use_container_width=True)
            st.markdown(f"<p style='text-align: center; font-size: 13px; color: #64748b; margin-top: 8px;'>{t('reg_note')}</p>", unsafe_allow_html=True)

    if start:
        st.session_state.student_name = name.strip()
        st.session_state.student_email = email.strip()
        st.session_state.student_major = major
        st.session_state.student_year = year

        _name_val  = st.session_state.student_name
        _email_val = st.session_state.student_email
        _at_count  = _email_val.count("@")
        _parts     = _email_val.split("@")
        _user      = _parts[0].strip() if _at_count >= 1 else ""
        _domain    = _parts[1].strip() if _at_count == 1 else ""
        _tld       = _domain.split(".")[-1] if "." in _domain else ""

        if not _name_val and not _email_val:
            st.warning(t("reg_warning"))
        elif not _name_val:
            st.error(t("reg_name_missing"))
        elif not _email_val:
            st.error(t("reg_email_missing"))
        elif _at_count == 0:
            st.error(t("reg_email_no_at"))
        elif _at_count > 1:
            st.error(t("reg_email_multi_at"))
        elif not _user:
            st.error(t("reg_email_no_user"))
        elif not _domain:
            st.error(t("reg_email_no_domain"))
        elif "." not in _domain or _domain.startswith(".") or len(_tld) < 2:
            st.error(t("reg_email_domain_invalid"))
        else:
            st.session_state.step = 2
            st.rerun()

elif step == 2:
    st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .block-container { max-width: 900px !important; padding-top: 3rem !important; }
    </style>
    """, unsafe_allow_html=True)
    render_progress_bar(2)
    st.markdown(f"## {t('q_title')}")
    st.markdown(
        f"<p style='color: #64748b; margin-bottom: 24px; font-size: 15px;'>"
        f"{t('q_subtitle')}"
        "</p>", unsafe_allow_html=True
    )

    _q_lang = st.session_state.get("lang", "en")
    _is_rtl_q = _q_lang in ("ar", "he")

    if _is_rtl_q:
        st.markdown("""
        <style>
        .stSlider label, .stSlider p,
        [data-testid="stMarkdownContainer"] p {
            direction: rtl !important;
            text-align: right !important;
        }
        </style>
        """, unsafe_allow_html=True)

    slider_opts = [t("slider_1"), t("slider_2"), t("slider_3"), t("slider_4"), t("slider_5"), t("slider_6")]
    dim_colors = {"AW": "#0ea5e9", "DB": "#10b981", "SV": "#f59e0b"}
    _dim_t_keys = {"AW": "dim_AW", "DB": "dim_DB", "SV": "dim_SV"}

    for dim in ("AW", "DB", "SV"):
        st.markdown(f"<h3 style='color: {dim_colors[dim]}; margin-top: 32px;'>{t(_dim_t_keys[dim])}</h3>", unsafe_allow_html=True)
        for i, q in enumerate(QUESTIONS[dim]):
            q_text = q.get(_q_lang, q["en"])
            _rtl_style = "direction: rtl; text-align: right;" if _is_rtl_q else ""
            st.markdown(
                f"<p style='font-weight: 600; font-size: 16px; {_rtl_style}'>{q_text}</p>",
                unsafe_allow_html=True,
            )

            val = st.select_slider(
                "Rating",
                options=slider_opts,
                value=t("slider_3"),
                key=f"q_{dim}_{i}",
                label_visibility="collapsed"
            )

    cols = st.columns([1, 2, 1])
    with cols[1]:
        submit_q = st.button(t("btn_submit_q"), use_container_width=True)

    if submit_q:
        scores: dict[str, float] = {}
        risks: dict[str, float] = {}
        responses: dict[str, list[int]] = {}

        for dim, items in QUESTIONS.items():
            vals = [int(str(st.session_state[f"q_{dim}_{j}"]).split(" ")[0]) for j in range(len(items))]
            responses[dim] = vals
            avg = sum(vals) / len(vals)
            scores[dim] = avg
            risks[dim] = (avg - 1.0) / 5.0

        st.session_state.questionnaire_responses = responses
        st.session_state.scores = scores
        st.session_state.self_report_risk = risks

        try:
            st.session_state.sim1_emails = select_sim1_version1_messages(_load_messages_json())
        except FileNotFoundError:
            st.error("messages.json was not found next to app.py.")
            st.stop()

        # Reset simulation bookkeeping when restarting from questionnaire (defensive).
        for k in list(st.session_state.keys()):
            ks = str(k)
            if ks.startswith("sim1_timer_start_") or ks.startswith("sim1_pick_"):
                st.session_state.pop(k, None)
        st.session_state.pop("sim1_current_idx", None)
        st.session_state.pop("sim1_trials", None)
        st.session_state.pop("sim1_gpt_recommendation", None)
        st.session_state.pop("sim1_gpt_error", None)
        st.session_state.sim1_current_idx = 0
        st.session_state.sim1_trials = []

        st.session_state.step = 3
        st.rerun()

elif step == 3:
    st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .block-container { max-width: 900px !important; padding-top: 3rem !important; }
    </style>
    """, unsafe_allow_html=True)
    render_progress_bar(3)
    st.markdown(f"## {t('sim1_title')}")
    st.markdown(
        f"<p style='color: #64748b; font-size: 15px;'>{t('sim1_subtitle')}</p>",
        unsafe_allow_html=True
    )

    emails = st.session_state.get("sim1_emails") or []
    if len(emails) != 6:
        st.error("Simulation messages are unavailable. Complete the questionnaire first.")
        st.stop()

    idx = int(st.session_state.get("sim1_current_idx", 0))
    n = len(emails)

    if idx >= n:
        st.session_state.step = 4
        st.rerun()  # -> results dashboard

    msg = emails[idx]

    st.markdown(f'<p class="sim-progress-text">{t("sim_scenario").format(n=idx + 1, total=n)}</p>', unsafe_allow_html=True)

    st.markdown(f'<div class="animate-fade-in"{_rtl()}>', unsafe_allow_html=True)
    st.markdown(render_email(msg), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<p class="sim-question">{t("sim_question")}</p>', unsafe_allow_html=True)

    st.markdown(f'<div class="sim-buttons-container"{_rtl()}>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        clicked_phishing = st.button(t("btn_phishing"), use_container_width=True, key=f"btn_p1_{idx}")
    with col2:
        clicked_legit = st.button(t("btn_legitimate"), use_container_width=True, key=f"btn_l1_{idx}")
    st.markdown('</div>', unsafe_allow_html=True)

    tk = f"sim1_timer_start_{idx}"
    if tk not in st.session_state:
        st.session_state[tk] = time.time()

    choice = None
    if clicked_phishing: choice = "Phishing"
    elif clicked_legit: choice = "Legitimate"

    if choice:
        if True:
            t0 = float(st.session_state[tk])
            elapsed = time.time() - t0
            correct_answer = msg["correct"]
            wrong = choice != correct_answer
            penalty = timer_penalty_for_response(elapsed, wrong)

            trial = {
                "email_id": msg["id"],
                "dimension": msg["dimension"],
                "tactic": msg.get("tactic", ""),
                "user_answer": choice,
                "correct": correct_answer,
                "incorrect": wrong,
                "elapsed_seconds": round(elapsed, 3),
                "timer_penalty": penalty,
            }
            trials_list: list = st.session_state.get("sim1_trials") or []
            trials_list.append(trial)
            st.session_state.sim1_trials = trials_list

            st.session_state.sim1_current_idx = idx + 1

            if st.session_state.sim1_current_idx >= n:
                self_r = dict(st.session_state.self_report_risk)
                agg = aggregate_sim1_dimension_metrics(st.session_state.sim1_trials, self_r)
                (
                    st.session_state.sim1_error_rate,
                    st.session_state.sim1_avg_timer_penalty,
                    st.session_state.sim1_actual_risk,
                    st.session_state.sim1_gap,
                    st.session_state.sim1_gap_type,
                ) = agg
                st.session_state.step = 4  # -> results dashboard

            st.rerun()


elif step == 4:
    st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .block-container { max-width: 900px !important; padding-top: 3rem !important; }
    </style>
    """, unsafe_allow_html=True)
    render_progress_bar(4)
    # ── STEP 4: Results Dashboard ─────────────────────────────────────
    st.markdown(f"## {t('res_title')}")

    req = [
        "sim1_trials", "scores", "self_report_risk",
        "sim1_actual_risk", "sim1_gap", "sim1_gap_type",
        "sim1_error_rate", "sim1_emails",
    ]
    if not all(k in st.session_state for k in req):
        st.error(t("res_error_incomplete"))
        st.stop()

    _trials = st.session_state.sim1_trials
    _msgs_by_id = {m["id"]: m for m in _load_messages_json()}
    _n_correct = sum(1 for t in _trials if not t["incorrect"])
    _n_wrong = sum(1 for t in _trials if t["incorrect"])
    _sim1_score = _n_correct

    # ── Section 1: Score Summary ──────────────────────────────────────
    st.markdown(f"### {t('res_score_summary')}")
    _score_color = "#16a34a" if _sim1_score >= 4 else ("#ea580c" if _sim1_score >= 2 else "#dc2626")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            f'<div style="text-align:center; padding:18px 0;"{_rtl()}>'
            f'<div style="font-size:36px; font-weight:700; color:{_score_color};">{_sim1_score}/6</div>'
            f'<div style="font-size:13px; color:#666; margin-top:4px;">{t("res_your_score")}</div></div>',
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f'<div style="text-align:center; padding:18px 0;"{_rtl()}>'
            f'<div style="font-size:36px; font-weight:700; color:#16a34a;">✓ {_n_correct}</div>'
            f'<div style="font-size:13px; color:#666; margin-top:4px;">{t("res_correct")}</div></div>',
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            f'<div style="text-align:center; padding:18px 0;"{_rtl()}>'
            f'<div style="font-size:36px; font-weight:700; color:#dc2626;">✗ {_n_wrong}</div>'
            f'<div style="font-size:13px; color:#666; margin-top:4px;">{t("res_mistakes")}</div></div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Section 2: Message-by-Message Breakdown ───────────────────────
    with st.expander(t("res_breakdown_expander"), expanded=False):
        for ti, _trial in enumerate(_trials):
            mid = _trial["email_id"]
            meta = _msgs_by_id.get(mid, {})
            is_wrong = _trial["incorrect"]
            badge_color = "#dc2626" if is_wrong else "#16a34a"
            badge_icon = "✗" if is_wrong else "✓"
            badge_label = t("res_badge_wrong") if is_wrong else t("res_badge_correct")
            subj = html.escape(meta.get("subject", mid))
            tactic = html.escape(meta.get("tactic", ""))
            student_ans_display = html.escape(t(f"res_answer_{_trial['user_answer'].lower()}"))
            correct_ans_display = html.escape(t(f"res_answer_{_trial['correct'].lower()}"))
            resp_time = _trial["elapsed_seconds"]

            card_html = f"""
<div style="border:1px solid #e5e7eb; border-radius:8px; padding:14px 16px;
     margin-bottom:10px; background:#fafafa;"{_rtl()}>
  <div style="display:flex; justify-content:space-between; align-items:center;
       flex-wrap:wrap; gap:6px;">
    <div style="flex:1; min-width:200px;">
      <div style="font-size:14px; font-weight:600; color:#202124;">
        {ti + 1}. {subj}</div>
      <div style="font-size:11px; color:#888; margin-top:2px;">{t("res_tactic")}: {tactic}</div>
    </div>
    <div style="display:flex; align-items:center; gap:12px;">
      <span style="font-size:12px; color:#666;">⏱ {resp_time:.1f}s</span>
      <span style="display:inline-block; padding:3px 10px; border-radius:12px;
           font-size:12px; font-weight:600; color:#fff;
           background:{badge_color};">{badge_icon} {badge_label}</span>
    </div>
  </div>
  <div style="margin-top:8px; font-size:12px; color:#555;">
    {t("res_your_answer")}: <strong>{student_ans_display}</strong> &nbsp;|&nbsp;
    {t("res_correct_label")}: <strong>{correct_ans_display}</strong>
  </div>"""

            if is_wrong:
                why_text = html.escape(meta.get("why", ""))
                teach_text = html.escape(meta.get("teach", ""))
                why_label = t("res_why_was").format(answer=correct_ans_display)
                card_html += f"""
  <div style="margin-top:10px; padding:10px 12px; border-radius:6px;
       background:#fef2f2; border-left:3px solid #dc2626;">
    <div style="font-size:12px; font-weight:600; color:#991b1b;
         margin-bottom:4px;">{why_label}</div>
    <div style="font-size:12px; color:#7f1d1d; line-height:1.6;">{why_text}</div>
  </div>
  <div style="margin-top:6px; padding:10px 12px; border-radius:6px;
       background:#eff6ff; border-left:3px solid #3b82f6;">
    <div style="font-size:12px; font-weight:600; color:#1e40af;
         margin-bottom:4px;">{t("res_tip")}</div>
    <div style="font-size:12px; color:#1e3a5f; line-height:1.6;">{teach_text}</div>
  </div>"""

            card_html += "\n</div>"
            st.markdown(card_html, unsafe_allow_html=True)

    st.divider()

    # ── Section 3: Gap Analysis Summary ───────────────────────────────
    st.markdown(f"### {t('res_gap_analysis')}")

    _gap_styles = {
        "large":       ("#dc2626", "#fef2f2", t("gap_large_label"),      t("gap_large_desc")),
        "medium":      ("#ea580c", "#fff7ed", t("gap_medium_label"),     t("gap_medium_desc")),
        "aligned":     ("#16a34a", "#f0fdf4", t("gap_aligned_label"),    t("gap_aligned_desc")),
        "better":      ("#2563eb", "#eff6ff", t("gap_better_label"),     t("gap_better_desc")),
        "much_better": ("#7c3aed", "#f5f3ff", t("gap_much_better_label"),t("gap_much_better_desc")),
    }

    g1, g2, g3 = st.columns(3)
    for col, dim in zip([g1, g2, g3], ["AW", "DB", "SV"]):
        with col:
            sr = st.session_state.self_report_risk[dim]
            ar = st.session_state.sim1_actual_risk[dim]
            gap_val = st.session_state.sim1_gap[dim]
            gt = st.session_state.sim1_gap_type[dim]
            gc, gbg, glabel, gdesc = _gap_styles.get(gt, ("#666", "#f9fafb", gt, ""))

            st.markdown(
                f'<div style="border:1px solid #e5e7eb; border-radius:8px; padding:14px;'
                f' background:{gbg}; margin-bottom:8px;"{_rtl()}>'
                f'<div style="font-size:13px; font-weight:600; color:#202124;">'
                f'{t(f"dim_label_{dim}")}</div>'
                f'<div style="margin-top:10px; font-size:12px; color:#555; line-height:1.7;">'
                f'{t("res_self_report_risk")}: <strong>{sr:.0%}</strong><br>'
                f'{t("res_actual_risk")}: <strong>{ar:.0%}</strong><br>'
                f'{t("res_gap")}: <strong style="color:{gc};">{gap_val:+.2f}</strong></div>'
                f'<div style="margin-top:8px;">'
                f'<span style="display:inline-block; padding:3px 10px; border-radius:12px;'
                f' font-size:11px; font-weight:600; color:#fff; background:{gc};">'
                f'{glabel}</span></div>'
                f'<div style="margin-top:8px; font-size:11px; color:#666;'
                f' line-height:1.5;">{gdesc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Section 4: Behavioral Insights ────────────────────────────────
    st.markdown(f"### {t('res_behavioral_insights')}")

    all_times = [_tr["elapsed_seconds"] for _tr in _trials]
    avg_time = sum(all_times) / len(all_times) if all_times else 0
    fastest_idx = min(range(len(all_times)), key=lambda i: all_times[i])
    fastest_trial = _trials[fastest_idx]
    fastest_meta = _msgs_by_id.get(fastest_trial["email_id"], {})
    fastest_subj = fastest_meta.get("subject", fastest_trial["email_id"])

    bi1, bi2 = st.columns(2)
    with bi1:
        st.metric(t("res_avg_response_time"), f"{avg_time:.1f}s")
    with bi2:
        st.metric(t("res_fastest_response"), f"{all_times[fastest_idx]:.1f}s",
                  help=f'{t("res_message_prefix")}: {fastest_subj}')

    # Warning for quick wrong answers
    quick_wrong = [_tr for _tr in _trials if _tr["incorrect"] and _tr["elapsed_seconds"] < 5]
    if quick_wrong:
        st.warning(t("res_quick_wrong_warning"))

    st.divider()

    cols = st.columns([1, 2, 1])
    with cols[1]:
        if st.button(t("res_btn_recommendations"), use_container_width=True):
            st.session_state.step = 5
            st.rerun()


elif step == 5:
    st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .block-container { max-width: 900px !important; padding-top: 3rem !important; }
    </style>
    """, unsafe_allow_html=True)
    render_progress_bar(5)
    # ── STEP 5: GPT Personalized Recommendation ───────────────────────
    st.markdown(f"## {t('rec_title')}")
    req = [
        "sim1_trials",
        "scores",
        "self_report_risk",
        "sim1_actual_risk",
        "sim1_gap",
        "sim1_gap_type",
        "student_name",
    ]
    if not all(k in st.session_state for k in req):
        st.error(t("rec_error_incomplete"))
        st.stop()

    if isinstance(st.session_state.get("sim1_gpt_error"), str):
        st.error(st.session_state.sim1_gpt_error)
        if st.button(t("rec_btn_retry")):
            st.session_state.pop("sim1_gpt_error", None)
            st.session_state.pop("sim1_gpt_recommendation", None)
            st.rerun()
        st.stop()

    if "sim1_gpt_recommendation" not in st.session_state:
        user_content = _build_sim1_gpt_user_content()
        _lang_name = _LANG_NAMES.get(st.session_state.get("lang", "en"), "English")
        _system_prompt = f"Respond entirely in {_lang_name}.\n" + GPT_SYSTEM_PROMPT_SIM1
        try:
            with st.spinner(t("rec_spinner")):
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {"role": "system", "content": _system_prompt},
                        {"role": "user", "content": user_content}
                    ]
                )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from model")
            st.session_state.pop("sim1_gpt_error", None)
            st.session_state.sim1_gpt_recommendation = content
        except Exception as ex:  # noqa: BLE001 -- show user-friendly API errors
            st.session_state.sim1_gpt_error = str(ex)
            st.rerun()

    _rec_lang = st.session_state.get("lang", "en")
    _rec_dir = "rtl" if _rec_lang in ("ar", "he") else "ltr"
    _rec_align = "right" if _rec_lang in ("ar", "he") else "left"
    _recommendation = _md_to_html(st.session_state.sim1_gpt_recommendation)
    st.markdown(f"""
<div style="
    direction: {_rec_dir};
    text-align: {_rec_align};
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 28px 32px;
    margin: 16px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    line-height: 2;
    font-size: 15px;
    color: #1e293b;
">
{_recommendation}
</div>

<style>
div h1, div h2, div h3 {{
    color: #0ea5e9 !important;
    font-size: 20px !important;
    margin-top: 20px !important;
    margin-bottom: 8px !important;
}}
div h1:first-child {{
    font-size: 22px !important;
    margin-top: 0 !important;
}}
div ul, div ol {{
    padding-{_rec_align}: 20px !important;
}}
div strong, div b {{
    color: #1e293b !important;
}}
</style>
""", unsafe_allow_html=True)

    # ── AI Coach Chatbot ──────────────────────────────────────────────
    st.divider()

    lang = st.session_state.get("lang", "en")
    chat_titles = {
        "en": "🤖 Ask the AI Coach",
        "ar": "🤖 اسأل المدرب الذكي",
        "he": "🤖 שאל את המאמן החכם"
    }
    chat_placeholders = {
        "en": "Ask about your mistakes, gaps, or how to improve...",
        "ar": "اسأل عن أخطائك، الفجوات، أو كيف تتحسن...",
        "he": "שאל על השגיאות שלך, הפערים, או איך להשתפר..."
    }


    st.markdown("""
<div style="text-align: center; margin: 20px 0 10px;">
<svg width="200" height="140" viewBox="0 0 260 130" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="gh1" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#805ad5"/>
<stop offset="100%" style="stop-color:#38b2ac"/>
</linearGradient>
</defs>

<g>
  <animateTransform attributeName="transform" type="translate"
    values="0,0; 0,-3; 0,0; 0,3; 0,0"
    dur="4s" repeatCount="indefinite" calcMode="spline" keySplines="0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1"/>
  <path d="M65 8 C65 2 74 0 84 0 L176 0 C186 0 195 2 195 8 L195 82 C195 88 186 90 176 90 L148 90 L130 105 L127 90 L84 90 C74 90 65 88 65 82 Z" fill="url(#gh1)" opacity="0.1" stroke="url(#gh1)" stroke-width="2.5"/>

  <circle cx="112" cy="32" r="11" fill="white"/>
  <circle cx="148" cy="32" r="11" fill="white"/>
  <circle cx="114" cy="32" r="5.5" fill="#805ad5">
    <animate attributeName="cx" values="114;117;114;111;114" dur="3s" repeatCount="indefinite"/>
  </circle>
  <circle cx="150" cy="32" r="5.5" fill="#38b2ac">
    <animate attributeName="cx" values="150;153;150;147;150" dur="3s" repeatCount="indefinite"/>
  </circle>
  <circle cx="111" cy="29" r="2.5" fill="white" opacity="0.8"/>
  <circle cx="147" cy="29" r="2.5" fill="white" opacity="0.8"/>

  <path d="M110 52 Q130 66 150 52" fill="none" stroke="url(#gh1)" stroke-width="2.5" stroke-linecap="round"/>

  <circle cx="112" cy="74" r="2" fill="#805ad5" opacity="0.4">
    <animate attributeName="opacity" values="0.3;0.8;0.3" dur="1s" repeatCount="indefinite"/>
  </circle>
  <circle cx="124" cy="74" r="2" fill="#38b2ac" opacity="0.4">
    <animate attributeName="opacity" values="0.3;0.8;0.3" dur="1s" begin="0.2s" repeatCount="indefinite"/>
  </circle>
  <circle cx="136" cy="74" r="2" fill="#805ad5" opacity="0.4">
    <animate attributeName="opacity" values="0.3;0.8;0.3" dur="1s" begin="0.4s" repeatCount="indefinite"/>
  </circle>
</g>

<g>
  <animateTransform attributeName="transform" type="rotate"
    values="0 65 55; -5 65 55; 0 65 55; 5 65 55; 0 65 55"
    dur="3s" repeatCount="indefinite" calcMode="spline" keySplines="0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1"/>
  <path d="M65 55 Q50 60 40 72" fill="none" stroke="url(#gh1)" stroke-width="2.5" stroke-linecap="round"/>

  <path d="M30 72 L50 80 L50 100 C50 112 38 120 30 124 C22 120 10 112 10 100 L10 80 Z" fill="url(#gh1)" opacity="0.18" stroke="url(#gh1)" stroke-width="2">
    <animate attributeName="opacity" values="0.18;0.3;0.18" dur="2s" repeatCount="indefinite"/>
  </path>
  <path d="M30 78 L44 84 L44 98 C44 107 36 113 30 116 C24 113 16 107 16 98 L16 84 Z" fill="url(#gh1)" opacity="0.06"/>
  <text x="30" y="100" text-anchor="middle" font-size="12" fill="#805ad5" font-weight="800" font-family="monospace">AI</text>
</g>

<g>
  <animateTransform attributeName="transform" type="rotate"
    values="0 195 55; 5 195 55; 0 195 55; -5 195 55; 0 195 55"
    dur="3s" repeatCount="indefinite" calcMode="spline" keySplines="0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1"/>
  <path d="M195 55 Q210 60 218 72" fill="none" stroke="url(#gh1)" stroke-width="2.5" stroke-linecap="round"/>

  <rect x="210" y="72" width="44" height="32" rx="3" fill="#e0e7ff" stroke="#818cf8" stroke-width="1.5"/>
  <path d="M210 72 L232 58 L254 72" fill="#c7d2fe" stroke="#818cf8" stroke-width="1.5"/>
  <rect x="216" y="62" width="32" height="20" rx="2" fill="white" stroke="#e2e8f0" stroke-width="0.5"/>
  <line x1="220" y1="68" x2="243" y2="68" stroke="#cbd5e1" stroke-width="1.2"/>
  <line x1="220" y1="72" x2="240" y2="72" stroke="#cbd5e1" stroke-width="1.2"/>
  <line x1="220" y1="76" x2="236" y2="76" stroke="#cbd5e1" stroke-width="1"/>

  <circle cx="252" cy="100" r="9" fill="#ef4444">
    <animate attributeName="r" values="9;11;9" dur="1.5s" repeatCount="indefinite" calcMode="spline" keySplines="0.42 0 0.58 1;0.42 0 0.58 1"/>
  </circle>
  <text x="252" y="104" text-anchor="middle" font-size="11" fill="white" font-weight="800">!</text>
</g>

</svg>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"### {chat_titles.get(lang, chat_titles['en'])}")

    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Build student data summary for the chatbot system prompt
    _trials_chat = st.session_state.get("sim1_trials") or []
    _msgs_by_id_chat = {m["id"]: m for m in _load_messages_json()}
    _n_correct_chat = sum(1 for _t in _trials_chat if not _t["incorrect"])

    # Build errors summary
    _errors_list = []
    for _t in _trials_chat:
        if _t.get("incorrect"):
            _meta = _msgs_by_id_chat.get(_t["email_id"], {})
            _errors_list.append(
                f"  - Message '{_meta.get('subject', _t['email_id'])}' "
                f"(dimension={_t['dimension']}, tactic={_t.get('tactic', 'N/A')}): "
                f"answered {_t['user_answer']}, correct was {_t['correct']}, "
                f"response time={_t['elapsed_seconds']:.1f}s. "
                f"Red flags: {_meta.get('teach', 'N/A')}"
            )
    errors_summary = "\n".join(_errors_list) if _errors_list else "No errors — all answers were correct."

    # Build response times summary
    _times_list = []
    for _t in _trials_chat:
        _meta = _msgs_by_id_chat.get(_t["email_id"], {})
        _times_list.append(
            f"  - '{_meta.get('subject', _t['email_id'])}': {_t['elapsed_seconds']:.1f}s "
            f"({'WRONG' if _t['incorrect'] else 'correct'})"
        )
    times_summary = "\n".join(_times_list)

    # Dimension data
    _scores = st.session_state.get("scores", {})
    _sr = st.session_state.get("self_report_risk", {})
    _ar = st.session_state.get("sim1_actual_risk", {})
    _gap = st.session_state.get("sim1_gap", {})
    _gap_type = st.session_state.get("sim1_gap_type", {})

    chat_system_prompt = f"""You are a friendly cybersecurity coach helping a student understand their phishing test results.

Here is this student's data:
- Name: {st.session_state.get('student_name', 'Student')}
- Simulation Score: {_n_correct_chat}/6
- Security awareness deficit (score): {_scores.get('AW', 'N/A')}
- Risky digital behavior (score): {_scores.get('DB', 'N/A')}
- Emotional & situational vulnerability (score): {_scores.get('SV', 'N/A')}
- Self-assessed risk — security awareness deficit: {_sr.get('AW', 'N/A')}, risky digital behavior: {_sr.get('DB', 'N/A')}, emotional & situational vulnerability: {_sr.get('SV', 'N/A')}
- Actual risk — security awareness deficit: {_ar.get('AW', 'N/A')}, risky digital behavior: {_ar.get('DB', 'N/A')}, emotional & situational vulnerability: {_ar.get('SV', 'N/A')}
- Gap in security awareness deficit: {_gap.get('AW', 'N/A')} ({_gap_type.get('AW', 'N/A')}), risky digital behavior: {_gap.get('DB', 'N/A')} ({_gap_type.get('DB', 'N/A')}), emotional & situational vulnerability: {_gap.get('SV', 'N/A')} ({_gap_type.get('SV', 'N/A')})
- Errors:
{errors_summary}
- Response times:
{times_summary}

The student already received these recommendations:
{st.session_state.get('sim1_gpt_recommendation', '')}

Rules:
- Answer based ONLY on this student's actual data
- Be encouraging but honest
- If asked about a specific email they got wrong, explain exactly what the red flags were
- If asked how to improve, give practical specific tips
- Keep answers concise (3-5 sentences)
- Respond in the same language the student writes in
- Do NOT make up data that isn't provided above
- NEVER use codes like AW, DB, SV, AW_01, DB_03 etc. in your response — always use plain human language
"""


    # Display chat history
    _chat_lang = st.session_state.get("lang", "en")
    _chat_dir = "rtl" if _chat_lang in ("ar", "he") else "ltr"
    _chat_align = "right" if _chat_lang in ("ar", "he") else "left"
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(
                f'<div style="direction: {_chat_dir}; text-align: {_chat_align}; line-height: 2; font-size: 15px;">'
                f'{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    # Handle user input
    with st.container():
        _user_text = st.chat_input(chat_placeholders.get(lang, chat_placeholders["en"]))
    if _user_text:
        st.session_state.chat_messages.append({"role": "user", "content": _user_text})
        st.session_state.chat_submitted = True

    if st.session_state.get("chat_submitted", False):
        st.session_state.chat_submitted = False

        # Build messages for API call
        messages = [{"role": "system", "content": chat_system_prompt}]
        messages.append({
            "role": "assistant",
            "content": "I understand. I have the student's complete results and I'm ready to help them understand their performance."
        })

        # Add chat history
        for _msg in st.session_state.chat_messages:
            messages.append({"role": _msg["role"], "content": _msg["content"]})

        # Call API
        with st.spinner("..."):
            try:
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages,
                )
                answer = response.choices[0].message.content
                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as e:
                st.error(f"Error: {e}")

        st.rerun()

    # Clear chat button
    if st.session_state.chat_messages:
        clear_labels = {"en": "🗑️ Clear Chat", "ar": "🗑️ مسح المحادثة", "he": "🗑️ נקה צ'אט"}
        if st.button(clear_labels.get(lang, "🗑️ Clear Chat"), key="clear_chat_btn"):
            st.session_state.chat_messages = []
            st.rerun()

    st.divider()

    cols = st.columns([1, 2, 1])
    with cols[1]:
        if st.button(t("rec_btn_continue"), use_container_width=True):
            st.session_state.step = 6
            st.rerun()


elif step == 6:
    st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .block-container { max-width: 900px !important; padding-top: 3rem !important; }
    </style>
    """, unsafe_allow_html=True)
    render_progress_bar(6)
    # ── STEP 5: Simulation 2 ──────────────────────────────────────────
    st.markdown(f"## {t('sim2_title')}")
    st.markdown(
        f"<p style='color: #64748b; font-size: 15px;'>{t('sim2_subtitle')}</p>",
        unsafe_allow_html=True
    )

    # Prepare sim2 emails once
    if "sim2_emails" not in st.session_state:
        try:
            st.session_state.sim2_emails = select_sim2_version2_messages(
                _load_messages_json()
            )
        except (FileNotFoundError, KeyError) as exc:
            st.error(f"Cannot load Simulation 2 messages: {exc}")
            st.stop()
        st.session_state.sim2_current_idx = 0
        st.session_state.sim2_trials = []

    emails = st.session_state.get("sim2_emails") or []
    if len(emails) != 6:
        st.error("Simulation 2 messages are unavailable.")
        st.stop()

    idx = int(st.session_state.get("sim2_current_idx", 0))
    n = len(emails)

    if idx >= n:
        st.session_state.step = 7
        st.rerun()

    msg = emails[idx]

    st.markdown(f'<p class="sim-progress-text">{t("sim_scenario").format(n=idx + 1, total=n)}</p>', unsafe_allow_html=True)

    st.markdown(f'<div class="animate-fade-in"{_rtl()}>', unsafe_allow_html=True)
    st.markdown(render_email(msg), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<p class="sim-question">{t("sim_question")}</p>', unsafe_allow_html=True)

    st.markdown(f'<div class="sim-buttons-container"{_rtl()}>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        clicked_phishing = st.button(t("btn_phishing"), use_container_width=True, key=f"btn_p2_{idx}")
    with col2:
        clicked_legit = st.button(t("btn_legitimate"), use_container_width=True, key=f"btn_l2_{idx}")
    st.markdown('</div>', unsafe_allow_html=True)

    tk = f"sim2_timer_start_{idx}"
    if tk not in st.session_state:
        st.session_state[tk] = time.time()

    choice = None
    if clicked_phishing: choice = "Phishing"
    elif clicked_legit: choice = "Legitimate"

    if choice:
        if True:
            t0 = float(st.session_state[tk])
            elapsed = time.time() - t0
            correct_answer = msg["correct"]
            wrong = choice != correct_answer
            penalty = timer_penalty_for_response(elapsed, wrong)

            trial = {
                "email_id": msg["id"],
                "dimension": msg["dimension"],
                "tactic": msg.get("tactic", ""),
                "user_answer": choice,
                "correct": correct_answer,
                "incorrect": wrong,
                "elapsed_seconds": round(elapsed, 3),
                "timer_penalty": penalty,
            }
            trials_list: list = st.session_state.get("sim2_trials") or []
            trials_list.append(trial)
            st.session_state.sim2_trials = trials_list

            st.session_state.sim2_current_idx = idx + 1

            if st.session_state.sim2_current_idx >= n:
                # Compute scores & improvement
                sim1_score = compute_sim_score(st.session_state.sim1_trials)
                sim2_score = compute_sim_score(st.session_state.sim2_trials)
                st.session_state.sim1_score = sim1_score
                st.session_state.sim2_score = sim2_score
                st.session_state.improvement = sim2_score - sim1_score
                st.session_state.step = 7

            st.rerun()


elif step == 7:
    st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .block-container { max-width: 900px !important; padding-top: 3rem !important; }
    </style>
    """, unsafe_allow_html=True)
    render_progress_bar(7)
    # ── STEP 6: Final Report ──────────────────────────────────────────
    st.markdown(f"## {t('rep_title')}")

    # Guard: make sure we have the data
    required_keys = [
        "sim1_score", "sim2_score", "improvement",
        "sim1_gap_type", "scores", "self_report_risk",
    ]
    if not all(k in st.session_state for k in required_keys):
        st.error(t("rep_error_incomplete"))
        st.stop()

    st.markdown(
        f'<div class="custom-card"{_rtl()} style="text-align: center; background: linear-gradient(135deg, #f0fdfa, #ecfeff); border-color: #ccfbf1;">'
        f"<h2 style='color: #0d9488; margin-bottom: 8px;'>{t('rep_great_job').format(name=st.session_state.student_name)}</h2>"
        f"<p style='color: #0f766e;'>{t('rep_completed')}</p>"
        '</div>', unsafe_allow_html=True
    )

    # ── Before / After comparison ────────────────────────────────────
    st.markdown(f"### {t('rep_performance')}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(t("rep_sim1"), f"{st.session_state.sim1_score} / 6")
    with col2:
        st.metric(
            t("rep_sim2"),
            f"{st.session_state.sim2_score} / 6",
            delta=f"{st.session_state.improvement:+d}",
        )

    # ── Per-dimension gap types ──────────────────────────────────────
    st.markdown(f"### {t('rep_per_dim')}")
    gap_cols = st.columns(3)
    for i, dim in enumerate(("AW", "DB", "SV")):
        with gap_cols[i]:
            gt = st.session_state.sim1_gap_type[dim]
            _gt_label = t(f"gap_{gt}_label") if f"gap_{gt}_label" in TRANSLATIONS.get(st.session_state.get("lang", "en"), {}) else gt.replace("_", " ").title()
            st.metric(t(f"dim_label_{dim}"), _gt_label)

    st.divider()

    # ── Satisfaction survey ──────────────────────────────────────────
    st.markdown(f"### {t('rep_satisfaction')}")
    slider_opts_sat = [t("sat_slider_1"), t("sat_slider_2"), t("sat_slider_3"), t("sat_slider_4"), t("sat_slider_5")]
    for qi in range(4):
        st.markdown(f"<p style='font-weight: 600; font-size: 14px;'>{t(f'sat_q_{qi}')}</p>", unsafe_allow_html=True)
        st.select_slider(
            "Rating",
            options=slider_opts_sat,
            value=t("sat_slider_3"),
            key=f"sat_{qi}",
            label_visibility="collapsed"
        )

    st.markdown(f"<p style='font-weight: 600; font-size: 14px; margin-top: 12px;'>{t('sat_open_label')}</p>", unsafe_allow_html=True)
    if st.session_state.get("lang", "en") in ("ar", "he"):
        st.markdown("""
        <style>
        textarea, input[type="text"] {
            direction: rtl !important;
            text-align: right !important;
        }
        textarea::placeholder, input::placeholder {
            direction: rtl !important;
            text-align: right !important;
        }
        </style>
        """, unsafe_allow_html=True)
    st.text_area(
        label="open_feedback",
        placeholder=t("sat_open_placeholder"),
        key="sat_open_feedback",
        height=100,
        label_visibility="collapsed",
    )

    cols = st.columns([1, 2, 1])
    with cols[1]:
        submit_save = st.button(t("btn_submit_save"), use_container_width=True)

    if submit_save:
        sat_vals = [int(str(st.session_state[f"sat_{qi}"]).split(" ")[0]) for qi in range(4)]
        satisfaction_avg = round(sum(sat_vals) / len(sat_vals), 2)

        # Build errors & response_times JSON strings
        sim1_trials = st.session_state.get("sim1_trials") or []
        sim2_trials = st.session_state.get("sim2_trials") or []
        all_errors = [
            {"sim": 1, "email_id": t["email_id"], "dim": t["dimension"],
             "user": t["user_answer"], "correct": t["correct"]}
            for t in sim1_trials if t["incorrect"]
        ] + [
            {"sim": 2, "email_id": t["email_id"], "dim": t["dimension"],
             "user": t["user_answer"], "correct": t["correct"]}
            for t in sim2_trials if t["incorrect"]
        ]
        all_response_times = [
            {"sim": 1, "email_id": t["email_id"], "seconds": t["elapsed_seconds"]}
            for t in sim1_trials
        ] + [
            {"sim": 2, "email_id": t["email_id"], "seconds": t["elapsed_seconds"]}
            for t in sim2_trials
        ]

        csv_path = Path(__file__).resolve().parent / "results.csv"
        fieldnames = [
            "student_id", "timestamp", "student_name", "student_email", "student_major", "student_year",
            "score_AW", "score_DB", "score_SV",
            "risk_AW", "risk_DB", "risk_SV",
            "actual_risk_AW", "actual_risk_DB", "actual_risk_SV",
            "gap_AW", "gap_DB", "gap_SV",
            "gap_type_AW", "gap_type_DB", "gap_type_SV",
            "sim1_score", "sim2_score", "improvement",
            "errors", "response_times",
            "gpt_recommendation", "satisfaction_avg", "open_feedback",
        ]

        write_header = not csv_path.exists()
        row = {
            "student_id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "student_name": st.session_state.get("student_name", ""),
            "student_email": st.session_state.get("student_email", ""),
            "student_major": st.session_state.get("student_major", ""),
            "student_year": st.session_state.get("student_year", ""),
            "score_AW": st.session_state["scores"]["AW"],
            "score_DB": st.session_state["scores"]["DB"],
            "score_SV": st.session_state["scores"]["SV"],
            "risk_AW": st.session_state["self_report_risk"]["AW"],
            "risk_DB": st.session_state["self_report_risk"]["DB"],
            "risk_SV": st.session_state["self_report_risk"]["SV"],
            "actual_risk_AW": st.session_state["sim1_actual_risk"]["AW"],
            "actual_risk_DB": st.session_state["sim1_actual_risk"]["DB"],
            "actual_risk_SV": st.session_state["sim1_actual_risk"]["SV"],
            "gap_AW": st.session_state["sim1_gap"]["AW"],
            "gap_DB": st.session_state["sim1_gap"]["DB"],
            "gap_SV": st.session_state["sim1_gap"]["SV"],
            "gap_type_AW": st.session_state["sim1_gap_type"]["AW"],
            "gap_type_DB": st.session_state["sim1_gap_type"]["DB"],
            "gap_type_SV": st.session_state["sim1_gap_type"]["SV"],
            "sim1_score": st.session_state["sim1_score"],
            "sim2_score": st.session_state["sim2_score"],
            "improvement": st.session_state["improvement"],
            "errors": json.dumps(all_errors, ensure_ascii=False),
            "response_times": json.dumps(all_response_times, ensure_ascii=False),
            "gpt_recommendation": st.session_state.get("sim1_gpt_recommendation", ""),
            "satisfaction_avg": satisfaction_avg,
            "open_feedback": st.session_state.get("sat_open_feedback", ""),
        }

        with csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(row)

        st.success(t("rep_success"))
        st.balloons()


else:
    st.error("Unknown step.")
