/**
 * 侧边栏面板 - iframe 嵌入组件
 * 兼容 Home Assistant 2025.x - 2026.x
 */
class HaPanelIframe extends HTMLElement {

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._panel = null;
    this._hass = null;
    this._narrow = false;
  }

  set panel(panel) {
    this._panel = panel;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._updateMenuButton();
  }

  set narrow(narrow) {
    this._narrow = narrow;
    this._updateMenuButton();
    this._render();
  }

  /** 更新 Shadow DOM 内的 ha-menu-button 属性 */
  _updateMenuButton() {
    const menuBtn = this.shadowRoot && this.shadowRoot.querySelector('ha-menu-button');
    if (menuBtn) {
      if (this._hass) menuBtn.hass = this._hass;
      if (this._narrow !== undefined) menuBtn.narrow = this._narrow;
    }
  }

  _fireEvent(type, data) {
    this.dispatchEvent(new Event(type, {
      bubbles: true,
      cancelable: false,
      composed: true,
      detail: data,
    }));
  }

  _toggleMenu(event) {
    this._fireEvent('hass-toggle-menu');
    event.stopPropagation();
  }

  /** HTML 转义，防止 XSS */
  _escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  /** 规范化 URL：支持端口号、双斜杠、冒号开头的简写 */
  _normalizeUrl(url) {
    if (!url) return '';
    // 纯端口号
    if (/^\d+$/.test(url)) {
      return 'http://' + location.hostname + ':' + url;
    }
    // 双斜杠开头
    if (url.indexOf('//') === 0) {
      return location.protocol + '//' + location.hostname + url.substring(1);
    }
    // 冒号开头（端口路径）
    if (url.indexOf(':') === 0) {
      return location.protocol + '//' + location.hostname + url;
    }
    return url;
  }

  _render() {
    if (!this._panel) return;

    const { config, title } = this._panel;
    const url = this._normalizeUrl(config.url);
    const mode = config.mode;

    // 内置页面 - 在 HA 内部导航（使用原始路径，不规范化）
    if (mode === '3') {
      history.replaceState(null, null, config.url);
      return this._fireEvent('location-changed', { replace: true });
    }

    // HTTPS 环境下嵌入 HTTP 页面
    if (location.protocol === 'https:' && url.indexOf('http://') === 0) {
      this._renderHttpsWarning(title, url);
      return;
    }

    // 全屏模式
    if (mode === '1') {
      this._renderFullscreen(title, url);
      return;
    }

    // 默认模式 - 带 HA 顶部工具栏
    this._renderDefault(title, url, mode);
  }

  /** 渲染 HTTPS 安全提示 */
  _renderHttpsWarning(title, url) {
    const safeTitle = this._escapeHtml(title);
    const safeUrl = this._escapeHtml(url);
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; height: 100%; background: var(--primary-background-color); }
        .toolbar { display: flex; align-items: center; font-size: 20px; height: var(--header-height);
          padding: 8px 12px; background-color: var(--app-header-background-color);
          color: var(--app-header-text-color, white); border-bottom: var(--app-header-border-bottom, none);
          box-sizing: border-box; width: 100%; }
        .main-title { margin: 0 0 0 24px; line-height: 20px; flex-grow: 1; }
        .container { display: flex; align-items: center; justify-content: center;
          height: calc(100% - var(--header-height)); flex-direction: column; padding: 24px; }
        .warning-icon { font-size: 48px; color: var(--warning-color, #ffa726); margin-bottom: 16px; }
        .message { color: var(--secondary-text-color, #666); text-align: center; margin-bottom: 24px; line-height: 1.6; }
        .open-btn { color: var(--primary-color); font-size: 16px; text-decoration: none;
          padding: 10px 24px; border: 2px solid var(--primary-color); border-radius: 24px;
          transition: all 0.2s ease; }
        .open-btn:hover { background: var(--primary-color); color: white; }
      </style>
      <div class="toolbar" role="banner">
        <ha-menu-button></ha-menu-button>
        <div class="main-title">${safeTitle}</div>
      </div>
      <div class="container" role="alert">
        <div class="warning-icon" aria-hidden="true">&#9888;&#65039;</div>
        <div class="message">
          由于浏览器安全限制，HTTPS 页面无法嵌入 HTTP 内容<br>
          请在新标签页中打开此链接
        </div>
        <a class="open-btn" href="${safeUrl}" target="_blank" rel="noreferrer noopener">在新标签页打开</a>
      </div>
    `;
    this._updateMenuButton();
  }

  /** 渲染全屏模式 */
  _renderFullscreen(title, url) {
    const safeTitle = this._escapeHtml(title);
    const safeUrl = this._escapeHtml(url);
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; height: 100%; background: var(--primary-background-color);
          overflow: hidden; position: relative; }
        :host([narrow]) { width: 100%; position: fixed; }
        .loading { display: flex; align-items: center; justify-content: center;
          height: 100%; color: var(--secondary-text-color, #666); }
        .spinner { width: 40px; height: 40px; border: 3px solid var(--divider-color, #e0e0e0);
          border-top-color: var(--primary-color); border-radius: 50%;
          animation: spin 0.8s linear infinite; margin-right: 12px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .iframe-wrapper { display: none; width: 100%; height: 100vh; }
        .iframe-wrapper.loaded { display: block; }
        .iframe-wrapper.loaded ~ .loading { display: none; }
        iframe { border: none; width: 100%; height: 100%; }
        .nav-btn { position: fixed; bottom: 16px; right: 16px; z-index: 10;
          background: var(--card-background-color, white); border-radius: 50%;
          box-shadow: 0 2px 8px rgba(0,0,0,0.2); width: 48px; height: 48px;
          display: flex; align-items: center; justify-content: center; cursor: pointer;
          border: none; }
        .nav-btn:hover { background: var(--secondary-background-color, #f5f5f5); }
      </style>
      <div class="iframe-wrapper">
        <iframe title="${safeTitle}" allow="fullscreen" src="${safeUrl}"></iframe>
      </div>
      <div class="loading" role="status"><div class="spinner" aria-hidden="true"></div>加载中...</div>
    `;

    const wrapper = this.shadowRoot.querySelector('.iframe-wrapper');
    const iframe = this.shadowRoot.querySelector('iframe');
    iframe.addEventListener('load', () => {
      wrapper.classList.add('loaded');
    });

    // 移动端导航按钮
    if (this._narrow) {
      const btn = document.createElement('button');
      btn.className = 'nav-btn';
      btn.title = '打开菜单';
      btn.setAttribute('aria-label', '打开侧边栏菜单');
      btn.innerHTML = '<ha-icon icon="mdi:menu" style="color:var(--primary-text-color)"></ha-icon>';
      btn.addEventListener('click', this._toggleMenu.bind(this));
      this.shadowRoot.appendChild(btn);
    }
  }

  /** 渲染默认模式（带工具栏） */
  _renderDefault(title, url, mode) {
    const safeTitle = this._escapeHtml(title);
    const safeUrl = this._escapeHtml(url);
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; height: 100%; background: var(--primary-background-color);
          overflow: hidden; position: relative; }
        :host([narrow]) { width: 100%; position: fixed; }
        .toolbar { display: flex; align-items: center; font-size: 20px;
          height: var(--header-height); padding: 8px 12px;
          pointer-events: none; background-color: var(--app-header-background-color);
          font-weight: 400; color: var(--app-header-text-color, white);
          border-bottom: var(--app-header-border-bottom, none); box-sizing: border-box; }
        @media (max-width: 599px) { .toolbar { padding: 4px; } }
        ha-menu-button { pointer-events: auto; }
        .main-title { margin: 0 0 0 24px; line-height: 20px; flex-grow: 1; }
        .content { position: relative; width: 100%;
          height: calc(100% - 1px - var(--header-height)); }
        .loading { display: flex; align-items: center; justify-content: center;
          height: 100%; color: var(--secondary-text-color, #666); }
        .spinner { width: 32px; height: 32px; border: 3px solid var(--divider-color, #e0e0e0);
          border-top-color: var(--primary-color); border-radius: 50%;
          animation: spin 0.8s linear infinite; margin-right: 12px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .iframe-wrapper { display: none; width: 100%; height: 100%; }
        .iframe-wrapper.loaded { display: block; }
        .iframe-wrapper.loaded ~ .loading { display: none; }
        iframe { border: none; width: 100%; height: 100%; }
      </style>
      <div class="toolbar" role="banner">
        <ha-menu-button></ha-menu-button>
        <div class="main-title">${safeTitle}</div>
      </div>
      <div class="content">
        <div class="iframe-wrapper">
          <iframe title="${safeTitle}" allow="fullscreen" src="/panel_iframe_www/index.html?mode=${mode}&url=${encodeURIComponent(url)}"></iframe>
        </div>
        <div class="loading" role="status"><div class="spinner" aria-hidden="true"></div>加载中...</div>
      </div>
    `;

    const wrapper = this.shadowRoot.querySelector('.iframe-wrapper');
    const iframe = this.shadowRoot.querySelector('iframe');
    iframe.addEventListener('load', () => {
      wrapper.classList.add('loaded');
    });

    this._updateMenuButton();
  }
}

customElements.define('ha-panel_iframe', HaPanelIframe);
