/**
 * NutriTrack - Core Storage & State Management
 * Strict Monochrome Minimal System with Defensive XSS Sanitization
 */

const Storage = {
    // User Profile
    getProfile() {
        try {
            return JSON.parse(localStorage.getItem('nt_profile') || 'null');
        } catch (e) {
            return null;
        }
    },
    saveProfile(profile) {
        localStorage.setItem('nt_profile', JSON.stringify(profile));
    },

    // Daily Nutrition Targets
    getTargets() {
        try {
            return JSON.parse(localStorage.getItem('nt_targets') || 'null');
        } catch (e) {
            return null;
        }
    },
    saveTargets(targets) {
        localStorage.setItem('nt_targets', JSON.stringify(targets));
    },

    // Daily Meal Logs: { 'YYYY-MM-DD': { breakfast: [], lunch: [], snack: [], dinner: [] } }
    getAllMealLogs() {
        try {
            return JSON.parse(localStorage.getItem('nt_meal_logs') || '{}');
        } catch (e) {
            return {};
        }
    },
    getMealLogs(dateStr) {
        const all = this.getAllMealLogs();
        if (!all[dateStr]) {
            return { breakfast: [], lunch: [], snack: [], dinner: [] };
        }
        return {
            breakfast: Array.isArray(all[dateStr].breakfast) ? all[dateStr].breakfast : [],
            lunch: Array.isArray(all[dateStr].lunch) ? all[dateStr].lunch : [],
            snack: Array.isArray(all[dateStr].snack) ? all[dateStr].snack : [],
            dinner: Array.isArray(all[dateStr].dinner) ? all[dateStr].dinner : []
        };
    },
    saveMealLog(dateStr, mealType, item) {
        const all = this.getAllMealLogs();
        if (!all[dateStr]) {
            all[dateStr] = { breakfast: [], lunch: [], snack: [], dinner: [] };
        }
        if (!Array.isArray(all[dateStr][mealType])) {
            all[dateStr][mealType] = [];
        }
        if (!item.id) {
            item.id = 'itm_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4);
        }
        all[dateStr][mealType].push(item);
        localStorage.setItem('nt_meal_logs', JSON.stringify(all));
    },
    deleteMealItem(dateStr, mealType, itemId) {
        const all = this.getAllMealLogs();
        if (all[dateStr] && Array.isArray(all[dateStr][mealType])) {
            all[dateStr][mealType] = all[dateStr][mealType].filter(item => item.id !== itemId);
            localStorage.setItem('nt_meal_logs', JSON.stringify(all));
        }
    },

    // Gemini API Key
    getApiKey() {
        return localStorage.getItem('nt_gemini_api_key') || '';
    },
    saveApiKey(key) {
        localStorage.setItem('nt_gemini_api_key', (key || '').trim());
    },

    // Reset local data
    clearAll() {
        localStorage.clear();
    },

    // Date Utilities
    getTodayDateString() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },
    formatDateDisplay(dateStr) {
        if (!dateStr || typeof dateStr !== 'string') return '';
        const parts = dateStr.split('-').map(Number);
        if (parts.length < 3 || isNaN(parts[0])) return dateStr;
        const [year, month, day] = parts;
        const dateObj = new Date(year, month - 1, day);
        return dateObj.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric'
        });
    }
};

// Calculate Nutrition Totals with bounds & NaN safety
function calculateTotals(logs) {
    let totals = { calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0 };
    if (!logs || typeof logs !== 'object') return totals;

    const meals = ['breakfast', 'lunch', 'snack', 'dinner'];
    meals.forEach(m => {
        const items = Array.isArray(logs[m]) ? logs[m] : [];
        items.forEach(item => {
            totals.calories += Math.max(0, Number(item.calories) || 0);
            totals.protein += Math.max(0, Number(item.protein) || 0);
            totals.carbs += Math.max(0, Number(item.carbs) || 0);
            totals.fat += Math.max(0, Number(item.fat) || 0);
            totals.fiber += Math.max(0, Number(item.fiber) || 0);
        });
    });

    totals.calories = Math.round(totals.calories);
    totals.protein = Math.round(totals.protein * 10) / 10;
    totals.carbs = Math.round(totals.carbs * 10) / 10;
    totals.fat = Math.round(totals.fat * 10) / 10;
    totals.fiber = Math.round(totals.fiber * 10) / 10;
    return totals;
}

// XSS HTML Entity Escaper for safe client-side DOM injection
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Minimal Toast Notification
function showToast(message) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = String(message || '');
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.2s ease';
        setTimeout(() => toast.remove(), 200);
    }, 2400);
}
