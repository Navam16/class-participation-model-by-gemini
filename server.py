from fastapi import FastAPI, Request
from supabase import create_client

app = FastAPI()

# ── YOUR DATABASE CREDENTIALS ─────────────────────────────────────────────
SUPABASE_URL = "https://fisiwpdpvalyvvmixbap.supabase.co"
# REPLACE THE TEXT BELOW WITH YOUR ACTUAL SUPABASE PUBLISHABLE KEY
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpc2l3cGRwdmFseXZ2bWl4YmFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyODAwNDMsImV4cCI6MjA4OTg1NjA0M30.Iw9AuJLv929sQ8BmyWZI3-W5ar0x3x56Pf7F-c_7KjQ"

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
