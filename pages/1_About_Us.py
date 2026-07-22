# -*- coding: utf-8 -*-
import base64
from pathlib import Path

from PIL import Image
import streamlit as st

_qp_lang = st.query_params.get("_lang", "en")
if _qp_lang in ("en", "ar", "he") and "lang" not in st.session_state:
    st.session_state.lang = _qp_lang
lang = st.session_state.get("lang", "en")

ABOUT_TEXT = {
    "en": {
        "title": "About PhishGap",
        "subtitle": "AI-Powered Phishing Resilience Assessment System",
        "problem_title": "🔍 The Problem",
        "problem_p1": "Did you know? Our research found that students' self-reported security awareness explains only <strong>2.5%</strong> of their actual ability to detect phishing attacks.",
        "problem_p2": "This means most students who believe they are safe are actually the most vulnerable. Traditional security training gives everyone the same generic advice — but each person has different blind spots.",
        "solution_title": "💡 Our Solution",
        "solution_desc": "PhishGap uses a unique 3-step approach:",
        "solution_1": "<strong>Measure what you THINK</strong> — Self-assessment questionnaire (12 questions)",
        "solution_2": "<strong>Measure what you DO</strong> — Realistic phishing simulation with hidden timer (6 emails)",
        "solution_3": "<strong>Bridge the GAP</strong> — AI-powered personalized recommendations",
        "principle_1": "The error type determines <strong>WHAT</strong> to teach.",
        "principle_2": "The gap type determines <strong>HOW</strong> to teach.",
        "how_title": "⚙️ How the Gap Analysis Works",
        "how_desc": "The system compares two numbers for each dimension:",
        "how_1": "<strong>Self-Report Risk</strong> — calculated from questionnaire: (score 1-6)  ",
        "how_2": "<strong>Actual Risk</strong> — calculated from simulation errors + response time penalties",
        "how_gap": "<strong>Gap = Actual Risk − Self-Report Risk</strong>",
        "how_large": "Large gap (overconfidence) → Direct confrontation style",
        "how_medium": "Medium gap → Gentle warning style",
        "how_aligned": "Aligned → Supportive style",
        "how_better": "Better than expected → Confidence reinforcement",
        "how_note": "The system calculates all scores and gaps automatically using precise formulas. The AI then writes a personalized recommendation based on these results — it focuses on explaining, not calculating. Students can also chat with an AI Coach that understands their personal results — ask about specific mistakes, learn how to spot fake domains, and get practical tips to stay safe from phishing.",
        "gap_title": "⚙️ How the Gap Analysis Works",
        "gap_desc": "The system compares two numbers for each dimension:",
        "gap_self": "Self-Report Risk — calculated from questionnaire: (score 1–6)",
        "gap_actual": "Actual Risk — calculated from simulation errors + response time penalties",
        "gap_formula": "Gap = Actual Risk − Self-Report Risk",
        "gap_large": "+0.50 or higher → Large gap (overconfidence) → Direct confrontation style",
        "gap_medium": "+0.25 to +0.49 → Medium gap → Gentle warning style",
        "gap_aligned": "-0.24 to +0.24 → Aligned → Supportive style",
        "gap_better": "-0.25 or lower → Better than expected → Confidence reinforcement",
        "gap_note": "The system calculates all scores and gaps automatically using precise formulas. The AI then writes a personalized recommendation based on these results — it focuses on explaining, not calculating. Students can also chat with an AI Coach that understands their personal results — ask about specific mistakes, learn how to spot fake domains, and get practical tips to stay safe from phishing.",

        "team_title": "👥 The Team",
        "role": "Developer & Researcher",
        "institution_title": "👨‍🏫 Supervision & Details",
        "supervisor": "Supervisor",
        "supervisor_name": "[Supervisor name]",
        "supervisors_label": "Academic Supervisors",
        "supervisors_names": "Mr. Avraham Morduch | Dr. Shoshi Reiter",
        "department_label": "Department",
        "department": "Industrial Engineering",
        "academic_year": "Academic Year",
        "year": "2025 – 2026",
        "footer": "© 2026 PhishGap — Built at Azrieli College of Engineering, Jerusalem",
    },
    "ar": {
        "title": "عن PhishGap",
        "subtitle": "نظام تقييم المرونة ضد التصيد المدعوم بالذكاء الاصطناعي",
        "problem_title": "🔍 المشكلة",
        "problem_p1": "هل تعلم؟ أظهر بحثنا أن التقييم الذاتي للوعي الأمني لدى الطلاب يفسر فقط <strong>2.5%</strong> من قدرتهم الفعلية على كشف هجمات التصيد.",
        "problem_p2": "هذا يعني أن معظم الطلاب الذين يعتقدون أنهم آمنون هم في الواقع الأكثر عرضة للخطر. التدريب الأمني التقليدي يعطي الجميع نفس النصائح العامة — لكن لكل شخص نقاط ضعف مختلفة.",
        "solution_title": "💡 الحل",
        "solution_desc": "يستخدم PhishGap منهجية فريدة من 3 خطوات:",
        "solution_1": "<strong>قياس ما تعتقده</strong> — استبيان تقييم ذاتي (12 سؤالاً)",
        "solution_2": "<strong>قياس ما تفعله</strong> — محاكاة تصيد واقعية مع مؤقت مخفي (6 رسائل)",
        "solution_3": "<strong>سد الفجوة</strong> — توصيات مخصصة مدعومة بالذكاء الاصطناعي",
        "principle_1": "نوع الخطأ يحدد <strong>ماذا</strong> نعلّم.",
        "principle_2": "نوع الفجوة يحدد <strong>كيف</strong> نعلّم.",
        "how_title": "⚙️ كيف يعمل تحليل الفجوة",
        "how_desc": "يقارن النظام رقمين لكل بُعد:",
        "how_1": "<strong>خطر التقييم الذاتي</strong> — محسوب من الاستبيان: (النتيجة 1 - 6)  ",
        "how_2": "<strong>الخطر الفعلي</strong> — محسوب من أخطاء المحاكاة + عقوبات وقت الاستجابة",
        "how_gap": "<strong>الفجوة = الخطر الفعلي − خطر التقييم الذاتي</strong>",
        "how_large": "فجوة كبيرة (ثقة زائدة) → أسلوب المواجهة المباشرة",
        "how_medium": "فجوة متوسطة → أسلوب التحذير اللطيف",
        "how_aligned": "متوافق → أسلوب الدعم",
        "how_better": "أفضل من المتوقع → تعزيز الثقة",
        "how_note": "يقوم النظام بحساب جميع الدرجات والفجوات تلقائيًا باستخدام صيغ رياضية دقيقة. بعد ذلك، يكتب الذكاء الاصطناعي توصية مخصصة بناءً على هذه النتائج — دوره الشرح والتوجيه وليس الحساب. يمكن للطالب أيضًا التحدث مع مدرب ذكاء اصطناعي يفهم نتائجه الشخصية — يسأل عن أخطائه، يتعلم كيف يكشف النطاقات المزيفة، ويحصل على نصائح عملية للحماية من التصيد.",
        "gap_title": "⚙️ كيف يعمل تحليل الفجوات",
        "gap_desc": "النظام يقارن رقمين لكل بُعد:",
        "gap_self": "خطر التقرير الذاتي — يُحسب من الاستبيان: (الدرجة 6–1)",
        "gap_actual": "الخطر الفعلي — يُحسب من أخطاء المحاكاة + عقوبات وقت الاستجابة",
        "gap_formula": "الفجوة = الخطر الفعلي − خطر التقرير الذاتي",
        "gap_large": "0.50+ أو أكثر ← فجوة كبيرة (ثقة مفرطة) ← أسلوب مواجهة مباشرة",
        "gap_medium": "0.25+ إلى 0.49+ ← فجوة متوسطة ← أسلوب تحذير لطيف",
        "gap_aligned": "0.24- إلى 0.24+ ← متطابق ← أسلوب داعم",
        "gap_better": "0.25- أو أقل ← أفضل من المتوقع ← تعزيز الثقة",
        "gap_note": "يقوم النظام بحساب جميع الدرجات والفجوات تلقائيًا باستخدام صيغ رياضية دقيقة. بعد ذلك، يكتب الذكاء الاصطناعي توصية مخصصة بناءً على هذه النتائج — دوره الشرح والتوجيه وليس الحساب. يمكن للطالب أيضًا التحدث مع مدرب ذكاء اصطناعي يفهم نتائجه الشخصية — يسأل عن أخطائه، يتعلم كيف يكشف النطاقات المزيفة، ويحصل على نصائح عملية للحماية من التصيد.",

        "team_title": "👥 الفريق",
        "role": "مطور وباحث",
        "institution_title": "👨‍🏫 الإشراف والتفاصيل",
        "supervisor": "المشرف",
        "supervisor_name": "[اسم المشرف]",
        "supervisors_label": "المشرفون الأكاديميون",
        "supervisors_names": "السيد أبراهام موردوخ | د. شوشي رايتر",
        "department_label": "القسم",
        "department": "الهندسة الصناعية",
        "academic_year": "السنة الأكاديمية",
        "year": "2025 – 2026",
        "footer": "© 2026 PhishGap — كلية عزرائيلي للهندسة، القدس",
    },
    "he": {
        "title": "אודות PhishGap",
        "subtitle": "מערכת הערכת חוסן מפני פישינג מבוססת בינה מלאכותית",
        "problem_title": "🔍 הבעיה",
        "problem_p1": "הידעת? המחקר שלנו מצא שהדיווח העצמי של סטודנטים על המודעות האבטחתית שלהם מסביר רק <strong>2.5%</strong> מהיכולת בפועל לזהות מתקפות פישינג.",
        "problem_p2": "המשמעות היא שרוב הסטודנטים שמאמינים שהם בטוחים הם בפועל הפגיעים ביותר. הדרכות אבטחה מסורתיות נותנות לכולם את אותן עצות כלליות — אבל לכל אדם יש נקודות עיוורות שונות.",
        "solution_title": "💡 הפתרון שלנו",
        "solution_desc": "PhishGap משתמש בגישה ייחודית בת 3 שלבים:",
        "solution_1": "<strong>למדוד מה אתה חושב</strong> — שאלון הערכה עצמית (12 שאלות)",
        "solution_2": "<strong>למדוד מה אתה עושה</strong> — סימולציית פישינג מציאותית עם טיימר נסתר (6 מיילים)",
        "solution_3": "<strong>לגשר על הפער</strong> — המלצות מותאמות אישית מבוססות AI",
        "principle_1": "סוג השגיאה קובע <strong>מה</strong> ללמד.",
        "principle_2": "סוג הפער קובע <strong>איך</strong> ללמד.",
        "how_title": "⚙️ כיצד עובד ניתוח הפער",
        "how_desc": "המערכת משווה שני מספרים לכל ממד:",
        "how_1": "<strong>סיכון דיווח עצמי</strong> — מחושב מהשאלון: (ציון 6-1)  ",
        "how_2": "<strong>סיכון בפועל</strong> — מחושב משגיאות הסימולציה + עונשי זמן תגובה",
        "how_gap": "<strong>פער = סיכון בפועל − סיכון דיווח עצמי</strong>",
        "how_large": "פער גדול (ביטחון יתר) → סגנון עימות ישיר",
        "how_medium": "פער בינוני → סגנון אזהרה עדינה",
        "how_aligned": "מיושר → סגנון תמיכה",
        "how_better": "טוב מהצפוי → חיזוק ביטחון",
        "how_note": "המערכת מחשבת את כל הציונים והפערים באופן אוטומטי באמצעות נוסחאות מדויקות. לאחר מכן, הבינה המלאכותית כותבת המלצה מותאמת אישית על סמך התוצאות — תפקידה להסביר ולהנחות, לא לחשב. הסטודנט יכול גם לשוחח עם מאמן בינה מלאכותית שמבין את התוצאות האישיות שלו — לשאול על טעויות, ללמוד איך לזהות דומיינים מזויפים, ולקבל טיפים מעשיים להגנה מפני פישינג.",
        "gap_title": "⚙️ איך ניתוח הפערים עובד",
        "gap_desc": "המערכת משווה שני מספרים לכל ממד:",
        "gap_self": "סיכון דיווח עצמי — מחושב מהשאלון: (ציון 6–1)",
        "gap_actual": "סיכון בפועל — מחושב משגיאות הסימולציה + קנסות זמן תגובה",
        "gap_formula": "פער = סיכון בפועל − סיכון דיווח עצמי",
        "gap_large": "0.50+ ומעלה ← פער גדול (ביטחון יתר) ← סגנון עימות ישיר",
        "gap_medium": "0.25+ עד 0.49+ ← פער בינוני ← סגנון אזהרה עדינה",
        "gap_aligned": "0.24- עד 0.24+ ← מיושר ← סגנון תמיכה",
        "gap_better": "0.25- ומטה ← טוב מהצפוי ← חיזוק ביטחון",
        "gap_note": "המערכת מחשבת את כל הציונים והפערים באופן אוטומטי באמצעות נוסחאות מדויקות. לאחר מכן, הבינה המלאכותית כותבת המלצה מותאמת אישית על סמך התוצאות — תפקידה להסביר ולהנחות, לא לחשב. הסטודנט יכול גם לשוחח עם מאמן בינה מלאכותית שמבין את התוצאות האישיות שלו — לשאול על טעויות, ללמוד איך לזהות דומיינים מזויפים, ולקבל טיפים מעשיים להגנה מפני פישינג.",

        "team_title": "👥 הצוות",
        "role": "מפתח וחוקר",
        "institution_title": "👨‍🏫 הנחיה ופרטים",
        "supervisor": "מנחה",
        "supervisor_name": "[שם המנחה]",
        "supervisors_label": "מנחים אקדמיים",
        "supervisors_names": "מר אברהם מורדוך | ד״ר שושי רייטר",
        "department_label": "מחלקה",
        "department": "הנדסת תעשייה",
        "academic_year": "שנה אקדמית",
        "year": "2025 – 2026",
        "footer": "© 2026 PhishGap — מכללת עזריאלי להנדסה, ירושלים",
    },
}

def ta(key):
    return ABOUT_TEXT.get(lang, ABOUT_TEXT["en"]).get(key, ABOUT_TEXT["en"].get(key, ""))

direction = "rtl" if lang in ("ar", "he") else "ltr"
align = "right" if lang in ("ar", "he") else "left"
he_font = "font-family: Arial, sans-serif !important;" if lang == "he" else ""
is_rtl = lang in ("ar", "he")

_logo_raw = Image.open(Path(__file__).resolve().parent.parent / "logoCropped.png").convert("RGBA")
_pad = 8
_favicon = Image.new("RGBA", (_logo_raw.width + _pad * 2, _logo_raw.height + _pad * 2), (0, 0, 0, 0))
_favicon.paste(_logo_raw, (_pad, _pad))
st.set_page_config(page_title=f"PhishGap - {ta('title')}", page_icon=_favicon, layout="wide")

css = """
<style>
.stApp {
    background-color: #f8fafc;
    $HE_FONT
}
.block-container {
    max-width: 900px !important;
    padding-top: 2rem !important;
    direction: $DIR !important;
    $HE_FONT
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.about-hero {
    text-align: center;
    padding: 40px 20px 30px;
}
.about-hero h1 {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}
.about-hero p {
    font-size: 16px;
    color: #64748b;
    font-weight: 500;
}
.about-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.about-card h3 {
    font-size: 20px;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 12px;
}
.about-card p, .about-card li {
    font-size: 14px;
    color: #475569;
    line-height: 1.8;
}
.stat-highlight {
    background: linear-gradient(135deg, #eff6ff, #f0fdf4);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    border: 1px solid #e0f2fe;
}
.stat-highlight .num {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-highlight .label {
    font-size: 13px;
    color: #64748b;
    margin-top: 4px;
}
.team-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}
.team-avatar {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 12px;
    font-size: 24px;
    font-weight: 700;
    color: white;
}
.team-name {
    font-size: 16px;
    font-weight: 600;
    color: #1e293b;
}
.team-role {
    font-size: 13px;
    color: #64748b;
}
.timeline-item {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 12px 0;
    border-bottom: 1px solid #f1f5f9;
}
.timeline-item:last-child { border-bottom: none; }
.timeline-num {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 700;
    flex-shrink: 0;
}
.timeline-text {
    font-size: 14px;
    color: #334155;
    line-height: 1.6;
    padding-top: 4px;
}
.principle-box {
    background: linear-gradient(135deg, #eff6ff, #faf5ff);
    border: 1px solid #c7d2fe;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 16px 0;
}
.principle-box p {
    font-size: 16px;
    font-weight: 600;
    color: #4338ca;
    line-height: 1.6;
}
/* Fix bullet points for RTL */
.about-card ul {
    padding-right: 20px !important;
    padding-left: 0 !important;
    list-style-position: inside !important;
}
</style>
"""
css = css.replace("$HE_FONT", he_font).replace(
    "$DIR", "rtl" if is_rtl else "ltr"
)
if lang == "he":
    css += "<style>.about-card, .team-card, .stat-highlight, .timeline-text, .principle-box { " + he_font + " }</style>\n"
st.markdown(css, unsafe_allow_html=True)

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

# ── Sidebar: language selector + navigation ───────────────────────────────
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    direction: ltr !important;
    left: 0 !important;
    right: auto !important;
}
section[data-testid="stSidebar"] > div { direction: ltr !important; }
[data-testid="stSidebarCollapsedControl"] {
    left: 0.5rem !important;
    right: auto !important;
}
[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

def _pill_au(code: str, label: str) -> str:
    if lang == code:
        style = "background:#0ea5e9;color:white;"
    else:
        style = "background:white;color:#64748b;border:1px solid #cbd5e1;"
    return (
        f'<a href="/?nav=about&_lang={code}" target="_self" style="text-decoration:none;">'
        f'<span style="display:inline-block;padding:5px 14px;border-radius:20px;'
        f'font-size:13px;font-weight:600;{style}">{label}</span></a>'
    )

_nav_labels_au = {
    "en": {"home": "Home", "about": "About Us"},
    "ar": {"home": "الرئيسية", "about": "من نحن"},
    "he": {"home": "דף הבית", "about": "אודותינו"},
}
_nl_au = _nav_labels_au.get(lang, _nav_labels_au["en"])

st.sidebar.markdown(f"""
<style>
[data-testid="stSidebarNav"] {{ display: none !important; }}
section[data-testid="stSidebar"] > div:first-child {{
    background-color: #dde4ec !important;
    padding: 20px 14px !important;
}}
</style>
<div style="text-align:center;padding:12px 0 18px 0;">
    <span style="font-size:38px;display:block;margin-bottom:14px;">🌐</span>
    <div style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap;">
        {_pill_au("en","EN")}
        {_pill_au("ar","ع")}
        {_pill_au("he","עב")}
    </div>
</div>
<div style="background:white;border-radius:14px;padding:8px;
            box-shadow:0 2px 8px rgba(0,0,0,0.07);">
    <a href="/?_lang={lang}" target="_self" style="text-decoration:none;">
        <div style="display:flex;align-items:center;gap:10px;padding:10px 14px;
                    border-radius:10px;color:#475569;font-weight:500;font-size:14px;
                    margin-bottom:4px;">
            <span style="font-size:18px;">🏠</span>
            <span>{_nl_au["home"]}</span>
        </div>
    </a>
    <a href="/?nav=about&_lang={lang}" target="_self" style="text-decoration:none;">
        <div style="display:flex;align-items:center;gap:10px;padding:10px 14px;
                    border-radius:10px;background:#dbeafe;color:#1d4ed8;
                    font-weight:600;font-size:14px;">
            <span style="font-size:18px;">👥</span>
            <span>{_nl_au["about"]}</span>
        </div>
    </a>
</div>
""", unsafe_allow_html=True)

# ── Hero ──
st.markdown(f"""
<div class="about-hero" style="direction: {direction}; text-align: {align};">
    <h1>{ta('title')}</h1>
    <p>{ta('subtitle')}</p>
</div>
""", unsafe_allow_html=True)

# ── The Problem ──
st.markdown(f"""
<div class="about-card" style="direction: {direction}; text-align: {align};">
    <h3>{ta('problem_title')}</h3>
    <p>{ta('problem_p1')}</p>
    <p style="margin-top: 12px;">{ta('problem_p2')}</p>
</div>
""", unsafe_allow_html=True)

# ── Our Solution ──
st.markdown(f"""
<div class="about-card" style="direction: {direction}; text-align: {align};">
    <h3>{ta('solution_title')}</h3>
    <p>{ta('solution_desc')}</p>
    <div style="margin: 12px 0; line-height: 2.2;">
        <div>✅ {ta('solution_1')}</div>
        <div>✅ {ta('solution_2')}</div>
        <div>✅ {ta('solution_3')}</div>
    </div>
    <div class="principle-box">
        <p>{ta('principle_1')}<br/>{ta('principle_2')}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── How It Works ──
st.markdown(f"""
<div class="about-card" style="direction: {direction}; text-align: {align};">
    <h3>{ta('gap_title')}</h3>
    <p>{ta('gap_desc')}</p>
    <ul>
        <li>{ta('gap_self')}</li>
        <li>{ta('gap_actual')}</li>
    </ul>
    <p style="margin-top: 8px;"><strong>{ta('gap_formula')}</strong></p>
    <ul>
        <li><span style="color: #dc2626; font-weight: 600;">{ta('gap_large')}</span></li>
        <li><span style="color: #ea580c; font-weight: 600;">{ta('gap_medium')}</span></li>
        <li><span style="color: #16a34a; font-weight: 600;">{ta('gap_aligned')}</span></li>
        <li><span style="color: #2563eb; font-weight: 600;">{ta('gap_better')}</span></li>
    </ul>
    <p style="margin-top: 16px; font-size: 14px; color: #1e293b; line-height: 1.9;">{ta('gap_note')}</p>
</div>
""", unsafe_allow_html=True)

# ── Team ──
def _img_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

_img1 = _img_b64("moayad.jpg")
_img2 = _img_b64("ali.jpg")

_avatar_m = (
    f'<img src="data:image/jpeg;base64,{_img1}" '
    'style="width:120px;height:120px;border-radius:50%;object-fit:cover;'
    'border:4px solid #6699cc;box-shadow:0 4px 15px rgba(102,153,204,0.3);"/>'
    if _img1 else
    '<div style="width:120px;height:120px;border-radius:50%;'
    'background:linear-gradient(135deg,#0ea5e9,#06b6d4);'
    'display:flex;align-items:center;justify-content:center;'
    'font-size:40px;font-weight:700;color:white;'
    'margin:0 auto;border:4px solid white;'
    'box-shadow:0 4px 15px rgba(14,165,233,0.3);">M</div>'
)

_avatar_a = (
    f'<img src="data:image/jpeg;base64,{_img2}" '
    'style="width:120px;height:120px;border-radius:50%;object-fit:cover;'
    'border:4px solid #6699cc;box-shadow:0 4px 15px rgba(102,153,204,0.3);"/>'
    if _img2 else
    '<div style="width:120px;height:120px;border-radius:50%;'
    'background:linear-gradient(135deg,#8b5cf6,#a78bfa);'
    'display:flex;align-items:center;justify-content:center;'
    'font-size:40px;font-weight:700;color:white;'
    'margin:0 auto;border:4px solid white;'
    'box-shadow:0 4px 15px rgba(139,92,246,0.3);">A</div>'
)

st.markdown(f"""
<div class="about-card" style="direction: {direction}; text-align: {align};">
    <h3 style="text-align: center; margin-bottom: 24px;">{ta('team_title')}</h3>
    <div style="display: flex; justify-content: center; gap: 60px; flex-wrap: wrap;">
        <div style="text-align: center;">
            {_avatar_m}
            <div style="font-size: 18px; font-weight: 600; color: #1e293b; margin-top: 12px;">
                Moayad Tamimi
            </div>
            <div style="font-size: 14px; color: #6699cc; font-weight: 500;">
                {ta('role')}
            </div>
        </div>
        <div style="text-align: center;">
            {_avatar_a}
            <div style="font-size: 18px; font-weight: 600; color: #1e293b; margin-top: 12px;">
                Ali Shweiki
            </div>
            <div style="font-size: 14px; color: #6699cc; font-weight: 500;">
                {ta('role')}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Institution ──
st.markdown(f"""
<div class="about-card" style="direction: {direction}; text-align: center;">
    <h3>{ta('institution_title')}</h3>
    <p><strong>{ta('supervisors_label')}:</strong> {ta('supervisors_names')}</p>
    <p><strong>{ta('department_label')}:</strong> {ta('department')}</p>
    <p><strong>{ta('academic_year')}:</strong> {ta('year')}</p>
</div>
""", unsafe_allow_html=True)

# ── Footer ──
st.markdown(f"""
<div style="direction: {direction}; text-align: center; padding: 30px 0 10px; color: #94a3b8; font-size: 13px;">
    {ta('footer')}
</div>
""", unsafe_allow_html=True)
