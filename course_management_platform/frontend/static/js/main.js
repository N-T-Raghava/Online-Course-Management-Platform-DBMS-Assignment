/**
 * Main JavaScript for Course Management Platform Frontend
 */

// Alert dismissal
document.addEventListener('DOMContentLoaded', function() {
    // Auto-close alerts after 5 seconds if they have the data-auto-close attribute
    const alerts = document.querySelectorAll('.alert[data-auto-close]');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Close alert on close button click
    const closeButtons = document.querySelectorAll('.btn-close');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        });
    });
});

// Utility Functions
const Utils = {
    /**
     * Show a toast notification
     */
    showToast: function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type}`;
        toast.textContent = message;
        toast.setAttribute('data-auto-close', 'true');
        
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(toast, container.firstChild);
        }
    },

    /**
     * Format datetime to readable format
     */
    formatDate: function(date) {
        if (!date) return '';
        const d = new Date(date);
        return d.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    /**
     * Format datetime with time
     */
    formatDateTime: function(date) {
        if (!date) return '';
        const d = new Date(date);
        return d.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    /**
     * Validate email format
     */
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    /**
     * Deep copy object
     */
    deepCopy: function(obj) {
        return JSON.parse(JSON.stringify(obj));
    }
};

// API Client
const API = {
    /**
     * Make a GET request
     */
    get: async function(url, options = {}) {
        return this._request('GET', url, null, options);
    },

    /**
     * Make a POST request
     */
    post: async function(url, data, options = {}) {
        return this._request('POST', url, data, options);
    },

    /**
     * Make a PUT request
     */
    put: async function(url, data, options = {}) {
        return this._request('PUT', url, data, options);
    },

    /**
     * Make a DELETE request
     */
    delete: async function(url, options = {}) {
        return this._request('DELETE', url, null, options);
    },

    /**
     * Internal request handler
     */
    _request: async function(method, url, data, options = {}) {
        try {
            const config = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            };

            if (data) {
                config.body = JSON.stringify(data);
            }

            const response = await fetch(url, config);
            
            let result = null;
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                result = await response.json();
            } else {
                result = await response.text();
            }

            return {
                status: response.status,
                ok: response.ok,
                data: result
            };
        } catch (error) {
            return {
                status: 0,
                ok: false,
                error: error.message
            };
        }
    }
};

// Export for use in other scripts
window.Utils = Utils;
window.API = API;
