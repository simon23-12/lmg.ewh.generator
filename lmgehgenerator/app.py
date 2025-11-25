{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
from groq import Groq\
import os\
\
# --- 1. KONFIGURATION UND UTILITY FUNKTIONEN ---\
\
# Wortzahl-Limits basierend auf den NRW-Vorgaben\
WORD_LIMITS = \{\
    "GK (Lesen/Schreiben, Q-Phase)": 800,\
    "LK (Lesen/Schreiben, Q-Phase)": 1000,\
    "Mediation/Sprachmittlung": 650,\
    "EF/GK (Allgemein)": 600,\
    "LK Q-Phase (Allgemein)": 800\
\}\
\
def load_example(thema):\
    """L\'e4dt die passende .md Vorlage aus dem 'vorlagen' Ordner."""\
    file_path = os.path.join("vorlagen", f"\{thema\}.md")\
    if os.path.exists(file_path):\
        with open(file_path, "r", encoding="utf-8") as f:\
            return f.read()\
    return "Fehler: Beispiel-Vorlage nicht gefunden."\
\
def count_words(text):\
    """Z\'e4hlt die W\'f6rter im Eingabetext."""\
    # Split auf Leerzeichen und filtert leere Strings heraus\
    return len([word for word in text.split() if word])\
\
# --- 2. STREAMLIT APP LAYOUT ---\
\
st.set_page_config(page_title="NRW EH-Generator", page_icon="\uc0\u55356 \u57235 ")\
st.title("\uc0\u55356 \u57235  NRW Erwartungshorizont-Generator (Kostenlos)")\
st.caption("Powered by Llama 3 & Groq API")\
\
# Sidebar f\'fcr Einstellungen\
st.sidebar.header("\uc0\u9881 \u65039  Konfiguration")\
api_key = st.sidebar.text_input("Groq API Key (kostenlos von console.groq.com)", type="password")\
st.sidebar.markdown("---")\
\
# Selection 1: Course Type (GK/LK/EF)\
course_type = st.sidebar.selectbox(\
    "1. Kursniveau:",\
    ["GK/EF (Grundkurs)", "LK (Leistungskurs)"]\
)\
\
# Selection 2: Task Type (used for Word Count Validation)\
task_type = st.sidebar.selectbox(\
    "2. Aufgabentyp (zur Wortzahl-Pr\'fcfung):",\
    list(WORD_LIMITS.keys())\
)\
st.sidebar.markdown("---")\
\
# Selection 3: LLM Template (to improve EH quality)\
example_theme = st.sidebar.selectbox(\
    "3. W\'e4hle das am besten passende Musterbeispiel (f\'fcr die KI-F\'fchrung):",\
    ["Q1_American_Dream", "Q1_Nigeria", "Q1_Gender_Identity", "Q1_Monarchy"] \
)\
st.sidebar.markdown("---")\
\
# Main Content Area\
st.subheader("\uc0\u55357 \u56541  Klausurtext Eingabe")\
st.markdown("Bitte **kopiere den vollst\'e4ndigen Klausurtext** (Source Text & Aufgaben) hier ein.")\
text_input = st.text_area("Klausurtext (Copy/Paste):", height=400)\
\
# --- 3. WORTZAHL-VALIDIERUNG ---\
word_count = count_words(text_input)\
# W\'e4hlt das Limit basierend auf der Auswahl aus, Standard ist 800\
limit = WORD_LIMITS.get(task_type, 800) \
\
# Anzeige der Wortzahl\
st.info(f"Aktuelle Wortzahl: **\{word_count\}** W\'f6rter. Das Limit f\'fcr '\{task_type\}' ist **\{limit\}** W\'f6rter.")\
\
# Warnung bei \'dcberschreitung\
if word_count > limit:\
    st.warning(f"\uc0\u9888 \u65039  ACHTUNG: Die Wortzahl (\{word_count\}) \'fcberschreitet die empfohlene Obergrenze (\{limit\}) f\'fcr **\{task_type\}**.")\
elif word_count < 200 and word_count > 0:\
    st.warning("\uc0\u9888 \u65039  WARNUNG: Der Text ist sehr kurz. Bitte pr\'fcfen Sie, ob Sie den vollst\'e4ndigen Source Text und die Aufgabenstellung eingef\'fcgt haben.")\
\
\
# --- 4. EXECUTION ---\
if st.button("\uc0\u55357 \u56960  Erwartungshorizont erstellen"):\
    if not api_key:\
        st.error("Bitte gib den Groq API Key in der Seitenleiste ein.")\
    elif not text_input:\
        st.error("Bitte f\'fcge den Klausurtext in das Eingabefeld ein.")\
    else:\
        # LLM Call Logic\
        client = Groq(api_key=api_key)\
        \
        # Lade das relevante Muster aus dem 'vorlagen' Ordner\
        muster_eh = load_example(example_theme)\
        \
        # System Prompt: Anpassung an das ausgew\'e4hlte Kursniveau\
        system_prompt = f"""\
        Du bist ein Fachleiter f\'fcr Englisch in Nordrhein-Westfalen (NRW) f\'fcr das Kursniveau \{course_type\}. \
        Deine Hauptaufgabe ist es, f\'fcr den vom User bereitgestellten Klausurtext einen detaillierten Erwartungshorizont (EH) zu erstellen.\
        \
        **BEFOLGE STRENG DIE VORGABEN DES FOLGENDEN MUSTERBEISPIELS:**\
        Das Musterbeispiel unten zeigt dir das exakte Format (AFB I, II, III) und die Punkteverteilung.\
        \
        ### MUSTERBEISPIEL ANFANG (Formatvorlage: \{example_theme\}) ###\
        \{muster_eh\} \
        ### MUSTERBEISPIEL ENDE ###\
        \
        Erstelle nun f\'fcr den neuen Input-Text (Wortzahl: \{word_count\}) einen EH im exakt gleichen Format und Stil.\
        """\
\
        with st.spinner(f'KI analysiert den Text und orientiert sich an \{example_theme\}.md...'):\
            try:\
                chat_completion = client.chat.completions.create(\
                    messages=[\
                        \{"role": "system", "content": system_prompt\},\
                        \{"role": "user", "content": text_input\}\
                    ],\
                    model="llama3-70b-8192", \
                    temperature=0.5,\
                )\
                st.subheader("\uc0\u9989  Generierter Erwartungshorizont")\
                st.markdown(chat_completion.choices[0].message.content)\
            except Exception as e:\
                st.error(f"Fehler bei der Groq API: \{e\}")}