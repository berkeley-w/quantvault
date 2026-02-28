const API_BASE = "";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// #region agent log
function debugLog(payload: Record<string, unknown>) {
  const body = {
    sessionId: "2d4e32",
    runId: "run1",
    timestamp: Date.now(),
    location: "client.ts:apiClient",
    ...payload,
  };
  fetch("http://127.0.0.1:7688/ingest/2e63d0a3-e37d-44ef-b884-a85b9acd98e6", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Debug-Session-Id": "2d4e32" },
    body: JSON.stringify(body),
  }).catch(() => {});
}
// #endregion

export async function apiClient<T>(url: string, options?: RequestInit): Promise<T> {
  const token =
    typeof window !== "undefined"
      ? window.localStorage.getItem("authToken")
      : null;

  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};
  const fullUrl = `${API_BASE}${url}`;

  // #region agent log
  debugLog({
    hypothesisId: "H1",
    message: "apiRequest",
    data: { url, fullUrl, apiBase: API_BASE, tokenPresent: !!token },
  });
  // #endregion

  let response: Response;
  try {
    response = await fetch(fullUrl, {
      headers: {
        "Content-Type": "application/json",
        ...authHeaders,
        ...(options?.headers || {}),
      },
      ...options,
    });
  } catch (e) {
    // #region agent log
    debugLog({
      hypothesisId: "H4",
      message: "apiNetworkError",
      data: { url, fullUrl, error: String(e) },
    });
    // #endregion
    throw e;
  }

  // #region agent log
  debugLog({
    hypothesisId: "H2,H3",
    message: "apiResponse",
    data: { url, status: response.status, ok: response.ok },
  });
  if (!response.ok) {
    debugLog({
      hypothesisId: "H3",
      message: "apiNotOk",
      data: { url, status: response.status },
    });
  }
  // #endregion

  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new ApiError(response.status, body.detail || response.statusText);
  }

  try {
    return (await response.json()) as Promise<T>;
  } catch (e) {
    // #region agent log
    debugLog({
      hypothesisId: "H5",
      message: "apiParseError",
      data: { url, error: String(e) },
    });
    // #endregion
    throw e;
  }
}

