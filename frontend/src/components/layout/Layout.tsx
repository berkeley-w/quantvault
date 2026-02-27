import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import type { TokenResponse } from "../../types";

interface LayoutProps {
  auth: TokenResponse;
  onLogout: () => void;
}

export function Layout({ auth, onLogout }: LayoutProps) {
  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <Sidebar user={auth.user} onLogout={onLogout} />
      <main className="flex-1 overflow-y-auto bg-slate-950">
        <div className="mx-auto max-w-7xl p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

