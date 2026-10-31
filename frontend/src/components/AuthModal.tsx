"use client";

import React, { useState, useEffect } from "react";
import { useAuth, ScanHistoryItem } from "../context/AuthContext";
import { useI18n } from "../i18n/context";
import {
  User,
  Shield,
  Trash2,
  LogOut,
  X,
  History,
  CheckCircle,
  AlertTriangle,
  Lock,
  Sparkles,
} from "lucide-react";

export function AuthModal() {
  const { user, showAuthModal, setShowAuthModal, loginWithGoogleToken, logout, fetchHistory, deleteHistory } = useAuth();
  const { t } = useI18n();
  const [historyItems, setHistoryItems] = useState<ScanHistoryItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState<boolean>(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  useEffect(() => {
    if (showAuthModal && user) {
      loadHistory();
    }
  }, [showAuthModal, user]);

  const loadHistory = async () => {
    setLoadingHistory(true);
    const items = await fetchHistory();
    setHistoryItems(items);
    setLoadingHistory(false);
  };

  const handleDeleteHistory = async () => {
    if (!confirm("Are you sure you want to permanently erase all your scan history? (DPDP Act 2023 Right to Erasure)")) return;
    const ok = await deleteHistory();
    if (ok) {
      setHistoryItems([]);
      setActionMessage("Scan history successfully erased.");
      setTimeout(() => setActionMessage(null), 3000);
    }
  };

  if (!showAuthModal) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border-2 border-slate-700 rounded-2xl w-full max-w-lg p-6 shadow-2xl text-white max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <User className="w-6 h-6 text-indigo-400" />
            <h3 className="text-xl font-bold">
              {user ? "Your Account & History" : "Sign In (Optional)"}
            </h3>
          </div>
          <button
            onClick={() => setShowAuthModal(false)}
            aria-label="Close"
            className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto py-4 space-y-5">
          {!user ? (
            /* Guest / Not Signed In View */
            <div className="space-y-4 text-center">
              <div className="w-16 h-16 rounded-2xl bg-indigo-950/80 border border-indigo-700 mx-auto flex items-center justify-center text-indigo-400">
                <Lock className="w-8 h-8" />
              </div>

              <div>
                <h4 className="text-lg font-bold text-white">Login is Optional</h4>
                <p className="text-sm text-slate-400 mt-1 max-w-sm mx-auto">
                  Anyone can scan messages without an account. Sign in only if you want to keep track of your personal scan history across devices.
                </p>
              </div>

              {/* Demo Sign In Quick Buttons */}
              <div className="pt-2 space-y-2.5">
                <button
                  onClick={async () => {
                    await loginWithGoogleToken("dev-test-token:sub-user-demo:user.demo@example.com:Demo User");
                  }}
                  className="w-full min-h-[50px] px-4 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-bold flex items-center justify-center gap-2 shadow-md transition-colors"
                >
                  <Sparkles className="w-5 h-5 text-amber-300" />
                  <span>One-Click Sign In (User Demo)</span>
                </button>

                <button
                  onClick={async () => {
                    await loginWithGoogleToken("dev-test-token:sub-admin-demo:admin@scamshield.org:Admin Lead");
                  }}
                  className="w-full min-h-[50px] px-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl font-bold flex items-center justify-center gap-2 text-slate-200 transition-colors"
                >
                  <Shield className="w-5 h-5 text-emerald-400" />
                  <span>One-Click Sign In (Admin Demo)</span>
                </button>
              </div>

              <div className="p-3 bg-slate-950/60 rounded-xl text-xs text-slate-400 border border-slate-800">
                Google OAuth Scopes: <code>openid email profile</code> only. No personal contacts or messages are requested.
              </div>
            </div>
          ) : (
            /* Signed In User View */
            <div className="space-y-5">
              {/* Profile Card */}
              <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white">{user.email || "Signed-in User"}</span>
                    {user.role === "admin" && (
                      <span className="text-[10px] uppercase font-black px-2 py-0.5 rounded bg-emerald-600 text-white">
                        Admin
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-slate-400 block mt-0.5">
                    User ID: {user.id.slice(0, 8)}... (Zero Raw Text Stored)
                  </span>
                </div>

                <button
                  onClick={logout}
                  className="min-h-touch px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-red-950/80 hover:text-red-400 text-xs font-bold flex items-center gap-1 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Sign Out</span>
                </button>
              </div>

              {actionMessage && (
                <div className="p-3 rounded-lg bg-emerald-950 border border-emerald-500 text-emerald-200 text-xs font-bold text-center">
                  {actionMessage}
                </div>
              )}

              {/* Scan History Section */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-sm text-slate-300 flex items-center gap-1.5">
                    <History className="w-4 h-4 text-indigo-400" />
                    <span>Personal Scan History (Metadata Only)</span>
                  </h4>

                  {historyItems.length > 0 && (
                    <button
                      onClick={handleDeleteHistory}
                      className="text-xs text-red-400 hover:text-red-300 font-bold flex items-center gap-1"
                      title="Permanently erase history"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Erase All</span>
                    </button>
                  )}
                </div>

                {loadingHistory ? (
                  <p className="text-xs text-slate-500 text-center py-4">Loading your scan records...</p>
                ) : historyItems.length === 0 ? (
                  <div className="bg-slate-950/50 rounded-xl p-6 text-center text-slate-500 text-xs">
                    No scan history yet. Scan messages while logged in to view your threat logs here.
                  </div>
                ) : (
                  <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                    {historyItems.map((item) => (
                      <div
                        key={item.id}
                        className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between text-xs"
                      >
                        <div>
                          <div className="flex items-center gap-1.5 font-bold">
                            <span
                              className={`w-2 h-2 rounded-full ${
                                item.risk_level === "critical"
                                  ? "bg-red-500"
                                  : item.risk_level === "high"
                                  ? "bg-orange-500"
                                  : item.risk_level === "medium"
                                  ? "bg-amber-500"
                                  : "bg-emerald-500"
                              }`}
                            />
                            <span className="text-white">{t(`categories.${item.category}`, item.category)}</span>
                          </div>
                          <span className="text-slate-500 text-[11px] block mt-0.5">
                            {new Date(item.created_at).toLocaleDateString()} • {Math.round(item.risk_score * 100)}% Risk
                          </span>
                        </div>

                        <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                          {item.input_type}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

