/**
 * Utility functions for the Manga Application
 */

// Show a temporary notification to the user
function showNotification(message, type = 'info', duration = 3000) {
    // Remove existing notifications
    const existing = document.querySelectorAll('.notification');
    existing.forEach(n => n.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '4px',
        color: 'white',
        fontWeight: '500',
        zIndex: '10000',
        maxWidth: '400px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
        transition: 'all 0.3s ease'
    });
    
    // Set background color based on type
    const colors = {
        info: '#3b82f6',
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444'
    };
    notification.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // Animate in
    requestAnimationFrame(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    });
    
    // Auto-remove after duration
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// Show success message
function showSuccess(message, duration) {
    showNotification(message, 'success', duration);
}

// Show error message
function showError(message, duration) {
    showNotification(message, 'error', duration);
}

// Show warning message
function showWarning(message, duration) {
    showNotification(message, 'warning', duration);
}

// Validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Sanitize HTML to prevent XSS
function sanitizeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Format numbers with commas
function formatNumber(num) {
    return Number(num).toLocaleString();
}

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Make API requests with proper error handling
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        // Check for login redirect
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('text/html') || response.redirected) {
            if (response.url.includes('/login')) {
                showError('Please log in to continue');
                setTimeout(() => window.location.href = '/login', 1500);
                return null;
            }
        }
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        showError('Request failed. Please try again.');
        throw error;
    }
}

// Export functions for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showNotification,
        showSuccess,
        showError,
        showWarning,
        isValidEmail,
        sanitizeHtml,
        formatNumber,
        debounce,
        apiRequest
    };
}