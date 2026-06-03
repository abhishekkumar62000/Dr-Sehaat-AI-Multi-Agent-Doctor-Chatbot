# 🏥 Feature Documentation - Dr. Sehaat Healthcare Chatbot

## 📋 TABLE OF CONTENTS

1. [Frontend Features](#frontend-features)
2. [Backend Features](#backend-features)
3. [Healthcare Features](#healthcare-features)
4. [AI/NLP Features](#ainlp-features)
5. [API Reference](#api-reference)
6. [Customization Guide](#customization-guide)

---

## 🎨 FRONTEND FEATURES

### User Interface
- **Beautiful Dark Theme** - Reduces eye strain, modern design
- **Gradient Effects** - Green and blue healthcare colors
- **Smooth Animations** - Slideup, fade, pulse effects
- **Responsive Design** - Desktop, tablet, mobile optimized
- **Real-time Typing** - Textarea auto-resize
- **Status Indicators** - Online/offline status with pulse animation

### Chat Interface
- **Message Bubbles** - User messages (right, green/blue)
- **Assistant Messages** - Doctor responses (left, dark)
- **Timestamps** - All messages timestamped
- **Emergency Highlighting** - Red highlighting for emergencies
- **Auto-scroll** - Automatically scrolls to latest message
- **Message History** - Visible in sidebar

### Sidebar Features
- **New Chat** - Start fresh conversation
- **Chat History** - List of recent chats
- **Settings** - Configure preferences
- **Quick Actions** - One-click common queries

### Settings Panel
- **Sound Toggle** - Enable/disable notification sounds
- **Dark Mode** - Switch theme (always on)
- **Auto-scroll** - Automatic scrolling preference

### Quick Action Cards
- 🌡️ Symptoms Info
- 😴 Wellness Tips
- ❤️ Health Awareness
- 🧘 Mental Health Support

---

## 🔧 BACKEND FEATURES

### API Endpoints

#### 1. Health Check
```
GET /api/health
Response: { status, service, version }
```

#### 2. Create Session
```
POST /api/chat/new-session
Response: { session_id, initial_message }
```

#### 3. Send Message
```
POST /api/chat/send
Body: { session_id, message }
Response: { 
    user_message, 
    assistant_response, 
    is_emergency,
    timestamp 
}
```

#### 4. Get History
```
GET /api/chat/history/<session_id>
Response: { messages[], count }
```

#### 5. Clear Chat
```
POST /api/chat/clear/<session_id>
Response: { message }
```

#### 6. Close Session
```
POST /api/chat/close-session/<session_id>
Response: { message }
```

#### 7. Get All Sessions
```
GET /api/chat/sessions
Response: { active_sessions, session_ids[] }
```

### Error Handling
- Comprehensive error responses
- Detailed error messages for debugging
- Graceful failure handling
- Input validation on all endpoints

### Session Management
- Unique session IDs (UUID)
- Session isolation (one conversation per session)
- Session cleanup on close
- Memory management with max history

---

## 🏥 HEALTHCARE FEATURES

### Medical Knowledge Base
- **Symptom Guidance** - Preliminary assessment
- **Medication Info** - Side effects, dosage info
- **Wellness Tips** - Lifestyle recommendations
- **Mental Health Support** - Stress, anxiety management
- **Prevention** - Disease prevention strategies
- **When to Seek Care** - Emergency indicators

### Emergency Detection
Automatically detects keywords:
- Chest pain
- Difficulty breathing
- Severe bleeding
- Loss of consciousness
- Suicidal thoughts
- Severe allergic reactions
- Acute trauma

When detected:
1. Shows emergency alert modal
2. Displays emergency contact numbers
3. Recommends calling 911
4. Highlights response in red
5. Plays notification sound

### Medical Entity Recognition
Extracts from user messages:
- **Symptoms** - Pain, fatigue, burning, etc.
- **Conditions** - Diabetes, asthma, depression, etc.
- **Medications** - Drug names mentioned
- **Vitals** - Temperature, blood pressure, etc.

### Professional Disclaimers
- Automatic disclaimer on startup
- Reminder in quick actions
- Emergency notice
- Professional language
- Clear limitations stated

---

## 🤖 AI/NLP FEATURES

### LangChain Integration
- **Conversation Chain** - Multi-turn dialogues
- **Memory Management** - Context retention
- **Prompt Templates** - Customizable prompts
- **Message History** - Conversation context
- **Response Generation** - AI-powered responses

### Natural Language Processing
- **Intent Recognition** - Understands user intent
- **Entity Extraction** - Medical entities
- **Context Understanding** - Multi-turn awareness
- **Semantic Similarity** - Relevant responses
- **Temperature Control** - Adjustable creativity

### Groq API Integration
- **Fast Inference** - Sub-second responses
- **High Quality** - Mixtral 8x7B model
- **Cost Effective** - Free tier available
- **Streaming Support** - Real-time responses
- **Error Handling** - Fallback mechanisms

### Conversation Management
- **Message Buffer** - Recent 50 messages kept
- **Context Window** - 4000 token context
- **History Truncation** - Prevents memory bloat
- **Session Isolation** - No cross-talk
- **Cleanup** - Automatic session cleanup

### Response Customization
```python
# In prompts.py, customize:
HEALTHCARE_SYSTEM_PROMPT = """Your custom prompt"""
HEALTHCARE_PROMPT_TEMPLATE = """Your template"""
INITIAL_GREETING = """Your greeting"""
FALLBACK_RESPONSE = """Your fallback"""
```

---

## 🔌 API REFERENCE

### Common Response Format
```json
{
    "success": true,
    "data": { ... },
    "timestamp": "2024-01-01T12:00:00"
}
```

### Error Response Format
```json
{
    "success": false,
    "error": "Error message here",
    "timestamp": "2024-01-01T12:00:00"
}
```

### Chat Message Format
```json
{
    "role": "patient|assistant",
    "content": "Message text",
    "timestamp": "ISO timestamp",
    "is_emergency": false,
    "entities": {
        "symptoms": ["pain", "fever"],
        "conditions": ["diabetes"]
    }
}
```

---

## 🛠️ CUSTOMIZATION GUIDE

### Change System Prompt
Edit `backend/prompts.py`:
```python
HEALTHCARE_SYSTEM_PROMPT = """
You are Dr. [Name], specialized in [specialty]...
"""
```

### Change Welcome Message
Edit `backend/prompts.py`:
```python
INITIAL_GREETING = """
Your custom greeting here
"""
```

### Change AI Model
Edit `backend/config.py`:
```python
GROQ_MODEL = "llama2-70b-4096"  # Change this
```

### Add Emergency Keywords
Edit `backend/utils.py`:
```python
def is_emergency_query(message: str):
    emergency_keywords = [
        "emergency", "911",
        # Add more keywords
    ]
```

### Customize Colors
Edit `frontend/css/style.css`:
```css
:root {
    --primary: #0066ff;
    --health-green: #22c55e;
    --health-blue: #3b82f6;
    /* Change these colors */
}
```

### Add New API Endpoint
Edit `backend/app.py`:
```python
@app.route('/api/custom/endpoint', methods=['POST'])
def custom_endpoint():
    # Your logic here
    return success_response(data)
```

### Modify Frontend Logic
Edit `frontend/js/chat.js`:
- `handleSendMessage()` - Message sending
- `displayMessage()` - Message display
- `setupEventListeners()` - Event handling

---

## 📊 CONFIGURATION OPTIONS

### Model Settings (`config.py`)
```python
GROQ_MODEL = "mixtral-8x7b-32768"  # AI model
TEMPERATURE = 0.7                   # 0-1: creativity
MAX_TOKENS = 2048                   # Response length
```

### Chat Settings
```python
MAX_HISTORY = 50                    # Messages kept
CONTEXT_WINDOW = 4000               # Context size
```

### Server Settings
```python
FLASK_ENV = "development"           # dev/production
DEBUG = True                        # Enable debug mode
SECRET_KEY = "your-secret"          # Session key
CORS_ORIGINS = ["http://localhost:5000"]  # Allowed origins
```

---

## 🚀 ADVANCED FEATURES

### Conversation Logging
Enabled by default in `utils.log_conversation()`:
```python
log_entry = {
    "timestamp": timestamp,
    "session_id": session_id,
    "user_message": user_message,
    "assistant_message": response,
    "medical_entities": extracted_entities
}
```

### Medical Entity Extraction
Automatic extraction of:
- Common symptoms
- Medical conditions
- Medications
- Vital signs

### Input Validation
- Max length: 2000 characters
- Empty message check
- Special character handling
- HTML escape for security

### Response Formatting
- Line break conversion
- Bold text support (**text**)
- HTML escaping
- Special character handling

---

## 🔒 SECURITY FEATURES

### Input Security
- ✅ HTML escaping
- ✅ Length validation
- ✅ Special character handling
- ✅ SQL injection prevention

### API Security
- ✅ CORS configuration
- ✅ Error message sanitization
- ✅ Rate limiting ready
- ✅ Session validation

### Data Protection
- ✅ Environment variables for secrets
- ✅ API key never exposed
- ✅ Session isolation
- ✅ HTTPS ready

---

## 📈 MONITORING & ANALYTICS

### Logged Information
- Conversation timestamps
- Session IDs
- User messages
- AI responses
- Medical entities detected
- Response times

### Performance Metrics
- Response time tracking
- Model inference timing
- API call statistics
- Error rates

---

## 🎓 LEARNING RESOURCES

### Study Topics
1. LangChain documentation
2. Groq API best practices
3. Flask application development
4. REST API design
5. Healthcare NLP

### External Links
- LangChain: https://python.langchain.com
- Groq: https://console.groq.com
- Flask: https://flask.palletsprojects.com
- Healthcare NLP: https://www.paperswithcode.com/task/medical-nlp

---

## ✅ FEATURE CHECKLIST

- [x] Beautiful UI/UX
- [x] Healthcare specialization
- [x] Emergency detection
- [x] Chat history
- [x] Multi-turn conversations
- [x] Medical entity recognition
- [x] Responsive design
- [x] Dark theme
- [x] Settings panel
- [x] Quick actions
- [x] Session management
- [x] Error handling
- [x] API endpoints
- [x] Docker support
- [x] Production ready

---

**All features are fully implemented and production-ready! 🚀**
