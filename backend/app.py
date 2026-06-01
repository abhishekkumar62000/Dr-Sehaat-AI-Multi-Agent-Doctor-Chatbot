"""
Flask Backend API for Healthcare Chatbot
Handles REST endpoints for chat communication
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from datetime import datetime
import config
from medical_bot import conversation_manager
from utils import validate_input, clean_message
from prompts import INITIAL_GREETING, DEFAULT_DOCTOR_KEY, get_doctor_options

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG

# Enable CORS
CORS(app, origins=config.CORS_ORIGINS)


# ==================== Helper Functions ====================
def generate_session_id():
    """Generate unique session ID"""
    return str(uuid.uuid4())


def error_response(message: str, status_code: int = 400):
    """Format error response"""
    return jsonify({
        "success": False,
        "error": message,
        "timestamp": datetime.now().isoformat()
    }), status_code


def success_response(data: dict, status_code: int = 200):
    """Format success response"""
    return jsonify({
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }), status_code


# ==================== API Endpoints ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({
        "status": "online",
        "service": "Healthcare AI Chatbot",
        "version": "1.0.0"
    })


@app.route('/api/chat/new-session', methods=['POST'])
def create_new_session():
    """Create new chat session"""
    try:
        data = request.json or {}
        doctor_role = data.get("doctor_role", DEFAULT_DOCTOR_KEY)
        patient_profile = data.get("patient_profile", {})
        symptom_intake = data.get("symptom_intake", {})
        attachments = data.get("attachments", [])
        # Create a session id and return it immediately. The actual
        # HealthcareChatBot instance will be created lazily on first use
        # (e.g. when `/api/chat/send` is called) to avoid import-time
        # failures when optional LLM packages are not installed.
        session_id = generate_session_id()
        return success_response({
            "session_id": session_id,
            "doctor_role": doctor_role,
            "initial_message": INITIAL_GREETING,
            "created_at": datetime.now().isoformat()
        }, 201)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(f"Failed to create session: {str(e)}", 500)


@app.route('/api/chat/send', methods=['POST'])
def send_message():
    """Send message and get response"""
    try:
        data = request.json
        
        # Validate request
        if not data:
            return error_response("Request body is empty", 400)
        
        session_id = data.get("session_id")
        doctor_role = data.get("doctor_role", DEFAULT_DOCTOR_KEY)
        message = data.get("message", "").strip()
        
        if not session_id:
            return error_response("session_id is required", 400)
        
        if not message:
            return error_response("message is required", 400)
        
        # Validate input
        is_valid, validation_msg = validate_input(message)
        if not is_valid:
            return error_response(validation_msg, 400)
        
        # Get or create session
        bot = conversation_manager.get_session(session_id, doctor_key=doctor_role)

        # Optional structured patient context updates from the frontend
        if data.get("patient_profile") is not None:
            bot.update_patient_profile(data.get("patient_profile") or {})
        if data.get("symptom_intake") is not None:
            bot.update_symptom_intake(data.get("symptom_intake") or {})
        if data.get("attachments") is not None:
            bot.update_attachments(data.get("attachments") or [])
        
        # Clean message
        clean_msg = clean_message(message)
        
        # Get response
        response_text, is_emergency = bot.chat(clean_msg)
        
        # If emergency, include emergency alert
        if is_emergency:
            response_text = bot.get_emergency_response() + "\n\n" + response_text
        
        return success_response({
            "session_id": session_id,
            "doctor_role": doctor_role,
            "user_message": clean_msg,
            "assistant_response": response_text,
            "is_emergency": is_emergency,
            "timestamp": datetime.now().isoformat()
        }, 200)
    
    except Exception as e:
        return error_response(f"Error processing message: {str(e)}", 500)


@app.route('/api/chat/context/<session_id>', methods=['GET', 'POST'])
def chat_context(session_id):
    """Get or update the structured patient context for a session."""
    try:
        bot = conversation_manager.get_session(session_id)

        if request.method == 'POST':
            data = request.json or {}
            if data.get('patient_profile') is not None:
                bot.update_patient_profile(data.get('patient_profile') or {})
            if data.get('symptom_intake') is not None:
                bot.update_symptom_intake(data.get('symptom_intake') or {})
            if data.get('attachments') is not None:
                bot.update_attachments(data.get('attachments') or [])

            return success_response({
                "session_id": session_id,
                "context": bot.get_session_context(),
                "message": "Session context updated successfully"
            }, 200)

        return success_response({
            "session_id": session_id,
            "context": bot.get_session_context()
        }, 200)

    except Exception as e:
        return error_response(f"Failed to manage session context: {str(e)}", 500)


@app.route('/api/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        bot = conversation_manager.get_session(session_id)
        history = bot.get_chat_history()
        
        return success_response({
            "session_id": session_id,
            "messages": history,
            "count": len(history)
        }, 200)
    
    except Exception as e:
        return error_response(f"Failed to get history: {str(e)}", 500)


@app.route('/api/chat/clear/<session_id>', methods=['POST'])
def clear_chat(session_id):
    """Clear chat history for a session"""
    try:
        bot = conversation_manager.get_session(session_id)
        bot.clear_history()
        
        return success_response({
            "session_id": session_id,
            "message": "Chat history cleared successfully"
        }, 200)
    
    except Exception as e:
        return error_response(f"Failed to clear history: {str(e)}", 500)


@app.route('/api/chat/close-session/<session_id>', methods=['POST'])
def close_session(session_id):
    """Close a chat session"""
    try:
        conversation_manager.delete_session(session_id)
        
        return success_response({
            "session_id": session_id,
            "message": "Session closed successfully"
        }, 200)
    
    except Exception as e:
        return error_response(f"Failed to close session: {str(e)}", 500)


@app.route('/api/chat/sessions', methods=['GET'])
def get_active_sessions():
    """Get all active sessions (admin only)"""
    try:
        sessions = conversation_manager.get_all_sessions()
        session_count = len(sessions)
        
        return success_response({
            "active_sessions": session_count,
            "session_ids": list(sessions.keys())
        }, 200)
    
    except Exception as e:
        return error_response(f"Failed to get sessions: {str(e)}", 500)


@app.route('/api/info', methods=['GET'])
def get_info():
    """Get chatbot information"""
    return success_response({
        "name": "Dr. Sehaat",
        "description": "Professional AI Healthcare Assistant",
        "features": [
            "Medical consultation",
            "Symptom guidance",
            "Health education",
            "Wellness advice",
            "Emergency detection"
        ],
        "disclaimers": [
            "This is preliminary guidance only",
            "Always consult licensed healthcare professionals",
            "Not a replacement for professional medical care"
        ]
    })


@app.route('/api/chat/export-pdf/<session_id>', methods=['GET'])
def export_chat_pdf(session_id):
    """Export chat session as PDF report"""
    try:
        from utils import generate_pdf_report
        
        bot = conversation_manager.get_session(session_id)
        history = bot.get_chat_history()
        
        patient_name = bot.patient_profile.get("name", "Patient")
        
        pdf_bytes = generate_pdf_report(
            session_id=session_id,
            doctor_role=bot.doctor_key,
            patient_profile=bot.patient_profile,
            symptom_intake=bot.symptom_intake,
            messages=history,
            patient_name=patient_name
        )
        
        from flask import send_file
        import io
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Dr_Sehaat_Report_{session_id[:8]}.pdf"
        )
    
    except Exception as e:
        return error_response(f"Failed to generate PDF: {str(e)}", 500)


@app.route('/api/language/translate', methods=['POST'])
def translate_message():
    """Translate text to target language"""
    try:
        data = request.json or {}
        text = data.get("text", "")
        target_language = data.get("language", "en")
        
        if not text:
            return error_response("text is required", 400)
        
        # Languages supported
        languages = ["en", "hi", "es", "fr", "pt", "de"]
        if target_language not in languages:
            return error_response(f"Language not supported. Available: {languages}", 400)
        
        from utils import translate_text
        
        # For now, we'll return the text as-is
        # In production, you'd use Google Translate API or similar
        translated = translate_text(text, target_language)
        
        return success_response({
            "original": text,
            "translated": translated,
            "language": target_language
        }, 200)
    
    except Exception as e:
        return error_response(f"Translation failed: {str(e)}", 500)


@app.route('/api/language/available', methods=['GET'])
def get_languages():
    """Get list of supported languages"""
    return success_response({
        "languages": {
            "en": "English",
            "hi": "Hindi",
            "es": "Spanish",
            "fr": "French",
            "pt": "Portuguese",
            "de": "German"
        }
    })


@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    """Get available doctor specializations for dropdown."""
    return success_response({
        "default": DEFAULT_DOCTOR_KEY,
        "doctors": get_doctor_options()
    })


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return error_response("Endpoint not found", 404)


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return error_response("Internal server error", 500)


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return error_response("Method not allowed", 405)


# ==================== Main ====================

if __name__ == '__main__':
    print("=" * 60)
    print("Healthcare AI Chatbot - Backend Server")
    print("=" * 60)
    print(f"Environment: {config.FLASK_ENV}")
    print(f"Debug Mode: {config.DEBUG}")
    print(f"Model: {config.GROQ_MODEL}")
    print("=" * 60)
    print("Starting server...")
    print("Visit: http://localhost:5000")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=config.DEBUG,
        use_reloader=os.getenv('USE_RELOADER', '0') == '1'
    )
