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
     * Build the request body for ADK API
     * @param {string} message - User message text
     * @returns {object} - Request body in ADK format
     */
    function buildRequestBody(message) {
        return {
            app_name: CONFIG.appName,
            user_id: currentUserId,
            session_id: currentSessionId,
            new_message: {
                role: 'user',
                parts: [
                    { text: message }
                ]
            }
        };
    }

    /**
     * Send a message to the agent (non-streaming)
     * @param {string} message - User message
     * @param {string} [authToken] - Optional auth token for Cloud Run
     * @returns {Promise<Array>} - Array of event objects
     */
    async function sendMessage(message, authToken = null) {
        if (CONFIG.useMock) {
            return mockSendMessage(message);
        }

        const url = `${getBaseUrl()}/run`;
        const body = buildRequestBody(message);

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
     * @param {function} onEvent - Callback for each event
     * @param {function} onError - Callback for errors
     * @param {function} onComplete - Callback when stream ends
     * @param {string} [authToken] - Optional auth token
     */
    async function sendMessageStream(message, onEvent, onError, onComplete, authToken = null) {
        if (CONFIG.useMock) {
            return mockSendMessageStream(message, onEvent, onComplete);
        }

        const url = `${getBaseUrl()}/run_sse`;
        const body = buildRequestBody(message);
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
     * Extract text content from an event
     * @param {object} event - ADK event object
     * @returns {string|null} - Extracted text or null
     */
    function extractTextFromEvent(event) {
        if (!event || !event.content || !event.content.parts) {
            return null;
        }

        const textParts = event.content.parts
            .filter(part => part.text)
            .map(part => part.text);

        return textParts.length > 0 ? textParts.join('') : null;
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
        "Hola, soy DATAR. Estoy aquí para ayudarte a explorar el mundo natural que te rodea. ¿Qué te gustaría descubrir hoy?",
        "¡Qué interesante pregunta! En el Bosque de la Macarena, podrías encontrar diversas especies de hongos, líquenes y musgos que forman parte de un ecosistema fascinante.",
        "Los humedales de Bogotá son hogar de más de 100 especies de aves. ¿Te gustaría que exploremos juntos los sonidos de la Conejera?",
        "La simbiosis entre hongos y plantas es un ejemplo perfecto de cooperación en la naturaleza. ¿Has notado algún hongo en tu entorno?"
    ];

    function mockSendMessage(message) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const randomResponse = MOCK_RESPONSES[Math.floor(Math.random() * MOCK_RESPONSES.length)];
                resolve([{
                    id: generateId('evt'),
                    timestamp: new Date().toISOString(),
                    author: 'Gente_Raiz',
                    content: {
                        role: 'model',
                        parts: [{ text: randomResponse }]
                    }
                }]);
            }, 800 + Math.random() * 1200);
        });
    }

    function mockSendMessageStream(message, onEvent, onComplete) {
        const randomResponse = MOCK_RESPONSES[Math.floor(Math.random() * MOCK_RESPONSES.length)];
        const words = randomResponse.split(' ');
        let index = 0;

        const interval = setInterval(() => {
            if (index < words.length) {
                const partialText = words.slice(0, index + 1).join(' ');
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
        getEventAuthor,
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
