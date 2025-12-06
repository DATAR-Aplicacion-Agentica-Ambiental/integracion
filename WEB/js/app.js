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
        audioCanvas: document.getElementById('audio-canvas'),

        // File Preview
        filePreview: document.getElementById('file-preview'),

        // Lightbox
        lightbox: document.getElementById('lightbox'),
        lightboxImg: document.getElementById('lightbox-img'),
        lightboxClose: document.getElementById('lightbox-close'),

        // Dev Panel
        devPanel: document.getElementById('dev-panel'),
        devToggle: document.getElementById('dev-toggle'),
        devContent: document.getElementById('dev-content'),
        devStatus: document.getElementById('dev-status'),
        authTokenInput: document.getElementById('auth-token-input'),
        btnSetToken: document.getElementById('btn-set-token'),
        btnClearToken: document.getElementById('btn-clear-token'),
        btnCreateSession: document.getElementById('btn-create-session')
    };

    // ========================================
    // State
    // ========================================
    const state = {
        isLoading: false,
        isRecording: false,
        currentAgent: 'Gente_Raiz',
        messages: [],
        pendingFiles: [] // Files waiting to be sent
    };

    // ========================================
    // Initialization
    // ========================================
    function init() {
        // Initialize API
        DatarAPI.init();

        // Configure marked.js for Markdown parsing
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true,
                headerIds: false,
                mangle: false
            });
        }

        // Bind events
        bindEvents();

        // Initialize audio visualization
        initAudioVisualization();

        // Initialize lightbox
        initLightbox();

        // Initialize dev panel
        initDevPanel();

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
        const files = [...state.pendingFiles];

        if ((!message && files.length === 0) || state.isLoading) return;

        // Add user message to chat (with file info if present)
        if (message || files.length > 0) {
            addUserMessage(message, files);
        }

        // Clear input and files
        elements.messageInput.value = '';
        clearPendingFiles();
        updateSendButtonState();

        // Set loading state
        setLoading(true);

        // Show typing indicator
        const typingId = showTypingIndicator();

        try {
            // Send message to API with files
            const events = await DatarAPI.sendMessage(message, files);

            // Remove typing indicator
            removeTypingIndicator(typingId);

            // Process response events
            for (const event of events) {
                const content = DatarAPI.extractContentFromEvent(event);
                const author = DatarAPI.getEventAuthor(event);

                // Only add message if there's content
                if (content.text || content.images.length > 0 || content.audio.length > 0) {
                    addAgentMessage(content, author);
                }
            }
        } catch (error) {
            console.error('[App] Error sending message:', error);
            removeTypingIndicator(typingId);
            addAgentMessage({ text: 'Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.', images: [], audio: [] }, 'Sistema');
        } finally {
            setLoading(false);
        }
    }

    /**
     * Add a user message to the chat
     */
    function addUserMessage(text, files = []) {
        const messageEl = document.createElement('div');
        messageEl.className = 'message message-user';

        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';

        // Add text if present
        if (text) {
            const textEl = document.createElement('p');
            textEl.textContent = text;
            contentEl.appendChild(textEl);
        }

        // Add file previews
        if (files.length > 0) {
            const filesContainer = document.createElement('div');
            filesContainer.className = 'message-files';

            for (const file of files) {
                if (file.type.startsWith('image/')) {
                    const img = document.createElement('img');
                    img.className = 'message-image';
                    img.src = URL.createObjectURL(file);
                    img.alt = file.name;
                    img.addEventListener('click', () => openLightbox(img.src));
                    filesContainer.appendChild(img);
                } else if (file.type.startsWith('audio/')) {
                    const audioContainer = document.createElement('div');
                    audioContainer.className = 'message-audio';
                    const audio = document.createElement('audio');
                    audio.controls = true;
                    audio.src = URL.createObjectURL(file);
                    audioContainer.appendChild(audio);
                    filesContainer.appendChild(audioContainer);
                } else {
                    const fileInfo = document.createElement('div');
                    fileInfo.className = 'message-file-info';
                    fileInfo.textContent = `📎 ${file.name}`;
                    filesContainer.appendChild(fileInfo);
                }
            }

            contentEl.appendChild(filesContainer);
        }

        messageEl.appendChild(contentEl);
        insertMessage(messageEl);

        // Store in state
        state.messages.push({ text, type: 'user', files: files.map(f => f.name), timestamp: Date.now() });
    }

    /**
     * Add an agent message to the chat with Markdown and media support
     */
    function addAgentMessage(content, author = null) {
        const messageEl = document.createElement('div');
        messageEl.className = 'message message-agent';

        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';

        // Render Markdown text
        if (content.text) {
            const textContainer = document.createElement('div');
            textContainer.className = 'markdown';

            // Use marked.js to parse Markdown
            if (typeof marked !== 'undefined') {
                textContainer.innerHTML = marked.parse(content.text);
                // Post-process to convert media URLs to players
                processMediaUrls(textContainer);
            } else {
                textContainer.textContent = content.text;
            }

            contentEl.appendChild(textContainer);
        }

        // Add images
        if (content.images && content.images.length > 0) {
            const imagesContainer = document.createElement('div');
            imagesContainer.className = 'message-images';

            for (const image of content.images) {
                const img = document.createElement('img');
                img.className = 'message-image';
                img.src = image.url;
                img.alt = 'Imagen del agente';
                img.addEventListener('click', () => openLightbox(image.url));
                imagesContainer.appendChild(img);
            }

            contentEl.appendChild(imagesContainer);
        }

        // Add audio players
        if (content.audio && content.audio.length > 0) {
            for (const audioData of content.audio) {
                const audioContainer = document.createElement('div');
                audioContainer.className = 'message-audio';
                const audio = document.createElement('audio');
                audio.controls = true;
                audio.src = audioData.url;
                audioContainer.appendChild(audio);
                contentEl.appendChild(audioContainer);
            }
        }

        messageEl.appendChild(contentEl);

        // Add play/pause button for text-to-speech
        if (content.text) {
            const actionBtn = document.createElement('button');
            actionBtn.className = 'message-action';
            actionBtn.setAttribute('aria-label', 'Reproducir');
            actionBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 22v-20l18 10-18 10z"/>
                </svg>
            `;
            // Strip HTML/Markdown for cleaner TTS
            const plainText = content.text.replace(/[#*_`\[\]()]/g, '').trim();
            actionBtn.addEventListener('click', () => toggleSpeech(plainText, actionBtn));
            messageEl.appendChild(actionBtn);
        }

        insertMessage(messageEl);

        // Store in state
        state.messages.push({
            text: content.text,
            type: 'agent',
            author,
            images: content.images?.length || 0,
            audio: content.audio?.length || 0,
            timestamp: Date.now()
        });
    }

    /**
     * Insert a message element into the chat
     */
    function insertMessage(messageEl) {
        const audioViz = document.getElementById('audio-viz');
        if (audioViz) {
            elements.chatMessages.insertBefore(messageEl, audioViz);
        } else {
            elements.chatMessages.appendChild(messageEl);
        }
        scrollToBottom();
    }

    /**
     * Process media URLs in rendered markdown
     * Converts links to audio/image files into inline players/images
     */
    function processMediaUrls(container) {
        // Audio extensions
        const audioExtensions = /\.(wav|mp3|ogg|m4a|webm|flac)$/i;
        // Image extensions
        const imageExtensions = /\.(jpg|jpeg|png|gif|webp|svg)$/i;

        // Find all links in the container
        const links = container.querySelectorAll('a[href]');

        links.forEach(link => {
            const href = link.href;

            // Check if it's an audio file
            if (audioExtensions.test(href)) {
                const audioWrapper = document.createElement('div');
                audioWrapper.className = 'message-audio inline-audio';

                const audio = document.createElement('audio');
                audio.controls = true;
                audio.src = href;
                audio.preload = 'metadata';

                // Keep the link text as a label
                const label = document.createElement('span');
                label.className = 'audio-label';
                label.textContent = link.textContent || 'Audio';

                audioWrapper.appendChild(label);
                audioWrapper.appendChild(audio);

                // Replace the link with the audio player
                link.parentNode.replaceChild(audioWrapper, link);
            }
            // Check if it's an image file (and not already an img tag)
            else if (imageExtensions.test(href) && !link.querySelector('img')) {
                const img = document.createElement('img');
                img.className = 'message-image inline-image';
                img.src = href;
                img.alt = link.textContent || 'Imagen';
                img.addEventListener('click', () => openLightbox(href));

                // Replace the link with the image
                link.parentNode.replaceChild(img, link);
            }
        });
    }

    /**
     * Legacy addMessage function for backward compatibility
     */
    function addMessage(text, type, author = null) {
        if (type === 'user') {
            addUserMessage(text);
        } else {
            addAgentMessage({ text, images: [], audio: [] }, author);
        }
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
        const hasFiles = state.pendingFiles.length > 0;
        elements.btnSend.disabled = (!hasText && !hasFiles) || state.isLoading;
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
        console.log('[App] Files selected:', files);

        // Add files to pending state
        for (const file of files) {
            // Filter by accepted types (images and audio)
            if (file.type.startsWith('image/') || file.type.startsWith('audio/')) {
                state.pendingFiles.push(file);
            } else {
                console.warn('[App] Unsupported file type:', file.type);
            }
        }

        // Close modal
        closeAllModals();

        // Update file preview
        updateFilePreview();

        // Update send button state
        updateSendButtonState();

        // Focus input
        elements.messageInput.focus();
    }

    /**
     * Update the file preview area
     */
    function updateFilePreview() {
        const preview = elements.filePreview;
        if (!preview) return;

        // Clear existing preview
        preview.innerHTML = '';

        if (state.pendingFiles.length === 0) {
            preview.style.display = 'none';
            return;
        }

        preview.style.display = 'flex';

        for (let i = 0; i < state.pendingFiles.length; i++) {
            const file = state.pendingFiles[i];
            const item = document.createElement('div');
            item.className = 'file-preview-item';

            if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.alt = file.name;
                item.appendChild(img);
            } else if (file.type.startsWith('audio/')) {
                const icon = document.createElement('div');
                icon.className = 'file-preview-icon';
                icon.innerHTML = `
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 18V5l12-2v13"/>
                        <circle cx="6" cy="18" r="3"/>
                        <circle cx="18" cy="16" r="3"/>
                    </svg>
                `;
                item.appendChild(icon);

                const name = document.createElement('span');
                name.className = 'file-preview-name';
                name.textContent = file.name.length > 15 ? file.name.substring(0, 12) + '...' : file.name;
                item.appendChild(name);
            }

            // Remove button
            const removeBtn = document.createElement('button');
            removeBtn.className = 'file-preview-remove';
            removeBtn.innerHTML = '&times;';
            removeBtn.setAttribute('aria-label', 'Eliminar archivo');
            removeBtn.addEventListener('click', () => removePendingFile(i));
            item.appendChild(removeBtn);

            preview.appendChild(item);
        }
    }

    /**
     * Remove a file from the pending list
     */
    function removePendingFile(index) {
        state.pendingFiles.splice(index, 1);
        updateFilePreview();
        updateSendButtonState();
    }

    /**
     * Clear all pending files
     */
    function clearPendingFiles() {
        state.pendingFiles = [];
        updateFilePreview();
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
    let currentUtterance = null;
    let isSpeaking = false;

    // Pre-cargar voces (Chrome las carga async)
    if ('speechSynthesis' in window) {
        speechSynthesis.getVoices();
        speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices();
    }

    /**
     * Toggle speech: play, pause, or resume
     * @param {string} text - Text to speak
     * @param {HTMLElement} button - The button element to update icon
     */
    function toggleSpeech(text, button) {
        if (!('speechSynthesis' in window)) {
            console.warn('[App] Text-to-speech not supported');
            return;
        }

        const synth = window.speechSynthesis;

        // If currently speaking this text, pause it
        if (isSpeaking && synth.speaking) {
            if (synth.paused) {
                synth.resume();
                updateSpeechButton(button, 'speaking');
            } else {
                synth.pause();
                updateSpeechButton(button, 'paused');
            }
            return;
        }

        // Cancel any previous speech and start new
        synth.cancel();

        currentUtterance = new SpeechSynthesisUtterance(text);
        currentUtterance.lang = 'es-ES';
        currentUtterance.rate = 1.1;  // Más rápido
        currentUtterance.pitch = 1;

        // Usar voz por defecto del sistema (más rápida de cargar)
        const voices = synth.getVoices();
        const spanishVoice = voices.find(v => v.lang.startsWith('es')) || voices[0];
        if (spanishVoice) {
            currentUtterance.voice = spanishVoice;
        }

        currentUtterance.onstart = () => {
            isSpeaking = true;
            updateSpeechButton(button, 'speaking');
        };

        currentUtterance.onend = () => {
            isSpeaking = false;
            updateSpeechButton(button, 'idle');
        };

        currentUtterance.onerror = () => {
            isSpeaking = false;
            updateSpeechButton(button, 'idle');
        };

        synth.speak(currentUtterance);
    }

    /**
     * Update speech button icon based on state
     */
    function updateSpeechButton(button, state) {
        if (!button) return;

        const icons = {
            idle: `<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 22v-20l18 10-18 10z"/>
            </svg>`,
            speaking: `<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="4" width="4" height="16"/>
                <rect x="14" y="4" width="4" height="16"/>
            </svg>`,
            paused: `<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 22v-20l18 10-18 10z"/>
            </svg>`
        };

        button.innerHTML = icons[state] || icons.idle;
        button.setAttribute('aria-label', state === 'speaking' ? 'Pausar' : 'Reproducir');
    }

    /**
     * Legacy speakText function for backward compatibility
     */
    function speakText(text) {
        if (!('speechSynthesis' in window)) {
            console.warn('[App] Text-to-speech not supported');
            return;
        }
        const synth = window.speechSynthesis;
        synth.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'es-ES';
        utterance.rate = 1.1;
        utterance.pitch = 1;
        const voices = synth.getVoices();
        const spanishVoice = voices.find(v => v.lang.startsWith('es')) || voices[0];
        if (spanishVoice) utterance.voice = spanishVoice;
        synth.speak(utterance);
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
        // Escape to close modals and lightbox
        if (e.key === 'Escape') {
            closeAllModals();
            closeLightbox();
            if (state.isRecording) {
                stopVoiceRecording();
            }
        }
    }

    // ========================================
    // Lightbox
    // ========================================
    function initLightbox() {
        if (elements.lightboxClose) {
            elements.lightboxClose.addEventListener('click', closeLightbox);
        }

        if (elements.lightbox) {
            elements.lightbox.addEventListener('click', (e) => {
                // Close if clicking on backdrop (not the image)
                if (e.target === elements.lightbox) {
                    closeLightbox();
                }
            });
        }
    }

    function openLightbox(imageUrl) {
        if (!elements.lightbox || !elements.lightboxImg) return;

        elements.lightboxImg.src = imageUrl;
        elements.lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        if (!elements.lightbox) return;

        elements.lightbox.classList.remove('active');
        elements.lightboxImg.src = '';
        document.body.style.overflow = '';
    }

    // ========================================
    // Dev Panel
    // ========================================
    function initDevPanel() {
        const config = DatarAPI.getConfig();

        // Only show dev panel in dev mode
        if (!config.devMode || !elements.devPanel) {
            return;
        }

        elements.devPanel.style.display = 'block';

        // Toggle panel
        if (elements.devToggle) {
            elements.devToggle.addEventListener('click', () => {
                elements.devPanel.classList.toggle('open');
            });
        }

        // Set token button
        if (elements.btnSetToken) {
            elements.btnSetToken.addEventListener('click', handleSetToken);
        }

        // Clear token button
        if (elements.btnClearToken) {
            elements.btnClearToken.addEventListener('click', handleClearToken);
        }

        // Create session button
        if (elements.btnCreateSession) {
            elements.btnCreateSession.addEventListener('click', handleCreateSession);
        }

        // Update initial status
        updateDevStatus();
    }

    function updateDevStatus() {
        if (!elements.devStatus) return;

        const hasToken = DatarAPI.hasAuthToken();
        const config = DatarAPI.getConfig();

        const statusText = elements.devStatus.querySelector('.status-text');

        if (hasToken) {
            elements.devStatus.classList.add('connected');
            statusText.textContent = config.useMock ? 'Token OK (Mock activo)' : 'Token configurado';
        } else {
            elements.devStatus.classList.remove('connected');
            statusText.textContent = config.useMock ? 'Mock activo' : 'Sin token';
        }
    }

    async function handleSetToken() {
        const token = elements.authTokenInput?.value.trim();

        if (!token) {
            alert('Por favor, ingresa un token válido');
            return;
        }

        DatarAPI.setAuthToken(token);
        elements.authTokenInput.value = '';
        updateDevStatus();

        // Try to create a session
        await handleCreateSession();
    }

    function handleClearToken() {
        DatarAPI.setAuthToken(null);
        updateDevStatus();
    }

    async function handleCreateSession() {
        try {
            const result = await DatarAPI.createSession();
            console.log('[App] Session created:', result);
            addAgentMessage({
                text: `Sesión creada: **${result.id}**\n\nUsuario: \`${DatarAPI.getUserId()}\``,
                images: [],
                audio: []
            }, 'Sistema');
        } catch (error) {
            console.error('[App] Failed to create session:', error);
            addAgentMessage({
                text: `Error al crear sesión: ${error.message}`,
                images: [],
                audio: []
            }, 'Sistema');
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
