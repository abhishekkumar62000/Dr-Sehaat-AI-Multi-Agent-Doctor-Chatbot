"""
Medical Bot Logic using LangChain and Groq API
Handles healthcare conversations with NLP
"""

try:
    from langchain_groq import ChatGroq
except Exception:
    ChatGroq = None
import os
import requests
import json
try:
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationChain
    from langchain.prompts import PromptTemplate
    from langchain.callbacks import StreamingStdOutCallbackHandler
except Exception:
    # Provide lightweight fallbacks for environments without langchain installed.
    class ConversationBufferMemory:
        def __init__(self, ai_prefix="AI", human_prefix="Human"):
            self.ai_prefix = ai_prefix
            self.human_prefix = human_prefix
            self.chat_memory = self
            self._messages = []

        def add_message(self, msg):
            self._messages.append(msg)

        def clear(self):
            self._messages = []

    class ConversationChain:
        def __init__(self, llm=None, memory=None, prompt=None, verbose=False):
            self.llm = llm
            self.memory = memory
            self.prompt = prompt
            self.verbose = verbose

        def run(self, input=None):
            return "[offline] LLM not available; returning a safe mock response."

    class PromptTemplate:
        def __init__(self, input_variables=None, template=""):
            self.input_variables = input_variables or []
            self.template = template

    StreamingStdOutCallbackHandler = None
from typing import List, Dict, Tuple
import config
from prompts import (
    HEALTHCARE_SYSTEM_PROMPT,
    HEALTHCARE_PROMPT_TEMPLATE,
    DEFAULT_DOCTOR_KEY,
    get_doctor_system_prompt,
)
from utils import (
    is_emergency_query, format_chat_history, 
    extract_medical_entities, log_conversation, format_patient_context
)


class HealthcareChatBot:
    """Main Healthcare Chatbot Class"""
    
    def __init__(self, doctor_key: str = DEFAULT_DOCTOR_KEY):
        """Initialize the healthcare chatbot"""
        self.doctor_key = doctor_key or DEFAULT_DOCTOR_KEY
        self.chat_history: List[Dict[str, str]] = []
        self.patient_profile: Dict[str, str] = {}
        self.symptom_intake: Dict[str, str] = {}
        self.attachments: List[Dict[str, str]] = []

        # Determine offline/mock mode when no API key is present or LLM package is missing
        self.offline_mode = False
        if not config.GROQ_API_KEY or ChatGroq is None:
            if config.GROQ_API_KEY and ChatGroq is None:
                print("[medical_bot] GROQ_API_KEY is set but langchain_groq is missing; using offline/mock mode.")
            else:
                print("[medical_bot] GROQ_API_KEY not configured; using offline/mock mode.")
            self.llm = None
            self.offline_mode = True
        else:
            # Initialize Groq LLM with fallback if configured model is decommissioned
            try:
                self.llm = ChatGroq(
                    temperature=config.TEMPERATURE,
                    model_name=config.GROQ_MODEL,
                    api_key=config.GROQ_API_KEY,
                    max_tokens=config.MAX_TOKENS,
                )
            except Exception as e:
                err = str(e)
                # If model decommissioned, try a safe fallback model
                if 'decommission' in err.lower() or ('model' in err.lower() and 'decommission' in err.lower()):
                    fallback_model = os.getenv('GROQ_FALLBACK_MODEL', 'llama-3.3-70b-versatile')
                    print(f"[medical_bot] Configured model failed ({err}); falling back to model: {fallback_model}")
                    self.llm = ChatGroq(
                        temperature=config.TEMPERATURE,
                        model_name=fallback_model,
                        api_key=config.GROQ_API_KEY,
                        max_tokens=config.MAX_TOKENS,
                    )
                else:
                    # Re-raise for other errors so they can be surfaced
                    raise
        
        # Initialize memory for conversation history
        self.memory = ConversationBufferMemory(
            ai_prefix="Dr. Sehaat",
            human_prefix="Patient"
        )

        # Create conversation chain with selected doctor profile
        # Only build conversation chain when an LLM is configured
        if self.llm is not None:
            self._rebuild_conversation_chain()
        else:
            self.conversation_chain = None

    def _get_context_block(self) -> str:
        """Build the current patient context block for prompting."""
        context_block = format_patient_context(
            profile=self.patient_profile,
            symptom_intake=self.symptom_intake,
            attachments=self.attachments,
        )
        return context_block

    def _build_prompt_template(self) -> PromptTemplate:
        """Build prompt template for the active doctor specialization."""
        doctor_prompt = get_doctor_system_prompt(self.doctor_key)
        patient_context = self._get_context_block()
        context_section = f"\n\nPatient Context:\n{patient_context}" if patient_context else ""
        return PromptTemplate(
            input_variables=["history", "input"],
            template=doctor_prompt + context_section + "\n\n{history}\n\nPatient: {input}\n\nDoctor:",
        )

    def _rebuild_conversation_chain(self):
        """Rebuild conversation chain preserving memory with current doctor role."""
        self.prompt = self._build_prompt_template()
        self.conversation_chain = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=self.prompt,
            verbose=False
        )

    def set_doctor_role(self, doctor_key: str):
        """Update selected doctor role for current session."""
        new_key = doctor_key or DEFAULT_DOCTOR_KEY
        if new_key != self.doctor_key:
            self.doctor_key = new_key
            self._rebuild_conversation_chain()

    def update_patient_profile(self, profile: Dict[str, str]):
        """Store persistent patient profile information for the session."""
        self.patient_profile = profile or {}
        if self.llm is not None:
            self._rebuild_conversation_chain()

    def update_symptom_intake(self, symptom_intake: Dict[str, str]):
        """Store guided symptom-check answers for the session."""
        self.symptom_intake = symptom_intake or {}
        if self.llm is not None:
            self._rebuild_conversation_chain()

    def update_attachments(self, attachments: List[Dict[str, str]]):
        """Store uploaded attachment metadata for context."""
        self.attachments = attachments or []
        if self.llm is not None:
            self._rebuild_conversation_chain()

    def get_session_context(self) -> Dict[str, Dict[str, str]]:
        """Return the stored session context for the frontend."""
        return {
            "patient_profile": self.patient_profile,
            "symptom_intake": self.symptom_intake,
            "attachments": self.attachments,
        }
    
    def chat(self, user_message: str) -> Tuple[str, bool]:
        """
        Process user message and get healthcare response
        
        Args:
            user_message: Patient's message
            
        Returns:
            Tuple of (response_text, is_emergency)
        """
        # Check for emergency
        is_emergency = is_emergency_query(user_message)
        
        # Extract medical entities
        entities = extract_medical_entities(user_message)
        
        # Add to chat history
        self.chat_history.append({
            "role": "patient",
            "content": user_message,
            "entities": entities
        })
        
        try:
            # If running offline/mock mode, return a deterministic mock response
            if self.offline_mode or self.conversation_chain is None:
                response = self._generate_mock_response(user_message, entities)
                self.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "is_emergency": is_emergency
                })
                log_conversation(user_message, response)
                return response, is_emergency

            # Get response from LLM
            response = self.conversation_chain.run(input=user_message)

            # Add response to history
            self.chat_history.append({
                "role": "assistant",
                "content": response,
                "is_emergency": is_emergency
            })

            # Log conversation
            log_conversation(user_message, response)

            return response, is_emergency

        except Exception as e:
            err = str(e)
            # If the error indicates the configured model was decommissioned, retry with fallback
            if 'decommission' in err.lower():
                fallback_model = os.getenv('GROQ_FALLBACK_MODEL', 'llama-3.3-70b-versatile')
                print(f"[medical_bot] Model runtime error detected: {err}; retrying with fallback model: {fallback_model}")

                # Reinitialize LLM with fallback and try once more
                try:
                    self.llm = ChatGroq(
                        temperature=config.TEMPERATURE,
                        model_name=fallback_model,
                        api_key=config.GROQ_API_KEY,
                        max_tokens=config.MAX_TOKENS,
                    )
                    self._rebuild_conversation_chain()

                    response = self.conversation_chain.run(input=user_message)

                    # Add response to history
                    self.chat_history.append({
                        "role": "assistant",
                        "content": response,
                        "is_emergency": is_emergency
                    })

                    # Log conversation
                    log_conversation(user_message, response)

                    return response, is_emergency

                except Exception as e2:
                    error_message = f"I apologize, but I encountered an error processing your request after retry: {str(e2)}"
                    return error_message, False

            # If error indicates model not found or no access, try HuggingFace fallback
            if 'model_not_found' in err.lower() or 'does not exist' in err.lower() or 'you do not have access' in err.lower() or 'access' in err.lower():
                hf_key = os.getenv('HUGGINGFACE_API_KEY', '')
                hf_model = os.getenv('HUGGINGFACE_FALLBACK_MODEL', 'google/flan-t5-large')
                if hf_key:
                    try:
                        # Build a simple prompt for HF
                        prompt_text = get_doctor_system_prompt(self.doctor_key) + "\nPatient: " + user_message + "\nDoctor:"
                        headers = {"Authorization": f"Bearer {hf_key}", "Content-Type": "application/json"}
                        payload = {"inputs": prompt_text}
                        url = f"https://api-inference.huggingface.co/models/{hf_model}"
                        resp = requests.post(url, headers=headers, json=payload, timeout=60)
                        if resp.status_code == 200:
                            # HF returns a list or dict depending on model; handle common formats
                            try:
                                data = resp.json()
                                if isinstance(data, list) and 'generated_text' in data[0]:
                                    hf_text = data[0].get('generated_text', '')
                                elif isinstance(data, dict) and 'generated_text' in data:
                                    hf_text = data.get('generated_text', '')
                                elif isinstance(data, list) and isinstance(data[0], dict) and 'generated_text' in data[0]:
                                    hf_text = data[0]['generated_text']
                                else:
                                    hf_text = resp.text
                            except Exception:
                                hf_text = resp.text

                            # Add to history and return
                            self.chat_history.append({
                                "role": "assistant",
                                "content": hf_text,
                                "is_emergency": is_emergency
                            })
                            log_conversation(user_message, hf_text)
                            return hf_text, is_emergency

                        else:
                            hf_failed = f"HuggingFace returned {resp.status_code}: {resp.text}"
                    except Exception as e3:
                        hf_failed = f"HuggingFace fallback exception: {str(e3)}"
                else:
                    hf_failed = "No HUGGINGFACE_API_KEY configured"

                # If HF fallback didn't succeed, try Gemini (Google) fallback
                gem_failed = None
                try:
                    gemini_key = os.getenv('GEMINI_API_KEY', '')
                    gemini_model = os.getenv('GEMINI_MODEL', 'models/text-bison-001')
                    if gemini_key:
                        gen_url = f"https://generativelanguage.googleapis.com/v1beta2/{gemini_model}:generate?key={gemini_key}"
                        prompt_text = get_doctor_system_prompt(self.doctor_key) + "\nPatient: " + user_message + "\nDoctor:"
                        body = {
                            "prompt": {"text": prompt_text},
                            "temperature": float(config.TEMPERATURE),
                            "maxOutputTokens": int(config.MAX_TOKENS)
                        }
                        resp2 = requests.post(gen_url, headers={"Content-Type": "application/json"}, json=body, timeout=60)
                        if resp2.status_code == 200:
                            try:
                                data = resp2.json()
                                if 'candidates' in data and isinstance(data['candidates'], list) and len(data['candidates'])>0:
                                    gem_text = data['candidates'][0].get('output', '') or data['candidates'][0].get('content', '')
                                elif 'output' in data:
                                    gem_text = data.get('output', '')
                                else:
                                    gem_text = json.dumps(data)
                            except Exception:
                                gem_text = resp2.text

                            self.chat_history.append({
                                "role": "assistant",
                                "content": gem_text,
                                "is_emergency": is_emergency
                            })
                            log_conversation(user_message, gem_text)
                            return gem_text, is_emergency
                        else:
                            gem_failed = f"Gemini returned {resp2.status_code}: {resp2.text}"
                    else:
                        gem_failed = "No GEMINI_API_KEY configured"
                except Exception as e_g:
                    gem_failed = f"Gemini exception: {str(e_g)}"

                # Return a safe mock response (and log the failure reasons)
                combined = f"Original error: {err}. HF fallback: {hf_failed}. Gemini fallback: {gem_failed}"
                print("[medical_bot] Fallback reasons:", combined)
                mock = self._generate_mock_response(user_message, entities)
                return mock + "\n\n" + "[Note: live LLM providers were unreachable; displayed response is a safe, automated suggestion.]", is_emergency

            # Otherwise return the original error message
            error_message = f"I apologize, but I encountered an error processing your request: {err}"
            return error_message, False
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get formatted chat history"""
        return self.chat_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.memory.clear()
        self.chat_history = []
    
    def add_context(self, context: str):
        """Add additional context to the conversation"""
        self.memory.chat_memory.add_message(context)
    
    def get_emergency_response(self) -> str:
        """Get emergency response"""
        return """⚠️ EMERGENCY ALERT ⚠️

Based on your message, this appears to be an emergency situation.

**PLEASE CALL EMERGENCY SERVICES IMMEDIATELY:**

Do not wait for online consultation. Seek immediate medical attention!

If you're in a safe location, I can provide general guidance while you wait for emergency services, but professional emergency care is critical."""

    def _generate_mock_response(self, user_message: str, entities: dict) -> str:
        """Generate a safe, templated response when external LLMs are unreachable.

        This is a deterministic fallback for demos and offline testing only.
        """
        msg = user_message.lower()
        parts = []

        # Basic symptom guidance heuristics
        if any(k in msg for k in ("fever", "temperature", "hot", "chills")):
            parts.append("It sounds like you may have a fever. Monitor your temperature regularly and stay hydrated.")
            parts.append("For adults, consider over-the-counter fever reducers like acetaminophen or ibuprofen following the label instructions.")
        if any(k in msg for k in ("headache", "migraine", "head pain")):
            parts.append("For a headache, rest in a quiet, dark room, stay hydrated, and consider OTC pain relief if appropriate.")
        if any(k in msg for k in ("cough", "sore throat", "cold")):
            parts.append("A cough or sore throat can be managed with fluids, throat lozenges, and warm saline gargles.")
        if any(k in msg for k in ("stomach", "nausea", "vomit", "diarrhea")):
            parts.append("For gastrointestinal symptoms, focus on rehydration (oral rehydration solutions) and small bland meals.")
        if not parts:
            parts.append("Thanks for your message. I can help with general advice: describe your main symptoms, their duration, and any medications you are taking.")

        # Add extracted entities if present
        if entities:
            ent_lines = []
            for k, v in entities.items():
                if v:
                    ent_lines.append(f"{k}: {', '.join(v) if isinstance(v, list) else v}")
            if ent_lines:
                parts.append("I noticed these details in your message: " + "; ".join(ent_lines))

        parts.append("\nDisclaimer: This is general information only and not a medical diagnosis. See a licensed healthcare professional for personal advice.")
        return "\n\n".join(parts)


class ConversationManager:
    """Manages multiple chat sessions"""
    
    def __init__(self):
        """Initialize conversation manager"""
        self.sessions: Dict[str, HealthcareChatBot] = {}
    
    def create_session(self, session_id: str, doctor_key: str = DEFAULT_DOCTOR_KEY) -> HealthcareChatBot:
        """Create new chat session"""
        if session_id not in self.sessions:
            try:
                self.sessions[session_id] = HealthcareChatBot(doctor_key=doctor_key)
            except Exception:
                import traceback
                traceback.print_exc()
                raise
        else:
            self.sessions[session_id].set_doctor_role(doctor_key)
        return self.sessions[session_id]
    
    def get_session(self, session_id: str, doctor_key: str = DEFAULT_DOCTOR_KEY) -> HealthcareChatBot:
        """Get existing session"""
        if session_id not in self.sessions:
            return self.create_session(session_id, doctor_key=doctor_key)
        self.sessions[session_id].set_doctor_role(doctor_key)
        return self.sessions[session_id]
    
    def delete_session(self, session_id: str):
        """Delete session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_all_sessions(self) -> Dict[str, HealthcareChatBot]:
        """Get all active sessions"""
        return self.sessions


# Global conversation manager instance
conversation_manager = ConversationManager()
