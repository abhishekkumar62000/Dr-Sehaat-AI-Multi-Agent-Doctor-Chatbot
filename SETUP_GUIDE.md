# 🏥 DR. SEHAAT - COMPLETE SETUP GUIDEEEEe

## What You're Getting 

A **PRODUCTION-READY** AI Healthcare Chatbot with:
- ✅ Beautiful ChatGPT-like UI
- ✅ Groq API Integration (Fast & Free)
- ✅ LangChain for Advanced NLP
- ✅ Professional Medical Prompts
- ✅ Emergency Detection
- ✅ Fully Responsive Design
- ✅ Real-time Streaming Responses
- ✅ Complete Backend API
- ✅ Docker Support
- ✅ 4000+ lines of code

---

## 📋 SYSTEM REQUIREMENTS

✅ Windows, Mac, or Linux
✅ Python 3.8 or higher
✅ 4GB RAM minimum
✅ Internet connection (for Groq API)
✅ Free Groq API account

---

## 🎯 STEP-BY-STEP INSTALLATION

### STEP 1: Get Your Free Groq API Key (2 minutes)

1. Open: https://console.groq.com/keys
2. Click "Create API Key"
3. Copy the key to clipboard
4. **Don't share this key with anyone!**

> Note: Free tier allows 30 requests per minute - perfect for development

---

### STEP 2: Navigate to Chatbot Folder

**Windows:**
```cmd
cd c:\Users\DELL\Desktop\Chatbot
```

**Mac/Linux:**
```bash
cd ~/Desktop/Chatbot
```

---

### STEP 3: Run Automated Setup (Windows)

**Double-click:** `setup_windows.bat`

This will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create .env file

**OR Manual Setup:**
```cmd
python -m venv venv
venv\Scripts\activate
cd backend
pip install -r requirements.txt
cd ..
```

---

### STEP 4: Configure API Key

1. Open: `backend/.env`
2. Replace `GROQ_API_KEY=` with your actual key:
   ```
   GROQ_API_KEY=gsk_your_actual_key_here
   ```
3. Save file

---

### STEP 5: Start the Application

**Option 1: Automatic (Recommended)**
```cmd
python run_dev_servers.py
```
This starts both backend (5000) and frontend (8000) automatically!

**Option 2: Manual**

Terminal 1 - Backend:
```cmd
cd backend
python app.py
```

Terminal 2 - Frontend:
```cmd
cd frontend
python -m http.server 8000
```

---

### STEP 6: Open in Browser

Visit: **http://localhost:8000**

🎉 **You're done! Start chatting!**

---

## 🚀 QUICK TROUBLESHOOTING

### Problem: "Python not found"
**Solution:** 
- Install Python from https://www.python.org
- Check "Add Python to PATH" during installation
- Restart terminal

### Problem: "API Key error"
**Solution:**
- Verify `.env` file exists in `backend/` folder
- Check API key is correct
- Get new key from https://console.groq.com/keys

### Problem: "Cannot connect to server"
**Solution:**
- Ensure backend is running (port 5000)
- Check firewall settings
- Try: http://localhost:5000/api/health

### Problem: "Slow responses"
**Solution:**
- Check internet connection
- Try reducing MAX_TOKENS in `backend/config.py`
- Change model (see Advanced Configuration)

### Problem: "Port already in use"
**Solution:**
```cmd
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :5000   # Windows
```

---

## 🎨 FEATURES & CAPABILITIES

### Chat Features
- 💬 One-to-one conversations
- 🏥 Healthcare-specialized responses
- 📱 Mobile-responsive design
- 🌙 Dark theme (easy on eyes)
- 💾 Chat history
- ⚡ Real-time responses

### Medical Features
- 🚨 Emergency detection
- 🩺 Symptom guidance
- 💊 Medication information
- 🧠 Mental health support
- 🏃 Wellness recommendations
- 🚑 Know when to call emergency

### AI Features
- 🤖 LangChain integration
- 📊 NLP processing
- 💭 Context understanding
- 🎯 Multi-turn conversations
- 📈 Conversation history

---

## 🔧 ADVANCED CONFIGURATION

### Change AI Model

Edit `backend/config.py`:
```python
# Line 10 - Change this:
GROQ_MODEL = "mixtral-8x7b-32768"

# To one of these options:
GROQ_MODEL = "llama2-70b-4096"       # Most capable
GROQ_MODEL = "gemma-7b-it"            # Fastest
GROQ_MODEL = "openhermes-2.5-mistral-7b"  # Most creative
```

### Customize Healthcare Prompts

Edit `backend/prompts.py`:
```python
HEALTHCARE_SYSTEM_PROMPT = """
You are Dr. [YourName], an AI healthcare assistant...
"""
```

### Adjust Response Quality

Edit `backend/config.py`:
```python
TEMPERATURE = 0.7      # Higher = more creative (0-1)
MAX_TOKENS = 2048      # Longer = more detailed responses
```

---

## 🌐 DEPLOY TO PRODUCTION

### Option 1: Using Docker (Easiest)

```bash
# Make sure Docker is installed
docker-compose up -d

# Visit: http://localhost:8000
```

### Option 2: Cloud Deployment

**Heroku:**
1. Push code to GitHub
2. Connect to Heroku
3. Set environment variables
4. Deploy

**Render/Railway/Vercel:**
- Similar process
- Add deployment files

### Option 3: VPS/Server

1. Install Python on server
2. Clone repository
3. Setup virtual environment
4. Configure nginx/Apache
5. Run with gunicorn

---

## 📊 PROJECT STRUCTURE

```
Chatbot/
├── backend/
│   ├── app.py              # Flask API
│   ├── medical_bot.py      # AI Logic
│   ├── config.py           # Settings
│   ├── prompts.py          # Healthcare prompts
│   ├── utils.py            # Helpers
│   ├── requirements.txt    # Dependencies
│   ├── .env               # Your API keys
│   └── Dockerfile         # Docker config
│
├── frontend/
│   ├── index.html         # Main UI
│   ├── css/
│   │   └── style.css      # Beautiful styling
│   ├── js/
│   │   └── chat.js        # Chat logic
│   ├── assets/            # Images
│   └── Dockerfile         # Docker config
│
├── run_dev_servers.py     # Start both servers
├── setup_windows.bat      # Auto setup (Windows)
├── setup_linux_mac.sh     # Auto setup (Mac/Linux)
├── docker-compose.yml     # Docker orchestration
├── README.md              # Full documentation
├── QUICK_START.md         # Quick start guide
└── .env.example           # Example config
```

---

## 🧪 TEST YOUR SETUP

### Test Backend
```bash
curl http://localhost:5000/api/health
```

Should return:
```json
{
  "success": true,
  "data": {
    "status": "online",
    "service": "Healthcare AI Chatbot"
  }
}
```

### Test API
```bash
curl -X POST http://localhost:5000/api/chat/new-session
```

---

## 📚 EXAMPLE QUERIES TO TRY

1. "What are symptoms of diabetes?"
2. "How to manage anxiety naturally?"
3. "What should I do for severe headache?"
4. "Signs of depression?"
5. "When to go to emergency room?"
6. "Tips for better sleep?"
7. "How to lower blood pressure?"
8. "What is fever and treatments?"

---

## 🔒 SECURITY TIPS

✅ **DO:**
- Keep API key in `.env` file (never in code)
- Use HTTPS in production
- Add authentication for multi-user
- Validate all inputs
- Regular security updates

❌ **DON'T:**
- Share API key publicly
- Commit `.env` file to GitHub
- Use same key across environments
- Store patient data unencrypted
- Skip security updates

---

## 📞 SUPPORT & RESOURCES

### Get Help
1. Check README.md for detailed docs
2. Review QUICK_START.md for basics
3. Check browser console (F12) for errors
4. Verify all dependencies installed

### Learn More
- LangChain: https://python.langchain.com
- Groq API: https://console.groq.com/docs
- Flask: https://flask.palletsprojects.com

### Get API Keys
- Groq: https://console.groq.com/keys
- Gemini: https://makersuite.google.com

---

## ✅ SUCCESS CHECKLIST

- [ ] Python installed
- [ ] Groq API key obtained
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with API key
- [ ] Backend running (`python app.py`)
- [ ] Frontend accessible (`http://localhost:8000`)
- [ ] Can send messages and get responses
- [ ] Beautiful UI visible in browser
- [ ] Chat history working
- [ ] Settings panel accessible

---

## 🎯 NEXT STEPS

1. **Customize:** Modify prompts for your use case
2. **Test:** Try various health-related queries
3. **Deploy:** Use Docker or cloud platform
4. **Integrate:** Add to your existing system
5. **Monitor:** Track conversations and improve

---

## ⚠️ IMPORTANT DISCLAIMER

This chatbot provides **PRELIMINARY GUIDANCE ONLY**.

- ❌ NOT a replacement for professional doctors
- ❌ NOT for official diagnosis
- ❌ NOT for treatment planning
- ⚠️ ALWAYS consult licensed healthcare professionals
- 🚨 In emergencies, CALL 911 or emergency services

**Use responsibly and always encourage professional medical consultation.**

---

## 🎉 YOU'RE ALL SET!

You now have a **professional-grade AI healthcare chatbot** ready to serve patients!

**Start with:** `python run_dev_servers.py`

**Visit:** http://localhost:8000

**Happy chatting! 🏥💬**

---

**Built with ❤️ using LangChain, Groq API, Flask, and modern web technologies.**
