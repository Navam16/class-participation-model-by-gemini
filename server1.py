from fastapi import FastAPI, Request
from supabase import create_client
import traceback

app = FastAPI()

# ── CREDENTIALS ──────────────────────────────────────────────────────────────
SUPABASE_URL = "https://fisiwpdpvalyvvmixbap.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpc2l3cGRwdmFseXZ2bWl4YmFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyODAwNDMsImV4cCI6MjA4OTg1NjA0M30.Iw9AuJLv929sQ8BmyWZI3-W5ar0x3x56Pf7F-c_7KjQ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def extract_text_from_words(words):
    """
    Recall.ai sends words as either:
      - a plain string  (older / non-live mode)
      - a list of dicts: [{"text": "hello", "start_time": 0.1, ...}, ...]
    This handles both.
    """
    if isinstance(words, str):
        return words.strip()
    if isinstance(words, list):
        return " ".join(w.get("text", "") for w in words).strip()
    return ""


@app.post("/webhook/recall")
async def receive_transcript(request: Request):
    try:
        data = await request.json()
        print(f"📥 Incoming payload keys: {list(data.keys())}")

        # ── Recall.ai sends different shapes depending on event type ──────────
        # Shape 1: { "event": "transcript.data", "data": { "transcript": {...} } }
        # Shape 2: { "data": { "transcript": {...} } }
        # Shape 3 (live/streaming): words is a list of word objects

        transcript_data = None

        # Try shape 1 / 2
        if "data" in data and isinstance(data["data"], dict):
            inner = data["data"]
            if "transcript" in inner:
                transcript_data = inner["transcript"]
            elif "speaker" in inner:
                # Already flat — some webhook versions send it flat
                transcript_data = inner

        if not transcript_data:
            print(f"⚠️  No transcript found in payload: {data}")
            return {"status": "no_transcript"}

        speaker  = transcript_data.get("speaker", "Unknown")
        words_raw = transcript_data.get("words", "")
        text     = extract_text_from_words(words_raw)

        # Also check for 'text' field directly (some Recall versions)
        if not text:
            text = transcript_data.get("text", "").strip()

        if text:
            supabase.table("live_transcripts").insert({
                "speaker":    speaker,
                "transcript": text
            }).execute()
            print(f"✅ Saved | {speaker}: {text[:80]}")
        else:
            print(f"ℹ️  Empty transcript — skipping save")

        return {"status": "success"}

    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}


@app.post("/webhook/recall/status")
async def bot_status(request: Request):
    """
    Recall also sends bot status events (joining, in_call, done).
    Log them but don't fail.
    """
    try:
        data = await request.json()
        event = data.get("event", "unknown")
        print(f"🤖 Bot status event: {event}")
        return {"status": "ok"}
    except Exception:
        return {"status": "ok"}


@app.get("/")
def home():
    return {
        "message": "ClassPulse server is live",
        "endpoints": ["/webhook/recall", "/webhook/recall/status"]
    }
