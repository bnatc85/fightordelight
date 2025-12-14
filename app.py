import streamlit as st
import json
from datetime import datetime
import io

# Try to import audio recorder
try:
    from streamlit_mic_recorder import mic_recorder
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# Try to import speech recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="Fight or Delight",
    page_icon="✨",
    layout="centered"
)

# Background themes
THEMES = {
    "Purple Dream": """
        background: linear-gradient(135deg, #312e81 0%, #581c87 50%, #9d174d 100%);
    """,
    "Ocean Depths": """
        background: linear-gradient(135deg, #1e3a5f 0%, #164e63 50%, #115e59 100%);
    """,
    "Forest Night": """
        background: linear-gradient(135deg, #14532d 0%, #064e3b 50%, #134e4a 100%);
    """,
    "Sunset Glow": """
        background: linear-gradient(135deg, #7c2d12 0%, #7f1d1d 50%, #831843 100%);
    """,
    "Black": """
        background: linear-gradient(135deg, #111827 0%, #0f172a 50%, #18181b 100%);
    """,
    "Cotton Candy": """
        background: linear-gradient(135deg, #9d174d 0%, #86198f 50%, #5b21b6 100%);
    """,
    "Desert Sands": """
        background: linear-gradient(135deg, #78350f 0%, #713f12 50%, #7c2d12 100%);
    """,
    "Northern Lights": """
        background: linear-gradient(135deg, #064e3b 0%, #155e75 50%, #581c87 100%);
    """,
    "Cherry Blossom": """
        background: linear-gradient(135deg, #9f1239 0%, #9d174d 50%, #7f1d1d 100%);
    """,
    "Deep Space": """
        background: linear-gradient(135deg, #020617 0%, #1e1b4b 50%, #2e1065 100%);
    """
}

# Sentiment lexicon (VADER-style)
POSITIVE_WORDS = {
    'good': 1.9, 'great': 3.1, 'excellent': 3.4, 'amazing': 3.5, 'wonderful': 3.3,
    'fantastic': 3.4, 'awesome': 3.1, 'love': 3.2, 'loved': 3.2, 'loving': 3.0,
    'happy': 2.8, 'joy': 2.9, 'joyful': 3.0, 'delightful': 3.2, 'delight': 3.1,
    'pleasant': 2.4, 'pleased': 2.5, 'exciting': 2.8, 'excited': 2.9,
    'beautiful': 2.9, 'perfect': 3.0, 'best': 2.8, 'brilliant': 3.2,
    'fun': 2.5, 'funny': 2.4, 'laugh': 2.3, 'laughed': 2.3, 'smile': 2.1, 'smiled': 2.1,
    'nice': 1.8, 'cool': 1.8, 'pretty': 2.0, 'peaceful': 2.4, 'calm': 2.0,
    'success': 2.6, 'successful': 2.7, 'win': 2.5, 'won': 2.5, 'winning': 2.6,
    'celebrate': 2.7, 'celebration': 2.7, 'party': 2.0, 'grateful': 2.8,
    'thankful': 2.6, 'thanks': 1.9, 'thank': 1.8, 'blessed': 2.7, 'lucky': 2.4,
    'hope': 2.0, 'hopeful': 2.3, 'optimistic': 2.5, 'positive': 2.2,
    'enjoy': 2.4, 'enjoyed': 2.5, 'enjoying': 2.4, 'relaxed': 2.2, 'relaxing': 2.3,
    'proud': 2.5, 'accomplished': 2.7, 'achievement': 2.6, 'productive': 2.3,
    'helpful': 2.2, 'kind': 2.3, 'kindness': 2.5, 'sweet': 2.1, 'warm': 1.9,
    'incredible': 3.2, 'outstanding': 3.1, 'remarkable': 2.9, 'superb': 3.0,
    'terrific': 2.9, 'fabulous': 3.0, 'marvelous': 3.0, 'splendid': 2.8,
    'thrilled': 3.2, 'ecstatic': 3.5, 'elated': 3.3, 'overjoyed': 3.4, 'blissful': 3.2,
    'cheerful': 2.6, 'content': 2.3, 'satisfied': 2.4, 'fulfilling': 2.7, 'fulfilled': 2.8,
    'enthusiastic': 2.8, 'eager': 2.3, 'passionate': 2.7, 'inspired': 2.8, 'inspiring': 2.9,
    'motivated': 2.5, 'energized': 2.4, 'refreshed': 2.3, 'rejuvenated': 2.6, 'alive': 2.2,
    'friendly': 2.3, 'caring': 2.5, 'compassionate': 2.7, 'supportive': 2.5, 'generous': 2.6,
    'yay': 2.5, 'woohoo': 2.8, 'yeah': 1.8, 'yes': 1.6, 'definitely': 1.8,
    'healthy': 2.3, 'fit': 2.2, 'strong': 2.2, 'energetic': 2.4, 'vital': 2.3,
}

NEGATIVE_WORDS = {
    'bad': -2.1, 'terrible': -3.2, 'awful': -3.1, 'horrible': -3.3, 'worst': -3.4,
    'hate': -3.2, 'hated': -3.2, 'hating': -3.0, 'angry': -2.8, 'anger': -2.7,
    'sad': -2.5, 'sadness': -2.6, 'depressed': -3.1, 'depression': -3.0,
    'frustrated': -2.6, 'frustrating': -2.7, 'annoyed': -2.3, 'annoying': -2.4,
    'stressed': -2.5, 'stress': -2.4, 'stressful': -2.6, 'anxious': -2.4,
    'worried': -2.2, 'worry': -2.1, 'fear': -2.5, 'scared': -2.3, 'afraid': -2.3,
    'tired': -1.8, 'exhausted': -2.5, 'boring': -2.1, 'bored': -2.0,
    'disappointed': -2.6, 'disappointing': -2.7, 'upset': -2.4, 'unhappy': -2.5,
    'miserable': -3.0, 'painful': -2.7, 'pain': -2.4, 'hurt': -2.3, 'hurting': -2.4,
    'difficult': -1.8, 'hard': -1.5, 'tough': -1.6, 'rough': -1.8, 'struggle': -2.0,
    'fail': -2.4, 'failed': -2.5, 'failure': -2.7, 'lose': -2.2, 'lost': -2.3,
    'problem': -1.9, 'problems': -2.0, 'issue': -1.6, 'issues': -1.7,
    'wrong': -2.0, 'mistake': -2.1, 'mistakes': -2.2, 'error': -1.8,
    'stupid': -2.6, 'dumb': -2.4, 'ugly': -2.5, 'mean': -2.3, 'rude': -2.4,
    'sick': -2.0, 'ill': -1.9, 'disease': -2.3, 'cry': -2.1, 'cried': -2.2,
    'lonely': -2.4, 'alone': -1.8, 'helpless': -2.6, 'hopeless': -3.0,
    'disaster': -3.1, 'catastrophe': -3.6, 'crisis': -2.6, 'emergency': -2.3,
    'fight': -2.0, 'fighting': -2.1, 'conflict': -2.2, 'argument': -2.1,
    'devastated': -3.4, 'heartbroken': -3.3, 'crushed': -3.1, 'shattered': -3.2, 'broken': -2.8,
    'furious': -3.2, 'enraged': -3.3, 'livid': -3.1, 'outraged': -3.0, 'irate': -2.9,
    'terrified': -3.1, 'horrified': -3.2, 'petrified': -3.0, 'panicked': -2.8, 'paranoid': -2.5,
    'rejected': -2.8, 'abandoned': -3.0, 'betrayed': -3.2, 'deceived': -2.9, 'lied': -2.6,
    'sucks': -2.4, 'sucked': -2.5, 'stinks': -2.2, 'blows': -2.3, 'lame': -2.0,
    'crappy': -2.4, 'crap': -2.2, 'trash': -2.3, 'garbage': -2.4, 'junk': -2.0,
}

INTENSIFIERS = {
    'very': 1.5, 'really': 1.4, 'extremely': 1.8, 'absolutely': 1.7,
    'incredibly': 1.7, 'so': 1.3, 'super': 1.5, 'totally': 1.4,
    'completely': 1.5, 'utterly': 1.6, 'highly': 1.4, 'quite': 1.2,
}

NEGATIONS = ['not', "n't", 'never', 'no', 'none', 'nobody', 'nothing',
             'neither', 'nowhere', 'hardly', 'barely', 'scarcely']


def transcribe_audio(audio_bytes):
    """Transcribe audio bytes to text using speech recognition."""
    if not SPEECH_RECOGNITION_AVAILABLE:
        return None, "Speech recognition not available"

    try:
        import wave
        import tempfile
        import os

        recognizer = sr.Recognizer()

        # Try to convert audio using pydub if available
        try:
            from pydub import AudioSegment

            # Load audio from bytes
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))

            # Export as WAV to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
                audio_segment.export(tmp_path, format="wav")

            # Use the temporary WAV file for recognition
            with sr.AudioFile(tmp_path) as source:
                audio_data = recognizer.record(source)

            # Clean up temp file
            os.unlink(tmp_path)

        except ImportError:
            # Fallback: try direct reading (may not work with all formats)
            audio_file = io.BytesIO(audio_bytes)
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)

        # Use Google's free speech recognition
        text = recognizer.recognize_google(audio_data)
        return text, None
    except sr.UnknownValueError:
        return None, "Could not understand audio. Please try again."
    except sr.RequestError as e:
        return None, f"Speech recognition error: {e}"
    except Exception as e:
        return None, f"Error processing audio: {e}"


def analyze_sentiment(text):
    """Analyze sentiment of text using VADER-style approach."""
    import re
    words = re.sub(r'[^\w\s\']', '', text.lower()).split()

    score = 0
    positive_count = 0
    negative_count = 0
    positive_words_found = []
    negative_words_found = []

    for i, word in enumerate(words):
        word_score = 0

        if word in POSITIVE_WORDS:
            word_score = POSITIVE_WORDS[word]
        elif word in NEGATIVE_WORDS:
            word_score = NEGATIVE_WORDS[word]

        if word_score != 0:
            # Check for intensifiers
            intensifier = 1
            for j in range(max(0, i - 2), i):
                if words[j] in INTENSIFIERS:
                    intensifier = max(intensifier, INTENSIFIERS[words[j]])

            # Check for negations
            negated = False
            for j in range(max(0, i - 3), i):
                if any(neg in words[j] for neg in NEGATIONS):
                    negated = True
                    break

            word_score *= intensifier
            if negated:
                word_score *= -0.5

            score += word_score

            if word_score > 0:
                positive_count += 1
                positive_words_found.append(word)
            elif word_score < 0:
                negative_count += 1
                negative_words_found.append(word)

    # Normalize score
    normalized_score = score / (abs(score) + 5) if score != 0 else 0

    return {
        'score': normalized_score,
        'raw_score': score,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'positive_words': list(set(positive_words_found)),
        'negative_words': list(set(negative_words_found)),
        'total_words': len(words),
        'is_delight': normalized_score > 0.05,
        'is_fight': normalized_score < -0.05,
        'is_neutral': -0.05 <= normalized_score <= 0.05
    }


def load_journal():
    """Load journal entries from session state."""
    if 'journal_entries' not in st.session_state:
        st.session_state.journal_entries = []
    return st.session_state.journal_entries


def save_journal_entry(entry):
    """Save a journal entry."""
    if 'journal_entries' not in st.session_state:
        st.session_state.journal_entries = []
    st.session_state.journal_entries.insert(0, entry)
    # Keep only last 30 entries
    st.session_state.journal_entries = st.session_state.journal_entries[:30]


def delete_journal_entry(entry_id):
    """Delete a journal entry by ID."""
    st.session_state.journal_entries = [
        e for e in st.session_state.journal_entries if e['id'] != entry_id
    ]


# Initialize session state
if 'theme' not in st.session_state:
    st.session_state.theme = "Purple Dream"
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'day_description' not in st.session_state:
    st.session_state.day_description = ""

# Apply theme
theme_css = THEMES[st.session_state.theme]
st.markdown(f"""
<style>
    .stApp {{
        {theme_css}
    }}
    .main-container {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 1rem;
    }}
    .result-delight {{
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(20, 184, 166, 0.2));
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 20px;
        padding: 2rem;
    }}
    .result-fight {{
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(249, 115, 22, 0.2));
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 20px;
        padding: 2rem;
    }}
    .result-neutral {{
        background: linear-gradient(135deg, rgba(107, 114, 128, 0.2), rgba(100, 116, 139, 0.2));
        border: 1px solid rgba(107, 114, 128, 0.3);
        border-radius: 20px;
        padding: 2rem;
    }}
    .stat-box {{
        background: rgba(0, 0, 0, 0.2);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }}
    .journal-entry {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    h1, h2, h3, p, label {{
        color: white !important;
    }}
    .stTextArea textarea {{
        background: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px !important;
    }}
    .stButton button {{
        background: linear-gradient(135deg, #ec4899, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.5rem 2rem !important;
        font-weight: 600 !important;
    }}
    .stButton button:hover {{
        background: linear-gradient(135deg, #db2777, #7c3aed) !important;
    }}
    .stSelectbox > div > div {{
        background: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px !important;
    }}
    .educational-box {{
        background: rgba(139, 92, 246, 0.1);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }}
    /* Audio styling */
    .stAudio {{
        background: rgba(0, 0, 0, 0.2) !important;
        border-radius: 12px !important;
        padding: 0.5rem !important;
    }}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 1rem;">
    <p style="color: rgba(216, 180, 254, 0.8); font-size: 0.875rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">Presidential AI Challenge Submission</p>
    <p style="color: rgba(196, 181, 253, 0.6); font-size: 0.75rem; margin-bottom: 1rem;">by Alexander, Melissa, and Bonnie Rushing</p>
    <h1 style="font-size: 3rem; font-weight: 800; background: linear-gradient(to right, #f9a8d4, #c4b5fd, #a5b4fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">Fight or Delight</h1>
    <p style="color: rgba(196, 181, 253, 0.7);">Tell me about your day, and I'll tell you how it went</p>
</div>
""", unsafe_allow_html=True)

# Theme selector in sidebar
with st.sidebar:
    st.markdown("### Choose Theme")
    selected_theme = st.selectbox(
        "Background",
        list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.theme),
        label_visibility="collapsed"
    )
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()

# Educational section
with st.expander("Why Does Positive Communication Matter?"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Positive Communication**
        - Builds trust and connection
        - Improves mental health
        - Enhances problem-solving
        - Creates upward spirals
        """)
    with col2:
        st.markdown("""
        **Negative Communication**
        - Triggers stress responses
        - Damages relationships
        - Becomes self-fulfilling
        - Affects physical health
        """)
    st.markdown("""
    **The 5:1 Ratio**: Research shows healthy relationships maintain at least 5 positive interactions for every 1 negative.
    """)

# Main input
st.markdown("### How was your day?")

# Input mode toggle
voice_available = AUDIO_AVAILABLE and SPEECH_RECOGNITION_AVAILABLE
if voice_available:
    input_mode = st.radio(
        "Choose input method",
        ["Type", "Voice"],
        horizontal=True,
        label_visibility="collapsed"
    )
else:
    input_mode = "Type"

# Voice input section
if input_mode == "Voice" and voice_available:
    st.markdown("<p style='color: rgba(196, 181, 253, 0.7); text-align: center;'>Press Start, speak, then press Stop</p>", unsafe_allow_html=True)

    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹️ Stop Recording",
        just_once=False,
        use_container_width=True,
        key="voice_recorder"
    )

    if audio:
        st.audio(audio['bytes'], format="audio/wav")
        with st.spinner("Transcribing..."):
            transcribed_text, error = transcribe_audio(audio['bytes'])
            if transcribed_text:
                st.session_state.day_description = transcribed_text
                st.success("Transcription complete!")
            elif error:
                st.error(error)

# Text input
day_text = st.text_area(
    "Tell me about your day",
    value=st.session_state.day_description,
    height=150,
    placeholder="How was your day? Tell me about the good, the bad, and everything in between...",
    label_visibility="collapsed"
)

col1, col2 = st.columns([3, 1])
with col1:
    analyze_btn = st.button("✨ Analyze My Day", use_container_width=True)
with col2:
    reset_btn = st.button("🔄 Reset", use_container_width=True)

if reset_btn:
    st.session_state.analysis_result = None
    st.session_state.day_description = ""
    st.rerun()

if analyze_btn and day_text.strip():
    st.session_state.day_description = day_text
    st.session_state.analysis_result = analyze_sentiment(day_text)

# Results
if st.session_state.analysis_result:
    result = st.session_state.analysis_result

    if result['is_delight']:
        result_class = "result-delight"
        icon = "🎉"
        title = "A Delight!"
        message = "Sounds like you had a wonderful day!"
        title_color = "#6ee7b7"
    elif result['is_fight']:
        result_class = "result-fight"
        icon = "😔"
        title = "A Fight!"
        message = "Seems like today was a tough one. How could we make tomorrow better?"
        title_color = "#fca5a5"
    else:
        result_class = "result-neutral"
        icon = "😐"
        title = "Neutral"
        message = "A balanced day with ups and downs."
        title_color = "#d1d5db"

    st.markdown(f"""
    <div class="{result_class}">
        <div style="text-align: center;">
            <span style="font-size: 4rem;">{icon}</span>
            <h2 style="color: {title_color}; font-size: 2rem; margin: 0.5rem 0;">{title}</h2>
            <p style="color: rgba(255,255,255,0.6);">{message}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Score display
    score_pct = (result['score'] + 1) * 50
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; font-size: 0.875rem; margin-bottom: 0.5rem;">
            <span style="color: #fca5a5;">Fight</span>
            <span style="color: #d1d5db;">Neutral</span>
            <span style="color: #6ee7b7;">Delight</span>
        </div>
        <div style="height: 1rem; background: rgba(0,0,0,0.3); border-radius: 9999px; position: relative;">
            <div style="position: absolute; inset: 0; background: linear-gradient(to right, #ef4444, #9ca3af, #10b981); opacity: 0.3; border-radius: 9999px;"></div>
            <div style="position: absolute; top: 0; bottom: 0; left: {score_pct}%; width: 0.75rem; background: white; border-radius: 9999px; transform: translateX(-50%);"></div>
        </div>
        <p style="text-align: center; color: rgba(255,255,255,0.7); font-size: 0.875rem; margin-top: 0.5rem;">Score: {result['score']*100:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-box" style="background: rgba(16, 185, 129, 0.2);">
            <p style="font-size: 2rem; font-weight: bold; color: #6ee7b7; margin: 0;">{result['positive_count']}</p>
            <p style="color: rgba(167, 243, 208, 0.7); font-size: 0.875rem; margin: 0;">Positive words</p>
            <p style="color: rgba(167, 243, 208, 0.5); font-size: 0.75rem; margin: 0.25rem 0 0 0;">{', '.join(result['positive_words'][:5])}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-box" style="background: rgba(239, 68, 68, 0.2);">
            <p style="font-size: 2rem; font-weight: bold; color: #fca5a5; margin: 0;">{result['negative_count']}</p>
            <p style="color: rgba(254, 202, 202, 0.7); font-size: 0.875rem; margin: 0;">Negative words</p>
            <p style="color: rgba(254, 202, 202, 0.5); font-size: 0.75rem; margin: 0.25rem 0 0 0;">{', '.join(result['negative_words'][:5])}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<p style='text-align: center; color: rgba(255,255,255,0.5); font-size: 0.875rem;'>Analyzed {result['total_words']} words</p>", unsafe_allow_html=True)

# Journal Section
st.markdown("---")
st.markdown("### 📔 Daily Journal")
st.markdown("<p style='color: rgba(196, 181, 253, 0.6); font-size: 0.875rem;'>Reflect on your day and plan for tomorrow</p>", unsafe_allow_html=True)

reflection = st.text_area("How do you feel about today? What stood out?", placeholder="Today I felt... The best part was... I struggled with...", key="reflection")
improvements = st.text_area("What could you do differently tomorrow?", placeholder="Tomorrow I will... I want to improve... I'll try to...", key="improvements")
gratitude = st.text_area("Three things you're grateful for today", placeholder="1. I'm grateful for...\n2. I appreciate...\n3. I'm thankful for...", key="gratitude")

if st.button("💾 Save Journal Entry", use_container_width=True):
    if reflection.strip() or improvements.strip() or gratitude.strip():
        entry = {
            'id': datetime.now().timestamp(),
            'date': datetime.now().strftime("%A, %B %d, %Y"),
            'timestamp': datetime.now().isoformat(),
            'day_description': st.session_state.day_description,
            'score': st.session_state.analysis_result['score'] if st.session_state.analysis_result else 0,
            'result': 'Delight' if st.session_state.analysis_result and st.session_state.analysis_result['is_delight'] else ('Fight' if st.session_state.analysis_result and st.session_state.analysis_result['is_fight'] else 'Neutral'),
            'reflection': reflection,
            'improvements': improvements,
            'gratitude': gratitude
        }
        save_journal_entry(entry)
        st.success("Entry saved successfully!")
        st.rerun()
    else:
        st.warning("Please write something before saving!")

# Past entries
journal_entries = load_journal()
if journal_entries:
    with st.expander(f"📅 Past Journal Entries ({len(journal_entries)})"):
        for entry in journal_entries:
            result_color = "#6ee7b7" if entry['result'] == 'Delight' else ("#fca5a5" if entry['result'] == 'Fight' else "#d1d5db")
            st.markdown(f"""
            <div class="journal-entry">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <div>
                        <p style="color: rgba(255,255,255,0.8); font-weight: 500; font-size: 0.875rem; margin: 0;">{entry['date']}</p>
                        <span style="background: rgba(255,255,255,0.1); color: {result_color}; font-size: 0.75rem; padding: 0.125rem 0.5rem; border-radius: 9999px;">{entry['result']} ({entry['score']*100:.0f}%)</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if entry.get('day_description'):
                st.markdown(f"<p style='color: rgba(196, 181, 253, 0.6); font-size: 0.75rem; text-transform: uppercase;'>What I said</p><p style='color: rgba(255,255,255,0.6); font-size: 0.875rem;'>{entry['day_description'][:100]}...</p>", unsafe_allow_html=True)
            if entry.get('reflection'):
                st.markdown(f"<p style='color: rgba(196, 181, 253, 0.6); font-size: 0.75rem; text-transform: uppercase;'>Reflection</p><p style='color: rgba(255,255,255,0.7); font-size: 0.875rem;'>{entry['reflection']}</p>", unsafe_allow_html=True)
            if entry.get('improvements'):
                st.markdown(f"<p style='color: rgba(196, 181, 253, 0.6); font-size: 0.75rem; text-transform: uppercase;'>Tomorrow's Goals</p><p style='color: rgba(255,255,255,0.7); font-size: 0.875rem;'>{entry['improvements']}</p>", unsafe_allow_html=True)
            if entry.get('gratitude'):
                st.markdown(f"<p style='color: rgba(196, 181, 253, 0.6); font-size: 0.75rem; text-transform: uppercase;'>Gratitude</p><p style='color: rgba(255,255,255,0.7); font-size: 0.875rem;'>{entry['gratitude']}</p>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            if st.button(f"🗑️ Delete", key=f"delete_{entry['id']}"):
                delete_journal_entry(entry['id'])
                st.rerun()

# Footer
st.markdown("""
<p style="text-align: center; color: rgba(196, 181, 253, 0.4); font-size: 0.875rem; margin-top: 2rem;">
    Powered by VADER-style sentiment analysis
</p>
""", unsafe_allow_html=True)
