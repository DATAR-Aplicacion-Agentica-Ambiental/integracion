/**
 * DATAR Chat Application
 * Main application logic
 */

(function() {
    'use strict';

    // ========================================
    // DOM Elements
    // ========================================
    const elements = {
        // Chat
        chatMessages: document.getElementById('chat-messages'),
        messageInput: document.getElementById('message-input'),
        btnSend: document.getElementById('btn-send'),

        // Actions
        btnAttach: document.getElementById('btn-attach'),
        btnMic: document.getElementById('btn-mic'),
        btnVoice: document.getElementById('btn-voice'),

        // Navigation
        navButtons: document.querySelectorAll('.nav-btn'),

        // Modals
        uploadModal: document.getElementById('upload-modal'),
        uploadZone: document.getElementById('upload-zone'),
        fileInput: document.getElementById('file-input'),

        // Voice
        voiceOverlay: document.getElementById('voice-overlay'),
        voiceStop: document.getElementById('voice-stop'),
        voiceCanvas: document.getElementById('voice-canvas'),

        // Audio
        audioCanvas: document.getElementById('audio-canvas')
    };

    // ========================================
    // State
    // ========================================
    const state = {
        isLoading: false,
        isRecording: false,
        currentAgent: 'Gente_Raiz',
        messages: []
    };

    // ========================================
    // Initialization
    // ========================================
    function init() {
        // Initialize API
        DatarAPI.init();

        // Bind events
        bindEvents();

        // Initialize audio visualization
        initAudioVisualization();

        // Focus input
        elements.messageInput.focus();

        console.log('[App] DATAR Chat initialized');
    }

    // ========================================
    // Event Bindings
    // ========================================
    function bindEvents() {
        // Send message
        elements.btnSend.addEventListener('click', handleSendMessage);
        elements.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });

        // Input state
        elements.messageInput.addEventListener('input', updateSendButtonState);

        // Attach file
        elements.btnAttach.addEventListener('click', () => openModal('upload'));

        // Voice recording
        if (elements.btnMic) {
            elements.btnMic.addEventListener('click', toggleVoiceRecording);
        }
        if (elements.btnVoice) {
            elements.btnVoice.addEventListener('click', toggleVoiceRecording);
        }
        if (elements.voiceStop) {
            elements.voiceStop.addEventListener('click', stopVoiceRecording);
        }

        // Navigation buttons
        elements.navButtons.forEach(btn => {
            btn.addEventListener('click', () => handleNavAction(btn.dataset.action));
        });

        // Upload zone
        if (elements.uploadZone) {
            elements.uploadZone.addEventListener('click', () => elements.fileInput.click());
            elements.uploadZone.addEventListener('dragover', handleDragOver);
            elements.uploadZone.addEventListener('dragleave', handleDragLeave);
            elements.uploadZone.addEventListener('drop', handleFileDrop);
        }

        if (elements.fileInput) {
            elements.fileInput.addEventListener('change', handleFileSelect);
        }

        // Modal backdrop click
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
            backdrop.addEventListener('click', closeAllModals);
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', handleKeyboard);
    }

    // ========================================
    // Message Handling
    // ========================================
    async function handleSendMessage() {
        const message = elements.messageInput.value.trim();

        if (!message || state.isLoading) return;

        // Add user message to chat
        addMessage(message, 'user');

        // Clear input
        elements.messageInput.value = '';
        updateSendButtonState();

        // Set loading state
        setLoading(true);

        // Show typing indicator
        const typingId = showTypingIndicator();

        try {
            // Send message to API
            const events = await DatarAPI.sendMessage(message);

            // Remove typing indicator
            removeTypingIndicator(typingId);

            // Process response events
            for (const event of events) {
                const text = DatarAPI.extractTextFromEvent(event);
                if (text) {
                    const author = DatarAPI.getEventAuthor(event);
                    addMessage(text, 'agent', author);
                }
            }
        } catch (error) {
            console.error('[App] Error sending message:', error);
            removeTypingIndicator(typingId);
            addMessage('Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.', 'agent', 'Sistema');
        } finally {
            setLoading(false);
        }
    }

    function addMessage(text, type, author = null) {
        const messageEl = document.createElement('div');
        messageEl.className = `message message-${type}`;

        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';

        const textEl = document.createElement('p');
        textEl.textContent = text;
        contentEl.appendChild(textEl);

        messageEl.appendChild(contentEl);

        // Add play button for agent messages
        if (type === 'agent') {
            const actionBtn = document.createElement('button');
            actionBtn.className = 'message-action';
            actionBtn.setAttribute('aria-label', 'Reproducir');
            actionBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 22v-20l18 10-18 10z"/>
                </svg>
            `;
            actionBtn.addEventListener('click', () => speakText(text));
            messageEl.appendChild(actionBtn);
        }

        // Insert before audio visualization
        const audioViz = document.getElementById('audio-viz');
        if (audioViz) {
            elements.chatMessages.insertBefore(messageEl, audioViz);
        } else {
            elements.chatMessages.appendChild(messageEl);
        }

        // Scroll to bottom
        scrollToBottom();

        // Store in state
        state.messages.push({ text, type, author, timestamp: Date.now() });
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const typingEl = document.createElement('div');
        typingEl.id = id;
        typingEl.className = 'message message-agent';
        typingEl.innerHTML = `
            <div class="message-content">
                <div class="loading">
                    <div class="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;

        const audioViz = document.getElementById('audio-viz');
        if (audioViz) {
            elements.chatMessages.insertBefore(typingEl, audioViz);
        } else {
            elements.chatMessages.appendChild(typingEl);
        }

        scrollToBottom();
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) {
            el.remove();
        }
    }

    function scrollToBottom() {
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }

    // ========================================
    // UI State Management
    // ========================================
    function setLoading(loading) {
        state.isLoading = loading;
        elements.btnSend.disabled = loading;
        elements.messageInput.disabled = loading;

        if (loading) {
            elements.btnSend.classList.add('loading');
        } else {
            elements.btnSend.classList.remove('loading');
            elements.messageInput.focus();
        }
    }

    function updateSendButtonState() {
        const hasText = elements.messageInput.value.trim().length > 0;
        elements.btnSend.disabled = !hasText || state.isLoading;
    }

    // ========================================
    // Modal Management
    // ========================================
    function openModal(type) {
        closeAllModals();

        switch (type) {
            case 'upload':
                elements.uploadModal.classList.add('active');
                break;
        }
    }

    function closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    // ========================================
    // File Upload
    // ========================================
    function handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        elements.uploadZone.classList.add('dragover');
    }

    function handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        elements.uploadZone.classList.remove('dragover');
    }

    function handleFileDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        elements.uploadZone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            processFiles(files);
        }
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            processFiles(files);
        }
    }

    function processFiles(files) {
        // TODO: Implement file upload to API
        console.log('[App] Files selected:', files);

        // For now, just close modal and show message
        closeAllModals();
        addMessage(`Archivo(s) seleccionado(s): ${Array.from(files).map(f => f.name).join(', ')}`, 'user');
    }

    // ========================================
    // Voice Recording
    // ========================================
    function toggleVoiceRecording() {
        if (state.isRecording) {
            stopVoiceRecording();
        } else {
            startVoiceRecording();
        }
    }

    function startVoiceRecording() {
        // Check for browser support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Tu navegador no soporta reconocimiento de voz.');
            return;
        }

        state.isRecording = true;
        elements.voiceOverlay.classList.add('active');

        // Initialize speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();

        recognition.lang = 'es-ES';
        recognition.continuous = false;
        recognition.interimResults = true;

        recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0].transcript)
                .join('');

            elements.messageInput.value = transcript;
        };

        recognition.onend = () => {
            stopVoiceRecording();
        };

        recognition.onerror = (event) => {
            console.error('[App] Speech recognition error:', event.error);
            stopVoiceRecording();
        };

        recognition.start();
        state.recognition = recognition;

        // Start voice animation
        startVoiceAnimation();
    }

    function stopVoiceRecording() {
        state.isRecording = false;
        elements.voiceOverlay.classList.remove('active');

        if (state.recognition) {
            state.recognition.stop();
            state.recognition = null;
        }

        stopVoiceAnimation();
        updateSendButtonState();
    }

    // ========================================
    // Audio Visualization
    // ========================================
    let audioAnimationId = null;
    let voiceAnimationId = null;

    function initAudioVisualization() {
        const canvas = elements.audioCanvas;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width = 200;
        const height = canvas.height = 100;

        function draw() {
            ctx.clearRect(0, 0, width, height);

            // Draw wave
            ctx.strokeStyle = '#D4763D';
            ctx.lineWidth = 2;
            ctx.beginPath();

            const time = Date.now() / 1000;
            for (let x = 0; x < width; x++) {
                const y = height / 2 + Math.sin(x * 0.05 + time * 2) * 20 * Math.sin(time * 0.5);
                if (x === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }

            ctx.stroke();

            // Add glow effect
            ctx.shadowColor = '#FF8C42';
            ctx.shadowBlur = 10;

            audioAnimationId = requestAnimationFrame(draw);
        }

        draw();
    }

    function startVoiceAnimation() {
        const canvas = elements.voiceCanvas;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width = 200;
        const height = canvas.height = 100;

        function draw() {
            ctx.clearRect(0, 0, width, height);

            ctx.strokeStyle = '#FF8C42';
            ctx.lineWidth = 3;
            ctx.beginPath();

            const time = Date.now() / 1000;
            for (let x = 0; x < width; x++) {
                const amplitude = 30 + Math.sin(time * 3) * 15;
                const y = height / 2 + Math.sin(x * 0.08 + time * 4) * amplitude;
                if (x === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }

            ctx.stroke();
            voiceAnimationId = requestAnimationFrame(draw);
        }

        draw();
    }

    function stopVoiceAnimation() {
        if (voiceAnimationId) {
            cancelAnimationFrame(voiceAnimationId);
            voiceAnimationId = null;
        }
    }

    // ========================================
    // Text-to-Speech
    // ========================================
    function speakText(text) {
        if (!('speechSynthesis' in window)) {
            console.warn('[App] Text-to-speech not supported');
            return;
        }

        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'es-ES';
        utterance.rate = 0.9;
        utterance.pitch = 1;

        window.speechSynthesis.speak(utterance);
    }

    // ========================================
    // Navigation Actions
    // ========================================
    function handleNavAction(action) {
        switch (action) {
            case 'gallery':
            case 'documents':
                openModal('upload');
                break;
            case 'camera':
            case 'video':
                // TODO: Implement camera capture
                alert('Función de cámara próximamente disponible');
                break;
        }
    }

    // ========================================
    // Keyboard Shortcuts
    // ========================================
    function handleKeyboard(e) {
        // Escape to close modals
        if (e.key === 'Escape') {
            closeAllModals();
            if (state.isRecording) {
                stopVoiceRecording();
            }
        }
    }

    // ========================================
    // Start Application
    // ========================================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
