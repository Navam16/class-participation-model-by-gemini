import streamlit as st
import requests
import pandas as pd
from supabase import create_client
import time

# ==========================================
# 1. PASTE YOUR CREDENTIALS HERE
# ==========================================
RECALL_API_KEY = "66b6f5a760a2aeabd216379937d1a9cb004369d99"  # Your Recall.ai API Key
SUPABASE_URL = "https://fisiwpdpvalyvvmixbap.supabase.co" # Your Supabase Project URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpc2l3cGRwdmFseXZ2bWl4YmFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyODAwNDMsImV4cCI6MjA4OTg1NjA0M30.Iw9AuJLv929sQ8BmyWZI3-W5ar0x3x56Pf7F-c_7KjQ" # Your Supabase Anon/Public Key

# API URL for Asia Pacific (Tokyo) region
RECALL_API_URL = "https://ap-northeast-1.recall.ai/api/v1/bot/"

# Connect to Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. STREAMLIT UI SETUP
# ==========================================
st.set_page_config(page_title="Live Class Participation", layout="wide")
st.title("🎓 Live Class Participation Scorecard")
st.markdown("---")

# Sidebar for Launching the Bot
with st.sidebar:
    st.header("Step 1: Invite Bot")
    meet_url = st.text_input("Enter Google Meet Link:", placeholder="https://meet.google.com/xxx-xxxx-xxx")
    
    if st.button("🚀 Launch Live Bot"):
        if meet_url:
            # This JSON configuration FORCES Low Latency (Live) Mode
            payload = {
                "meeting_url": meet_url,
                "bot_name": "ClassPulse_Live_Assistant",
                "transcription_options": { "provider": "recallai" },
                "recording_config": {
                    "transcript": {
                        "provider": {
                            "recallai_streaming": { 
                                "mode": "prioritize_low_latency" # <--- THE LIVE SWITCH
                            }
                        }
                    }
                }
            }
            headers = {
                "Authorization": f"Token {RECALL_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Send request to Recall
            response = requests.post(RECALL_API_URL, json=payload, headers=headers)
            
            if response.status_code == 201:
                st.success("Bot is joining! Switch to Meet and click ADMIT.")
            else:
                st.error(f"Failed: {response.text}")
        else:
            st.warning("Please enter a meeting URL first.")

# ==========================================
# 3. LIVE DATA VISUALIZATION
# ==========================================
# ==========================================
# 3. LIVE DATA VISUALIZATION
# ==========================================
st.header("Step 2: Real-Time Participation Scores")
chart_placeholder = st.empty()

# This loop runs forever while the app is open
while True:
    try:
        # 1. CHANGED 'student_name' TO 'speaker'
        res = supabase.table("live_transcripts").select("speaker").execute()
        df = pd.DataFrame(res.data)
        
        if not df.empty:
            # 2. CHANGED 'student_name' TO 'speaker'
            score_data = df['speaker'].value_counts().reset_index()
            score_data.columns = ['Student', 'Participation Points']
            
            # Update the chart in the placeholder
            with chart_placeholder.container():
                st.bar_chart(data=score_data, x='Student', y='Participation Points')
                st.write(f"Total entries captured: {len(df)}")
        else:
            chart_placeholder.info("Waiting for students to speak... (Ensure Bot is Admitted)")
            
    except Exception as e:
        st.error(f"Connection Error: {e}")
        
    # Refresh every 5 seconds
    time.sleep(5)
