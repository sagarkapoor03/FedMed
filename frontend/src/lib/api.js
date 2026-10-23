/**
 * FedMed API client.
 *
 * A thin wrapper around the FastAPI backend that the dashboard uses for
 * every request. The base URL is resolved from Vite's env variables so
 * the same bundle works against a local backend or a deployed one.
 */

const RAW_BASE =
  import.meta.env.VITE_API_BASE_URL ??
  (import.meta.env.DEV ? "http://127.0.0.1:8000" : "http://127.0.0.1:8000");

export const API_BASE = RAW_BASE.replace(/\/$/, "");
export const WS_BASE = API_BASE.replace(/^http/, "ws");

/** Raised for a non-2xx API response. */
export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

async function request(path, options = {}) {
  const { timeout = 120000, ...init } = options;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(init.headers || {}),
      },
    });

    const text = await response.text();
    let payload = null;
    if (text) {
      try {
        payload = JSON.parse(text);
      } catch {
        payload = { detail: text };
      }
    }

    if (!response.ok) {
      const detail =
        payload?.detail || payload?.message || `Request failed (${response.status})`;
      throw new ApiError(detail, response.status, payload);
    }

    return payload;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error.name === "AbortError") {
      throw new ApiError("The request timed out", 408, null);
    }
    throw new ApiError(
      `Cannot reach the FedMed API at ${API_BASE}. Is the backend running?`,
      0,
      null,
    );
  } finally {
    clearTimeout(timer);
  }
}

export const api = {
  health: () => request("/api/health", { timeout: 8000 }),

  status: () => request("/api/status", { timeout: 15000 }),

  nodes: () => request("/api/nodes", { timeout: 15000 }),

  metrics: () => request("/api/metrics", { timeout: 30000 }),

  privacy: () => request("/api/privacy", { timeout: 15000 }),

  settings: () => request("/api/settings", { timeout: 15000 }),

  updateSettings: (payload) =>
    request("/api/settings", {
      method: "POST",
      body: JSON.stringify(payload),
      timeout: 15000,
    }),

  startBaseline: (epochs = 30) =>
    request("/api/train/baseline", {
      method: "POST",
      body: JSON.stringify({ epochs }),
      timeout: 20000,
    }),

  startFederated: (rounds = 10, dropoutRound = 0) =>
    request("/api/train/federated", {
      method: "POST",
      body: JSON.stringify({ rounds, dropout_round: dropoutRound }),
      timeout: 20000,
    }),

  mriAnalyze: (model = "federated", sample = null) => {
    const params = new URLSearchParams({ model });
    if (sample !== null && sample !== undefined) params.set("sample", String(sample));
    return request(`/api/mri/analyze?${params.toString()}`, { timeout: 120000 });
  },
};

/**
 * Open the live metrics WebSocket.
 *
 * Returns a handle with a `close()` method; the caller supplies `onEvent`
 * for every frame and `onStatus` for connection-state changes.
 */
export function openMetricsSocket({ onEvent, onStatus } = {}) {
  let socket = null;
  let closed = false;
  let retry = null;

  const connect = () => {
    if (closed) return;

    onStatus?.("connecting");

    try {
      socket = new WebSocket(`${WS_BASE}/ws/metrics`);
    } catch {
      onStatus?.("offline");
      scheduleRetry();
      return;
    }

    socket.onopen = () => onStatus?.("online");

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === "ping") return;
        onEvent?.(payload);
      } catch {
        // Ignore malformed frames rather than tearing down the socket.
      }
    };

    socket.onerror = () => onStatus?.("error");

    socket.onclose = () => {
      onStatus?.("offline");
      scheduleRetry();
    };
  };

  const scheduleRetry = () => {
    if (closed) return;
    clearTimeout(retry);
    retry = setTimeout(connect, 3000);
  };

  connect();

  return {
    close() {
      closed = true;
      clearTimeout(retry);
      socket?.close();
    },
  };
}
