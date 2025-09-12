// Automatically detect environment and set correct API URL
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000'   // Local development
    : 'https://flowchat-production.up.railway.app';   // Production

const API_ENDPOINTS = {
    GOOGLE_LOGIN: `${API_BASE_URL}/api/routes/users/google-login`,
    MESSAGES: `${API_BASE_URL}/api/routes/messages`,
    SEARCH: `${API_BASE_URL}/api/routes/search`
};
