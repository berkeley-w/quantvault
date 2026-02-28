import { FormEvent, useState } from "react";
import toast from "react-hot-toast";
import { apiClient } from "../api/client";
import { TokenResponse } from "../types";

interface AuthPageProps {
  onAuthenticated: (payload: TokenResponse) => void;
}

export function AuthPage({ onAuthenticated }: AuthPageProps) {
  const [mode, setMode] = useState<"setup" | "login">("setup");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload: TokenResponse =
        mode === "setup"
          ? await apiClient("/api/v1/auth/setup", {
              method: "POST",
              body: JSON.stringify({ username, email, password }),
            })
          : await apiClient("/api/v1/auth/login", {
              method: "POST",
              body: JSON.stringify({ username, password }),
            });

      onAuthenticated(payload);
      toast.success(
        mode === "setup"
          ? "Admin user created and logged in"
          : "Successfully logged in"
      );
    } catch (err: any) {
      toast.error(
        err?.message ||
          (mode === "setup"
            ? "Failed to create admin user"
            : "Login failed")
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-100">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/70 p-8 shadow-xl">
        <div className="mb-6 text-center">
          <div className="text-sm font-semibold uppercase tracking-wide text-green-400">
            QuantVault
          </div>
          <h1 className="mt-2 text-2xl font-semibold text-slate-50">
            Secure Access
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            {mode === "setup"
              ? "Create the first admin account to get started."
              : "Sign in with your QuantVault credentials."}
          </p>
        </div>

        <div className="mb-6 flex rounded-full border border-slate-800 bg-slate-900 p-1 text-xs font-medium text-slate-300">
          <button
            type="button"
            className={`flex-1 rounded-full px-3 py-1 transition ${
              mode === "setup"
                ? "bg-slate-800 text-slate-50"
                : "hover:bg-slate-800/60"
            }`}
            onClick={() => setMode("setup")}
            disabled={loading}
          >
            First-time setup
          </button>
          <button
            type="button"
            className={`flex-1 rounded-full px-3 py-1 transition ${
              mode === "login"
                ? "bg-slate-800 text-slate-50"
                : "hover:bg-slate-800/60"
            }`}
            onClick={() => setMode("login")}
            disabled={loading}
          >
            Existing user login
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-300">
              Username
            </label>
            <input
              type="text"
              required
              minLength={3}
              className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none ring-0 transition focus:border-green-500 focus:ring-1 focus:ring-green-500"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          {mode === "setup" && (
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-300">
                Email
              </label>
              <input
                type="email"
                required
                className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none ring-0 transition focus:border-green-500 focus:ring-1 focus:ring-green-500"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          )}

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-300">
              Password
            </label>
            <input
              type="password"
              required
              minLength={8}
              className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none ring-0 transition focus:border-green-500 focus:ring-1 focus:ring-green-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-2 flex w-full items-center justify-center rounded-lg bg-green-500 px-4 py-2 text-sm font-semibold text-slate-950 shadow hover:bg-green-400 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {loading
              ? mode === "setup"
                ? "Creating admin..."
                : "Signing in..."
              : mode === "setup"
                ? "Create admin & continue"
                : "Sign in"}
          </button>

          {mode === "setup" && (
            <p className="mt-2 text-xs text-slate-500">
              This endpoint can only be used once. After the first admin is
              created, switch to{" "}
              <span className="font-semibold text-slate-300">
                Existing user login
              </span>{" "}
              to sign in.
            </p>
          )}
        </form>
      </div>
    </div>
  );
}

