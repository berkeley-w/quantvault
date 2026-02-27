import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { apiClient } from "../api/client";

export function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSetupMode, setIsSetupMode] = useState(false);
  const [setupData, setSetupData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    apiClient<{ has_users: boolean }>("/api/auth/setup")
      .then((data) => {
        setIsSetupMode(!data.has_users);
      })
      .catch(() => {
        setIsSetupMode(false);
      });
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await login(username, password);
    } catch (err: any) {
      setError(err.message || "Login failed");
    }
  };

  const handleSetup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (setupData.password !== setupData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    if (setupData.password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    try {
      const response = await apiClient<{
        access_token: string;
        token_type: string;
        user: any;
      }>("/api/auth/setup", {
        method: "POST",
        body: JSON.stringify({
          username: setupData.username,
          email: setupData.email,
          password: setupData.password,
        }),
      });
      localStorage.setItem("token", response.access_token);
      localStorage.setItem("user", JSON.stringify(response.user));
      navigate("/");
    } catch (err: any) {
      setError(err.message || "Setup failed");
    }
  };

  if (isSetupMode) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-6">
          <h1 className="mb-4 text-2xl font-semibold text-slate-100">
            Setup Admin Account
          </h1>
          <p className="mb-6 text-sm text-slate-400">
            Create the first admin account to get started.
          </p>
          {error && (
            <div className="mb-4 rounded-lg bg-red-900/50 p-3 text-sm text-red-200">
              {error}
            </div>
          )}
          <form onSubmit={handleSetup} className="space-y-4">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Username
              </label>
              <input
                type="text"
                required
                minLength={3}
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
                value={setupData.username}
                onChange={(e) =>
                  setSetupData((prev) => ({ ...prev, username: e.target.value }))
                }
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Email
              </label>
              <input
                type="email"
                required
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
                value={setupData.email}
                onChange={(e) =>
                  setSetupData((prev) => ({ ...prev, email: e.target.value }))
                }
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Password
              </label>
              <input
                type="password"
                required
                minLength={8}
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
                value={setupData.password}
                onChange={(e) =>
                  setSetupData((prev) => ({ ...prev, password: e.target.value }))
                }
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Confirm Password
              </label>
              <input
                type="password"
                required
                minLength={8}
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
                value={setupData.confirmPassword}
                onChange={(e) =>
                  setSetupData((prev) => ({
                    ...prev,
                    confirmPassword: e.target.value,
                  }))
                }
              />
            </div>
            <button
              type="submit"
              className="w-full rounded-lg bg-green-600 px-4 py-2 font-medium text-white hover:bg-green-700"
            >
              Create Admin Account
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950">
      <div className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-6">
        <h1 className="mb-4 text-2xl font-semibold text-slate-100">
          QuantVault Login
        </h1>
        {error && (
          <div className="mb-4 rounded-lg bg-red-900/50 p-3 text-sm text-red-200">
            {error}
          </div>
        )}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Username
            </label>
            <input
              type="text"
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Password
            </label>
            <input
              type="password"
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button
            type="submit"
            className="w-full rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
          >
            Login
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-slate-400">
          Don't have an account?{" "}
          <Link to="/register" className="text-blue-400 hover:text-blue-300">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}

