# Backend

```bash
cd backend
pip3 install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Tests: `python3 -m pytest`.

The dashboard snapshot changes on a two-second time bucket. Chat state is process-local only and is discarded on restart. To replace the demo AI, provide an object implementing `AIService.stream(message, snapshot)` and inject it in the chat route.
