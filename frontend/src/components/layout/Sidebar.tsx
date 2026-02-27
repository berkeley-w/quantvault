import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FileText,
  Briefcase,
  Shield,
  Building2,
  Users,
  Ban,
  ClipboardList,
  BarChart3,
  LogOut,
  User as UserIcon,
} from "lucide-react";
import type { AuthUser } from "../../types";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/blotter", label: "Blotter", icon: FileText },
  { to: "/holdings", label: "Holdings", icon: Briefcase },
  { to: "/compliance", label: "Compliance", icon: Shield },
  { to: "/securities", label: "Securities", icon: Building2 },
  { to: "/restricted", label: "Restricted", icon: Ban },
  { to: "/audit", label: "Audit Log", icon: ClipboardList },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
];

interface SidebarProps {
  user: AuthUser;
  onLogout: () => void;
}

export function Sidebar({ user, onLogout }: SidebarProps) {
  return (
    <aside className="flex h-screen w-64 flex-col border-r border-slate-800 bg-slate-900">
      <div className="px-4 py-4 text-lg font-semibold text-green-400">
        QuantVault
      </div>
      <nav className="flex-1 space-y-1 px-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                [
                  "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium",
                  "text-slate-300 hover:bg-slate-800 hover:text-white",
                  isActive ? "bg-slate-800 text-white border-l-2 border-green-400" : "",
                ].join(" ")
              }
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
        {user.role === "admin" && (
          <NavLink
            to="/admin/users"
            className={({ isActive }) =>
              [
                "mt-4 flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium",
                "text-slate-300 hover:bg-slate-800 hover:text-white",
                isActive ? "bg-slate-800 text-white border-l-2 border-green-400" : "",
              ].join(" ")
            }
          >
            <Users className="h-4 w-4" />
            <span>Traders</span>
          </NavLink>
        )}
      </nav>
      <div className="border-t border-slate-800 px-4 py-3 text-xs text-slate-300">
        <div className="mb-2 flex items-center gap-2">
          <UserIcon className="h-4 w-4 text-slate-400" />
          <div>
            <div className="font-semibold text-slate-100">{user.username}</div>
            <div className="text-[10px] uppercase tracking-wide text-slate-500">
              {user.role}
            </div>
          </div>
        </div>
        <button
          type="button"
          onClick={onLogout}
          className="flex w-full items-center justify-center gap-2 rounded-md border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-100 hover:bg-slate-800"
        >
          <LogOut className="h-3 w-3" />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );
}

