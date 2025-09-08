// Authentication utility functions
class AuthManager {
    constructor() {
        this.baseURL = 'http://localhost:8000'; // Change to your deployed backend URL
        this.token = localStorage.getItem('auth_token');
        this.user = JSON.parse(localStorage.getItem('user_data') || 'null');
    }

    // Check if user is authenticated
    isAuthenticated() {
        return this.token && this.user;
    }

    // Get current user
    getCurrentUser() {
        return this.user;
    }

    // Make authenticated API calls
    async apiCall(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (response.status === 401) {
                // Token expired, redirect to login
                this.logout();
                window.location.href = 'auth.html';
                return null;
            }

            return response;
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    // Search users
    async searchUsers(query, limit = 10) {
        const response = await this.apiCall('/api/users/search', {
            method: 'POST',
            body: JSON.stringify({ query, limit })
        });
        
        if (response && response.ok) {
            return await response.json();
        }
        return null;
    }

    // Logout
    logout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        this.token = null;
        this.user = null;
    }
}

// Global auth manager instance
const auth = new AuthManager();
