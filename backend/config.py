import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Model Configuration
# Read model from environment so it can be updated without changing code
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")  # Default to active production model
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/text-bison-001")
TEMPERATURE = 0.3  # Lower randomness for more accurate, concise medical guidance
MAX_TOKENS = 1024

# Flask Configuration
FLASK_ENV = os.getenv("FLASK_ENV", "development")
DEBUG = FLASK_ENV == "development"
SECRET_KEY = os.getenv("SECRET_KEY", "healthcare-chatbot-secret-key")

# CORS Configuration
CORS_ORIGINS = [
	"http://localhost:5000",
	"http://localhost:3000",
	"http://127.0.0.1:5000",
	"http://localhost:8000",
	"http://127.0.0.1:8000",
]

# Chat Configuration
MAX_HISTORY = 50  # Maximum messages to keep in memory
CONTEXT_WINDOW = 4000  # Context window size
