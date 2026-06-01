"""
Utility functions for the Healthcare Chatbot
"""
from datetime import datetime
from typing import List, Dict, Any
import re


def format_timestamp():
    """Get current timestamp"""
    return datetime.now().isoformat()


def clean_message(message: str) -> str:
    """Clean and normalize user input"""
    message = message.strip()
    # Remove multiple spaces
    message = re.sub(r'\s+', ' ', message)
    return message


def format_chat_history(messages: List[Dict[str, str]]) -> str:
    """Format chat history for context"""
    if not messages:
        return "No previous messages"
    
    history = []
    for msg in messages[-10:]:  # Last 10 messages for context
        role = msg.get("role", "").upper()
        content = msg.get("content", "")
        history.append(f"{role}: {content}")
    
    return "\n".join(history)


def is_emergency_query(message: str) -> bool:
    """Check if the message contains emergency indicators"""
    emergency_keywords = [
        "emergency", "911", "ambulance", "chest pain", "can't breathe",
        "difficulty breathing", "unconscious", "severe bleeding",
        "suicidal", "suicide", "hurt myself", "overdose", "poison",
        "anaphylaxis", "shock", "severe allergic", "cardiac"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in emergency_keywords)


def format_response(content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Format API response"""
    response = {
        "content": content,
        "timestamp": format_timestamp(),
        "type": "assistant"
    }
    
    if metadata:
        response.update(metadata)
    
    return response


def truncate_history(messages: List[Dict[str, str]], max_items: int = 50) -> List[Dict[str, str]]:
    """Keep only recent messages to manage memory"""
    if len(messages) > max_items:
        return messages[-max_items:]
    return messages


def extract_medical_entities(message: str) -> Dict[str, List[str]]:
    """Extract potential medical entities from message"""
    symptoms = []
    conditions = []
    
    # Simple pattern matching for common medical terms
    symptom_keywords = ["pain", "ache", "burning", "tingling", "numbness", "weakness", "fatigue"]
    condition_keywords = ["diabetes", "hypertension", "asthma", "arthritis", "depression", "anxiety"]
    
    message_lower = message.lower()
    
    for symptom in symptom_keywords:
        if symptom in message_lower:
            symptoms.append(symptom)
    
    for condition in condition_keywords:
        if condition in message_lower:
            conditions.append(condition)
    
    return {
        "symptoms": symptoms,
        "conditions": conditions
    }


def _normalize_multi_value(value: Any) -> List[str]:
    """Normalize comma/newline separated values into a clean list."""
    if value is None:
        return []

    if isinstance(value, list):
        items = value
    else:
        items = re.split(r"[,;\n]", str(value))

    cleaned = []
    for item in items:
        text = str(item).strip()
        if text:
            cleaned.append(text)
    return cleaned


def format_patient_context(
    profile: Dict[str, Any] = None,
    symptom_intake: Dict[str, Any] = None,
    attachments: List[Dict[str, Any]] = None,
) -> str:
    """Build a compact patient context block for prompt injection."""
    sections = []

    if profile:
        profile_lines = []
        field_map = [
            ("name", "Name"),
            ("age", "Age"),
            ("sex", "Sex"),
            ("gender", "Gender"),
            ("language", "Preferred language"),
            ("pregnancy", "Pregnancy status"),
            ("height", "Height"),
            ("weight", "Weight"),
        ]
        for key, label in field_map:
            value = str(profile.get(key, "")).strip()
            if value:
                profile_lines.append(f"- {label}: {value}")

        allergies = _normalize_multi_value(profile.get("allergies"))
        conditions = _normalize_multi_value(profile.get("chronic_conditions"))
        medications = _normalize_multi_value(profile.get("medications"))

        if allergies:
            profile_lines.append(f"- Allergies: {', '.join(allergies)}")
        if conditions:
            profile_lines.append(f"- Chronic conditions: {', '.join(conditions)}")
        if medications:
            profile_lines.append(f"- Current medications: {', '.join(medications)}")

        if profile_lines:
            sections.append("Patient Profile:\n" + "\n".join(profile_lines))

    if symptom_intake:
        intake_lines = []
        field_map = [
            ("main_symptom", "Main symptom"),
            ("duration", "Duration"),
            ("severity", "Severity (1-10)"),
            ("fever", "Fever"),
            ("pain_location", "Pain location"),
            ("triggers", "Triggers"),
            ("relief", "Relief factors"),
            ("other_symptoms", "Other symptoms"),
        ]
        for key, label in field_map:
            value = str(symptom_intake.get(key, "")).strip()
            if value:
                intake_lines.append(f"- {label}: {value}")

        if intake_lines:
            sections.append("Symptom Check-In:\n" + "\n".join(intake_lines))

    if attachments:
        attachment_lines = []
        for attachment in attachments[:5]:
            name = str(attachment.get("name", "attachment")).strip()
            attachment_type = str(attachment.get("type", "file")).strip()
            note = str(attachment.get("note", "")).strip()
            attachment_lines.append(
                f"- {name} ({attachment_type})" + (f" | Note: {note}" if note else "")
            )

        if attachment_lines:
            sections.append("Uploaded Attachments:\n" + "\n".join(attachment_lines))

    return "\n\n".join(sections)


def validate_input(message: str, max_length: int = 2000) -> tuple[bool, str]:
    """Validate user input"""
    if not message or not message.strip():
        return False, "Please enter a message"
    
    if len(message) > max_length:
        return False, f"Message is too long (max {max_length} characters)"
    
    return True, "Valid"


def log_conversation(user_message: str, assistant_message: str, session_id: str = None):
    """Log conversation for analytics (can be extended to database)"""
    log_entry = {
        "timestamp": format_timestamp(),
        "session_id": session_id,
        "user_message": user_message,
        "assistant_message": assistant_message,
        "medical_entities": extract_medical_entities(user_message)
    }
    return log_entry


def generate_pdf_report(
    session_id: str,
    doctor_role: str,
    patient_profile: Dict[str, Any],
    symptom_intake: Dict[str, Any],
    messages: List[Dict[str, Any]],
    patient_name: str = "Patient"
) -> bytes:
    """
    Generate a PDF report of the healthcare consultation
    
    Returns PDF as bytes for downloading
    """
    from fpdf import FPDF
    from datetime import datetime
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "Dr. Sehaat - Healthcare Consultation Report", 0, 1, "C")
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "C")
    pdf.cell(0, 8, f"Session ID: {session_id}", 0, 1, "C")
    pdf.ln(5)
    
    # Patient Information
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "PATIENT INFORMATION", 0, 1)
    pdf.set_font("Helvetica", "", 10)
    
    pdf.cell(60, 8, f"Name:", 0, 0)
    pdf.cell(0, 8, patient_name, 0, 1)
    pdf.cell(60, 8, f"Doctor:", 0, 0)
    pdf.cell(0, 8, doctor_role.replace('_', ' ').title(), 0, 1)
    pdf.ln(3)
    
    # Symptom Information
    if symptom_intake and any(symptom_intake.values()):
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "SYMPTOM CHECK-IN", 0, 1)
        pdf.set_font("Helvetica", "", 10)
        
        symptom_labels = {
            "main_symptom": "Main Symptom",
            "duration": "Duration",
            "severity": "Severity",
            "fever": "Fever/Temperature",
            "pain_location": "Pain Location",
            "triggers": "Triggers",
            "other_symptoms": "Other Symptoms"
        }
        
        for key, label in symptom_labels.items():
            value = str(symptom_intake.get(key, "")).strip()
            if value:
                pdf.cell(60, 8, f"{label}:", 0, 0)
                # Use multi_cell for long text
                pdf.multi_cell(0, 8, value)
        pdf.ln(3)
    
    # Patient Profile
    if patient_profile and any(patient_profile.values()):
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "PATIENT PROFILE", 0, 1)
        pdf.set_font("Helvetica", "", 10)
        
        profile_labels = {
            "age": "Age",
            "sex": "Gender",
            "allergies": "Allergies",
            "chronic_conditions": "Chronic Conditions",
            "medications": "Current Medications"
        }
        
        for key, label in profile_labels.items():
            value = str(patient_profile.get(key, "")).strip()
            if value:
                pdf.cell(60, 8, f"{label}:", 0, 0)
                pdf.multi_cell(0, 8, value)
        pdf.ln(3)
    
    # Consultation Summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "CONSULTATION SUMMARY", 0, 1)
    pdf.set_font("Helvetica", "", 9)
    
    user_messages = [m for m in messages if m.get("role") == "user"]
    ai_messages = [m for m in messages if m.get("role") == "assistant"]
    
    for i, msg in enumerate(ai_messages[:3], 1):  # Last 3 responses
        content = str(msg.get("content", "")).strip()
        if content:
            pdf.multi_cell(0, 7, f"Response {i}:\n{content}\n")
            pdf.ln(2)
    
    # Footer
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.ln(5)
    pdf.cell(0, 10, "This is an AI-generated consultation report. Please consult a real doctor for medical advice.", 0, 1, "C")
    
    return pdf.output()


def translate_text(text: str, target_language: str, translations_dict: Dict[str, Dict[str, str]] = None) -> str:
    """
    Translate UI text to target language
    Uses provided translations_dict or returns original text if not found
    """
    if not translations_dict or target_language == "en":
        return text
    
    lang_dict = translations_dict.get(target_language, {})
    return lang_dict.get(text, text)
