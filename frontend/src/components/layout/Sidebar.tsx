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
} from "lucide-react";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/blotter", label: "Blotter", icon: FileText },
  { to: "/holdings", label: "Holdings", icon: Briefcase },
  { to: "/compliance", label: "Compliance", icon: Shield },
  { to: "/securities", label: "Securities", icon: Building2 },
  { to: "/traders", label: "Traders", icon: Users },
  { to: "/restricted", label: "Restricted", icon: Ban },
  { to: "/audit", label: "Audit Log", icon: ClipboardList },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
];

export function Sidebar() {
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
      </nav>
    </aside>
  );
}

