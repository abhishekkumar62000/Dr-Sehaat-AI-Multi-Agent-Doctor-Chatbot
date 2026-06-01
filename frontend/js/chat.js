/* =====================================================
   Dr. Sehaat - Healthcare Chatbot Frontend JavaScript
   Interactive Chat Logic and UI Management
   ===================================================== */

// =====================================================
// Configuration
// =====================================================

const API_BASE_URL = 'http://localhost:5000/api';
let currentSessionId = null;
let messageHistory = [];
let isWaitingForResponse = false;
let autoScroll = true;
let currentDoctorRole = localStorage.getItem('doctorRole') || 'general_physician';
let doctorOptions = [];
let patientProfile = loadStoredJson('patientProfile', {});
let symptomIntake = loadStoredJson('symptomIntake', {});
let pendingAttachments = [];

// ===== NEW FEATURES =====
let currentLanguage = localStorage.getItem('language') || 'en';
let ttsEnabled = localStorage.getItem('ttsEnabled') === 'true' || false;
let isRecording = false;
let speechRecognition = null;
let translations = {};
let currentSynthesis = null;

// =====================================================
// DOM Elements
// =====================================================

const messagesContainer = document.getElementById('messagesContainer');
const messageInput = document.getElementById('messageInput');
const chatForm = document.getElementById('chatForm');
const sendBtn = document.getElementById('sendBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const newChatBtn = document.getElementById('newChatBtn');
const clearAllBtn = document.getElementById('clearAllBtn');
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const emergencyModal = document.getElementById('emergencyModal');
const chatHistoryList = document.getElementById('chatHistoryList');
const soundToggle = document.getElementById('soundToggle');
const darkModeToggle = document.getElementById('darkModeToggle');
const autoScrollToggle = document.getElementById('autoScrollToggle');
const doctorSelect = document.getElementById('doctorSelect');
const doctorHint = document.getElementById('doctorHint');
const headerSubtitle = document.getElementById('headerSubtitle');
const doctorLiveBadge = document.getElementById('doctorLiveBadge');
const symptomWizardBtn = document.getElementById('symptomWizardBtn');
const profileBtn = document.getElementById('profileBtn');
const symptomWizardModal = document.getElementById('symptomWizardModal');
const profileModal = document.getElementById('profileModal');
const saveSymptomWizardBtn = document.getElementById('saveSymptomWizardBtn');
const saveProfileBtn = document.getElementById('saveProfileBtn');
const attachBtn = document.getElementById('attachBtn');
const attachmentInput = document.getElementById('attachmentInput');

// ===== NEW FEATURE DOM ELEMENTS =====
const voiceBtn = document.getElementById('voiceBtn');
const ttsToggleBtn = document.getElementById('ttsToggleBtn');
const ttsEnabledToggle = document.getElementById('ttsEnabledToggle');
const languageSelect = document.getElementById('languageSelect');
const downloadPdfBtn = document.getElementById('downloadPdfBtn');

// =====================================================
// Initialize Application
// =====================================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🏥 Dr. Sehaat - Healthcare Chatbot Initialized');

    // Load translations and set language
    await loadTranslations();
    setupLanguageSelector();
    
    await loadDoctorOptions();
    setupDoctorSelection();
    updateDoctorHeader();
    
    // Start new chat
    await startNewChat();
    syncStructuredContextToServer();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize new features
    initializeVoiceInput();
    initializeTextToSpeech();
    
    // Check server status
    await checkServerStatus();
});

// =====================================================
// Event Listeners
// =====================================================

function setupEventListeners() {
    // Chat form submission
    chatForm.addEventListener('submit', handleSendMessage);
    
    // New chat button
    newChatBtn.addEventListener('click', startNewChat);

    // Structured context buttons
    symptomWizardBtn?.addEventListener('click', openSymptomWizard);
    profileBtn?.addEventListener('click', openProfileModal);
    saveSymptomWizardBtn?.addEventListener('click', saveSymptomWizard);
    saveProfileBtn?.addEventListener('click', saveProfile);

    // Attachment handling
    attachBtn?.addEventListener('click', () => attachmentInput?.click());
    attachmentInput?.addEventListener('change', handleAttachmentSelection);
    
    // New feature listeners
    voiceBtn?.addEventListener('click', toggleVoiceInput);
    ttsToggleBtn?.addEventListener('click', toggleTextToSpeech);
    ttsEnabledToggle?.addEventListener('change', (e) => {
        ttsEnabled = e.target.checked;
        localStorage.setItem('ttsEnabled', ttsEnabled);
        updateTtsButtonState();
        showSystemNotice(ttsEnabled ? 'Text-to-Speech enabled' : 'Text-to-Speech disabled');
    });
    languageSelect?.addEventListener('change', handleLanguageChange);
    downloadPdfBtn?.addEventListener('click', downloadSessionPdf);
    
    // Clear all button
    clearAllBtn.addEventListener('click', clearAllChats);
    
    // Settings button
    settingsBtn.addEventListener('click', openSettings);
    
    // Modal close buttons
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-close')) {
                closeModal(e.target.closest('.modal'));
            }
        });
    });
    
    // Settings toggles
    soundToggle.addEventListener('change', (e) => {
        localStorage.setItem('soundEnabled', e.target.checked);
    });
    
    darkModeToggle.addEventListener('change', (e) => {
        localStorage.setItem('darkMode', e.target.checked);
    });
    
    autoScrollToggle.addEventListener('change', (e) => {
        autoScroll = e.target.checked;
        localStorage.setItem('autoScroll', e.target.checked);
    });
    
    // Message input auto-resize
    messageInput.addEventListener('input', autoResizeTextarea);
    
    // Message input - Shift+Enter for new line
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // Close modals on background click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal);
            }
        });
    });
}

// =====================================================
// Chat Functions
// =====================================================

async function startNewChat() {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/new-session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                doctor_role: currentDoctorRole,
                patient_profile: patientProfile,
                symptom_intake: symptomIntake,
                attachments: pendingAttachments
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentSessionId = data.data.session_id;
            messageHistory = [];
            messagesContainer.innerHTML = '';
            messageInput.value = '';
            messageInput.focus();
            pendingAttachments = [];
            
            // Display welcome message
            displayWelcomeMessage(data.data.initial_message);
            updateDoctorHeader();
            updateLocalizedUI();
            renderAttachmentChips();
            
            // Add to history
            addToChatHistory();
            
            console.log('✅ New chat session created:', currentSessionId);
        }
    } catch (error) {
        console.error('❌ Error creating new chat:', error);
        showErrorMessage('Failed to create new chat session');
    }
}

async function handleSendMessage(e) {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    
    if (!message || isWaitingForResponse) {
        return;
    }
    
    if (!currentSessionId) {
        await startNewChat();
        return;
    }
    
    // Display user message
    displayMessage(message, 'user', false, pendingAttachments);
    messageHistory.push({ role: 'patient', content: message });
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Show loading
    showLoading();
    isWaitingForResponse = true;
    sendBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message,
                doctor_role: currentDoctorRole,
                patient_profile: patientProfile,
                symptom_intake: symptomIntake,
                attachments: pendingAttachments
            })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            const assistantMessage = data.data.assistant_response;
            const isEmergency = data.data.is_emergency;
            
            // Display response
            displayMessage(assistantMessage, 'assistant', isEmergency);
            speakText(assistantMessage);
            messageHistory.push({ role: 'assistant', content: assistantMessage, isEmergency });
            pendingAttachments = [];
            renderAttachmentChips();
            
            // Show emergency alert if needed
            if (isEmergency) {
                showEmergencyAlert();
                playNotificationSound();
            } else {
                playNotificationSound();
            }
        } else {
            showErrorMessage(data.error || 'Failed to get response');
        }
    } catch (error) {
        console.error('❌ Error sending message:', error);
        hideLoading();
        showErrorMessage('Network error. Please check your connection and try again.');
    } finally {
        isWaitingForResponse = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

// =====================================================
// Message Display Functions
// =====================================================

function displayMessage(content, role = 'assistant', isEmergency = false, attachments = []) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    if (isEmergency) messageDiv.classList.add('emergency');
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.innerHTML = formatMessage(content);

    if (attachments && attachments.length) {
        const attachmentWrap = document.createElement('div');
        attachmentWrap.className = 'message-attachments';
        attachments.forEach((attachment) => {
            const chip = document.createElement('div');
            chip.className = 'attachment-chip';
            chip.textContent = `${attachment.name} • ${attachment.type}`;
            attachmentWrap.appendChild(chip);
        });
        messageContent.appendChild(attachmentWrap);
    }
    
    messageDiv.appendChild(messageContent);
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = getTimeString();
    messageDiv.appendChild(timeDiv);
    
    messagesContainer.appendChild(messageDiv);
    
    if (autoScroll) {
        scrollToBottom();
    }
}

function displayWelcomeMessage(content) {
    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'welcome-section';
    welcomeDiv.innerHTML = `
        <div class="welcome-icon">🏥</div>
        <h2>${t('welcome', 'Welcome to Dr. Sehaat')}</h2>
        <p class="welcome-subtitle">${t('welcome_subtitle', 'Your AI Healthcare Assistant')}</p>
        <div class="quick-actions">
            <div class="action-card" onclick="fillMessage('What are the symptoms of fever?')">
                <span class="action-emoji">🌡️</span>
                <span>Symptoms Info</span>
            </div>
            <div class="action-card" onclick="fillMessage('How can I improve my sleep?')">
                <span class="action-emoji">😴</span>
                <span>Wellness Tips</span>
            </div>
            <div class="action-card" onclick="fillMessage('What are the warning signs of heart disease?')">
                <span class="action-emoji">❤️</span>
                <span>Health Awareness</span>
            </div>
            <div class="action-card" onclick="fillMessage('How to manage stress and anxiety?')">
                <span class="action-emoji">🧘</span>
                <span>Mental Health</span>
            </div>
        </div>
        <div class="disclaimer">
            <strong>⚠️ Important Disclaimer:</strong>
            <p>${t('disclaimer', 'This is preliminary medical guidance only. Always consult with licensed healthcare professionals for diagnosis and treatment.')}</p>
        </div>
    `;
    
    messagesContainer.appendChild(welcomeDiv);
}

function displayErrorMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.style.borderColor = 'var(--danger)';
    messageContent.style.color = 'var(--danger)';
    messageContent.innerHTML = `⚠️ <strong>Error:</strong> ${escapeHtml(content)}`;
    
    messageDiv.appendChild(messageContent);
    messagesContainer.appendChild(messageDiv);
    
    if (autoScroll) {
        scrollToBottom();
    }
}

function fillMessage(text) {
    messageInput.value = text;
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
    messageInput.focus();
}

function loadStoredJson(key, fallback) {
    try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : fallback;
    } catch (error) {
        return fallback;
    }
}

function saveStoredJson(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}

function openSymptomWizard() {
    populateSymptomWizard();
    symptomWizardModal?.classList.add('active');
}

function openProfileModal() {
    populateProfileModal();
    profileModal?.classList.add('active');
}

function closeAllWizards() {
    symptomWizardModal?.classList.remove('active');
    profileModal?.classList.remove('active');
}

function populateSymptomWizard() {
    document.getElementById('symptomMain').value = symptomIntake.main_symptom || '';
    document.getElementById('symptomDuration').value = symptomIntake.duration || '';
    document.getElementById('symptomSeverity').value = symptomIntake.severity || '';
    document.getElementById('symptomFever').value = symptomIntake.fever || '';
    document.getElementById('symptomPainLocation').value = symptomIntake.pain_location || '';
    document.getElementById('symptomTriggers').value = symptomIntake.triggers || '';
    document.getElementById('symptomOther').value = symptomIntake.other_symptoms || '';
}

function populateProfileModal() {
    document.getElementById('profileName').value = patientProfile.name || '';
    document.getElementById('profileAge').value = patientProfile.age || '';
    document.getElementById('profileGender').value = patientProfile.gender || patientProfile.sex || '';
    document.getElementById('profileLanguage').value = patientProfile.language || '';
    document.getElementById('profileAllergies').value = Array.isArray(patientProfile.allergies) ? patientProfile.allergies.join(', ') : (patientProfile.allergies || '');
    document.getElementById('profileConditions').value = Array.isArray(patientProfile.chronic_conditions) ? patientProfile.chronic_conditions.join(', ') : (patientProfile.chronic_conditions || '');
    document.getElementById('profileMeds').value = Array.isArray(patientProfile.medications) ? patientProfile.medications.join(', ') : (patientProfile.medications || '');
    document.getElementById('profilePregnancy').value = patientProfile.pregnancy || '';
    document.getElementById('profileHeight').value = patientProfile.height || '';
    document.getElementById('profileWeight').value = patientProfile.weight || '';
}

async function saveSymptomWizard() {
    symptomIntake = {
        main_symptom: document.getElementById('symptomMain').value.trim(),
        duration: document.getElementById('symptomDuration').value.trim(),
        severity: document.getElementById('symptomSeverity').value.trim(),
        fever: document.getElementById('symptomFever').value.trim(),
        pain_location: document.getElementById('symptomPainLocation').value.trim(),
        triggers: document.getElementById('symptomTriggers').value.trim(),
        other_symptoms: document.getElementById('symptomOther').value.trim(),
    };
    saveStoredJson('symptomIntake', symptomIntake);
    await syncStructuredContextToServer();
    updateDoctorHint();
    closeAllWizards();
    showSystemNotice('Symptom check saved. You can now ask your question with more context.');
}

async function saveProfile() {
    patientProfile = {
        name: document.getElementById('profileName').value.trim(),
        age: document.getElementById('profileAge').value.trim(),
        gender: document.getElementById('profileGender').value.trim(),
        language: document.getElementById('profileLanguage').value.trim(),
        allergies: splitCsv(document.getElementById('profileAllergies').value),
        chronic_conditions: splitCsv(document.getElementById('profileConditions').value),
        medications: splitCsv(document.getElementById('profileMeds').value),
        pregnancy: document.getElementById('profilePregnancy').value.trim(),
        height: document.getElementById('profileHeight').value.trim(),
        weight: document.getElementById('profileWeight').value.trim(),
    };
    saveStoredJson('patientProfile', patientProfile);
    await syncStructuredContextToServer();
    updateDoctorHint();
    closeAllWizards();
    showSystemNotice('Health profile saved. Future responses will use this context.');
}

function splitCsv(value) {
    return value
        .split(/[\n,;]/)
        .map((item) => item.trim())
        .filter(Boolean);
}

function handleAttachmentSelection(event) {
    const files = Array.from(event.target.files || []);
    pendingAttachments = files.slice(0, 3).map((file) => ({
        name: file.name,
        type: file.type || 'file',
        size: file.size,
        note: file.type.startsWith('image/') ? 'Image uploaded for context' : 'Document uploaded for context'
    }));
    renderAttachmentChips();
}

function renderAttachmentChips() {
    let chips = document.querySelector('.attachment-preview-row');
    if (!chips) {
        chips = document.createElement('div');
        chips.className = 'attachment-preview-row';
        document.querySelector('.input-section').insertBefore(chips, document.querySelector('.chat-form'));
    }
    chips.innerHTML = '';
    if (!pendingAttachments.length) {
        chips.style.display = 'none';
        return;
    }
    chips.style.display = 'flex';
    pendingAttachments.forEach((attachment, index) => {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'attachment-preview-chip';
        chip.textContent = `${attachment.name}`;
        chip.title = 'Click to remove attachment';
        chip.addEventListener('click', () => {
            pendingAttachments.splice(index, 1);
            renderAttachmentChips();
        });
        chips.appendChild(chip);
    });
}

async function syncStructuredContextToServer() {
    if (!currentSessionId) {
        return;
    }
    try {
        await fetch(`${API_BASE_URL}/chat/context/${currentSessionId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_profile: patientProfile,
                symptom_intake: symptomIntake,
                attachments: pendingAttachments,
            })
        });
    } catch (error) {
        console.warn('Could not sync structured context:', error);
    }
}

// =====================================================
// Utility Functions
// =====================================================

function formatMessage(content) {
    // Escape HTML
    let formatted = escapeHtml(content);
    
    // Convert line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Bold important terms
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    return formatted;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getTimeString() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
}

function showLoading() {
    loadingIndicator.classList.add('active');
    scrollToBottom();
}

function hideLoading() {
    loadingIndicator.classList.remove('active');
}

function showErrorMessage(message) {
    displayErrorMessage(message);
}

function showSystemNotice(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.innerHTML = escapeHtml(message);

    messageDiv.appendChild(messageContent);
    messagesContainer.appendChild(messageDiv);

    if (autoScroll) {
        scrollToBottom();
    }
}

async function loadTranslations() {
    try {
        const response = await fetch(`lang/${currentLanguage}.json`);
        if (response.ok) {
            translations = await response.json();
            return;
        }
    } catch (error) {
        console.warn('Translation file load failed:', error);
    }
    translations = {};
}

function t(key, fallback = '') {
    return translations[key] || fallback || key;
}

function setupLanguageSelector() {
    if (!languageSelect) {
        return;
    }

    languageSelect.value = currentLanguage;
    updateLocalizedUI();
}

async function handleLanguageChange(event) {
    currentLanguage = event.target.value;
    localStorage.setItem('language', currentLanguage);
    await loadTranslations();
    updateLocalizedUI();
    showSystemNotice(`Language changed to ${currentLanguage.toUpperCase()}`);
}

function updateLocalizedUI() {
    document.title = t('app_title', 'Dr. Sehaat - AI Healthcare Assistant');

    const welcomeTitle = messagesContainer?.querySelector('.welcome-section h2');
    const welcomeSubtitle = messagesContainer?.querySelector('.welcome-subtitle');
    const disclaimerText = messagesContainer?.querySelector('.disclaimer p');
    const messagePlaceholder = messageInput;

    if (welcomeTitle) welcomeTitle.textContent = t('welcome', 'Welcome to Dr. Sehaat');
    if (welcomeSubtitle) welcomeSubtitle.textContent = t('welcome_subtitle', 'Your AI Healthcare Assistant');
    if (disclaimerText) disclaimerText.textContent = t('disclaimer', disclaimerText.textContent);
    if (messagePlaceholder) messagePlaceholder.placeholder = t('placeholder', messagePlaceholder.placeholder);
    if (doctorHint) doctorHint.textContent = t('doctor_hint', 'Choose doctor based on your health concern.');
    if (headerSubtitle) {
        const selected = doctorOptions.find(d => d.key === currentDoctorRole);
        const label = selected ? selected.label : t('general_physician', 'General Physician');
        headerSubtitle.textContent = `Professional AI Healthcare Assistant | Active Specialist: ${label}`;
    }
    if (downloadPdfBtn) downloadPdfBtn.textContent = t('download_pdf', '📄 PDF');
    if (voiceBtn) voiceBtn.title = t('start_voice', 'Click to start speaking...');
    if (ttsToggleBtn) ttsToggleBtn.title = t('tts_enabled', 'Text-to-Speech enabled');
    if (ttsEnabledToggle) ttsEnabledToggle.checked = ttsEnabled;
    if (soundToggle) soundToggle.checked = true;
}

function updateTtsButtonState() {
    if (!ttsToggleBtn) return;
    ttsToggleBtn.classList.toggle('enabled', ttsEnabled);
    ttsToggleBtn.title = ttsEnabled ? t('tts_enabled', 'Text-to-Speech enabled') : t('tts_disabled', 'Text-to-Speech disabled');
}

function initializeTextToSpeech() {
    updateTtsButtonState();
    if (ttsEnabledToggle) {
        ttsEnabledToggle.checked = ttsEnabled;
    }
}

function speakText(text) {
    if (!ttsEnabled || !window.speechSynthesis) {
        return;
    }

    window.speechSynthesis.cancel();
    currentSynthesis = new SpeechSynthesisUtterance(text);
    currentSynthesis.lang = currentLanguage === 'hi' ? 'hi-IN' : 'en-US';
    currentSynthesis.rate = 1;
    currentSynthesis.pitch = 1;
    window.speechSynthesis.speak(currentSynthesis);
}

function toggleTextToSpeech() {
    ttsEnabled = !ttsEnabled;
    localStorage.setItem('ttsEnabled', String(ttsEnabled));
    if (ttsEnabledToggle) {
        ttsEnabledToggle.checked = ttsEnabled;
    }
    updateTtsButtonState();
    showSystemNotice(ttsEnabled ? t('tts_enabled', 'Text-to-Speech enabled') : t('tts_disabled', 'Text-to-Speech disabled'));
}

function initializeVoiceInput() {
    const SpeechRecognitionClass = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognitionClass || !voiceBtn) {
        return;
    }

    speechRecognition = new SpeechRecognitionClass();
    speechRecognition.continuous = false;
    speechRecognition.interimResults = false;
    speechRecognition.lang = currentLanguage === 'hi' ? 'hi-IN' : 'en-US';

    speechRecognition.onstart = () => {
        isRecording = true;
        voiceBtn.classList.add('recording');
        voiceBtn.title = t('listening', 'Listening... (Click to stop)');
        showSystemNotice(t('listening', 'Listening... (Click to stop)'));
    };

    speechRecognition.onresult = (event) => {
        const transcript = event.results?.[0]?.[0]?.transcript || '';
        if (transcript) {
            messageInput.value = transcript;
            autoResizeTextarea();
        }
    };

    speechRecognition.onerror = () => {
        showErrorMessage(t('voice_error', 'Could not process voice input. Please try again.'));
        stopVoiceInput();
    };

    speechRecognition.onend = () => {
        stopVoiceInput();
    };
}

function toggleVoiceInput() {
    if (!speechRecognition) {
        showErrorMessage('Voice input is not supported in this browser.');
        return;
    }

    if (isRecording) {
        speechRecognition.stop();
        return;
    }

    speechRecognition.lang = currentLanguage === 'hi' ? 'hi-IN' : 'en-US';
    speechRecognition.start();
}

function stopVoiceInput() {
    isRecording = false;
    voiceBtn?.classList.remove('recording');
    if (voiceBtn) {
        voiceBtn.title = t('start_voice', 'Click to start speaking...');
    }
}

async function downloadSessionPdf() {
    if (!currentSessionId) {
        showErrorMessage('Start a chat before downloading a PDF report.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/chat/export-pdf/${currentSessionId}`);
        if (!response.ok) {
            throw new Error('PDF export failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `Dr_Sehaat_Report_${currentSessionId.slice(0, 8)}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        showSystemNotice(t('pdf_download', 'Downloaded consultation report'));
    } catch (error) {
        console.error('PDF download error:', error);
        showErrorMessage('Unable to download PDF report right now.');
    }
}

// =====================================================
// Settings and UI Functions
// =====================================================

function openSettings() {
    settingsModal.classList.add('active');
}

function closeModal(modal) {
    modal.classList.remove('active');
}

function showEmergencyAlert() {
    emergencyModal.classList.add('active');
}

function closeEmergencyModal() {
    emergencyModal.classList.remove('active');
}

function playNotificationSound() {
    if (soundToggle.checked) {
        // Simple beep using Web Audio API
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
    }
}

async function clearAllChats() {
    if (confirm('Are you sure you want to clear all chats? This action cannot be undone.')) {
        localStorage.removeItem('chatHistory');
        await startNewChat();
        console.log('✅ All chats cleared');
    }
}

function addToChatHistory() {
    const timestamp = new Date().toLocaleTimeString();
    const item = document.createElement('div');
    item.className = 'history-item active';
    item.textContent = `Chat - ${timestamp}`;
    
    const existingEmpty = document.querySelector('.empty-history');
    if (existingEmpty) {
        existingEmpty.remove();
    }
    
    chatHistoryList.insertBefore(item, chatHistoryList.firstChild);
}

async function loadDoctorOptions() {
    try {
        const response = await fetch(`${API_BASE_URL}/doctors`);
        const data = await response.json();
        if (!data.success || !Array.isArray(data.data.doctors)) {
            return;
        }

        doctorOptions = data.data.doctors;
        if (!doctorSelect) {
            return;
        }

        doctorSelect.innerHTML = '';
        doctorOptions.forEach((doctor) => {
            const option = document.createElement('option');
            option.value = doctor.key;
            option.textContent = doctor.label;
            doctorSelect.appendChild(option);
        });

        const hasCurrent = doctorOptions.some(d => d.key === currentDoctorRole);
        currentDoctorRole = hasCurrent ? currentDoctorRole : (data.data.default || 'general_physician');
        doctorSelect.value = currentDoctorRole;
        localStorage.setItem('doctorRole', currentDoctorRole);
        updateDoctorHint();
    } catch (error) {
        console.error('❌ Error loading doctor options:', error);
    }
}

function setupDoctorSelection() {
    if (!doctorSelect) {
        return;
    }

    doctorSelect.value = currentDoctorRole;
    updateDoctorHint();

    doctorSelect.addEventListener('change', async (e) => {
        currentDoctorRole = e.target.value;
        localStorage.setItem('doctorRole', currentDoctorRole);
        updateDoctorHint();
        updateDoctorHeader();

        // Start a fresh session on specialist switch to keep context consistent.
        await startNewChat();
    });
}

function updateDoctorHint() {
    if (!doctorHint) {
        return;
    }
    const selected = doctorOptions.find(d => d.key === currentDoctorRole);
    if (selected && selected.description) {
        doctorHint.textContent = selected.description;
    } else {
        doctorHint.textContent = 'Choose doctor based on your health concern.';
    }
}

function updateDoctorHeader() {
    if (!headerSubtitle) {
        return;
    }
    const selected = doctorOptions.find(d => d.key === currentDoctorRole);
    const label = selected ? selected.label : 'General Physician';
    headerSubtitle.textContent = `Professional AI Healthcare Assistant | Active Specialist: ${label}`;
    if (doctorLiveBadge) {
        doctorLiveBadge.textContent = label;
        doctorLiveBadge.title = label;
    }
}

// =====================================================
// Server Status Check
// =====================================================

async function checkServerStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ Server is online');
        }
    } catch (error) {
        console.error('❌ Server is not responding:', error);
        showErrorMessage('Cannot connect to server. Make sure the backend is running on http://localhost:5000');
    }
}

// =====================================================
// Page Unload Handler
// =====================================================

window.addEventListener('beforeunload', async () => {
    if (currentSessionId) {
        // Optional: Send close session request
        await fetch(`${API_BASE_URL}/chat/close-session/${currentSessionId}`, {
            method: 'POST'
        }).catch(err => console.log('Session closed'));
    }
});

console.log('✅ Frontend script loaded successfully');

window.openSymptomWizard = openSymptomWizard;
window.openProfileModal = openProfileModal;
window.saveSymptomWizard = saveSymptomWizard;
window.saveProfile = saveProfile;
