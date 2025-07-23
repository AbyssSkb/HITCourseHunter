// Main JavaScript for HITCourseHunter

$(document).ready(function() {
    // Update current time
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('zh-CN', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    $('#current-time').text(timeString);
}

// Show loading spinner
function showLoading(element) {
    element.html(`
        <div class="loading">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            <span class="ms-2">加载中...</span>
        </div>
    `);
}

// Show success message
function showSuccess(message) {
    showAlert('success', message, 'fas fa-check-circle');
}

// Show error message
function showError(message) {
    showAlert('danger', message, 'fas fa-exclamation-triangle');
}

// Show info message
function showInfo(message) {
    showAlert('info', message, 'fas fa-info-circle');
}

// Generic alert function
function showAlert(type, message, icon) {
    const alert = $(`
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="${icon}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    // Add to container or create one
    let container = $('.container').first();
    if (!container.length) {
        container = $('<div class="container"></div>').prependTo('main');
    }
    
    alert.prependTo(container);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alert.alert('close');
    }, 5000);
}

// Format course information for display
function formatCourseInfo(info) {
    return info.replace(/\n/g, '<br>');
}

// Truncate text
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

// API request helper
function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    return fetch(url, { ...defaultOptions, ...options })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || `HTTP ${response.status}`);
                });
            }
            return response.json();
        });
}

// Course selection functions
function selectCourse(courseData) {
    return apiRequest('/api/courses/select', {
        method: 'POST',
        body: JSON.stringify(courseData)
    });
}

function removeCourse(courseId) {
    return apiRequest('/api/courses/remove', {
        method: 'POST',
        body: JSON.stringify({ course_id: courseId })
    });
}

// Update selected course count
function updateSelectedCount(count) {
    $('.selected-count').text(count);
    
    // Update badge in navigation
    let badge = $('.navbar .badge');
    if (count > 0) {
        if (badge.length === 0) {
            badge = $('<span class="badge bg-danger rounded-pill ms-1"></span>');
            $('.nav-link[href*="selected"]').append(badge);
        }
        badge.text(count);
    } else {
        badge.remove();
    }
}

// Debounce function for search
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