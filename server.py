from fastapi import FastAPI, Request
from supabase import create_client

app = FastAPI()

# ── YOUR DATABASE CREDENTIALS ─────────────────────────────────────────────
SUPABASE_URL = "https://fisiwpdpvalyvvmixbap.supabase.co"
# REPLACE THE TEXT BELOW WITH YOUR ACTUAL SUPABASE PUBLISHABLE KEY
SUPABASE_KEY = "sb_publishable_y-gLi7LBisf3qViqg_ccow_GJLTgpPh"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── THE WEBHOOK (This catches the text from Recall.ai) ────────────────────
@app.post("/webhook/recall")
async def receive_transcript(request: Request):
    try:
        data = await request.json()
        
        # Check if the incoming data contains transcript words
        if 'data' in data and 'transcript' in data['data']:
            transcript_data = data['data']['transcript']
            speaker = transcript_data.get('speaker', 'Unknown')
            words = transcript_data.get('words', '')
            
            # If the student actually said something, save it!
            if words.strip():
                supabase.table("live_transcripts").insert({
                    "speaker": speaker, 
                    "transcript": words
                }).execute()
                print(f"✅ Saved: {speaker} -> {words}")
                
        return {"status": "success"}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error"}

# ── A simple test page to make sure the server is online ──────────────────
@app.get("/")
def home():
    return {"message": "The ClassPulse Catcher is live and ready!"}
