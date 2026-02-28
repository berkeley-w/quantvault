import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/layout/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { BlotterPage } from "./pages/BlotterPage";
import { HoldingsPage } from "./pages/HoldingsPage";
import { CompliancePage } from "./pages/CompliancePage";
import { SecuritiesPage } from "./pages/SecuritiesPage";
import { RestrictedPage } from "./pages/RestrictedPage";
import { AuditPage } from "./pages/AuditPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { TechnicalAnalysisPage } from "./pages/TechnicalAnalysisPage";
import { SignalsPage } from "./pages/SignalsPage";
import { StrategiesPage } from "./pages/StrategiesPage";
import { RiskPage } from "./pages/RiskPage";
import { AuthPage } from "./pages/AuthPage";
import { UsersAdminPage } from "./pages/UsersAdminPage";
import type { TokenResponse } from "./types";

function App() {
  const [auth, setAuth] = useState<TokenResponse | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const token = window.localStorage.getItem("authToken");
    const userRaw = window.localStorage.getItem("authUser");
    if (!token || !userRaw) return;
    try {
      const user = JSON.parse(userRaw);
      setAuth({
        access_token: token,
        token_type: "bearer",
        user,
      });
    } catch {
      // ignore parse errors and treat as unauthenticated
    }
  }, []);

  const handleLogout = () => {
    if (typeof window !== "undefined") {
      window.localStorage.removeItem("authToken");
      window.localStorage.removeItem("authUser");
    }
    setAuth(null);
  };

  if (!auth) {
    return (
      <AuthPage
        onAuthenticated={(payload) => {
          if (typeof window !== "undefined") {
            window.localStorage.setItem("authToken", payload.access_token);
            window.localStorage.setItem(
              "authUser",
              JSON.stringify(payload.user)
            );
          }
          setAuth(payload);
        }}
      />
    );
  }

  return (
    <Routes>
      <Route element={<Layout auth={auth} onLogout={handleLogout} />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/blotter" element={<BlotterPage />} />
        <Route path="/holdings" element={<HoldingsPage />} />
        <Route path="/technical" element={<TechnicalAnalysisPage />} />
        <Route path="/signals" element={<SignalsPage />} />
        <Route path="/strategies" element={<StrategiesPage />} />
        <Route path="/risk" element={<RiskPage />} />
        <Route path="/compliance" element={<CompliancePage />} />
        <Route path="/securities" element={<SecuritiesPage />} />
        <Route path="/traders" element={<UsersAdminPage />} />
        <Route path="/restricted" element={<RestrictedPage />} />
        <Route path="/audit" element={<AuditPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/admin/users" element={<UsersAdminPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;

