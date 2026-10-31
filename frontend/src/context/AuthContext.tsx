"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

export interface UserProfile {
  id: string;
  email: string | null;
  role: string;
  preferred_lang: string;
  created_at?: string;
}

export interface ScanHistoryItem {
  id: string;
  input_type: string;
  category: string;
  risk_level: "low" | "medium" | "high" | "critical";
  risk_score: number;
  reason_codes: string[];
  language: string;
  domain_hash: string | null;
  user_action_state: string | null;
  created_at: string;
}

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  loading: boolean;
  loginWithGoogleToken: (idToken: string) => Promise<boolean>;
  logout: () => void;
  fetchHistory: () => Promise<ScanHistoryItem[]>;
  deleteHistory: () => Promise<boolean>;
  showAuthModal: boolean;
  setShowAuthModal: (show: boolean) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [showAuthModal, setShowAuthModal] = useState<boolean>(false);

  useEffect(() => {
    const savedToken = localStorage.getItem("scamshield_token");
    if (savedToken) {
      setToken(savedToken);
      // Validate token with /api/users/me
      fetch("/api/users/me", {
        headers: { Authorization: `Bearer ${savedToken}` },
      })
        .then((res) => {
          if (res.ok) return res.json();
          throw new Error("Session expired");
        })
        .then((userData) => {
          setUser(userData);
        })
        .catch(() => {
          localStorage.removeItem("scamshield_token");
          setToken(null);
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const loginWithGoogleToken = async (idToken: string): Promise<boolean> => {
    try {
      const res = await fetch("/api/auth/google", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_token: idToken }),
      });

      if (!res.ok) return false;

      const data = await res.json();
      localStorage.setItem("scamshield_token", data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      return true;
    } catch (err) {
      console.error("Google auth error", err);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem("scamshield_token");
    setToken(null);
    setUser(null);
  };

  const fetchHistory = async (): Promise<ScanHistoryItem[]> => {
    if (!token) return [];
    try {
      const res = await fetch("/api/users/me/history", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        return await res.json();
      }
      return [];
    } catch {
      return [];
    }
  };

  const deleteHistory = async (): Promise<boolean> => {
    if (!token) return false;
    try {
      const res = await fetch("/api/users/me/history", {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      return res.ok;
    } catch {
      return false;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        loginWithGoogleToken,
        logout,
        fetchHistory,
        deleteHistory,
        showAuthModal,
        setShowAuthModal,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
