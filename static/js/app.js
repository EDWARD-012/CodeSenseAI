/**
 * Main Application Controller for CodeSense AI.
 * Orchestrates review, execution, chat context, and account UI.
 */
const App = (() => {
  let lastReviewContext = '';
  let isReviewing = false;
  let isRunning = false;

  const reviewButtonHtml = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg><span>Review</span>';
  const runButtonHtml = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg><span>Run</span>';

  function getLastReviewContext() {
    return lastReviewContext;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function setStatus(text, state = 'ready') {
    const statusText = document.getElementById('status-text');
    const statusDot = document.getElementById('status-dot');
    const statusBar = document.getElementById('status-bar');

    if (statusText) statusText.textContent = text;
    if (statusDot) {
      statusDot.className = 'status-dot';
      if (state === 'loading') statusDot.classList.add('loading');
      else if (state === 'error') statusDot.classList.add('disconnected');
    }
    if (statusBar) statusBar.classList.toggle('active', state === 'loading');
  }

  function renderReviewResult(data) {
    const contentEl = document.getElementById('review-content');
    const badgeEl = document.getElementById('risk-badge');
    if (!contentEl) return;

    let html = '';

    if (badgeEl && data.riskLevel) {
      const level = data.riskLevel.toLowerCase();
      const cls = level === 'high' ? 'risk-high' : level === 'medium' ? 'risk-medium' : level === 'low' ? 'risk-low' : 'risk-unknown';
      badgeEl.innerHTML = `<span class="risk-badge ${cls}">${escapeHtml(data.riskLevel)}</span>`;
    }

    if (data.summary) {
      html += `<div class="review-summary"><h3>Summary</h3><p>${escapeHtml(data.summary)}</p></div>`;
    }

    if (data.issues && data.issues.length > 0) {
      html += '<div class="review-section"><h4>Issues Found</h4>';
      data.issues.forEach((issue) => {
        const typeCls = `issue-type-${(issue.type || 'bug').toLowerCase()}`;
        html += `
          <div class="issue-card">
            <div class="issue-header">
              <span class="issue-type ${typeCls}">${escapeHtml(issue.type || 'Issue')}</span>
              ${issue.line ? `<span class="issue-line">Line ${escapeHtml(String(issue.line))}</span>` : ''}
              <span class="issue-severity">${escapeHtml(issue.severity || '')}</span>
            </div>
            <div class="issue-description">${escapeHtml(issue.description || '')}</div>
            ${issue.suggestion ? `<div class="issue-suggestion">${escapeHtml(issue.suggestion)}</div>` : ''}
          </div>`;
      });
      html += '</div>';
    }

    if (data.suggestions && data.suggestions.length > 0) {
      html += '<div class="review-section"><h4>Suggestions</h4><ul class="review-list">';
      data.suggestions.forEach((suggestion) => { html += `<li>${escapeHtml(suggestion)}</li>`; });
      html += '</ul></div>';
    }

    if (data.positives && data.positives.length > 0) {
      html += '<div class="review-section"><h4>Positives</h4><ul class="review-list positives">';
      data.positives.forEach((positive) => { html += `<li>${escapeHtml(positive)}</li>`; });
      html += '</ul></div>';
    }

    if (data.rawResponse) {
      html += `<div class="review-section"><h4>Full Response</h4><div class="raw-response">${escapeHtml(data.rawResponse)}</div></div>`;
    }

    contentEl.innerHTML = html || '<div class="review-empty"><p>No issues found. Your code looks good.</p></div>';
  }

  function showReviewLoading() {
    const contentEl = document.getElementById('review-content');
    const badgeEl = document.getElementById('risk-badge');
    if (contentEl) {
      contentEl.innerHTML = '<div class="loading-overlay"><div class="loading-spinner" style="width:32px;height:32px;border-width:3px;"></div><span>Analyzing your code<span class="loading-dots"></span></span></div>';
    }
    if (badgeEl) badgeEl.innerHTML = '';
  }

  function showReviewError(message) {
    const contentEl = document.getElementById('review-content');
    if (contentEl) {
      contentEl.innerHTML = `<div class="review-empty"><div class="review-empty-icon">!</div><p>${escapeHtml(message)}</p></div>`;
    }
  }

  async function handleReview() {
    if (isReviewing) return;

    const code = Editor.getCode().trim();
    if (!code) {
      showReviewError('Please enter some code to review.');
      return;
    }

    const language = document.getElementById('language-select')?.value || 'python';
    const reviewMode = document.getElementById('review-mode-select')?.value || 'general';
    const reviewBtn = document.getElementById('review-btn');

    isReviewing = true;
    if (reviewBtn) {
      reviewBtn.disabled = true;
      reviewBtn.innerHTML = '<span class="loading-spinner" style="width:14px;height:14px;border-width:2px;"></span><span>Reviewing</span>';
    }
    showReviewLoading();
    setStatus('Analyzing code...', 'loading');

    try {
      const result = await ApiClient.reviewCode(code, language, reviewMode);
      if (result.success) {
        renderReviewResult(result);
        lastReviewContext = result.summary || '';
        setStatus('Review complete', 'ready');
      } else {
        showReviewError(result.error || 'Review failed.');
        setStatus('Review failed', 'error');
      }
    } catch (error) {
      showReviewError(error.message);
      setStatus('Error', 'error');
    } finally {
      isReviewing = false;
      if (reviewBtn) {
        reviewBtn.disabled = false;
        reviewBtn.innerHTML = reviewButtonHtml;
      }
    }
  }

  function renderOutput(result) {
    const outputEl = document.getElementById('output-content');
    const statusEl = document.getElementById('output-status');
    const panel = document.getElementById('output-panel');
    if (!outputEl) return;

    if (panel) panel.classList.remove('collapsed');

    let html = '';
    if (result.stdout) html += `<span class="output-stdout">${escapeHtml(result.stdout)}</span>`;
    if (result.stderr) html += `<span class="output-stderr">${escapeHtml(result.stderr)}</span>`;

    if (result.timed_out) {
      html += '\n<span class="output-exit-code timeout">Timed Out</span>';
    } else if (result.exit_code === 0) {
      html += '\n<span class="output-exit-code success">Exit Code: 0</span>';
    } else if (result.exit_code !== undefined && result.exit_code !== -1) {
      html += `\n<span class="output-exit-code error">Exit Code: ${result.exit_code}</span>`;
    } else if (!result.success && result.error) {
      html = `<span class="output-stderr">${escapeHtml(result.error)}</span>`;
    }

    outputEl.innerHTML = html || '<span class="output-placeholder">No output produced.</span>';
    if (statusEl) statusEl.textContent = result.success ? 'Done' : 'Error';
  }

  async function handleRunCode() {
    if (isRunning) return;

    const code = Editor.getCode().trim();
    if (!code) {
      const outputEl = document.getElementById('output-content');
      if (outputEl) outputEl.innerHTML = '<span class="output-stderr">No code to run.</span>';
      return;
    }

    const language = document.getElementById('language-select')?.value || 'python';
    const runBtn = document.getElementById('run-btn');
    const outputEl = document.getElementById('output-content');
    const statusEl = document.getElementById('output-status');
    const panel = document.getElementById('output-panel');

    isRunning = true;
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.innerHTML = '<span class="loading-spinner" style="width:14px;height:14px;border-width:2px;"></span><span>Running</span>';
    }
    if (outputEl) outputEl.innerHTML = '<span class="output-placeholder">Running...</span>';
    if (statusEl) statusEl.textContent = 'Running...';
    if (panel) panel.classList.remove('collapsed');
    setStatus('Running code...', 'loading');

    try {
      const result = await ApiClient.runCode(code, language);
      renderOutput(result);
      setStatus(result.success ? 'Execution complete' : 'Execution failed', result.success ? 'ready' : 'error');
    } catch (error) {
      renderOutput({ success: false, error: error.message, exit_code: -1 });
      setStatus('Run error', 'error');
    } finally {
      isRunning = false;
      if (runBtn) {
        runBtn.disabled = false;
        runBtn.innerHTML = runButtonHtml;
      }
    }
  }

  function initAuthControls() {
    const modal = document.getElementById('login-modal');
    const openBtn = document.getElementById('login-open-btn');
    const closeBtn = document.getElementById('login-close-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const form = document.getElementById('login-form');
    const usernameInput = document.getElementById('login-username');
    const passwordInput = document.getElementById('login-password');
    const submitBtn = document.getElementById('login-submit-btn');
    const errorEl = document.getElementById('login-error');
    const userChip = document.getElementById('user-chip');
    const userName = document.getElementById('user-name');
    const userAvatar = document.getElementById('user-avatar');
    const authStatus = document.getElementById('auth-status');

    function initials(name) {
      return String(name || 'CS').trim().slice(0, 2).toUpperCase() || 'CS';
    }

    function showModal() {
      if (!modal) return;
      modal.hidden = false;
      if (errorEl) errorEl.textContent = '';
      setTimeout(() => usernameInput?.focus(), 0);
    }

    function hideModal() {
      if (modal) modal.hidden = true;
      if (form) form.reset();
      if (errorEl) errorEl.textContent = '';
    }

    function renderAuthState() {
      const user = ApiClient.getUser();
      const signedIn = ApiClient.isAuthenticated() && user;
      if (openBtn) openBtn.hidden = Boolean(signedIn);
      if (userChip) userChip.hidden = !signedIn;
      if (userName && signedIn) userName.textContent = user.username || user.email || 'Signed in';
      if (userAvatar && signedIn) userAvatar.textContent = initials(user.username || user.email);
      if (authStatus) authStatus.textContent = signedIn ? `Signed in as ${user.username || user.email || 'user'}` : 'Guest workspace';
    }

    openBtn?.addEventListener('click', showModal);
    closeBtn?.addEventListener('click', hideModal);
    modal?.addEventListener('click', (event) => {
      if (event.target === modal) hideModal();
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && modal && !modal.hidden) hideModal();
    });

    logoutBtn?.addEventListener('click', () => {
      ApiClient.logout();
      renderAuthState();
      setStatus('Signed out', 'ready');
    });

    form?.addEventListener('submit', async (event) => {
      event.preventDefault();
      const username = usernameInput?.value.trim();
      const password = passwordInput?.value || '';
      if (!username || !password) {
        if (errorEl) errorEl.textContent = 'Enter your username and password.';
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading-spinner" style="width:14px;height:14px;border-width:2px;"></span><span>Signing in</span>';
      }
      if (errorEl) errorEl.textContent = '';

      try {
        const result = await ApiClient.login(username, password);
        if (result.success) {
          hideModal();
          renderAuthState();
          setStatus('Signed in', 'ready');
        }
      } catch (error) {
        if (errorEl) errorEl.textContent = error.message || 'Sign in failed.';
        setStatus('Sign in failed', 'error');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<span>Sign in</span>';
        }
      }
    });

    renderAuthState();
  }

  function initResizers() {
    const mainResizer = document.getElementById('main-pane-resizer');
    const rightPanel = document.getElementById('right-panel');
    let isMainDragging = false;
    let startX = 0;
    let startWidth = 0;

    if (mainResizer && rightPanel) {
      mainResizer.addEventListener('mousedown', (event) => {
        isMainDragging = true;
        startX = event.clientX;
        startWidth = rightPanel.getBoundingClientRect().width;
        document.querySelector('.main-content')?.classList.add('resizing');
        document.body.style.cursor = 'col-resize';
        event.preventDefault();
      });

      document.addEventListener('mousemove', (event) => {
        if (!isMainDragging) return;
        const delta = event.clientX - startX;
        const newWidth = Math.max(300, Math.min(window.innerWidth * 0.7, startWidth + delta));
        rightPanel.style.width = `${newWidth}px`;
        if (window.Editor && typeof window.Editor.layout === 'function') window.Editor.layout();
        else window.dispatchEvent(new Event('resize'));
      });

      document.addEventListener('mouseup', () => {
        if (!isMainDragging) return;
        isMainDragging = false;
        document.querySelector('.main-content')?.classList.remove('resizing');
        document.body.style.cursor = '';
      });
    }

    const chatResizer = document.getElementById('chat-resizer');
    const chatPanel = document.getElementById('chat-panel');
    let isChatDragging = false;
    let chatStartY = 0;
    let chatStartHeight = 0;

    if (chatResizer && chatPanel) {
      chatResizer.addEventListener('mousedown', (event) => {
        isChatDragging = true;
        chatStartY = event.clientY;
        chatStartHeight = chatPanel.getBoundingClientRect().height;
        document.querySelector('.right-panel')?.classList.add('resizing-vert');
        document.body.style.cursor = 'row-resize';
        event.preventDefault();
      });

      document.addEventListener('mousemove', (event) => {
        if (!isChatDragging) return;
        const delta = chatStartY - event.clientY;
        const newHeight = Math.max(100, Math.min(window.innerHeight * 0.7, chatStartHeight + delta));
        chatPanel.style.height = `${newHeight}px`;
      });

      document.addEventListener('mouseup', () => {
        if (!isChatDragging) return;
        isChatDragging = false;
        document.querySelector('.right-panel')?.classList.remove('resizing-vert');
        document.body.style.cursor = '';
      });
    }

    const outputResizer = document.getElementById('output-resizer');
    const outputPanel = document.getElementById('output-panel');
    let isOutputDragging = false;
    let outputStartY = 0;
    let outputStartHeight = 0;

    if (outputResizer && outputPanel) {
      outputResizer.addEventListener('mousedown', (event) => {
        if (outputPanel.classList.contains('collapsed')) return;
        isOutputDragging = true;
        outputStartY = event.clientY;
        outputStartHeight = outputPanel.getBoundingClientRect().height;
        outputPanel.classList.add('resizing');
        document.body.style.cursor = 'row-resize';
        event.preventDefault();
      });

      document.addEventListener('mousemove', (event) => {
        if (!isOutputDragging) return;
        const delta = outputStartY - event.clientY;
        const newHeight = Math.max(60, Math.min(800, outputStartHeight + delta));
        outputPanel.style.height = `${newHeight}px`;
        if (window.Editor && typeof window.Editor.layout === 'function') window.Editor.layout();
        else window.dispatchEvent(new Event('resize'));
      });

      document.addEventListener('mouseup', () => {
        if (!isOutputDragging) return;
        isOutputDragging = false;
        outputPanel.classList.remove('resizing');
        document.body.style.cursor = '';
      });
    }
  }

  function init() {
    ThemeManager.init();
    Editor.init();
    Chat.init();
    initAuthControls();

    document.getElementById('review-btn')?.addEventListener('click', handleReview);
    document.getElementById('run-btn')?.addEventListener('click', handleRunCode);

    document.getElementById('clear-output-btn')?.addEventListener('click', (event) => {
      event.stopPropagation();
      const outputEl = document.getElementById('output-content');
      if (outputEl) outputEl.innerHTML = '<span class="output-placeholder">Run your code to see output here...</span>';
    });

    function toggleOutput(event) {
      if (event) event.stopPropagation();
      document.getElementById('output-panel')?.classList.toggle('collapsed');
    }

    document.getElementById('toggle-output-btn')?.addEventListener('click', toggleOutput);
    document.querySelector('.output-header')?.addEventListener('click', toggleOutput);

    initResizers();

    document.addEventListener('keydown', (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        event.preventDefault();
        handleReview();
      }
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'Enter') {
        event.preventDefault();
        handleRunCode();
      }
      if (event.key === 'F5') {
        event.preventDefault();
        handleRunCode();
      }
    });

    setStatus('Ready', 'ready');
    console.log('CodeSense AI initialized');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  return { getLastReviewContext, handleReview, handleRunCode };
})();
