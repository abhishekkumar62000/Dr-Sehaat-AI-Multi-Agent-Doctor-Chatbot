# Quick Start Guide - Dr. Sehaat Healthcare Chatbot

## 🚀 5-Minute Setup

### 1. Install Dependencies (1 min)
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure API Key (1 min)
- Get free Groq API key: https://console.groq.com
- Edit `backend/.env` and add your GROQ_API_KEY

### 3. Start Backend (1 min)
```bash
cd backend
python app.py
```
Expected output:
```
🏥 Healthcare AI Chatbot - Backend Server
Starting server...
Visit: http://localhost:5000
```

### 4. Open Frontend (1 min)
- Open `frontend/index.html` in your browser
- Or run: `cd frontend && python -m http.server 8000`
- Visit: http://localhost:8000

### 5. Start Chatting! (1 min)
- Type your health concerns
- Get AI-powered healthcare guidance
- Enjoy the beautiful ChatGPT-like interface!

---

## 📦 Project Files

### Backend Files
- `app.py` - Flask API server
- `medical_bot.py` - LangChain integration
- `config.py` - Settings
- `prompts.py` - Healthcare prompts
- `utils.py` - Helper functions
- `requirements.txt` - Dependencies
- `.env` - Configuration (create from .env.example)

### Frontend Files
- `index.html` - Main page
- `css/style.css` - Beautiful styling
- `js/chat.js` - Chat logic

---

## 🎯 Common Tasks

### Change Model
Edit `backend/config.py`:
```python
GROQ_MODEL = "llama2-70b-4096"  # Change this
```

### Customize Healthcare Prompts
Edit `backend/prompts.py`:
```python
HEALTHCARE_SYSTEM_PROMPT = """Your custom prompt here"""
```

### Add More API Endpoints
Edit `backend/app.py` and add new `@app.route()` functions

### Deploy Frontend
1. Run: `python -m http.server 8000`
2. Or use: Vercel, Netlify, GitHub Pages
3. Update `API_BASE_URL` in `frontend/js/chat.js`

---

## ✅ Test Your Setup

### Check Backend
```bash
curl http://localhost:5000/api/health
```
Expected: `{"success":true,"data":{"status":"online"}}`

### Test Chat
```bash
curl -X POST http://localhost:5000/api/chat/new-session
```
Expected: `{"success":true,"data":{"session_id":"..."}}`

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot connect to server" | Run `python app.py` in backend folder |
| "API Key error" | Get key from https://console.groq.com |
| "Port 5000 in use" | Kill process: `lsof -ti:5000 \| xargs kill -9` |
| "CORS error" | Make sure backend is running |
| "Slow responses" | Try smaller model or reduce MAX_TOKENS |

---

## 📚 Next Steps

1. ✅ Customize healthcare prompts
2. ✅ Add database for chat history
3. ✅ Integrate with patient records
4. ✅ Add authentication
5. ✅ Deploy to production

---

## 🎓 Learning Resources

- LangChain: https://python.langchain.com
- Groq API: https://console.groq.com/docs
- Flask: https://flask.palletsprojects.com
- REST API: https://restfulapi.net

---

**Ready to serve patients with AI! 🏥💬**
