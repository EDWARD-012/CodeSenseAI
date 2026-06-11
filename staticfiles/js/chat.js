/**
 * Chat module for CodeSense AI.
 * Manages the AI chat interface for follow-up questions.
 */
const Chat = (() => {
  let messagesEl, inputEl, sendBtn, emptyEl, typingEl, suggestionsEl;
  let isLoading = false;

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatMarkdown(text) {
    let html = escapeHtml(text);
    html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/^### (.+)$/gm, '<strong style="font-size:14px">$1</strong>');
    html = html.replace(/^## (.+)$/gm, '<strong style="font-size:15px">$1</strong>');
    html = html.replace(/^[-*] (.+)$/gm, '• $1');
    html = html.replace(/\n/g, '<br>');
    return html;
  }

  function addMessage(role, content) {
    if (emptyEl) emptyEl.style.display = 'none';
    // Hide suggestions after first real exchange
    if (suggestionsEl) suggestionsEl.style.display = 'none';

    const msgEl = document.createElement('div');
    msgEl.className = `chat-message ${role}`;
    msgEl.innerHTML = role === 'assistant' ? formatMarkdown(content) : escapeHtml(content);
    messagesEl.appendChild(msgEl);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function showTyping() {
    if (typingEl) typingEl.removeAttribute('hidden');
    if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function hideTyping() {
    if (typingEl) typingEl.setAttribute('hidden', '');
  }

  // Keep legacy alias used elsewhere
  function showTypingIndicator() { showTyping(); }
  function removeTypingIndicator() { hideTyping(); }

  async function sendMessage(message) {
    if (isLoading || !inputEl) return;

    const text = message || inputEl.value.trim();
    if (!text) return;

    inputEl.value = '';
    addMessage('user', text);

    isLoading = true;
    if (sendBtn) sendBtn.disabled = true;
    showTyping();

    try {
      const code = typeof Editor !== 'undefined' ? Editor.getCode() : '';
      const reviewContext = typeof App !== 'undefined' ? App.getLastReviewContext() : '';
      const language = document.getElementById('language-select')?.value || '';

      const result = await ApiClient.chat(text, code, reviewContext, language);

      hideTyping();

      if (result.success) {
        addMessage('assistant', result.answer);
      } else {
        addMessage('assistant', `⚠️ ${result.error || 'Something went wrong.'}`);
      }
    } catch (error) {
      hideTyping();
      addMessage('assistant', `❌ Error: ${error.message}`);
    } finally {
      isLoading = false;
      if (sendBtn) sendBtn.disabled = false;
      if (inputEl) inputEl.focus();
    }
  }

  function init() {
    messagesEl  = document.getElementById('chat-messages');
    inputEl     = document.getElementById('chat-input');
    sendBtn     = document.getElementById('chat-send-btn');
    emptyEl     = document.getElementById('chat-empty');
    typingEl    = document.getElementById('chat-typing');
    suggestionsEl = document.getElementById('chat-suggestions');

    if (sendBtn) sendBtn.addEventListener('click', () => sendMessage());
    if (inputEl) {
      inputEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
      });
    }

    // Wire suggestion chips
    if (suggestionsEl) {
      suggestionsEl.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
          const msg = chip.getAttribute('data-msg');
          if (msg) sendMessage(msg);
        });
      });
    }
  }

  return { init, addMessage };
})();
