/**
 * API Client for CodeSense AI.
 * Handles all communication with the Django backend.
 */
const ApiClient = (() => {
  const BASE_URL = '';  // Same origin

  async function post(endpoint, data) {
    const response = await fetch(`${BASE_URL}/api/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (!response.ok && !result.success) {
      throw new Error(result.error || `Request failed (${response.status})`);
    }

    return result;
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

  return { reviewCode, chat, runCode };
})();
