(function(global) {
  'use strict';
  var BabelFlow = {
    _version: '1.0.0',
    _config: null,
    init: function(config) {
      this._config = Object.assign({
        apiUrl: '',
        position: 'bottom-right',
        defaultLang: 'en',
        sourceLang: 'auto',
        targetLang: 'en',
        theme: 'light',
        onTranslation: null,
        onSessionStart: null,
        onSessionEnd: null,
        onError: null
      }, config);
      console.log('[BabelFlow] Initialized v' + this._version);
    }
  };
  global.BabelFlow = BabelFlow;
})(typeof window !== 'undefined' ? window : this);
