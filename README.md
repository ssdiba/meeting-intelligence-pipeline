# meeting-intelligence-pipeline


I'm building this to turn a recorded meeting into something useful afterward: a short list of who agreed to do what, and a way to ask questions about past meetings without listening to them again.

It's a work in progress. Right now the repo only has the project setup, and I'm building the pipeline one stage at a time.

## How it's planned to work

You upload an audio file and Whisper transcribes it locally, so that part costs nothing. The transcript goes to an LLM that pulls out action items in a fixed format (task, owner, due date). Pydantic rejects anything that doesn't fit the schema.

Then a second pass checks each item against the transcript. LLMs like to fill in gaps, so this step drops anything the transcript doesn't support, like an owner nobody actually named. To test it, I'm writing transcripts that are designed to tempt the model into making things up.

Finally, the meetings get embedded and stored so they can be searched. A follow-up like "what did we agree on with X?" gets rewritten into a standalone question first, so words like "that" or "it" don't break the search.

## Not included yet

Live transcription. Everything runs after the meeting for now.

## Stack

Python, FastAPI, faster-whisper, Pydantic, Gemini and Groq free tiers, Supabase (pgvector)

## Results

Nothing yet. I'll add real numbers once I've run it against a test set.

## Running it

Coming once there's something to run.