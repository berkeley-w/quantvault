import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/layout/Layout";
import { ProtectedRoute } from "./components/auth/ProtectedRoute";
import { DashboardPage } from "./pages/DashboardPage";
import { BlotterPage } from "./pages/BlotterPage";
import { HoldingsPage } from "./pages/HoldingsPage";
import { CompliancePage } from "./pages/CompliancePage";
import { SecuritiesPage } from "./pages/SecuritiesPage";
import { TradersPage } from "./pages/TradersPage";
import { RestrictedPage } from "./pages/RestrictedPage";
import { AuditPage } from "./pages/AuditPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<DashboardPage />} />
        <Route path="/blotter" element={<BlotterPage />} />
        <Route path="/holdings" element={<HoldingsPage />} />
        <Route path="/compliance" element={<CompliancePage />} />
        <Route path="/securities" element={<SecuritiesPage />} />
        <Route path="/traders" element={<TradersPage />} />
        <Route path="/restricted" element={<RestrictedPage />} />
        <Route path="/audit" element={<AuditPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;

