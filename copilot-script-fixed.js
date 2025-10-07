// Copilot-Style Application State
let appState = {
    selectedService: null,
    userEmail: '',
    conversationHistory: [],
    isLoading: false,
    initialized: false
};

// CORRECTED API Configuration based on your actual APIs
const API_CONFIG = {
    // Timesheet API (from TimeSheetAPICode.py) - runs on port 8000
    timesheet: {
        baseUrl: 'http://localhost:8000',
        endpoint: '/chat',
        method: 'POST'
    },
    // HR Policy/RAG API (from RAG_api.py) - ALSO runs on port 8000 
    // But you should change this to port 8001 for separation
    'hr-policy': {
        baseUrl: 'http://localhost:8001', // Change your RAG API to run on 8001
        endpoint: '/query',
        method: 'POST'
    }
};

// Service Configuration
const SERVICES = {
    timesheet: {
        name: 'Timesheet Management',
        description: 'your Oracle and Mars timesheets',
        icon: '⏰',
        welcomeMessage: 'Hello! I\'m your Timesheet Management assistant. I can help you fill timesheets, view entries, and manage your Oracle and Mars timesheet data. How can I assist you today?'
    },
    'hr-policy': {
        name: 'HR Policy Assistant',
        description: 'HR policies and company documents', 
        icon: '📋',
        welcomeMessage: 'Hello! I\'m your HR Policy Assistant. I can help you understand company policies, HR procedures, and answer questions about employee documentation. How can I help you today?'
    }
};

// DOM Elements Cache
const elements = {
    // Views
    welcomeView: null,
    chatView: null,

    // Welcome screen
    emailInput: null,
    emailError: null,
    serviceCards: null,

    // Chat interface
    currentServiceName: null,
    currentUserEmail: null,
    messagesContainer: null,
    messageInput: null,
    sendButton: null,
    typingIndicator: null,
    resetButton: null,

    // Error handling
    errorToast: null,
    errorMessage: null,
    closeError: null
};

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    initializeEventListeners();
    resetToWelcome();
});

function initializeElements() {
    // Cache DOM elements
    elements.welcomeView = document.getElementById('welcome-view');
    elements.chatView = document.getElementById('chat-view');
    elements.emailInput = document.getElementById('user-email');
    elements.emailError = document.getElementById('email-error');
    elements.serviceCards = document.querySelectorAll('.service-card');
    elements.currentServiceName = document.getElementById('current-service-name');
    elements.currentUserEmail = document.getElementById('current-user-email');
    elements.messagesContainer = document.getElementById('messages-container');
    elements.messageInput = document.getElementById('message-input');
    elements.sendButton = document.getElementById('send-button');
    elements.typingIndicator = document.getElementById('typing-indicator');
    elements.resetButton = document.getElementById('reset-conversation');
    elements.errorToast = document.getElementById('error-toast');
    elements.errorMessage = document.getElementById('error-message');
    elements.closeError = document.getElementById('close-error');
}

function initializeEventListeners() {
    // Email validation
    elements.emailInput?.addEventListener('input', validateEmailInput);
    elements.emailInput?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const firstCard = document.querySelector('.service-card:not([disabled])');
            if (firstCard && validateEmail()) {
                firstCard.focus();
            }
        }
    });

    // Service selection
    elements.serviceCards?.forEach(card => {
        card.addEventListener('click', () => {
            const service = card.dataset.service;
            if (service) selectService(service);
        });

        card.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const service = card.dataset.service;
                if (service) selectService(service);
            }
        });
    });

    // Message input
    elements.messageInput?.addEventListener('input', function() {
        adjustTextareaHeight(this);
        updateSendButtonState();
    });

    elements.messageInput?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Send button
    elements.sendButton?.addEventListener('click', sendMessage);

    // Reset conversation
    elements.resetButton?.addEventListener('click', resetToWelcome);

    // Error toast
    elements.closeError?.addEventListener('click', hideError);

    // Auto-hide error after 5 seconds
    let errorTimeout;
    const originalShowError = showError;
    showError = function(message) {
        originalShowError(message);
        if (errorTimeout) clearTimeout(errorTimeout);
        errorTimeout = setTimeout(hideError, 5000);
    };
}

function validateEmail() {
    const email = elements.emailInput?.value?.trim() || '';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validateEmailInput() {
    const isValid = validateEmail();
    const email = elements.emailInput?.value?.trim() || '';

    if (elements.emailError) {
        if (!isValid && email.length > 0) {
            elements.emailError.textContent = 'Please enter a valid email address';
            elements.emailError.classList.remove('hidden');
        } else {
            elements.emailError.classList.add('hidden');
        }
    }

    // Enable/disable service cards
    elements.serviceCards?.forEach(card => {
        if (isValid && email.length > 0) {
            card.removeAttribute('disabled');
            card.style.opacity = '1';
            card.style.cursor = 'pointer';
        } else {
            card.setAttribute('disabled', 'true');
            card.style.opacity = '0.5';
            card.style.cursor = 'not-allowed';
        }
    });

    return isValid;
}

function selectService(serviceType) {
    const email = elements.emailInput?.value?.trim();

    if (!validateEmail() || !email) {
        showError('Please enter a valid email address first.');
        elements.emailInput?.focus();
        return;
    }

    // Update application state
    appState.selectedService = serviceType;
    appState.userEmail = email;
    appState.conversationHistory = [];
    appState.initialized = true;

    // Get service configuration
    const service = SERVICES[serviceType];
    if (!service) {
        showError('Invalid service selected.');
        return;
    }

    // Update UI
    if (elements.currentServiceName) {
        elements.currentServiceName.textContent = service.name;
    }
    if (elements.currentUserEmail) {
        elements.currentUserEmail.textContent = email;
    }

    // Update service badge icon
    const serviceIconSmall = document.querySelector('.service-icon-small');
    if (serviceIconSmall) {
        serviceIconSmall.textContent = service.icon;
    }

    // Switch to chat view
    elements.welcomeView?.classList.add('hidden');
    elements.chatView?.classList.remove('hidden');

    // Clear messages and add welcome message
    if (elements.messagesContainer) {
        elements.messagesContainer.innerHTML = '';
    }

    addMessage('assistant', service.welcomeMessage);

    // Focus on input
    elements.messageInput?.focus();

    console.log(`Selected service: ${service.name} for ${email}`);
}

function adjustTextareaHeight(textarea) {
    if (!textarea) return;

    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function updateSendButtonState() {
    const hasText = elements.messageInput?.value?.trim().length > 0;

    if (elements.sendButton) {
        elements.sendButton.disabled = !hasText || appState.isLoading;
    }
}

async function sendMessage() {
    const message = elements.messageInput?.value?.trim();

    if (!message || appState.isLoading || !appState.initialized) {
        return;
    }

    // Clear input
    if (elements.messageInput) {
        elements.messageInput.value = '';
        adjustTextareaHeight(elements.messageInput);
    }
    updateSendButtonState();

    // Add user message
    addMessage('user', message);

    // Show typing indicator
    showTyping(true);

    try {
        // Call API
        const response = await callAPI(message);
        addMessage('assistant', response);

        // Add to conversation history
        appState.conversationHistory.push(
            { role: 'user', content: message },
            { role: 'assistant', content: response }
        );

    } catch (error) {
        console.error('API Error:', error);
        let errorMsg = 'Sorry, I encountered an error. Please try again.';

        // Handle specific CORS/OPTIONS errors
        if (error.message.includes('CORS') || error.message.includes('OPTIONS')) {
            errorMsg = 'Connection issue - please ensure the API server is running and CORS is configured.';
        } else if (error.message.includes('405')) {
            errorMsg = 'Method not allowed - please check the API endpoint configuration.';
        } else if (error.message.includes('Failed to fetch')) {
            errorMsg = 'Cannot connect to API server. Please ensure it is running.';
        }

        showError(errorMsg);
        addMessage('assistant', 'I apologize, but I encountered an error processing your request. Please try again.');
    } finally {
        showTyping(false);
    }
}

// IMPROVED API CALL FUNCTION with proper error handling and CORS support
async function callAPI(message) {
    const serviceConfig = API_CONFIG[appState.selectedService];

    if (!serviceConfig) {
        throw new Error('Invalid service configuration');
    }

    // Prepare payload based on service type
    let payload;
    if (appState.selectedService === 'timesheet') {
        payload = {
            email: appState.userEmail,
            user_prompt: message
        };
    } else if (appState.selectedService === 'hr-policy') {
        // For RAG API - matching the QueryRequest model
        payload = {
            question: message
        };
    } else {
        throw new Error('Unknown service type');
    }

    console.log(`Calling ${appState.selectedService} API:`, {
        url: `${serviceConfig.baseUrl}${serviceConfig.endpoint}`,
        method: serviceConfig.method,
        payload: payload
    });

    try {
        const response = await fetch(`${serviceConfig.baseUrl}${serviceConfig.endpoint}`, {
            method: serviceConfig.method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                // Add CORS headers for cross-origin requests
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            body: JSON.stringify(payload),
            // Handle CORS mode
            mode: 'cors'
        });

        if (!response.ok) {
            if (response.status === 405) {
                throw new Error(`Method not allowed (405). Check if ${serviceConfig.endpoint} accepts ${serviceConfig.method} requests.`);
            } else if (response.status === 404) {
                throw new Error(`Endpoint not found (404). Check if ${serviceConfig.endpoint} exists.`);
            } else if (response.status >= 500) {
                throw new Error(`Server error (${response.status}). The API server may be down.`);
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        }

        const data = await response.json();
        console.log('API Response:', data);

        // Handle different response formats based on your APIs
        if (appState.selectedService === 'timesheet') {
            // TimeSheet API returns: {response: "..."}
            return data.response || data.message || 'Response received successfully.';
        } else if (appState.selectedService === 'hr-policy') {
            // RAG API returns: {answer: "...", sources: [...]}
            let answer = data.answer || data.response || data.message;
            if (data.sources && data.sources.length > 0) {
                answer += '\n\nSources: ' + data.sources.join(', ');
            }
            return answer || 'Response received successfully.';
        }

        return 'Response received successfully.';

    } catch (fetchError) {
        console.error('Fetch Error:', fetchError);

        // Handle network errors
        if (fetchError.name === 'TypeError' && fetchError.message === 'Failed to fetch') {
            throw new Error('Cannot connect to API server. Please ensure it is running and accessible.');
        }

        // Re-throw the error to be handled by the caller
        throw fetchError;
    }
}

function addMessage(role, content) {
    if (!elements.messagesContainer || !content) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';

    if (role === 'user') {
        avatar.textContent = appState.userEmail ? appState.userEmail.charAt(0).toUpperCase() : 'U';
    } else {
        const service = SERVICES[appState.selectedService];
        avatar.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 1a7 7 0 100 14A7 7 0 008 1zM7 5a1 1 0 112 0v3a1 1 0 11-2 0V5zm1 7a1 1 0 100-2 1 1 0 000 2z"/>
            </svg>
        `;
    }

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);

    elements.messagesContainer.appendChild(messageDiv);

    // Scroll to bottom with smooth animation
    setTimeout(() => {
        elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
    }, 50);
}

function showTyping(show) {
    appState.isLoading = show;

    if (elements.typingIndicator) {
        elements.typingIndicator.classList.toggle('hidden', !show);
    }

    updateSendButtonState();

    if (show && elements.messagesContainer) {
        // Scroll to show typing indicator
        setTimeout(() => {
            elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
        }, 50);
    }
}

function resetToWelcome() {
    // Reset application state
    appState.selectedService = null;
    appState.userEmail = '';
    appState.conversationHistory = [];
    appState.isLoading = false;
    appState.initialized = false;

    // Reset UI
    if (elements.emailInput) {
        elements.emailInput.value = '';
    }

    if (elements.emailError) {
        elements.emailError.classList.add('hidden');
    }

    if (elements.messagesContainer) {
        elements.messagesContainer.innerHTML = '';
    }

    if (elements.messageInput) {
        elements.messageInput.value = '';
        adjustTextareaHeight(elements.messageInput);
    }

    showTyping(false);
    hideError();
    validateEmailInput();

    // Show welcome view
    elements.welcomeView?.classList.remove('hidden');
    elements.chatView?.classList.add('hidden');

    // Focus on email input
    elements.emailInput?.focus();

    console.log('Reset to welcome screen');
}

function showError(message) {
    if (elements.errorMessage) {
        elements.errorMessage.textContent = message;
    }

    elements.errorToast?.classList.remove('hidden');

    console.error('Error:', message);
}

function hideError() {
    elements.errorToast?.classList.add('hidden');
}

// Handle online/offline status
window.addEventListener('online', () => {
    hideError();
    console.log('Connection restored');
});

window.addEventListener('offline', () => {
    showError('You are currently offline. Please check your internet connection.');
});

// Handle window resize for mobile
window.addEventListener('resize', function() {
    if (elements.messageInput?.value) {
        adjustTextareaHeight(elements.messageInput);
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape key - reset to welcome
    if (e.key === 'Escape' && appState.initialized) {
        resetToWelcome();
    }

    // Ctrl/Cmd + / - focus message input
    if ((e.ctrlKey || e.metaKey) && e.key === '/' && appState.initialized) {
        e.preventDefault();
        elements.messageInput?.focus();
    }
});

// Export functions for debugging
window.copilotApp = {
    appState,
    API_CONFIG,
    SERVICES,
    selectService,
    sendMessage,
    resetToWelcome,
    showError,
    hideError,
    callAPI
};

console.log('Copilot-style application initialized with corrected API configuration');
console.log('API Configuration:', API_CONFIG);