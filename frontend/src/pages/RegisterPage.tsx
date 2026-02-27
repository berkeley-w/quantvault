import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function RegisterPage() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const { register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    if (form.password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    if (form.username.length < 3) {
      setError("Username must be at least 3 characters");
      return;
    }
    try {
      await register(form.username, form.email, form.password);
    } catch (err: any) {
      setError(err.message || "Registration failed");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950">
      <div className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-6">
        <h1 className="mb-4 text-2xl font-semibold text-slate-100">
          Register
        </h1>
        {error && (
          <div className="mb-4 rounded-lg bg-red-900/50 p-3 text-sm text-red-200">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Username
            </label>
            <input
              type="text"
              required
              minLength={3}
              maxLength={64}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
              value={form.username}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, username: e.target.value }))
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
              value={form.email}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, email: e.target.value }))
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
              value={form.password}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, password: e.target.value }))
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
              value={form.confirmPassword}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, confirmPassword: e.target.value }))
              }
            />
          </div>
          <button
            type="submit"
            className="w-full rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
          >
            Register
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-slate-400">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-400 hover:text-blue-300">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}

