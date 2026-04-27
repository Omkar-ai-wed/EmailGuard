/**
 * EmailGuard Dashboard Core Integration
 * Centralized logic for Auth, API communication, and dynamic data loading.
 */

const RENDER_URL = 'https://emailguard-api.onrender.com/api/v1';
const LOCAL_URL  = 'http://localhost:8000/api/v1';
const API = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:' ? LOCAL_URL : RENDER_URL;

let authToken = localStorage.getItem('eg_token') || '';
let backendOnline = false;

// Initialize demo store if empty
if (!localStorage.getItem('eg_demo_emails')) {
    localStorage.setItem('eg_demo_emails', JSON.stringify([
        {id: 101, sender_email: 'demo-phish@example.com', subject: 'Urgent: Account Verification', risk_score: 92, category: 'phishing', received_at: new Date().toISOString()},
        {id: 102, sender_email: 'hello@newsletter.com', subject: 'Your Weekly Digest', risk_score: 12, category: 'wanted', received_at: new Date().toISOString()}
    ]));
}

/**
 * Ensures user is authenticated.
 * Returns the token if found, otherwise null (triggers Demo Mode).
 */
async function ensureAuth() {
    authToken = localStorage.getItem('eg_token') || '';
    if (authToken) {
        backendOnline = true;
        return authToken;
    }
    return null;
}

/**
 * Generic fetch wrapper with Auth headers
 * Returns null if not authenticated (triggers demo data fallback in components)
 */
async function apiFetch(path, options = {}) {
    const token = await ensureAuth();
    if (!token) {
        backendOnline = false;
        return null;
    }
    
    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };
    
    try {
        const r = await fetch(`${API}${path}`, { ...defaultOptions, ...options });
        backendOnline = r.ok;
        if (r.status === 401) {
            localStorage.removeItem('eg_token');
            authToken = '';
        }
        return r.ok ? r.json() : null;
    } catch (e) {
        backendOnline = false;
        return null;
    }
}

/**
 * Common UI updates
 */
function logout() {
    localStorage.removeItem('eg_token');
    window.location.href = 'Login.html';
}

function updateConnectionStatus() {
    const statusEl = document.getElementById('connection-status');
    if (statusEl) {
        if (authToken && backendOnline) {
            statusEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500"></span><span class="text-[10px] font-bold text-emerald-600 uppercase tracking-widest">Live Mode</span>`;
        } else if (authToken && !backendOnline) {
            statusEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span><span class="text-[10px] font-bold text-red-600 uppercase tracking-widest">Offline</span>`;
        } else {
            statusEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-orange-500"></span><span class="text-[10px] font-bold text-orange-600 uppercase tracking-widest">Demo Mode (Logged Out)</span>`;
        }
    }
}



function fmt(n) { return n?.toLocaleString() ?? '—'; }

function timeAgo(iso) {
    if (!iso) return '—';
    const diff = (Date.now() - new Date(iso)) / 1000;
    if (diff < 60) return Math.round(diff) + 's ago';
    if (diff < 3600) return Math.round(diff / 60) + 'm ago';
    if (diff < 86400) return Math.round(diff / 3600) + 'h ago';
    return Math.round(diff / 86400) + 'd ago';
}

// Global Exports
window.EmailGuard = {
    API,
    apiFetch,
    ensureAuth,
    updateConnectionStatus,
    logout,
    fmt,
    timeAgo,
    get authToken() { return localStorage.getItem('eg_token') || ''; }
};
