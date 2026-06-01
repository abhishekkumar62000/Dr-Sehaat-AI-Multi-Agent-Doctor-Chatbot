# 🏥 Dr. Sehaat - Professional AI Healthcare Chatbot

A beautiful, interactive AI-powered healthcare chatbot built with modern web technologies. One-on-one chat interface similar to ChatGPT with professional medical guidance capabilities.

## ✨ Features

- 🤖 **AI-Powered Healthcare Guidance** - Using Groq API with advanced LLM models
- 💬 **ChatGPT-like UI** - Beautiful, responsive interface for seamless conversations
- 🏥 **Professional Medical Focus** - Specialized healthcare chatbot for patient consultations
- 🚨 **Emergency Detection** - Automatic detection of emergency situations
- 📱 **Fully Responsive** - Works perfectly on desktop, tablet, and mobile
- 🌙 **Dark Mode** - Eye-friendly dark theme
- 💾 **Chat History** - Keep track of conversations
- 🔐 **Session Management** - Secure session-based conversations
- ⚡ **Real-time Responses** - Streaming responses with loading indicators
- 🎨 **Beautiful UI/UX** - Professional gradient design with smooth animations

## 🏗️ Project Structure

```
Chatbot/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── config.py              # Configuration management
│   ├── medical_bot.py         # LangChain & LLM integration
│   ├── prompts.py             # Healthcare system prompts
│   ├── utils.py               # Utility functions
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── index.html             # Main HTML file
│   ├── css/
│   │   └── style.css          # Beautiful styling
│   ├── js/
│   │   └── chat.js            # Interactive frontend logic
│   └── assets/                # Images and icons
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js (optional, for serving frontend)
- Groq API Key (get free key from https://console.groq.com)
- Gemini API Key (optional, for fallback)

### Step 1: Clone and Setup

```bash
# Navigate to the Chatbot directory
cd c:\Users\DELL\Desktop\Chatbot

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### Step 3: Configure Environment Variables

```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your API keys
# GROQ_API_KEY=your_actual_api_key_here
# GEMINI_API_KEY=your_gemini_key_here (optional)
```

**Get Your Groq API Key:**
1. Visit https://console.groq.com
2. Sign up (free)
3. Go to API Keys section
4. Create new API key
5. Copy and paste in `.env` file

### Step 4: Start the Backend Server

```bash
# From the Chatbot directory
cd backend
python app.py
```

You should see:
```
============================================================
🏥 Healthcare AI Chatbot - Backend Server
============================================================
Environment: development
Debug Mode: True
Model: mixtral-8x7b-32768
============================================================
Starting server...
Visit: http://localhost:5000
============================================================
```

### Step 5: Open the Frontend

```bash
# Open frontend in browser
# Navigate to: file:///path/to/Chatbot/frontend/index.html

# Or use Python's built-in server (from frontend directory):
cd frontend
python -m http.server 8000
# Then visit: http://localhost:8000
```

## 🎯 Usage

### Chat Interface

1. **New Chat** - Click "➕ New Chat" to start a new conversation
2. **Send Message** - Type your health concern and press Enter (or Shift+Enter for new line)
3. **Quick Actions** - Click quick action cards for common topics
4. **Chat History** - View previous chats in the sidebar
5. **Settings** - Configure notifications, dark mode, and auto-scroll

### Example Queries

- "What are the symptoms of diabetes?"
- "How can I improve my sleep quality?"
- "What should I do for a severe headache?"
- "How to manage anxiety naturally?"
- "When should I seek emergency care?"

## 🔌 API Endpoints

### Health Check
```
GET /api/health
```

### Create New Session
```
POST /api/chat/new-session
Response: { session_id, initial_message }
```

### Send Message
```
POST /api/chat/send
Body: { session_id, message }
Response: { user_message, assistant_response, is_emergency }
```

### Get Chat History
```
GET /api/chat/history/<session_id>
```

### Clear Chat
```
POST /api/chat/clear/<session_id>
```

### Get Active Sessions (Admin)
```
GET /api/chat/sessions
```

## 🛠️ Technologies Used

### Backend
- **Flask** - Web framework
- **LangChain** - LLM orchestration
- **LangGraph** - Advanced conversation graph
- **Groq API** - Fast LLM inference
- **Python** - Backend language
- **Flask-CORS** - Cross-origin requests

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with custom properties
- **JavaScript (ES6+)** - Interactivity
- **Fetch API** - API communication

## 🎨 UI/UX Features

### Color Scheme
- **Primary Green**: #22c55e (Health/Wellness)
- **Primary Blue**: #3b82f6 (Professional/Trust)
- **Dark Background**: #0f1419 (Easy on eyes)
- **Orange**: #ff8c00 (Warnings)
- **Red**: #ef4444 (Emergencies)

### Responsive Breakpoints
- 📱 **Mobile**: < 480px
- 📱 **Tablet**: 480px - 768px
- 🖥️ **Desktop**: > 768px

### Animations
- Smooth slide-in animations
- Gradient text effects
- Pulse animations for status indicators
- Bounce animations for welcome icon

## ⚙️ Configuration

### config.py Parameters

```python
# Model Settings
GROQ_MODEL = "mixtral-8x7b-32768"  # Fast model
TEMPERATURE = 0.7                  # Balanced creativity
MAX_TOKENS = 2048                  # Response length

# Chat Settings
MAX_HISTORY = 50                   # Messages to keep
CONTEXT_WINDOW = 4000              # Context size
```

### Alternative Models

- `llama2-70b-4096` - Larger, more capable
- `gemma-7b-it` - Lightweight
- `openhermes-2.5-mistral-7b` - Creative writing

## 🚨 Emergency Handling

The chatbot automatically detects emergency keywords:
- Chest pain, difficulty breathing
- Severe bleeding, unconsciousness
- Suicidal thoughts
- Severe allergic reactions
- Acute trauma

When detected:
1. Shows prominent emergency alert
2. Displays emergency contact numbers
3. Recommends calling emergency services
4. Plays notification sound

## 📊 Chat Analytics

The system logs:
- Timestamp of each message
- Session ID
- Medical entities detected (symptoms, conditions)
- Response times

Can be extended to store in database for analytics.

## 🔒 Security & Privacy

- ✅ Session-based conversations (no login required for demo)
- ✅ API key stored in environment variables
- ✅ CORS configured
- ✅ Input validation on all endpoints
- ✅ Error messages don't leak sensitive info

### Production Recommendations
- Use HTTPS
- Add authentication
- Implement rate limiting
- Add database encryption
- Regular security audits
- HIPAA compliance for healthcare

## 🐛 Troubleshooting

### "Cannot connect to server"
- Make sure backend is running: `python backend/app.py`
- Check port 5000 is not in use
- Verify firewall settings

### "API Key Error"
- Verify `.env` file exists
- Check GROQ_API_KEY is set correctly
- Get free API key from https://console.groq.com

### "Slow Responses"
- Check internet connection
- Try different model in config.py
- Reduce MAX_TOKENS
- Check Groq API status

### "CORS Error"
- Ensure backend is running
- Check CORS_ORIGINS in config.py
- Verify frontend URL matches

## 📚 Learn More

- [LangChain Documentation](https://python.langchain.com)
- [Groq API Documentation](https://console.groq.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com)

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📝 License

This project is open source and available for personal and educational use.

## ⚠️ Important Disclaimer

**THIS IS FOR EDUCATIONAL AND PRELIMINARY GUIDANCE ONLY**

- This chatbot is NOT a replacement for professional medical care
- Always consult with licensed healthcare professionals
- In case of emergency, call emergency services immediately
- Medical information provided is general in nature
- Not intended for diagnosis or treatment planning
- Use at your own risk

---

## 🎯 Next Steps

1. ✅ Install and run the chatbot
2. ✅ Test with various health queries
3. ✅ Customize prompts for your use case
4. ✅ Add database integration
5. ✅ Deploy to production with proper security

## 📞 Support

For issues or questions:
1. Check this README
2. Review error messages in console
3. Check browser developer tools (F12)
4. Verify all dependencies are installed

---

**Happy Healthcare Chatting! 🏥💬**

Built with ❤️ using LangChain, Groq, and modern web technologies.
