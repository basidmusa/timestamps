import streamlit as st
import re
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Load the NLP model (Cached so it only loads once)
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def srt_time_to_yt(srt_time):
    parts = srt_time.split(',')[0].split(':')
    h, m, s = parts[0], parts[1], parts[2]
    return f"{int(h)}:{m}:{s}" if int(h) > 0 else f"{m}:{s}"

def parse_srt(content):
    # Extracts timestamps and text lines
    pattern = re.compile(r'\d+\s+(\d{2}:\d{2}:\d{2},\d{3}) --> .+\s+((?:(?!\d+\s+\d{2}:).*\n?)+)')
    matches = pattern.findall(content)
    times = [m[0] for m in matches]
    texts = [m[1].replace('\n', ' ').strip() for m in matches]
    return times, texts

# --- UI Setup ---
st.set_page_config(page_title="AI Topic Chapter Generator", page_icon="🧠")
st.title("🧠 AI-Powered YouTube Chapters")
st.markdown("This app detects **topic changes** in your SRT file using Semantic Analysis.")

model = load_model()

uploaded_file = st.file_uploader("Upload SRT File", type="srt")

if uploaded_file:
    content = uploaded_file.getvalue().decode("utf-8")
    times, texts = parse_srt(content)
    
    col1, col2 = st.columns(2)
    with col1:
        sensitivity = st.slider("Topic Change Sensitivity", 0.1, 0.9, 0.4, help="Lower = more chapters, Higher = fewer chapters.")
    with col2:
        min_gap = st.slider("Min. Chapter Length (lines)", 5, 50, 15)

    if st.button("Generate Smart Chapters"):
        with st.spinner("Analyzing context..."):
            # 1. Convert text to vectors
            embeddings = model.encode(texts, convert_to_tensor=True)
            
            chapters = [f"00:00 Introduction"]
            last_idx = 0
            
            # 2. Compare window averages to find "meaning shifts"
            for i in range(min_gap, len(embeddings) - min_gap):
                # Compare the "vibe" of the previous window to the next window
                prev_window = embeddings[i-min_gap:i].mean(dim=0)
                next_window = embeddings[i:i+min_gap].mean(dim=0)
                
                similarity = util.cos_sim(prev_window, next_window).item()
                
                if similarity < sensitivity and (i - last_idx) > min_gap:
                    timestamp = srt_time_to_yt(times[i])
                    # Take first 5 words of the new section as a placeholder title
                    title = " ".join(texts[i].split()[:5]).capitalize()
                    chapters.append(f"{timestamp} {title}...")
                    last_idx = i
            
            st.subheader("Generated Chapters")
            final_output = "\n".join(chapters)
            st.text_area("Copy for YouTube Description:", value=final_output, height=300)
            st.success(f"Found {len(chapters)} distinct topics!")
