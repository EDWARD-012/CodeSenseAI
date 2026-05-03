/**
 * Main Application Controller for CodeSense AI.
 * Orchestrates the review workflow and connects all modules.
 */
const App = (() => {
  let lastReviewContext = '';
  let isReviewing = false;

  function getLastReviewContext() {
    return lastReviewContext;
  }

  // --- Status Bar ---
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
    if (statusBar) {
      statusBar.classList.toggle('active', state === 'loading');
    }
  }

  // --- Review Rendering ---
  function renderReviewResult(data) {
    const contentEl = document.getElementById('review-content');
    const badgeEl = document.getElementById('risk-badge');
    if (!contentEl) return;

    let html = '';

    // Risk badge
    if (badgeEl && data.riskLevel) {
      const level = data.riskLevel.toLowerCase();
      const cls = level === 'high' ? 'risk-high' : level === 'medium' ? 'risk-medium' : level === 'low' ? 'risk-low' : 'risk-unknown';
      const icon = level === 'high' ? '🔴' : level === 'medium' ? '🟡' : level === 'low' ? '🟢' : '⚪';
      badgeEl.innerHTML = `<span class="risk-badge ${cls}">${icon} ${data.riskLevel}</span>`;
    }

    // Summary
    if (data.summary) {
      html += `<div class="review-summary"><h3>Summary</h3><p>${escapeHtml(data.summary)}</p></div>`;
    }

    // Issues
    if (data.issues && data.issues.length > 0) {
      html += '<div class="review-section"><h4>🐛 Issues Found</h4>';
      data.issues.forEach(issue => {
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

    // Suggestions
    if (data.suggestions && data.suggestions.length > 0) {
      html += '<div class="review-section"><h4>💡 Suggestions</h4><ul class="review-list">';
      data.suggestions.forEach(s => { html += `<li>${escapeHtml(s)}</li>`; });
      html += '</ul></div>';
    }

    // Positives
    if (data.positives && data.positives.length > 0) {
      html += '<div class="review-section"><h4>✅ Positives</h4><ul class="review-list positives">';
      data.positives.forEach(p => { html += `<li>${escapeHtml(p)}</li>`; });
      html += '</ul></div>';
    }

    // Raw response fallback
    if (data.rawResponse) {
      html += `<div class="review-section"><h4>📄 Full Response</h4><div class="raw-response">${escapeHtml(data.rawResponse)}</div></div>`;
    }

    contentEl.innerHTML = html || '<div class="review-empty"><p>No issues found. Your code looks good! 🎉</p></div>';
  }

  function showReviewLoading() {
    const contentEl = document.getElementById('review-content');
    const badgeEl = document.getElementById('risk-badge');
    if (contentEl) {
      contentEl.innerHTML = `<div class="loading-overlay"><div class="loading-spinner" style="width:32px;height:32px;border-width:3px;"></div><span>Analyzing your code<span class="loading-dots"></span></span></div>`;
    }
    if (badgeEl) badgeEl.innerHTML = '';
  }

  function showReviewError(message) {
    const contentEl = document.getElementById('review-content');
    if (contentEl) {
      contentEl.innerHTML = `<div class="review-empty"><div class="review-empty-icon">⚠️</div><p>${escapeHtml(message)}</p></div>`;
    }
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // --- Review Action ---
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
    if (reviewBtn) { reviewBtn.disabled = true; reviewBtn.innerHTML = '<span class="loading-spinner" style="width:14px;height:14px;border-width:2px;"></span> Reviewing...'; }
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
      if (reviewBtn) { reviewBtn.disabled = false; reviewBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg> Review'; }
    }
  }

  // --- Run Code ---
  let isRunning = false;

  function renderOutput(result) {
    const outputEl = document.getElementById('output-content');
    const statusEl = document.getElementById('output-status');
    const panel = document.getElementById('output-panel');
    if (!outputEl) return;

    // Expand panel if collapsed
    if (panel) panel.classList.remove('collapsed');

    let html = '';

    if (result.stdout) {
      html += `<span class="output-stdout">${escapeHtml(result.stdout)}</span>`;
    }
    if (result.stderr) {
      html += `<span class="output-stderr">${escapeHtml(result.stderr)}</span>`;
    }

    // Exit code badge
    if (result.timed_out) {
      html += `\n<span class="output-exit-code timeout">⏱️ Timed Out</span>`;
    } else if (result.exit_code === 0) {
      html += `\n<span class="output-exit-code success">✓ Exit Code: 0</span>`;
    } else if (result.exit_code !== undefined && result.exit_code !== -1) {
      html += `\n<span class="output-exit-code error">✗ Exit Code: ${result.exit_code}</span>`;
    } else if (!result.success && result.error) {
      html = `<span class="output-stderr">${escapeHtml(result.error)}</span>`;
    }

    outputEl.innerHTML = html || '<span class="output-placeholder">No output produced.</span>';

    if (statusEl) {
      statusEl.textContent = result.success ? 'Done' : 'Error';
    }
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
    if (runBtn) { runBtn.disabled = true; runBtn.innerHTML = '<span class="loading-spinner" style="width:14px;height:14px;border-width:2px;"></span> Running...'; }
    if (outputEl) outputEl.innerHTML = '<span class="output-placeholder">⏳ Running...</span>';
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
      if (runBtn) { runBtn.disabled = false; runBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg> Run'; }
    }
  }

  // --- Init ---
  function init() {
    ThemeManager.init();
    Editor.init();
    Chat.init();

    const reviewBtn = document.getElementById('review-btn');
    if (reviewBtn) reviewBtn.addEventListener('click', handleReview);

    const runBtn = document.getElementById('run-btn');
    if (runBtn) runBtn.addEventListener('click', handleRunCode);

    // Output panel controls
    const clearOutputBtn = document.getElementById('clear-output-btn');
    if (clearOutputBtn) {
      clearOutputBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const el = document.getElementById('output-content');
        if (el) el.innerHTML = '<span class="output-placeholder">Run your code to see output here...</span>';
      });
    }

    const toggleOutputBtn = document.getElementById('toggle-output-btn');
    const outputHeader = document.querySelector('.output-header');
    function toggleOutput(e) {
      if (e) e.stopPropagation();
      const panel = document.getElementById('output-panel');
      if (panel) panel.classList.toggle('collapsed');
    }
    if (toggleOutputBtn) toggleOutputBtn.addEventListener('click', toggleOutput);
    if (outputHeader) outputHeader.addEventListener('click', toggleOutput);

    // Drag to resize main panes (horizontal)
    const mainResizer = document.getElementById('main-pane-resizer');
    const rightPanel = document.getElementById('right-panel');
    let isMainDragging = false;
    let startX = 0;
    let startWidth = 0;

    if (mainResizer && rightPanel) {
      mainResizer.addEventListener('mousedown', (e) => {
        isMainDragging = true;
        startX = e.clientX;
        startWidth = rightPanel.getBoundingClientRect().width;
        document.querySelector('.main-content').classList.add('resizing');
        document.body.style.cursor = 'col-resize';
        e.preventDefault();
      });

      document.addEventListener('mousemove', (e) => {
        if (!isMainDragging) return;
        // Since rightPanel is now on the left (order: 0), dragging right increases width
        const delta = e.clientX - startX;
        const newWidth = Math.max(300, Math.min(window.innerWidth * 0.7, startWidth + delta));
        rightPanel.style.width = `${newWidth}px`;
        
        if (window.Editor && typeof window.Editor.layout === 'function') {
           window.Editor.layout();
        } else {
           window.dispatchEvent(new Event('resize'));
        }
      });

      document.addEventListener('mouseup', () => {
        if (isMainDragging) {
          isMainDragging = false;
          document.querySelector('.main-content').classList.remove('resizing');
          document.body.style.cursor = '';
        }
      });
    }

    // Drag to resize left side (vertical between Review and Chat)
    const chatResizer = document.getElementById('chat-resizer');
    const chatPanel = document.getElementById('chat-panel');
    let isChatDragging = false;
    let chatStartY = 0;
    let chatStartHeight = 0;

    if (chatResizer && chatPanel) {
      chatResizer.addEventListener('mousedown', (e) => {
        isChatDragging = true;
        chatStartY = e.clientY;
        chatStartHeight = chatPanel.getBoundingClientRect().height;
        document.querySelector('.right-panel').classList.add('resizing-vert');
        document.body.style.cursor = 'row-resize';
        e.preventDefault();
      });

      document.addEventListener('mousemove', (e) => {
        if (!isChatDragging) return;
        // Dragging up increases chat panel height
        const delta = chatStartY - e.clientY;
        const newHeight = Math.max(100, Math.min(window.innerHeight * 0.7, chatStartHeight + delta));
        chatPanel.style.height = `${newHeight}px`;
      });

      document.addEventListener('mouseup', () => {
        if (isChatDragging) {
          isChatDragging = false;
          document.querySelector('.right-panel').classList.remove('resizing-vert');
          document.body.style.cursor = '';
        }
      });
    }

    // Drag to resize output panel
    const resizer = document.getElementById('output-resizer');
    const panel = document.getElementById('output-panel');
    let isDragging = false;
    let startY = 0;
    let startHeight = 0;

    if (resizer && panel) {
      resizer.addEventListener('mousedown', (e) => {
        if (panel.classList.contains('collapsed')) return;
        isDragging = true;
        startY = e.clientY;
        startHeight = panel.getBoundingClientRect().height;
        panel.classList.add('resizing');
        document.body.style.cursor = 'row-resize';
        e.preventDefault(); // Prevent text selection
      });

      document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const delta = startY - e.clientY;
        const newHeight = Math.max(60, Math.min(800, startHeight + delta));
        panel.style.height = `${newHeight}px`;
        
        // Let Monaco editor know it might need to resize
        if (window.Editor && typeof window.Editor.layout === 'function') {
           window.Editor.layout();
        } else {
           // Fallback to trigger resize event which Monaco listens to
           window.dispatchEvent(new Event('resize'));
        }
      });

      document.addEventListener('mouseup', () => {
        if (isDragging) {
          isDragging = false;
          panel.classList.remove('resizing');
          document.body.style.cursor = '';
        }
      });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); handleReview(); }
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'Enter') { e.preventDefault(); handleRunCode(); }
      if (e.key === 'F5') { e.preventDefault(); handleRunCode(); }
    });

    setStatus('Ready', 'ready');
    console.log('🧠 CodeSense AI initialized');
  }

  // Auto-init on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  return { getLastReviewContext, handleReview, handleRunCode };
})();
