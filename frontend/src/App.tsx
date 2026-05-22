import { useEffect } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import { LoginPage } from "./pages/LoginPage.tsx";
import { HomePage } from "./pages/HomePage.tsx";
import { DashboardPage } from "./pages/DashboardPage.tsx";
import { AccountDetailPage } from "./pages/AccountDetailPage.tsx";
import { TransactionPage } from "./pages/TransactionPage.tsx";
import { NavBar } from "./components/NavBar.tsx";
import {
  validateOrRefreshTokens,
  AUTH_CHANGED_EVENT,
} from "./services/auth.ts";

function App() {
  useEffect(() => {
    // Validate tokens on app load
    validateOrRefreshTokens();

    // Set up periodic token validation every 5 minutes
    const tokenCheckInterval = setInterval(
      () => {
        validateOrRefreshTokens();
      },
      5 * 60 * 1000,
    ); // 5 minutes in milliseconds

    // Also validate tokens when auth state changes (tokens saved/cleared)
    const handleAuthChanged = () => {
      validateOrRefreshTokens();
    };

    window.addEventListener(AUTH_CHANGED_EVENT, handleAuthChanged);

    return () => {
      clearInterval(tokenCheckInterval);
      window.removeEventListener(AUTH_CHANGED_EVENT, handleAuthChanged);
    };
  }, []);

  return (
    <Router>
      <NavBar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/accounts/:accountId" element={<AccountDetailPage />} />
        <Route path="/transactions/new" element={<TransactionPage />} />
      </Routes>
    </Router>
  );
}

export default App;
