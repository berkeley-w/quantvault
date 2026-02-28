/** Backend API URL. Empty = same origin. Set VITE_API_URL in production when frontend and backend are on different hosts (e.g. Render). */
const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? "";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export async function apiClient<T>(url: string, options?: RequestInit): Promise<T> {
  const token =
    typeof window !== "undefined"
      ? window.localStorage.getItem("authToken")
      : null;

  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      "Content-Type": "application/json",
      ...authHeaders,
      ...(options?.headers || {}),
    },
    ...options,
  });

  const text = await response.text();

  if (!response.ok) {
    let detail = response.statusText;
    if (text.startsWith("<")) {
      detail = "Server returned HTML instead of JSON. Check that the API is reachable.";
    } else {
      try {
        const body = JSON.parse(text);
        if (body?.detail) detail = body.detail;
      } catch {
        if (text) detail = text.slice(0, 200);
      }
    }
    throw new ApiError(response.status, detail);
  }

  if (text.startsWith("<")) {
    throw new ApiError(
      response.status,
      "Server returned HTML instead of JSON. Check that the API is reachable."
    );
  }

  try {
    return JSON.parse(text) as T;
  } catch {
    throw new ApiError(502, "Invalid JSON response from server.");
  }
}

