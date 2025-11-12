/**
 * {DATAR} - Frontend JavaScript
 * Lógica de interacción con los agentes
 */

// ===== CONFIGURACIÓN =====
const API_BASE_URL = 'http://localhost:8000';
let agents = [];
let selectedAgent = null;
let sessionId = null;
let attachedFiles = [];

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🌿 Iniciando {DATAR}...');

    // Cargar agentes
    await loadAgents();

    // Setup event listeners
    setupEventListeners();

    console.log('✅ Sistema inicializado');
});

// ===== FUNCIONES DE CARGA =====

/**
 * Carga la lista de agentes desde la API
 */
async function loadAgents() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/agents`);
        if (!response.ok) throw new Error('Error al cargar agentes');

        agents = await response.json();
        console.log('Agentes cargados:', agents.length);

        renderAgents();
    } catch (error) {
        console.error('Error al cargar agentes:', error);
        showNotification('Error al cargar agentes. Por favor, verifica que el servidor esté corriendo.', 'error');

        // Mostrar mensaje de error en el grid
        const grid = document.getElementById('agents-grid');
        if (grid) {
            grid.innerHTML = `
                <div class="loading" style="color: var(--color-error);">
                    ⚠️ Error al conectar con el servidor.<br>
                    Asegúrate de que el servidor esté corriendo en ${API_BASE_URL}
                </div>
            `;
        }
    }
}

// ===== FUNCIONES DE RENDERIZADO =====

/**
 * Renderiza las tarjetas de agentes en el grid
 */
function renderAgents() {
    const grid = document.getElementById('agents-grid');
    if (!grid) return;

    if (agents.length === 0) {
        grid.innerHTML = '<div class="loading">No hay agentes disponibles</div>';
        return;
    }

    grid.innerHTML = agents.map(agent => `
        <div class="agent-card" id="agent-${agent.id}" onclick="selectAgent('${agent.id}')">
            <div class="agent-card__header">
                <div class="agent-card__icon" style="background-color: ${agent.color};">
                    ${getAgentIcon(agent.id)}
                </div>
                <h3 class="agent-card__title">${agent.nombre}</h3>
            </div>
            <p class="agent-card__description">${agent.descripcion}</p>
            <button class="agent-card__button">
                Chatear con ${agent.nombre}
            </button>
        </div>
    `).join('');
}

/**
 * Retorna el icono emoji para cada agente
 */
function getAgentIcon(agentId) {
    const icons = {
        'root_agent': '🌿',
        'Gente_Montaña': '⛰️',
        'PastoBogotano': '🌾',
        'DiarioIntuitivo': '📔',
        'SequentialPipelineAgent': '🦎',
        'agente_bosque': '🌳',
        'agente_sonido': '🔊',
        'oráculo': '🔮'
    };
    return icons[agentId] || '🤖';
}

// ===== FUNCIONES DE CHAT =====

/**
 * Selecciona un agente y abre el chat
 */
function selectAgent(agentId) {
    const agent = agents.find(a => a.id === agentId);
    if (!agent) return;

    selectedAgent = agent;

    // Generar nuevo session ID
    sessionId = generateSessionId();

    // Actualizar título del header
    const headerTitle = document.getElementById('header-agent-name');
    if (headerTitle) {
        headerTitle.textContent = agent.nombre;
    }

    // Actualizar título del chat
    const chatTitle = document.getElementById('chat-title');
    if (chatTitle) {
        chatTitle.textContent = `Chat con ${agent.nombre}`;
    }

    // Limpiar mensajes anteriores
    const messagesContainer = document.getElementById('chat-messages');
    if (messagesContainer) {
        messagesContainer.style.display = 'block';
        messagesContainer.innerHTML = `
            <button class="chat-close" onclick="closeChat()" title="Cerrar chat">&times;</button>
            <div class="chat-message">
                <div class="chat-message__label">Sistema</div>
                <div class="chat-message__agent">
                    ¡Hola! Soy ${agent.nombre}. ${agent.descripcion}. ¿En qué puedo ayudarte?
                </div>
            </div>
        `;
    }

    // El chat siempre está visible, solo actualizamos el contenido

    // Focus en el input
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.focus();
    }

    // Scroll hacia abajo para mostrar el área de chat
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth'
    });
}

/**
 * Cierra el chat
 */
function closeChat() {
    const messagesContainer = document.getElementById('chat-messages');
    if (messagesContainer) {
        messagesContainer.style.display = 'none';
        messagesContainer.innerHTML = '<button class="chat-close" onclick="closeChat()" title="Cerrar chat">&times;</button>';
    }

    // Resetear título del header
    const headerTitle = document.getElementById('header-agent-name');
    if (headerTitle) {
        headerTitle.textContent = 'Sistema de Agentes {DATAR}';
    }

    // Limpiar input
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.value = '';
    }

    selectedAgent = null;
    sessionId = null;
}

/**
 * Envía un mensaje al agente
 */
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');

    if (!input || !sendButton) return;

    const message = input.value.trim();
    if (!message && attachedFiles.length === 0) return;

    // Deshabilitar input mientras se procesa
    input.disabled = true;
    sendButton.disabled = true;
    sendButton.textContent = '⏳';

    // Preparar mensaje con indicación de archivos
    let displayMessage = message;
    if (attachedFiles.length > 0) {
        const filesList = attachedFiles.map(f => `📎 ${f.name}`).join('\n');
        displayMessage = message ? `${message}\n\n${filesList}` : filesList;
    }

    // Agregar mensaje del usuario al chat
    addMessageToChat('user', displayMessage);

    // Limpiar input
    input.value = '';

    // Mostrar el área de mensajes si está oculta
    const messagesContainer = document.getElementById('chat-messages');
    if (messagesContainer) {
        messagesContainer.style.display = 'block';
    }

    try {
        // Crear FormData para enviar archivos
        const formData = new FormData();
        formData.append('message', message);
        formData.append('session_id', sessionId || '');

        // Agregar archivos al FormData
        attachedFiles.forEach((file, index) => {
            formData.append(`file_${index}`, file);
        });

        // Enviar mensaje a la API
        // Nota: El backend necesitará actualizarse para manejar FormData con archivos
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                files_count: attachedFiles.length,
                file_names: attachedFiles.map(f => f.name)
            })
        });

        if (!response.ok) {
            throw new Error('Error al enviar mensaje');
        }

        const data = await response.json();

        // Actualizar session ID
        sessionId = data.session_id;

        // Agregar respuesta del agente al chat
        addMessageToChat('agent', data.response);

        // Limpiar archivos adjuntos después de enviar exitosamente
        clearAttachedFiles();

    } catch (error) {
        console.error('Error al enviar mensaje:', error);
        addMessageToChat('system', '❌ Error al comunicarse con el agente. Por favor, intenta de nuevo.');
    } finally {
        // Rehabilitar input
        input.disabled = false;
        sendButton.disabled = false;
        sendButton.textContent = '➤';
        input.focus();
    }
}

/**
 * Agrega un mensaje al chat
 */
function addMessageToChat(role, content) {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message';

    let label = '';
    let messageClass = '';

    if (role === 'user') {
        label = 'Tú';
        messageClass = 'chat-message__user';
    } else if (role === 'agent') {
        label = selectedAgent ? selectedAgent.nombre : 'Agente';
        messageClass = 'chat-message__agent';
    } else {
        label = 'Sistema';
        messageClass = 'chat-message__agent';
    }

    messageDiv.innerHTML = `
        <div class="chat-message__label">${label}</div>
        <div class="${messageClass}">${escapeHtml(content)}</div>
    `;

    messagesContainer.appendChild(messageDiv);

    // Scroll al final
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ===== FUNCIONES DE ARCHIVOS =====

/**
 * Abre el selector de archivos
 */
function attachFiles() {
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.click();
    }
}

/**
 * Maneja la selección de archivos
 */
function handleFileSelect(event) {
    const files = event.target.files;
    if (files && files.length > 0) {
        Array.from(files).forEach(file => {
            attachedFiles.push(file);
        });
        updateAttachedFilesDisplay();
        console.log('Archivos adjuntos:', attachedFiles.length);
    }
}

/**
 * Actualiza la visualización de archivos adjuntos
 */
function updateAttachedFilesDisplay() {
    const chatInput = document.getElementById('chat-input');
    if (!chatInput) return;

    if (attachedFiles.length > 0) {
        const fileNames = attachedFiles.map(f => f.name).join(', ');
        chatInput.style.borderColor = 'var(--color-primary)';
        chatInput.title = `Archivos adjuntos: ${fileNames}`;

        // Cambiar el ícono del botón de adjuntar
        const attachButton = document.getElementById('attach-button');
        if (attachButton) {
            attachButton.textContent = `📎 ${attachedFiles.length}`;
        }
    } else {
        chatInput.style.borderColor = 'var(--color-border)';
        chatInput.title = '';

        const attachButton = document.getElementById('attach-button');
        if (attachButton) {
            attachButton.textContent = '📎';
        }
    }
}

/**
 * Limpia los archivos adjuntos
 */
function clearAttachedFiles() {
    attachedFiles = [];
    updateAttachedFilesDisplay();

    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.value = '';
    }
}

// ===== EVENT LISTENERS =====

/**
 * Configura los event listeners
 */
function setupEventListeners() {
    // Enter para enviar mensaje
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Drag & Drop
        chatInput.addEventListener('dragover', (e) => {
            e.preventDefault();
            chatInput.style.borderColor = 'var(--color-primary)';
            chatInput.style.background = 'rgba(231, 107, 19, 0.1)';
        });

        chatInput.addEventListener('dragleave', (e) => {
            e.preventDefault();
            chatInput.style.borderColor = 'var(--color-border)';
            chatInput.style.background = 'var(--color-card-bg)';
        });

        chatInput.addEventListener('drop', (e) => {
            e.preventDefault();
            chatInput.style.borderColor = 'var(--color-border)';
            chatInput.style.background = 'var(--color-card-bg)';

            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                Array.from(files).forEach(file => {
                    attachedFiles.push(file);
                });
                updateAttachedFilesDisplay();
                console.log('Archivos arrastrados:', files.length);
            }
        });
    }

    // File input change
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
}

// ===== UTILIDADES =====

/**
 * Genera un session ID único
 */
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Escapa HTML para prevenir XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Muestra una notificación
 */
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    // TODO: Implementar notificaciones visuales si es necesario
}
