dropdown_html = """
  <!-- Save Workspace Dropdown - body-level fixed overlay, never clipped -->
  <div id="profile-dropdown" hidden style="position:fixed;z-index:9999;width:300px;background:rgba(16,20,26,0.97);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.10);border-radius:12px;box-shadow:0 12px 40px rgba(0,0,0,0.6);padding:14px;display:flex;flex-direction:column;gap:12px;">
    <div class="dropdown-profile-header">
      <div class="dropdown-avatar" id="dropdown-avatar">CS</div>
      <div class="dropdown-user-info">
        <div class="dropdown-username" id="dropdown-username">User</div>
        <div class="dropdown-email" id="dropdown-email">user@gmail.com</div>
      </div>
      <button class="icon-button compact logout-action-btn" id="logout-btn" title="Sign out" aria-label="Sign out"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/></svg></button>
    </div>
    <div class="dropdown-divider"></div>
    <div class="dropdown-section active-file-section" id="active-file-section" style="display:none;">
      <div class="dropdown-section-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="13" height="13" style="margin-right:4px;vertical-align:middle;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><span>CURRENT FILE INFO</span></div>
      <div class="active-file-info">
        <div class="info-row"><span class="info-label">Name:</span><span class="info-value" id="active-file-name">-</span></div>
        <div class="info-row"><span class="info-label">Language:</span><span class="info-value" id="active-file-lang">-</span></div>
        <div class="info-row"><span class="info-label">Last Saved:</span><span class="info-value" id="active-file-time">-</span></div>
      </div>
      <div style="margin-top:8px;display:flex;gap:8px;"><button class="btn btn-secondary btn-xs" id="save-as-btn" style="flex:1;">Save As...</button><button class="btn btn-secondary btn-xs" id="new-file-btn" style="flex:1;">New File</button></div>
    </div>
    <div class="dropdown-divider active-file-divider" style="display:none;"></div>
    <div class="dropdown-section">
      <div class="dropdown-section-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13" style="margin-right:4px;vertical-align:middle;"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg><span>SAVED WORKSPACE</span></div>
      <div style="display:flex;gap:6px;margin-top:8px;margin-bottom:8px;">
        <input type="text" id="save-filename-input-popover" placeholder="Filename (e.g. 3sum.cpp)" style="flex:1;font-size:12px;padding:5px 8px;background:#1e2330;border:1px solid rgba(255,255,255,0.12);border-radius:6px;color:#e0e0e0;outline:none;">
        <button id="save-confirm-btn-popover" class="btn btn-primary" style="font-size:12px;padding:5px 12px;white-space:nowrap;">Save</button>
      </div>
      <div class="saved-files-list" id="saved-files-list"><div class="empty-list-msg">No codes saved yet.</div></div>
    </div>
    <div class="dropdown-divider"></div>
    <div class="dropdown-section">
      <div class="dropdown-section-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13" style="margin-right:4px;vertical-align:middle;"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg><span>RECENT CHATS</span></div>
      <div class="chat-sessions-list" id="chat-sessions-list"><div class="empty-list-msg">No recent chats.</div></div>
    </div>
    <div class="dropdown-divider"></div>
    <div class="dropdown-footer"><button class="dropdown-logout-link" id="logout-btn-bottom" type="button"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="11" height="11" style="vertical-align:middle;margin-right:3px;"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/></svg>Sign Out</button></div>
  </div>
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

if 'id="profile-dropdown"' not in content:
    content = content.replace('</body>', dropdown_html + '</body>')
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Dropdown injected successfully')
else:
    print('Dropdown already exists in file')
