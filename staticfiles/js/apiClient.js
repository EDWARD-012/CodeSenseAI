/**
 * API Client for CodeSense AI.
 * Handles all communication with the Django backend.
 */
const ApiClient = (() => {
  const BASE_URL = '';  // Same origin
  const TOKEN_KEY = 'codesense-auth-token';
  const USER_KEY = 'codesense-auth-user';

  async function post(endpoint, data) {
    const token = getToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;

    const response = await fetch(`${BASE_URL}/api/${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (!response.ok && !result.success) {
      throw new Error(result.error || `Request failed (${response.status})`);
    }

    return result;
  }

  async function login(username, password) {
    const result = await post('login', { username, password });
    if (result.success && result.access_token) {
      localStorage.setItem(TOKEN_KEY, result.access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(result.user || { username }));
    }
    return result;
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function getUser() {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY) || 'null');
    } catch (_error) {
      return null;
    }
  }

  function isAuthenticated() {
    return Boolean(getToken());
  }

  async function reviewCode(code, language, reviewMode) {
    return post('review-code', { code, language, reviewMode });
  }

  async function chat(message, code = '', reviewContext = '') {
    return post('chat', { message, code, reviewContext });
  }

  async function runCode(code, language) {
    return post('run-code', { code, language });
  }

  return { login, logout, getToken, getUser, isAuthenticated, reviewCode, chat, runCode };
})();
