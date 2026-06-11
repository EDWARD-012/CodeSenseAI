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
    
    // Convert markdown links: [Text](URL)
    html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="chat-link">$1</a>');
    
    // Convert YouTube search tag: [YOUTUBE_SEARCH: topic]
    html = html.replace(/\[YOUTUBE_SEARCH:\s*([^\]]+)\]/gi, (match, query) => {
      const decodedQuery = query.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
      return `<div class="youtube-results-container" data-query="${escapeHtml(decodedQuery)}">
        <div class="youtube-loading">
          <div class="spinner"></div>
          <span>Searching YouTube for "${escapeHtml(decodedQuery)}"...</span>
        </div>
      </div>`;
    });

    // Convert raw URLs: https://... (prevent matching URLs already inside href="..." or tags)
    html = html.replace(/(?<!href=")(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer" class="chat-link">$1</a>');
    
    html = html.replace(/\n/g, '<br>');
    return html;
  }

  async function loadYoutubeResults() {
    const containers = document.querySelectorAll('.youtube-results-container:not(.loaded)');
    for (const container of containers) {
      container.classList.add('loaded');
      const query = container.getAttribute('data-query');
      try {
        const response = await fetch(`/api/youtube-search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        if (data.success && data.videos && data.videos.length > 0) {
          container.innerHTML = `
            <div class="youtube-list-title">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="color:#ff0000;vertical-align:middle;margin-right:4px"><path d="M23.498 6.163a3.003 3.003 0 0 0-2.11-2.11C19.518 3.545 12 3.545 12 3.545s-7.518 0-9.388.508a3.003 3.003 0 0 0-2.11 2.11C0 8.033 0 12 0 12s0 3.967.502 5.837a3.003 3.003 0 0 0 2.11 2.11c1.87.508 9.388.508 9.388.508s7.518 0 9.388-.508a3.003 3.003 0 0 0 2.11-2.11C24 15.967 24 12 24 12s0-3.967-.502-5.837zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
              Recommended YouTube Lectures:
            </div>
            <div class="youtube-videos-grid">
              ${data.videos.map(video => `
                <a href="${video.link}" target="_blank" rel="noopener noreferrer" class="youtube-video-card">
                  <div class="youtube-thumbnail-wrapper">
                    <img src="${video.thumbnail}" alt="${video.title}" class="youtube-thumbnail" loading="lazy">
                    ${video.duration ? `<span class="youtube-duration">${video.duration}</span>` : ''}
                  </div>
                  <div class="youtube-video-info">
                    <div class="youtube-video-title" title="${video.title}">${video.title}</div>
                    <div class="youtube-channel-name">${video.channel}</div>
                    <div class="youtube-meta-text">
                      ${video.views ? `<span>${video.views}</span>` : ''}
                      ${video.published ? `<span>• ${video.published}</span>` : ''}
                    </div>
                  </div>
                </a>
              `).join('')}
            </div>
          `;
        } else {
          container.innerHTML = `
            <div class="youtube-no-results">
              No direct video lectures found. <a href="https://www.youtube.com/results?search_query=${encodeURIComponent(query)}" target="_blank" class="chat-link">Search YouTube manually for "${escapeHtml(query)}"</a>
            </div>
          `;
        }
      } catch (err) {
        console.error('Error loading YouTube videos:', err);
        container.innerHTML = `
          <div class="youtube-error">
            Failed to load videos. <a href="https://www.youtube.com/results?search_query=${encodeURIComponent(query)}" target="_blank" class="chat-link">Try searching on YouTube</a>
          </div>
        `;
      }
    }
  }

  function addMessage(role, content) {
    if (emptyEl) emptyEl.style.display = 'none';
    if (suggestionsEl) suggestionsEl.style.display = 'none';

    const msgEl = document.createElement('div');
    msgEl.className = `chat-message ${role}`;
    msgEl.innerHTML = role === 'assistant' ? formatMarkdown(content) : escapeHtml(content);
    messagesEl.appendChild(msgEl);
    messagesEl.scrollTop = messagesEl.scrollHeight;

    if (role === 'assistant') {
      loadYoutubeResults();
    }
  }

  function showTyping() {
    if (typingEl) typingEl.removeAttribute('hidden');
    if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function hideTyping() {
    if (typingEl) typingEl.setAttribute('hidden', '');
  }

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

    let assistantMsgEl = null;
    let assistantText = '';

    function onChunk(token) {
      hideTyping();

      if (emptyEl) emptyEl.style.display = 'none';
      if (suggestionsEl) suggestionsEl.style.display = 'none';

      if (!assistantMsgEl) {
        assistantMsgEl = document.createElement('div');
        assistantMsgEl.className = 'chat-message assistant';
        messagesEl.appendChild(assistantMsgEl);
      }

      assistantText += token;
      assistantMsgEl.innerHTML = formatMarkdown(assistantText);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    try {
      const code = typeof Editor !== 'undefined' ? Editor.getCode() : '';
      const reviewContext = typeof App !== 'undefined' ? App.getLastReviewContext() : '';
      const language = document.getElementById('language-select')?.value || '';

      await ApiClient.chatStream(
        text,
        code,
        reviewContext,
        language,
        onChunk,
        () => {
          hideTyping();
          isLoading = false;
          if (sendBtn) sendBtn.disabled = false;
          if (inputEl) inputEl.focus();
          loadYoutubeResults();
        },
        (error) => {
          hideTyping();
          if (!assistantMsgEl) {
            addMessage('assistant', `⚠️ Error: ${error.message}`);
          } else {
            assistantMsgEl.innerHTML += `<br><br>⚠️ <em>Error: ${escapeHtml(error.message)}</em>`;
          }
          isLoading = false;
          if (sendBtn) sendBtn.disabled = false;
          if (inputEl) inputEl.focus();
          loadYoutubeResults();
        }
      );
    } catch (error) {
      hideTyping();
      addMessage('assistant', `❌ Error: ${error.message}`);
      isLoading = false;
      if (sendBtn) sendBtn.disabled = false;
      if (inputEl) inputEl.focus();
      loadYoutubeResults();
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
