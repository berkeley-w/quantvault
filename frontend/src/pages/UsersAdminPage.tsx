import { FormEvent, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { apiClient, ApiError } from "../api/client";
import type { AuthUser } from "../types";

export function UsersAdminPage() {
  const [users, setUsers] = useState<AuthUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState<number | null>(null);
  const [createForm, setCreateForm] = useState({
    username: "",
    email: "",
    password: "",
    role: "trader",
  });

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const data = await apiClient<AuthUser[]>("/api/v1/auth/users");
        if (!cancelled) {
          setUsers(data);
        }
      } catch (err: any) {
        const message =
          err instanceof ApiError && err.status === 403
            ? "You do not have permission to view users."
            : err?.message || "Failed to load users";
        toast.error(message);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const updateLocalUser = (id: number, patch: Partial<AuthUser>) => {
    setUsers((prev) => prev.map((u) => (u.id === id ? { ...u, ...patch } : u)));
  };

  const handleFieldChange = (
    id: number,
    field: keyof Pick<AuthUser, "username" | "email" | "role" | "is_active">,
    value: any
  ) => {
    updateLocalUser(id, { [field]: value } as Partial<AuthUser>);
  };

  const handleSave = async (user: AuthUser) => {
    setSavingId(user.id);
    try {
      const updated = await apiClient<AuthUser>(`/api/v1/auth/users/${user.id}`, {
        method: "PUT",
        body: JSON.stringify({
          username: user.username,
          email: user.email,
          role: user.role,
          is_active: user.is_active,
        }),
      });
      updateLocalUser(user.id, updated);
      toast.success("User updated");
    } catch (err: any) {
      toast.error(err?.message || "Failed to update user");
    } finally {
      setSavingId(null);
    }
  };

  const handleResetPassword = async (user: AuthUser) => {
    const pwd = window.prompt(`Enter a new password for ${user.username}`);
    if (!pwd) return;
    setSavingId(user.id);
    try {
      await apiClient<AuthUser>(`/api/v1/auth/users/${user.id}`, {
        method: "PUT",
        body: JSON.stringify({ password: pwd }),
      });
      toast.success("Password reset");
    } catch (err: any) {
      toast.error(err?.message || "Failed to reset password");
    } finally {
      setSavingId(null);
    }
  };

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    if (!createForm.username || !createForm.email || !createForm.password) {
      toast.error("Username, email, and password are required");
      return;
    }
    try {
      const newUser = await apiClient<AuthUser>("/api/v1/auth/users", {
        method: "POST",
        body: JSON.stringify({
          username: createForm.username,
          email: createForm.email,
          password: createForm.password,
          role: createForm.role,
        }),
      });
      setUsers((prev) => [...prev, newUser]);
      setCreateForm({
        username: "",
        email: "",
        password: "",
        role: "trader",
      });
      toast.success("User created");
    } catch (err: any) {
      toast.error(err?.message || "Failed to create user");
    }
  };

  if (loading) {
    return <div className="text-sm text-slate-300">Loading users...</div>;
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-slate-50">User administration</h1>
        <p className="text-sm text-slate-400">
          View, create, and edit login details for all users on this QuantVault instance.
        </p>
      </div>

      <form
        onSubmit={handleCreate}
        className="rounded-lg border border-slate-800 bg-slate-900 p-4 text-xs text-slate-200"
      >
        <h2 className="mb-3 text-sm font-semibold text-slate-100">
          Create new user account
        </h2>
        <div className="grid gap-3 md:grid-cols-4">
          <div>
            <label className="mb-1 block text-[11px] text-slate-400">
              Username
            </label>
            <input
              className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs"
              value={createForm.username}
              onChange={(e) =>
                setCreateForm((f) => ({ ...f, username: e.target.value }))
              }
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-[11px] text-slate-400">Email</label>
            <input
              type="email"
              className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs"
              value={createForm.email}
              onChange={(e) =>
                setCreateForm((f) => ({ ...f, email: e.target.value }))
              }
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-[11px] text-slate-400">
              Password
            </label>
            <input
              type="password"
              className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs"
              value={createForm.password}
              onChange={(e) =>
                setCreateForm((f) => ({ ...f, password: e.target.value }))
              }
              required
              minLength={8}
            />
          </div>
          <div>
            <label className="mb-1 block text-[11px] text-slate-400">Role</label>
            <select
              className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs"
              value={createForm.role}
              onChange={(e) =>
                setCreateForm((f) => ({ ...f, role: e.target.value }))
              }
            >
              <option value="trader">trader</option>
              <option value="admin">admin</option>
            </select>
          </div>
        </div>
        <div className="mt-3">
          <button
            type="submit"
            className="rounded bg-green-500 px-4 py-1.5 text-xs font-semibold text-slate-950 hover:bg-green-400"
          >
            Create user
          </button>
        </div>
      </form>

      <div className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-900">
        <table className="min-w-full text-left text-xs">
          <thead className="bg-slate-900/70 text-slate-400">
            <tr>
              <th className="px-4 py-2">ID</th>
              <th className="px-4 py-2">Username</th>
              <th className="px-4 py-2">Email</th>
              <th className="px-4 py-2">Role</th>
              <th className="px-4 py-2">Active</th>
              <th className="px-4 py-2">Created</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr
                key={user.id}
                className="border-t border-slate-800 text-slate-200 hover:bg-slate-900/70"
              >
                <td className="px-4 py-2 text-slate-500">{user.id}</td>
                <td className="px-4 py-2">
                  <input
                    className="w-full rounded border border-slate-700 bg-slate-900 px-2 py-1 text-xs"
                    value={user.username}
                    onChange={(e) =>
                      handleFieldChange(user.id, "username", e.target.value)
                    }
                  />
                </td>
                <td className="px-4 py-2">
                  <input
                    className="w-full rounded border border-slate-700 bg-slate-900 px-2 py-1 text-xs"
                    value={user.email}
                    onChange={(e) =>
                      handleFieldChange(user.id, "email", e.target.value)
                    }
                  />
                </td>
                <td className="px-4 py-2">
                  <select
                    className="w-full rounded border border-slate-700 bg-slate-900 px-2 py-1 text-xs"
                    value={user.role}
                    onChange={(e) =>
                      handleFieldChange(user.id, "role", e.target.value)
                    }
                  >
                    <option value="admin">admin</option>
                    <option value="trader">trader</option>
                  </select>
                </td>
                <td className="px-4 py-2">
                  <input
                    type="checkbox"
                    className="h-3 w-3 accent-green-500"
                    checked={user.is_active}
                    onChange={(e) =>
                      handleFieldChange(user.id, "is_active", e.target.checked)
                    }
                  />
                </td>
                <td className="px-4 py-2 text-slate-500">
                  {new Date(user.created_at).toLocaleString()}
                </td>
                <td className="px-4 py-2 space-x-2">
                  <button
                    type="button"
                    onClick={() => handleSave(user)}
                    disabled={savingId === user.id}
                    className="rounded bg-green-500 px-3 py-1 text-xs font-semibold text-slate-950 hover:bg-green-400 disabled:opacity-60"
                  >
                    {savingId === user.id ? "Saving..." : "Save"}
                  </button>
                  <button
                    type="button"
                    onClick={() => handleResetPassword(user)}
                    disabled={savingId === user.id}
                    className="rounded border border-slate-600 px-3 py-1 text-xs font-semibold text-slate-100 hover:bg-slate-800 disabled:opacity-60"
                  >
                    Reset password
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

