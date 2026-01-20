// Shared utilities for Zalo Clone

class Utils {
  static debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  static formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) {
      return "Vừa xong";
    } else if (diffMins < 60) {
      return `${diffMins} phút trước`;
    } else if (diffHours < 24) {
      return `${diffHours} giờ trước`;
    } else if (diffDays < 7) {
      return `${diffDays} ngày trước`;
    } else {
      return date.toLocaleDateString("vi-VN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });
    }
  }

  static formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString("vi-VN", {
      day: "numeric",
      month: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  static truncateText(text, maxLength) {
    if (!text) return "";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  }

  static validatePhoneNumber(phone) {
    const regex = /^(0[0-9]{9,10})$/;
    return regex.test(phone);
  }

  static validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  }

  static getFileExtension(filename) {
    return filename.slice(((filename.lastIndexOf(".") - 1) >>> 0) + 2);
  }

  static isImageFile(filename) {
    const ext = this.getFileExtension(filename).toLowerCase();
    return ["jpg", "jpeg", "png", "gif", "webp"].includes(ext);
  }

  static async sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

class LocalStorageManager {
  static set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error("LocalStorage set error:", error);
      return false;
    }
  }

  static get(key) {
    try {
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      console.error("LocalStorage get error:", error);
      return null;
    }
  }

  static remove(key) {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error("LocalStorage remove error:", error);
      return false;
    }
  }

  static clear() {
    try {
      localStorage.clear();
      return true;
    } catch (error) {
      console.error("LocalStorage clear error:", error);
      return false;
    }
  }
}

class ApiClient {
  constructor(baseURL = "") {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    const defaultOptions = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      credentials: "include",
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return await response.json();
      }

      return await response.text();
    } catch (error) {
      console.error("API request error:", error);
      throw error;
    }
  }

  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url, { method: "GET" });
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: "DELETE" });
  }

  async upload(endpoint, formData) {
    return this.request(endpoint, {
      method: "POST",
      headers: {},
      body: formData,
    });
  }
}

class SocketManager {
  constructor() {
    this.socket = null;
    this.eventHandlers = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  connect(url = "") {
    this.socket = io(url, {
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
    });

    this.setupEventListeners();
  }

  setupEventListeners() {
    this.socket.on("connect", () => {
      console.log("Socket connected");
      this.reconnectAttempts = 0;
      this.emit("socket_connected");
    });

    this.socket.on("disconnect", (reason) => {
      console.log("Socket disconnected:", reason);
      this.emit("socket_disconnected", { reason });

      if (reason === "io server disconnect") {
        // Server initiated disconnect, need to manually reconnect
        setTimeout(() => this.socket.connect(), 1000);
      }
    });

    this.socket.on("connect_error", (error) => {
      console.error("Socket connection error:", error);
      this.emit("socket_error", { error });

      this.reconnectAttempts++;
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.emit("socket_connection_failed");
      }
    });

    this.socket.on("reconnect", (attemptNumber) => {
      console.log("Socket reconnected after", attemptNumber, "attempts");
      this.emit("socket_reconnected", { attemptNumber });
    });

    this.socket.on("reconnect_attempt", (attemptNumber) => {
      console.log("Socket reconnect attempt", attemptNumber);
      this.emit("socket_reconnect_attempt", { attemptNumber });
    });

    this.socket.on("reconnect_failed", () => {
      console.error("Socket reconnection failed");
      this.emit("socket_reconnect_failed");
    });
  }

  on(event, handler) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event).push(handler);

    if (this.socket) {
      this.socket.on(event, handler);
    }

    return () => this.off(event, handler);
  }

  off(event, handler) {
    if (this.eventHandlers.has(event)) {
      const handlers = this.eventHandlers.get(event);
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }

    if (this.socket) {
      this.socket.off(event, handler);
    }
  }

  emit(event, data) {
    if (this.socket) {
      this.socket.emit(event, data);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.eventHandlers.clear();
    }
  }

  get isConnected() {
    return this.socket && this.socket.connected;
  }
}

class NotificationManager {
  constructor() {
    this.permission = null;
    this.init();
  }

  async init() {
    if ("Notification" in window) {
      this.permission = Notification.permission;

      if (this.permission === "default") {
        this.permission = await Notification.requestPermission();
      }
    }
  }

  show(title, options = {}) {
    if (this.permission === "granted") {
      const notification = new Notification(title, {
        icon: options.icon || "/favicon.ico",
        body: options.body || "",
        tag: options.tag || "zalo-notification",
        requireInteraction: options.requireInteraction || false,
        silent: options.silent || false,
      });

      if (options.onclick) {
        notification.onclick = options.onclick;
      }

      if (options.onclose) {
        notification.onclose = options.onclose;
      }

      return notification;
    }

    return null;
  }

  showInApp(message, type = "info", duration = 5000) {
    const event = new CustomEvent("show-toast", {
      detail: { message, type, duration },
    });
    window.dispatchEvent(event);
  }
}

// Export for use in other files
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    Utils,
    LocalStorageManager,
    ApiClient,
    SocketManager,
    NotificationManager,
  };
}
