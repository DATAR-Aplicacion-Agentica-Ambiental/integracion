/**
 * DATAR API Client
 * Handles communication with the Google ADK backend
 */

const DatarAPI = (function() {
    'use strict';

    // Configuration
    const CONFIG = {
        // Production URL (Cloud Run)
        baseUrl: 'https://datar-integraciones-dd3vrcpotq-rj.a.run.app',
        // Local development URL
        localUrl: 'http://localhost:8000',
        appName: 'datar_integraciones',
        // Set to true to use mock data (when API is not available)
        useMock: true
    };

    // State
    let currentUserId = null;
    let currentSessionId = null;

    /**
     * Initialize API client with user and session IDs
     */
    function init(userId, sessionId) {
        currentUserId = userId || generateId('user');
        currentSessionId = sessionId || generateId('session');
        console.log('[DatarAPI] Initialized:', { userId: currentUserId, sessionId: currentSessionId });
        return { userId: currentUserId, sessionId: currentSessionId };
    }

    /**
     * Generate a random ID
     */
    function generateId(prefix) {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Get the base URL based on environment
     */
    function getBaseUrl() {
        // Check if running locally
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return CONFIG.localUrl;
        }
        return CONFIG.baseUrl;
    }

    /**
     * Convert a File to base64 string
     * @param {File} file - File object
     * @returns {Promise<string>} - Base64 encoded string
     */
    async function fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                // Remove the data URL prefix (e.g., "data:image/png;base64,")
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    /**
     * Get MIME type from file
     * @param {File} file - File object
     * @returns {string} - MIME type
     */
    function getFileMimeType(file) {
        return file.type || 'application/octet-stream';
    }

    /**
     * Build message parts from text and files
     * @param {string} message - Text message
     * @param {File[]} files - Array of files to send
     * @returns {Promise<Array>} - Array of parts for ADK API
     */
    async function buildMessageParts(message, files = []) {
        const parts = [];

        // Add text part if present
        if (message && message.trim()) {
            parts.push({ text: message });
        }

        // Add file parts
        for (const file of files) {
            const base64Data = await fileToBase64(file);
            const mimeType = getFileMimeType(file);

            // ADK uses inline_data for binary content
            parts.push({
                inline_data: {
                    mime_type: mimeType,
                    data: base64Data
                }
            });
        }

        return parts;
    }

    /**
     * Build the request body for ADK API
     * @param {string} message - User message text
     * @param {File[]} files - Optional files to send
     * @returns {Promise<object>} - Request body in ADK format
     */
    async function buildRequestBody(message, files = []) {
        const parts = await buildMessageParts(message, files);

        return {
            app_name: CONFIG.appName,
            user_id: currentUserId,
            session_id: currentSessionId,
            new_message: {
                role: 'user',
                parts: parts
            }
        };
    }

    /**
     * Send a message to the agent (non-streaming)
     * @param {string} message - User message
     * @param {File[]} files - Optional files to send
     * @param {string} [authToken] - Optional auth token for Cloud Run
     * @returns {Promise<Array>} - Array of event objects
     */
    async function sendMessage(message, files = [], authToken = null) {
        if (CONFIG.useMock) {
            return mockSendMessage(message, files);
        }

        const url = `${getBaseUrl()}/run`;
        const body = await buildRequestBody(message, files);

        const headers = {
            'Content-Type': 'application/json'
        };

        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new ApiError(
                    `API Error: ${response.status}`,
                    response.status,
                    errorData
                );
            }

            return await response.json();
        } catch (error) {
            if (error instanceof ApiError) throw error;
            throw new ApiError(`Network Error: ${error.message}`, 0, null);
        }
    }

    /**
     * Send a message with Server-Sent Events (streaming)
     * @param {string} message - User message
     * @param {File[]} files - Optional files to send
     * @param {function} onEvent - Callback for each event
     * @param {function} onError - Callback for errors
     * @param {function} onComplete - Callback when stream ends
     * @param {string} [authToken] - Optional auth token
     */
    async function sendMessageStream(message, files = [], onEvent, onError, onComplete, authToken = null) {
        if (CONFIG.useMock) {
            return mockSendMessageStream(message, onEvent, onComplete);
        }

        const url = `${getBaseUrl()}/run_sse`;
        const body = await buildRequestBody(message, files);
        body.streaming = true;

        const headers = {
            'Content-Type': 'application/json'
        };

        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                onError(new ApiError(`API Error: ${response.status}`, response.status, errorData));
                return;
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();

                if (done) {
                    onComplete();
                    break;
                }

                buffer += decoder.decode(value, { stream: true });

                // Process complete SSE messages
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            onEvent(data);
                        } catch (e) {
                            console.warn('[DatarAPI] Failed to parse SSE data:', line);
                        }
                    }
                }
            }
        } catch (error) {
            onError(new ApiError(`Stream Error: ${error.message}`, 0, null));
        }
    }

    /**
     * Extract all content from event parts
     * @param {object} event - ADK event object
     * @returns {object} - Object with text, images, and audio arrays
     */
    function extractContentFromEvent(event) {
        const result = {
            text: '',
            images: [],
            audio: []
        };

        if (!event || !event.content || !event.content.parts) {
            return result;
        }

        for (const part of event.content.parts) {
            // Text content
            if (part.text) {
                result.text += part.text;
            }

            // Inline data (base64 encoded)
            if (part.inline_data) {
                const mimeType = part.inline_data.mime_type || '';
                const data = part.inline_data.data;
                const dataUrl = `data:${mimeType};base64,${data}`;

                if (mimeType.startsWith('image/')) {
                    result.images.push({
                        url: dataUrl,
                        mimeType: mimeType
                    });
                } else if (mimeType.startsWith('audio/')) {
                    result.audio.push({
                        url: dataUrl,
                        mimeType: mimeType
                    });
                }
            }

            // File data with URI (external URL)
            if (part.file_data) {
                const mimeType = part.file_data.mime_type || '';
                const url = part.file_data.file_uri;

                if (mimeType.startsWith('image/')) {
                    result.images.push({
                        url: url,
                        mimeType: mimeType
                    });
                } else if (mimeType.startsWith('audio/')) {
                    result.audio.push({
                        url: url,
                        mimeType: mimeType
                    });
                }
            }
        }

        return result;
    }

    /**
     * Extract text content from an event (legacy function for compatibility)
     * @param {object} event - ADK event object
     * @returns {string|null} - Extracted text or null
     */
    function extractTextFromEvent(event) {
        const content = extractContentFromEvent(event);
        return content.text || null;
    }

    /**
     * Get the author from an event
     * @param {object} event - ADK event object
     * @returns {string} - Author name or 'unknown'
     */
    function getEventAuthor(event) {
        return event?.author || 'unknown';
    }

    // ========================================
    // Mock Functions (for development without API)
    // ========================================

    const MOCK_RESPONSES = [
        "**Hola, soy DATAR.** Estoy aquí para ayudarte a explorar el mundo natural que te rodea.\n\n¿Qué te gustaría descubrir hoy?\n\n- Explorar el **Bosque de la Macarena**\n- Conocer los sonidos del **Humedal la Conejera**\n- Aprender sobre **hongos y líquenes**",
        "## ¡Qué interesante pregunta!\n\nEn el *Bosque de la Macarena*, podrías encontrar:\n\n1. Diversas especies de **hongos**\n2. **Líquenes** y musgos\n3. Un ecosistema fascinante\n\n> La naturaleza siempre tiene algo nuevo que enseñarnos.",
        "Los humedales de Bogotá son hogar de más de **100 especies de aves**.\n\n### ¿Te gustaría que exploremos juntos?\n\n- Los sonidos de la Conejera\n- Las aves migratorias\n- La flora acuática",
        "La **simbiosis** entre hongos y plantas es un ejemplo perfecto de cooperación en la naturaleza.\n\n```\nHongo + Planta = Micorriza\n```\n\n¿Has notado algún hongo en tu entorno?"
    ];

    function mockSendMessage(message, files = []) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const randomResponse = MOCK_RESPONSES[Math.floor(Math.random() * MOCK_RESPONSES.length)];
                const response = [{
                    id: generateId('evt'),
                    timestamp: new Date().toISOString(),
                    author: 'Gente_Raiz',
                    content: {
                        role: 'model',
                        parts: [{ text: randomResponse }]
                    }
                }];

                // If files were sent, add a mock acknowledgment
                if (files.length > 0) {
                    response[0].content.parts[0].text =
                        `He recibido ${files.length} archivo(s). ${randomResponse}`;
                }

                resolve(response);
            }, 800 + Math.random() * 1200);
        });
    }

    function mockSendMessageStream(message, onEvent, onComplete) {
        const randomResponse = MOCK_RESPONSES[Math.floor(Math.random() * MOCK_RESPONSES.length)];
        const words = randomResponse.split(' ');
        let index = 0;

        const interval = setInterval(() => {
            if (index < words.length) {
                onEvent({
                    id: generateId('evt'),
                    timestamp: new Date().toISOString(),
                    author: 'Gente_Raiz',
                    content: {
                        role: 'model',
                        parts: [{ text: words[index] + ' ' }]
                    }
                });
                index++;
            } else {
                clearInterval(interval);
                onComplete();
            }
        }, 100);

        return () => clearInterval(interval);
    }

    // ========================================
    // Error Class
    // ========================================

    class ApiError extends Error {
        constructor(message, status, data) {
            super(message);
            this.name = 'ApiError';
            this.status = status;
            this.data = data;
        }
    }

    // ========================================
    // Public API
    // ========================================

    return {
        init,
        sendMessage,
        sendMessageStream,
        extractTextFromEvent,
        extractContentFromEvent,
        getEventAuthor,
        fileToBase64,
        getFileMimeType,
        getConfig: () => ({ ...CONFIG }),
        setMockMode: (enabled) => { CONFIG.useMock = enabled; },
        getUserId: () => currentUserId,
        getSessionId: () => currentSessionId,
        ApiError
    };

})();

// Export for ES modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DatarAPI;
}
