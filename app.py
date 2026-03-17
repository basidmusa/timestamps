import streamlit as st
import re

def convert_srt_time(srt_time):
    """Converts 00:00:20,000 to 00:20 or 1:05:20."""
    parts = srt_time.split(',')[0].split(':')
    hours, minutes, seconds = parts[0], parts[1], parts[2]
    
    if int(hours) > 0:
        return f"{int(hours)}:{minutes}:{seconds}"
    return f"{minutes}:{seconds}"

def parse_srt(srt_content):
    # Regex to find timestamp blocks and the first line of text following them
    pattern = re.compile(r'\d+\s+(\d{2}:\d{2}:\d{2},\d{3}) --> .+\s+(.+)')
    matches = pattern.findall(srt_content)
    
    chapters = []
    for i, match in enumerate(matches):
        time_str = convert_srt_time(match[0])
        # Force the very first entry to be 00:00 for YouTube requirements
        if i == 0:
            time_str = "00:00"
        
        text = match[1].strip()
        chapters.append(f"{time_str} {text}")
        
    return chapters

# --- Streamlit UI ---
st.set_page_config(page_title="SRT to YouTube Chapters", page_icon="🎬")

st.title("🎬 SRT to YouTube Chapters")
st.markdown("Upload your `.srt` file to generate copy-paste timestamps for your video description.")

uploaded_file = st.file_uploader("Choose an SRT file", type="srt")

if uploaded_file is not None:
    # Read file
    content = uploaded_file.getvalue().decode("utf-8")
    
    # Process
    try:
        chapter_list = parse_srt(content)
        
        st.subheader("YouTube Ready Timestamps")
        
        # Join list into a single string
        final_text = "\n".join(chapter_list)
        
        # Display in a text area for easy copying
        st.text_area("Copy the text below:", value=final_text, height=400)
        
        st.success(f"Successfully extracted {len(chapter_list)} timestamps!")
        st.info("💡 Tip: YouTube requires at least 3 timestamps, and the first one must be 00:00 (we've handled that for you!).")
        
    except Exception as e:
        st.error(f"Error processing file: {e}")

else:
    st.info("Please upload an SRT file to begin.")
