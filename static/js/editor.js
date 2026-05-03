/**
 * Editor module for CodeSense AI — Monaco Editor integration.
 * Full VS Code-style editor with syntax highlighting, minimap, and smooth scrolling.
 */
const Editor = (() => {
  let monacoEditor = null;
  let editorInfoEl = null;

  // Map our language values to Monaco language IDs
  const LANGUAGE_MAP = {
    python: 'python',
    javascript: 'javascript',
    typescript: 'typescript',
    java: 'java',
    cpp: 'cpp',
    csharp: 'csharp',
    go: 'go',
    rust: 'rust',
    ruby: 'ruby',
    php: 'php',
    sql: 'sql',
    html: 'html',
    css: 'css',
    bash: 'shell',
    other: 'plaintext',
  };

  const DEFAULT_CODE = `# Paste or write your code here...
# Select a language and review mode, then click Review.

def example():
    password = '12345'  # Hardcoded password
    data = eval(input())  # Unsafe eval
    return data
`;

  function getMonacoTheme(appTheme) {
    return appTheme === 'light' ? 'codesense-light' : 'codesense-dark';
  }

  function defineCustomThemes(monaco) {
    // Dark theme matching our Stitch design system
    monaco.editor.defineTheme('codesense-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6a737d', fontStyle: 'italic' },
        { token: 'keyword', foreground: 'c6bfff' },
        { token: 'string', foreground: '45edee' },
        { token: 'number', foreground: 'fdcb6e' },
        { token: 'type', foreground: 'a29bfe' },
        { token: 'function', foreground: '6c5ce7' },
        { token: 'variable', foreground: 'dfe2eb' },
        { token: 'operator', foreground: '928ea0' },
      ],
      colors: {
        'editor.background': '#0a0e14',
        'editor.foreground': '#dfe2eb',
        'editor.lineHighlightBackground': '#161b2280',
        'editor.selectionBackground': '#6c5ce740',
        'editor.inactiveSelectionBackground': '#6c5ce720',
        'editorLineNumber.foreground': '#474554',
        'editorLineNumber.activeForeground': '#928ea0',
        'editorCursor.foreground': '#6c5ce7',
        'editor.selectionHighlightBackground': '#6c5ce720',
        'editorIndentGuide.background': '#1c2026',
        'editorIndentGuide.activeBackground': '#30363d',
        'editorBracketMatch.background': '#6c5ce730',
        'editorBracketMatch.border': '#6c5ce7',
        'scrollbar.shadow': '#00000000',
        'scrollbarSlider.background': '#31353c80',
        'scrollbarSlider.hoverBackground': '#474554aa',
        'scrollbarSlider.activeBackground': '#928ea0',
        'editorOverviewRuler.border': '#0a0e14',
        'minimap.background': '#0a0e14',
        'editorGutter.background': '#0a0e14',
        'editorWidget.background': '#161b22',
        'editorWidget.border': '#30363d',
        'input.background': '#0d1117',
        'input.border': '#30363d',
        'input.foreground': '#dfe2eb',
        'focusBorder': '#6c5ce7',
      },
    });

    // Light theme
    monaco.editor.defineTheme('codesense-light', {
      base: 'vs',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6a737d', fontStyle: 'italic' },
        { token: 'keyword', foreground: '5847d2' },
        { token: 'string', foreground: '006a6b' },
        { token: 'number', foreground: 'b45309' },
        { token: 'type', foreground: '7c6ff0' },
        { token: 'function', foreground: '5847d2' },
      ],
      colors: {
        'editor.background': '#ffffff',
        'editor.foreground': '#1a1c20',
        'editor.lineHighlightBackground': '#f5f6f810',
        'editor.selectionBackground': '#5847d230',
        'editorLineNumber.foreground': '#c4c6d0',
        'editorLineNumber.activeForeground': '#44464f',
        'editorCursor.foreground': '#5847d2',
        'scrollbarSlider.background': '#c4c6d060',
        'scrollbarSlider.hoverBackground': '#74777f80',
        'minimap.background': '#ffffff',
        'editorGutter.background': '#f8f9fa',
        'editorWidget.background': '#ffffff',
        'editorWidget.border': '#c4c6d0',
        'focusBorder': '#5847d2',
      },
    });
  }

  function updateEditorInfo() {
    if (!monacoEditor || !editorInfoEl) return;
    const pos = monacoEditor.getPosition();
    const model = monacoEditor.getModel();
    if (pos && model) {
      const lines = model.getLineCount();
      const chars = model.getValueLength();
      editorInfoEl.textContent = `Ln ${pos.lineNumber}, Col ${pos.column} · ${lines} lines · ${chars} chars`;
    }
  }

  function getCode() {
    return monacoEditor ? monacoEditor.getValue() : '';
  }

  function setCode(code) {
    if (monacoEditor) {
      monacoEditor.setValue(code);
    }
  }

  function clear() {
    setCode('');
    if (monacoEditor) monacoEditor.focus();
  }

  function setLanguage(langId) {
    if (!monacoEditor) return;
    const monacoLang = LANGUAGE_MAP[langId] || 'plaintext';
    const model = monacoEditor.getModel();
    if (model && window.monaco) {
      window.monaco.editor.setModelLanguage(model, monacoLang);
    }
    // Update status bar
    const statusLang = document.getElementById('status-lang');
    if (statusLang) {
      const names = { python:'Python', javascript:'JavaScript', typescript:'TypeScript', java:'Java', cpp:'C++', csharp:'C#', go:'Go', rust:'Rust', ruby:'Ruby', php:'PHP', sql:'SQL', html:'HTML', css:'CSS', bash:'Bash', other:'Plain Text' };
      statusLang.textContent = names[langId] || langId;
    }
  }

  function updateTheme(appTheme) {
    if (monacoEditor && window.monaco) {
      window.monaco.editor.setTheme(getMonacoTheme(appTheme));
    }
  }

  function init() {
    editorInfoEl = document.getElementById('editor-info');

    // Load Monaco via AMD loader
    require.config({
      paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs' }
    });

    require(['vs/editor/editor.main'], function (monaco) {
      window.monaco = monaco;

      defineCustomThemes(monaco);

      const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';

      monacoEditor = monaco.editor.create(document.getElementById('monaco-editor'), {
        value: DEFAULT_CODE,
        language: 'python',
        theme: getMonacoTheme(currentTheme),

        // VS Code-style features
        fontSize: 14,
        fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace",
        fontLigatures: true,
        lineHeight: 22,
        letterSpacing: 0.3,

        // Minimap (VS Code scroll overview)
        minimap: {
          enabled: true,
          scale: 1,
          showSlider: 'mouseover',
          renderCharacters: true,
          maxColumn: 80,
        },

        // Smooth scrolling
        smoothScrolling: true,
        cursorSmoothCaretAnimation: 'on',
        cursorBlinking: 'smooth',
        cursorStyle: 'line',
        cursorWidth: 2,

        // Scrollbar styling
        scrollbar: {
          vertical: 'visible',
          horizontal: 'auto',
          verticalScrollbarSize: 12,
          horizontalScrollbarSize: 12,
          useShadows: false,
          verticalHasArrows: false,
          horizontalHasArrows: false,
          arrowSize: 0,
        },

        // Editor behavior
        automaticLayout: true,
        wordWrap: 'off',
        tabSize: 4,
        insertSpaces: true,
        renderWhitespace: 'selection',
        renderLineHighlight: 'all',
        renderLineHighlightOnlyWhenFocus: false,
        roundedSelection: true,
        selectOnLineNumbers: true,
        glyphMargin: false,
        folding: true,
        foldingStrategy: 'indentation',
        showFoldingControls: 'mouseover',
        lineNumbers: 'on',
        lineDecorationsWidth: 8,
        lineNumbersMinChars: 3,

        // Bracket matching
        bracketPairColorization: { enabled: true },
        matchBrackets: 'always',
        guides: {
          bracketPairs: true,
          indentation: true,
          highlightActiveIndentation: true,
        },

        // Suggestions & autocomplete
        quickSuggestions: true,
        suggestOnTriggerCharacters: true,
        acceptSuggestionOnEnter: 'on',
        snippetSuggestions: 'inline',
        parameterHints: { enabled: true },

        // Accessibility
        accessibilitySupport: 'auto',

        // Padding
        padding: { top: 12, bottom: 12 },

        // Hover
        hover: { enabled: true, delay: 300 },

        // Sticky scroll (VS Code feature)
        stickyScroll: { enabled: true },
      });

      // Update editor info on cursor change
      monacoEditor.onDidChangeCursorPosition(() => updateEditorInfo());
      monacoEditor.onDidChangeModelContent(() => updateEditorInfo());
      updateEditorInfo();

      // Handle resize
      window.addEventListener('resize', () => {
        if (monacoEditor) monacoEditor.layout();
      });

      console.log('✅ Monaco Editor initialized');
    });

    // Clear button
    const clearBtn = document.getElementById('clear-editor-btn');
    if (clearBtn) clearBtn.addEventListener('click', clear);

    // Language selector syncs with Monaco
    const langSelect = document.getElementById('language-select');
    if (langSelect) {
      langSelect.addEventListener('change', () => setLanguage(langSelect.value));
    }
  }

  return { init, getCode, setCode, clear, setLanguage, updateTheme };
})();
