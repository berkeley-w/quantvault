import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { apiClient } from "../api/client";
import { User, TokenResponse } from "../types";

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });
  const navigate = useNavigate();

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    const userStr = typeof window !== "undefined" ? localStorage.getItem("user") : null;
    if (token && userStr) {
      apiClient<User>("/api/auth/me")
        .then((currentUser) => {
          setState({
            user: currentUser,
            token,
            isAuthenticated: true,
            isLoading: false,
          });
        })
        .catch(() => {
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          setState({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          });
        });
    } else {
      setState((prev) => ({ ...prev, isLoading: false }));
    }
  }, []);

  const login = async (username: string, password: string) => {
    const response = await apiClient<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    localStorage.setItem("token", response.access_token);
    localStorage.setItem("user", JSON.stringify(response.user));
    setState({
      user: response.user,
      token: response.access_token,
      isAuthenticated: true,
      isLoading: false,
    });
    navigate("/");
  };

  const register = async (username: string, email: string, password: string) => {
    const response = await apiClient<TokenResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, email, password }),
    });
    localStorage.setItem("token", response.access_token);
    localStorage.setItem("user", JSON.stringify(response.user));
    setState({
      user: response.user,
      token: response.access_token,
      isAuthenticated: true,
      isLoading: false,
    });
    navigate("/");
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
    navigate("/login");
  };

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

