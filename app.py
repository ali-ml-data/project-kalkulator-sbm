import streamlit as st
import pandas as pd
from google import genai

# ==============================
# 1. SETUP CLIENT GEMINI
# ==============================
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

st.set_page_config(
    page_title="PUSBIN AI 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================
# 2. LOAD & FORMAT EXCEL CONTEXT
# ==============================
@st.cache_data
def get_excel_context(query):
    file_path = "Database_Kantor.xlsx"
    summary = ""
    xl = pd.ExcelFile(file_path)
    keywords = query.lower().split()

    for sheet in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet)
        df = df.dropna(axis=1, how="all")

# ✅ SESUDAH
mask = df.apply(
    lambda row: any(
        kw.lower() in " ".join(str(v) for v in row.values).lower()
        for kw in keywords
    ),
    axis=1,
)
        filtered = df[mask]
        if filtered.empty:
            filtered = df.head(5)

        filtered = filtered.drop(columns=["No"], errors="ignore")
        summary += f"\n[DATA]\n{filtered.to_csv(index=False)}\n"

    return summary

# ==============================
# INIT SESSION CHAT HISTORY
# ==============================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================
# 3. DARK MODE UI — ChatGPT STYLE
# ==============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ─── RESET & BASE ─── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
section.main,
section.main > div,
[data-testid="stHeader"] {
    background-color: #212121 !important;
    color: #ececec !important;
    font-family: 'Sora', sans-serif !important;
}

/* ─── BLOCK CONTAINER ─── */
.block-container {
    max-width: 780px !important;
    padding: 0 1rem 6rem 1rem !important;
    margin: 0 auto !important;
    background: transparent !important;
}

/* ─── HIDE STREAMLIT CHROME ─── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarNav"] { display: none !important; }

/* ─── HERO ─── */
.arin-hero {
    text-align: center;
    padding: 48px 24px 36px;
}
.arin-logo {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, #10a37f, #1a7f64);
    border-radius: 14px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    margin-bottom: 16px;
    box-shadow: 0 4px 20px rgba(16,163,127,0.35);
}
.arin-hero h1 {
    font-size: 1.6rem;
    font-weight: 600;
    color: #ececec;
    margin-bottom: 8px;
    letter-spacing: -0.3px;
}
.arin-hero p {
    font-size: 0.9rem;
    color: #8e8ea0;
    max-width: 480px;
    margin: 0 auto 20px;
    line-height: 1.6;
}
.arin-chips {
    display: flex;
    gap: 8px;
    justify-content: center;
    flex-wrap: wrap;
}
.arin-chip {
    background: #2f2f2f;
    border: 1px solid #3d3d3d;
    color: #b4b4c8;
    font-size: 0.78rem;
    padding: 6px 14px;
    border-radius: 999px;
    font-family: 'Sora', sans-serif;
}

/* ─── CHAT MESSAGES ─── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin-bottom: 4px !important;
    display: flex !important;
    align-items: flex-start !important;
    gap: 0 !important;
    box-shadow: none !important;
}

/* Hide default avatars */
[data-testid="stChatMessage"] > div:first-child {
    display: none !important;
}

/* The content wrapper */
[data-testid="stChatMessageContent"] {
    max-width: 72% !important;
    padding: 12px 16px !important;
    border-radius: 16px !important;
    font-size: 0.92rem !important;
    line-height: 1.65 !important;
    word-break: break-word !important;
}

/* ASSISTANT bubble — left aligned, dark gray */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageContent"]):nth-child(odd) {
    justify-content: flex-start !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageContent"]):nth-child(odd)
[data-testid="stChatMessageContent"] {
    background: #2f2f2f !important;
    color: #ececec !important;
    border-bottom-left-radius: 4px !important;
}

/* USER bubble — right aligned, green tint */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageContent"]):nth-child(even) {
    justify-content: flex-end !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageContent"]):nth-child(even)
[data-testid="stChatMessageContent"] {
    background: #1a3d2e !important;
    color: #d4f1e4 !important;
    border-bottom-right-radius: 4px !important;
}

/* ─── MARKDOWN TABLES (Gemini output) ─── */
[data-testid="stChatMessageContent"] table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 10px;
    background: #1a1a1a;
    border-radius: 10px;
    overflow: hidden;
}
[data-testid="stChatMessageContent"] th {
    background: #10a37f22;
    color: #10a37f;
    padding: 8px 12px;
    text-align: left;
    font-weight: 500;
    border-bottom: 1px solid #333;
}
[data-testid="stChatMessageContent"] td {
    padding: 7px 12px;
    color: #ccc;
    border-bottom: 1px solid #2a2a2a;
}
[data-testid="stChatMessageContent"] tr:last-child td {
    border-bottom: none;
}

/* ─── HEADINGS in chat ─── */
[data-testid="stChatMessageContent"] h3 {
    font-size: 0.9rem;
    color: #10a37f;
    font-weight: 600;
    margin: 14px 0 6px;
    letter-spacing: 0.2px;
}

/* ─── CHAT INPUT ─── */
[data-testid="stChatInput"],
[data-testid="stChatInputContainer"] {
    background: #2f2f2f !important;
    border: 1px solid #444 !important;
    border-radius: 14px !important;
    padding: 4px 4px 4px 16px !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputContainer"] textarea {
    background: transparent !important;
    color: #ececec !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.92rem !important;
    caret-color: #10a37f !important;
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInputContainer"] textarea::placeholder {
    color: #666 !important;
}
[data-testid="stChatInput"] button,
[data-testid="stChatInputContainer"] button {
    background: #10a37f !important;
    border-radius: 10px !important;
    color: white !important;
    border: none !important;
}
[data-testid="stChatInput"] button:hover,
[data-testid="stChatInputContainer"] button:hover {
    background: #0d8f6e !important;
}

/* ─── CAPTION ─── */
.stCaption, [data-testid="stCaption"] {
    color: #555 !important;
    font-size: 0.78rem !important;
    text-align: center;
}

/* ─── SPINNER ─── */
[data-testid="stSpinner"] > div {
    color: #10a37f !important;
}

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #212121; }
::-webkit-scrollbar-thumb { background: #3a3a3a; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #4a4a4a; }
</style>
""", unsafe_allow_html=True)

# ==============================
# HERO SECTION
# ==============================
st.markdown("""
<div class="arin-hero">
    <div class="arin-logo">🤖</div>
    <h1>PUSBIN Smart Assistant</h1>
    <p>Asisten analisis anggaran berbasis AI — baca data, hitung otomatis, susun tabel perhitungan dalam hitungan detik.</p>
    <div class="arin-chips">
        <span class="arin-chip">📊 Analisis Anggaran</span>
        <span class="arin-chip">🧮 Perhitungan Otomatis</span>
        <span class="arin-chip">⚡ Powered by Gemini</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.caption("💡 Coba: \"Hitung biaya perjalanan dinas luar kota 3 orang 2 hari\"")

# ==============================
# TAMPILKAN CHAT HISTORY
# ==============================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==============================
# CHAT INPUT
# ==============================
user_input = st.chat_input("Tanya Arin sesuatu...")

# ==============================
# 4. LOGIC AI
# ==============================
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Arin lagi mikir..."):
        context = get_excel_context(user_input)

        history_text = ""
        for m in st.session_state.messages:
            history_text += f"{m['role'].upper()}: {m['content']}\n"

        prompt = f"""
Kamu adalah sistem analis anggaran instansi pemerintah bernama Arin.

Riwayat Percakapan:
{history_text}

Gunakan data berikut sebagai database:
{context}

Instruksi:
- Identifikasi komponen biaya dari pertanyaan user
- Cocokkan dengan data SBM pada Excel
- Hitung sisa anggaran jika ada
- Gunakan HANYA data numerik yang muncul dalam tabel context. Jangan membuat asumsi tarif jika data ada.
- Fokus pada perhitungan, bukan jawaban umum
- Output WAJIB menggunakan tabel markdown

Format output:

### Tabel Perhitungan
| Komponen | Tarif | Jumlah | Total | Hari |
|----------|-------|--------|-------|-------|

### Ringkasan Anggaran
| Item | Nilai |
|------|------|

### Kesimpulan

Pertanyaan User:
{user_input}
"""
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            ai_reply = response.text or "Maaf, Arin tidak bisa memproses pertanyaan ini. Coba ulangi dengan kata yang lebih spesifik."
        except Exception as e:
            ai_reply = f"⚠️ Terjadi kesalahan: {str(e)}"

    with st.chat_message("assistant"):
        st.markdown(ai_reply)

    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
