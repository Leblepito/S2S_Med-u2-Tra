(function(global) {
  'use strict';

  var SUPPORTED_LANGS = [
    { code: 'auto', name: 'Auto-detect', flag: '\uD83C\uDF10' },
    { code: 'tr', name: 'Türkçe', flag: '\uD83C\uDDF9\uD83C\uDDF7' },
    { code: 'ru', name: 'Русский', flag: '\uD83C\uDDF7\uD83C\uDDFA' },
    { code: 'en', name: 'English', flag: '\uD83C\uDDEC\uD83C\uDDE7' },
    { code: 'th', name: 'ไทย', flag: '\uD83C\uDDF9\uD83C\uDDED' },
    { code: 'vi', name: 'Tiếng Việt', flag: '\uD83C\uDDFB\uD83C\uDDF3' },
    { code: 'zh', name: '中文', flag: '\uD83C\uDDE8\uD83C\uDDF3' },
    { code: 'id', name: 'Indonesia', flag: '\uD83C\uDDEE\uD83C\uDDE9' }
  ];

  var TARGET_LANGS = SUPPORTED_LANGS.filter(function(l) { return l.code !== 'auto'; });

  var BabelFlow = {
    _version: '1.0.0',
    _config: null,
    _container: null,
    _panel: null,
    _floatingBtn: null,
    _bodyEl: null,
    _micBtn: null,
    _statusEl: null,
    _ws: null,
    _mediaStream: null,
    _audioContext: null,
    _ttsContext: null,
    _processor: null,
    _source: null,
    _isRecording: false,
    _isOpen: false,
    _sessionId: null,
    _translations: [],
    _reconnectAttempts: 0,
    _maxReconnectAttempts: 5,
    _reconnectTimer: null,
    _micDenied: false,

    init: function(config) {
      this._config = Object.assign({
        apiUrl: '',
        position: 'bottom-right',
        sourceLang: 'auto',
        targetLang: 'en',
        theme: 'light',
        onTranslation: null,
        onSessionStart: null,
        onSessionEnd: null,
        onError: null
      }, config);

      this._injectStyles();
      this._createContainer();
      this._createPanel();
      this._createFloatingButton();
      console.log('[BabelFlow] Initialized v' + this._version);
    },

    _injectStyles: function() {
      if (document.getElementById('babelflow-styles')) return;
      var s = document.createElement('style');
      s.id = 'babelflow-styles';
      s.textContent = [
        '.bf-container{position:fixed;z-index:99999;font-family:system-ui,-apple-system,sans-serif;font-size:14px;line-height:1.4;}',
        '.bf-container.bottom-right{bottom:20px;right:20px;}',
        '.bf-container.bottom-left{bottom:20px;left:20px;}',
        '.bf-btn{width:56px;height:56px;border-radius:50%;border:none;cursor:pointer;background:#2563eb;color:#fff;font-size:24px;box-shadow:0 4px 12px rgba(0,0,0,0.2);display:flex;align-items:center;justify-content:center;transition:transform 0.2s;}',
        '.bf-btn:hover{transform:scale(1.1);}',
        '.bf-panel{display:none;width:360px;max-height:500px;background:#fff;border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,0.15);overflow:hidden;flex-direction:column;margin-bottom:12px;border:1px solid #e5e7eb;}',
        '.bf-panel.open{display:flex;}',
        '.bf-panel.dark{background:#1e1e1e;color:#e0e0e0;border-color:#333;}',
        '.bf-header{padding:12px 16px;background:#2563eb;color:#fff;display:flex;align-items:center;justify-content:space-between;}',
        '.bf-header h3{margin:0;font-size:14px;font-weight:600;}',
        '.bf-lang-row{display:flex;gap:8px;padding:8px 16px;border-bottom:1px solid #f3f4f6;}',
        '.bf-panel.dark .bf-lang-row{border-color:#333;}',
        '.bf-lang-select{flex:1;padding:6px 8px;border-radius:8px;border:1px solid #d1d5db;font-size:13px;background:#fff;color:#333;}',
        '.bf-panel.dark .bf-lang-select{background:#2a2a2a;color:#e0e0e0;border-color:#555;}',
        '.bf-body{flex:1;overflow-y:auto;padding:8px 16px;min-height:200px;max-height:320px;}',
        '.bf-msg{padding:8px 12px;margin:4px 0;border-radius:12px;font-size:13px;max-width:85%;word-wrap:break-word;}',
        '.bf-msg.partial{color:#888;font-style:italic;background:transparent;padding:4px 12px;margin:2px 0;}',
        '.bf-msg.source{background:#f3f4f6;color:#333;}',
        '.bf-panel.dark .bf-msg.source{background:#333;color:#e0e0e0;}',
        '.bf-msg.translated{background:#2563eb;color:#fff;margin-left:auto;}',
        '.bf-msg.error{background:#fef2f2;color:#dc2626;font-size:12px;}',
        '.bf-panel.dark .bf-msg.error{background:#3b1111;color:#f87171;}',
        '.bf-mic-bar{padding:12px 16px;display:flex;align-items:center;justify-content:center;gap:12px;border-top:1px solid #e5e7eb;}',
        '.bf-panel.dark .bf-mic-bar{border-color:#333;}',
        '.bf-mic-btn{width:48px;height:48px;border-radius:50%;border:2px solid #2563eb;background:transparent;cursor:pointer;font-size:20px;transition:all 0.2s;display:flex;align-items:center;justify-content:center;}',
        '.bf-mic-btn:disabled{opacity:0.4;cursor:not-allowed;}',
        '.bf-mic-btn.recording{background:#ef4444;border-color:#ef4444;color:#fff;animation:bf-pulse 1.5s infinite;}',
        '@keyframes bf-pulse{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0.4)}50%{box-shadow:0 0 0 12px rgba(239,68,68,0)}}',
        '.bf-status{font-size:12px;color:#888;}',
        '.bf-close{background:none;border:none;color:#fff;font-size:18px;cursor:pointer;padding:0 4px;}',
        '.bf-close:hover{opacity:0.8;}',
        '.bf-empty{text-align:center;color:#aaa;padding:40px 16px;font-size:13px;}',
        '@media(max-width:480px){.bf-panel{width:calc(100vw - 24px);max-height:70vh;}.bf-container.bottom-right,.bf-container.bottom-left{right:12px;left:12px;bottom:12px;}}'
      ].join('\n');
      document.head.appendChild(s);
    },

    _createContainer: function() {
      this._container = document.createElement('div');
      this._container.className = 'bf-container ' + this._config.position;
      document.body.appendChild(this._container);
    },

    _createFloatingButton: function() {
      var self = this;
      var btn = document.createElement('button');
      btn.className = 'bf-btn';
      btn.innerHTML = '&#127760;';
      btn.title = 'BabelFlow — Live Translation';
      btn.setAttribute('aria-label', 'Open BabelFlow translation widget');
      btn.onclick = function() { self.toggle(); };
      this._floatingBtn = btn;
      this._container.appendChild(btn);
    },

    _createPanel: function() {
      var self = this;
      var panel = document.createElement('div');
      panel.className = 'bf-panel' + (this._config.theme === 'dark' ? ' dark' : '');

      // Header
      var header = document.createElement('div');
      header.className = 'bf-header';
      header.innerHTML = '<h3>BabelFlow Live Translation</h3>';
      var closeBtn = document.createElement('button');
      closeBtn.className = 'bf-close';
      closeBtn.innerHTML = '&times;';
      closeBtn.setAttribute('aria-label', 'Close');
      closeBtn.onclick = function() { self.toggle(); };
      header.appendChild(closeBtn);
      panel.appendChild(header);

      // Language selectors row
      var langRow = document.createElement('div');
      langRow.className = 'bf-lang-row';

      var srcSelect = document.createElement('select');
      srcSelect.className = 'bf-lang-select';
      srcSelect.setAttribute('aria-label', 'Source language');
      SUPPORTED_LANGS.forEach(function(lang) {
        var opt = document.createElement('option');
        opt.value = lang.code;
        opt.textContent = lang.flag + ' ' + lang.name;
        if (lang.code === self._config.sourceLang) opt.selected = true;
        srcSelect.appendChild(opt);
      });
      srcSelect.onchange = function() { self._config.sourceLang = this.value; };

      var arrow = document.createElement('span');
      arrow.textContent = '\u2192';
      arrow.style.cssText = 'display:flex;align-items:center;color:#888;font-size:16px;';

      var tgtSelect = document.createElement('select');
      tgtSelect.className = 'bf-lang-select';
      tgtSelect.setAttribute('aria-label', 'Target language');
      TARGET_LANGS.forEach(function(lang) {
        var opt = document.createElement('option');
        opt.value = lang.code;
        opt.textContent = lang.flag + ' ' + lang.name;
        if (lang.code === self._config.targetLang) opt.selected = true;
        tgtSelect.appendChild(opt);
      });
      tgtSelect.onchange = function() { self._config.targetLang = this.value; };

      langRow.appendChild(srcSelect);
      langRow.appendChild(arrow);
      langRow.appendChild(tgtSelect);
      panel.appendChild(langRow);

      // Body (translation messages)
      var body = document.createElement('div');
      body.className = 'bf-body';
      body.innerHTML = '<div class="bf-empty">Tap the mic to start translating</div>';
      this._bodyEl = body;
      panel.appendChild(body);

      // Mic bar
      var micBar = document.createElement('div');
      micBar.className = 'bf-mic-bar';
      var micBtn = document.createElement('button');
      micBtn.className = 'bf-mic-btn';
      micBtn.innerHTML = '&#127908;';
      micBtn.setAttribute('aria-label', 'Toggle microphone');
      micBtn.onclick = function() { self._toggleRecording(); };
      this._micBtn = micBtn;
      var status = document.createElement('span');
      status.className = 'bf-status';
      status.textContent = 'Tap to speak';
      this._statusEl = status;
      micBar.appendChild(micBtn);
      micBar.appendChild(status);
      panel.appendChild(micBar);

      this._panel = panel;
      this._container.appendChild(panel);
    },

    toggle: function() {
      this._isOpen = !this._isOpen;
      this._panel.classList.toggle('open', this._isOpen);
      if (this._isOpen) {
        if (!this._ws || this._ws.readyState > 1) {
          this._reconnectAttempts = 0;
          this._connectWebSocket();
        }
      } else {
        this._disconnectWebSocket();
        this._stopRecording();
      }
    },

    _connectWebSocket: function() {
      var self = this;
      var url = this._config.apiUrl;
      if (!url) {
        console.error('[BabelFlow] No apiUrl configured');
        this._statusEl.textContent = 'No API URL configured';
        return;
      }

      if (this._reconnectTimer) {
        clearTimeout(this._reconnectTimer);
        this._reconnectTimer = null;
      }

      this._statusEl.textContent = 'Connecting...';
      try {
        this._ws = new WebSocket(url);
      } catch (e) {
        this._statusEl.textContent = 'Connection failed';
        if (this._config.onError) this._config.onError(e);
        return;
      }
      this._ws.binaryType = 'arraybuffer';

      this._ws.onopen = function() {
        self._reconnectAttempts = 0;
        self._sessionId = 'bf-' + Date.now();
        self._statusEl.textContent = 'Connected \u2014 tap to speak';
        if (self._config.onSessionStart) {
          self._config.onSessionStart(self._sessionId);
        }
        // Send config matching backend ConfigMessage schema
        self._ws.send(JSON.stringify({
          type: 'config',
          source_lang: self._config.sourceLang || 'auto',
          target_langs: [self._config.targetLang || 'en'],
          enable_diarization: false
        }));
      };

      this._ws.onmessage = function(event) {
        if (typeof event.data === 'string') {
          try {
            var msg = JSON.parse(event.data);
            self._handleMessage(msg);
          } catch (e) {
            console.warn('[BabelFlow] Invalid JSON:', e);
          }
        } else {
          self._playTtsAudio(event.data);
        }
      };

      this._ws.onclose = function() {
        if (!self._isOpen) return; // intentional close
        self._statusEl.textContent = 'Disconnected';
        self._ws = null;
        self._attemptReconnect();
      };

      this._ws.onerror = function(err) {
        console.error('[BabelFlow] WebSocket error:', err);
        if (self._config.onError) self._config.onError(err);
      };
    },

    _disconnectWebSocket: function() {
      if (this._reconnectTimer) {
        clearTimeout(this._reconnectTimer);
        this._reconnectTimer = null;
      }
      if (this._ws) {
        this._ws.onclose = null; // prevent reconnect
        this._ws.close();
        this._ws = null;
      }
      if (this._sessionId && this._config.onSessionEnd) {
        this._config.onSessionEnd(this._sessionId, {
          translations: this._translations.length
        });
      }
      this._sessionId = null;
    },

    _attemptReconnect: function() {
      var self = this;
      if (this._reconnectAttempts >= this._maxReconnectAttempts) {
        this._statusEl.textContent = 'Connection failed';
        if (this._config.onError) {
          this._config.onError(new Error('connection_failed'));
        }
        return;
      }
      var delay = Math.pow(2, this._reconnectAttempts) * 1000; // 1s, 2s, 4s, 8s, 16s
      this._reconnectAttempts++;
      this._statusEl.textContent = 'Reconnecting (' + this._reconnectAttempts + '/' + this._maxReconnectAttempts + ')...';
      this._reconnectTimer = setTimeout(function() {
        if (self._isOpen) self._connectWebSocket();
      }, delay);
    },

    _handleMessage: function(msg) {
      var type = msg.type;
      if (type === 'partial_transcript') {
        this._showPartial(msg.text);
      } else if (type === 'final_transcript') {
        this._clearPartial();
        this._addSourceBubble(msg.lang, msg.text);
      } else if (type === 'translation') {
        this._addTranslationBubble(msg);
        if (this._config.onTranslation) {
          this._config.onTranslation({
            source_lang: msg.source_lang,
            target_lang: Object.keys(msg.translations || {})[0] || '',
            original_text: msg.source_text,
            translated_text: Object.values(msg.translations || {})[0] || ''
          });
        }
      } else if (type === 'error') {
        this._showError(msg.message || 'Unknown error');
        if (this._config.onError) {
          this._config.onError(new Error(msg.code || msg.message));
        }
      }
    },

    _clearEmpty: function() {
      var empty = this._bodyEl.querySelector('.bf-empty');
      if (empty) empty.remove();
    },

    _showPartial: function(text) {
      this._clearEmpty();
      var el = this._bodyEl.querySelector('.bf-msg.partial');
      if (!el) {
        el = document.createElement('div');
        el.className = 'bf-msg partial';
        this._bodyEl.appendChild(el);
      }
      el.textContent = text + '...';
      this._bodyEl.scrollTop = this._bodyEl.scrollHeight;
    },

    _clearPartial: function() {
      var el = this._bodyEl.querySelector('.bf-msg.partial');
      if (el) el.remove();
    },

    _addSourceBubble: function(lang, text) {
      this._clearEmpty();
      var div = document.createElement('div');
      div.className = 'bf-msg source';
      div.textContent = '[' + (lang || '?') + '] ' + text;
      this._bodyEl.appendChild(div);
      this._bodyEl.scrollTop = this._bodyEl.scrollHeight;
    },

    _addTranslationBubble: function(msg) {
      this._clearEmpty();
      var translations = msg.translations || {};
      for (var lang in translations) {
        if (translations.hasOwnProperty(lang)) {
          var div = document.createElement('div');
          div.className = 'bf-msg translated';
          div.textContent = '[' + lang + '] ' + translations[lang];
          this._bodyEl.appendChild(div);
        }
      }
      this._bodyEl.scrollTop = this._bodyEl.scrollHeight;
      this._translations.push(msg);
    },

    _showError: function(message) {
      var div = document.createElement('div');
      div.className = 'bf-msg error';
      div.textContent = '\u26A0 ' + message;
      this._bodyEl.appendChild(div);
      this._bodyEl.scrollTop = this._bodyEl.scrollHeight;
    },

    _toggleRecording: function() {
      if (this._micDenied) return;
      if (this._isRecording) {
        this._stopRecording();
      } else {
        this._startRecording();
      }
    },

    _startRecording: function() {
      var self = this;
      if (!this._ws || this._ws.readyState !== 1) {
        this._statusEl.textContent = 'Not connected';
        return;
      }
      this._statusEl.textContent = 'Requesting mic access...';

      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
          self._mediaStream = stream;
          self._audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
          var source = self._audioContext.createMediaStreamSource(stream);

          var processor = self._audioContext.createScriptProcessor(4096, 1, 1);
          processor.onaudioprocess = function(e) {
            if (!self._isRecording || !self._ws || self._ws.readyState !== 1) return;
            var float32 = e.inputBuffer.getChannelData(0);
            var int16 = new Int16Array(float32.length);
            for (var i = 0; i < float32.length; i++) {
              int16[i] = Math.max(-32768, Math.min(32767, Math.round(float32[i] * 32767)));
            }
            self._ws.send(int16.buffer);
          };

          source.connect(processor);
          processor.connect(self._audioContext.destination);
          self._processor = processor;
          self._source = source;

          self._isRecording = true;
          self._micBtn.classList.add('recording');
          self._statusEl.textContent = 'Listening...';
        })
        .catch(function(err) {
          console.error('[BabelFlow] Mic access failed:', err);
          if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            self._micDenied = true;
            self._micBtn.disabled = true;
            self._statusEl.textContent = 'Mic access denied \u2014 check browser settings';
          } else {
            self._statusEl.textContent = 'Mic error: ' + err.message;
          }
          if (self._config.onError) self._config.onError(err);
        });
    },

    _stopRecording: function() {
      this._isRecording = false;
      if (this._micBtn) this._micBtn.classList.remove('recording');
      if (this._statusEl && !this._micDenied) this._statusEl.textContent = 'Tap to speak';
      if (this._processor) { this._processor.disconnect(); this._processor = null; }
      if (this._source) { this._source.disconnect(); this._source = null; }
      if (this._audioContext) { this._audioContext.close(); this._audioContext = null; }
      if (this._mediaStream) {
        this._mediaStream.getTracks().forEach(function(t) { t.stop(); });
        this._mediaStream = null;
      }
    },

    _playTtsAudio: function(arrayBuffer) {
      try {
        if (!this._ttsContext || this._ttsContext.state === 'closed') {
          this._ttsContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
        }
        // TTS frame: 4-byte header length (LE) + JSON header + PCM16 audio
        var view = new DataView(arrayBuffer);
        var headerLen = view.getUint32(0, true);
        var audioStart = 4 + headerLen;
        if (audioStart >= arrayBuffer.byteLength) return;

        var audioBytes = new Int16Array(arrayBuffer.slice(audioStart));
        var float32 = new Float32Array(audioBytes.length);
        for (var i = 0; i < audioBytes.length; i++) {
          float32[i] = audioBytes[i] / 32768;
        }
        var buffer = this._ttsContext.createBuffer(1, float32.length, 24000);
        buffer.getChannelData(0).set(float32);
        var src = this._ttsContext.createBufferSource();
        src.buffer = buffer;
        src.connect(this._ttsContext.destination);
        src.start();
      } catch (e) {
        console.warn('[BabelFlow] TTS playback error:', e);
      }
    },

    destroy: function() {
      this._stopRecording();
      this._disconnectWebSocket();
      if (this._ttsContext) {
        try { this._ttsContext.close(); } catch (e) { /* ignore */ }
        this._ttsContext = null;
      }
      if (this._container) { this._container.remove(); this._container = null; }
      var styles = document.getElementById('babelflow-styles');
      if (styles) styles.remove();
      this._translations = [];
      this._isOpen = false;
    }
  };

  global.BabelFlow = BabelFlow;
})(typeof window !== 'undefined' ? window : this);
