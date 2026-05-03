/**
 * Chat module for CodeSense AI.
 * Manages the AI chat interface for follow-up questions.
 */
const Chat = (() => {
  let messagesEl, inputEl, sendBtn, emptyEl;
  let isLoading = false;

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatMarkdown(text) {
    // Simple markdown: code blocks, inline code, bold, headers, lists
    let html = escapeHtml(text);

    // Code blocks
    html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    // Bold
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Headers
    html = html.replace(/^### (.+)$/gm, '<strong style="font-size:14px">$1</strong>');
    html = html.replace(/^## (.+)$/gm, '<strong style="font-size:15px">$1</strong>');
    // Lists
    html = html.replace(/^[-*] (.+)$/gm, '• $1');
    // Line breaks
    html = html.replace(/\n/g, '<br>');

    return html;
  }

  function addMessage(role, content) {
    if (emptyEl) emptyEl.style.display = 'none';

    const msgEl = document.createElement('div');
    msgEl.className = `chat-message ${role}`;
    msgEl.innerHTML = role === 'assistant' ? formatMarkdown(content) : escapeHtml(content);
    messagesEl.appendChild(msgEl);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function showTypingIndicator() {
    const el = document.createElement('div');
    el.className = 'chat-message assistant';
    el.id = 'typing-indicator';
    el.innerHTML = '<span class="loading-spinner" style="width:14px;height:14px;border-width:2px;"></span> Thinking...';
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function removeTypingIndicator() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
  }

  async function sendMessage() {
    if (isLoading || !inputEl) return;

    const message = inputEl.value.trim();
    if (!message) return;

    inputEl.value = '';
    addMessage('user', message);

    isLoading = true;
    sendBtn.disabled = true;
    showTypingIndicator();

    try {
      const code = typeof Editor !== 'undefined' ? Editor.getCode() : '';
      const reviewContext = typeof App !== 'undefined' ? App.getLastReviewContext() : '';

      const result = await ApiClient.chat(message, code, reviewContext);
      removeTypingIndicator();

      if (result.success) {
        addMessage('assistant', result.answer);
      } else {
        addMessage('assistant', `⚠️ ${result.error || 'Something went wrong.'}`);
      }
    } catch (error) {
      removeTypingIndicator();
      addMessage('assistant', `❌ Error: ${error.message}`);
    } finally {
      isLoading = false;
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }

  function init() {
    messagesEl = document.getElementById('chat-messages');
    inputEl = document.getElementById('chat-input');
    sendBtn = document.getElementById('chat-send-btn');
    emptyEl = document.getElementById('chat-empty');

    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (inputEl) {
      inputEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
      });
    }
  }

  return { init, addMessage };
})();
