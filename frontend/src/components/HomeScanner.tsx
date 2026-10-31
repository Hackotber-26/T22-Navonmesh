"use client";

import React, { useState, useEffect } from "react";
import { useI18n } from "../i18n/context";
import { VerdictBanner, AnalyzeResult } from "./VerdictBanner";
import { ActionStateSelector, UserActionState } from "./ActionStateSelector";
import { ActionChecklist } from "./ActionChecklist";
import {
  Clipboard,
  QrCode,
  Search,
  RotateCcw,
  Share2,
  AlertCircle,
  Loader2,
} from "lucide-react";

interface HomeScannerProps {
  onAnalyzeComplete?: (result: AnalyzeResult) => void;
  onReset?: () => void;
}

export function HomeScanner({ onAnalyzeComplete, onReset }: HomeScannerProps) {
  const { t, language } = useI18n();
  const [content, setContent] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [stateLoading, setStateLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [userActionState, setUserActionState] = useState<UserActionState>("not_acted");
  const [actionCodes, setActionCodes] = useState<string[]>([]);
  const [shareReceived, setShareReceived] = useState<boolean>(false);

  // 1. Detect Web Share Target query params on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const sharedText = params.get("text") || params.get("url") || params.get("title");
      if (sharedText) {
        setContent(sharedText);
        setShareReceived(true);
        // Clean URL to prevent re-populating on page refresh
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    }
  }, []);

  // 2. Paste from clipboard helper
  const handlePaste = async () => {
    try {
      if (navigator.clipboard && navigator.clipboard.readText) {
        const text = await navigator.clipboard.readText();
        if (text) {
          setContent(text);
          setError(null);
        }
      } else {
        setError("Clipboard access not available. Please paste manually into the box.");
      }
    } catch (err) {
      setError("Please allow clipboard permission to paste.");
    }
  };

  // 3. Clear all state
  const handleClear = () => {
    setContent("");
    setResult(null);
    setError(null);
    setShareReceived(false);
    setUserActionState("not_acted");
    setActionCodes([]);
    if (onReset) onReset();
  };

  // 4. Submit scan to FastAPI backend
  const handleAnalyze = async () => {
    const trimmed = content.trim();
    if (!trimmed) {
      setError("Please enter or paste a message, link, or UPI message.");
      return;
    }

    setLoading(true);
    setError(null);

    // Determine input type heuristic
    let inputType: "text" | "url" | "qr" = "text";
    if (
      trimmed.startsWith("http://") ||
      trimmed.startsWith("https://") ||
      trimmed.includes(".xyz") ||
      trimmed.includes(".top")
    ) {
      inputType = "url";
    }

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          input_type: inputType,
          content: trimmed,
          language: language,
          user_action_state: "not_acted",
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Unable to analyze. Please try again.");
      }

      const data: AnalyzeResult = await response.json();
      setResult(data);
      setUserActionState("not_acted");
      setActionCodes(data.action_codes || []);

      if (onAnalyzeComplete) {
        onAnalyzeComplete(data);
      }
    } catch (err: any) {
      setError(err.message || "Network error. Please check your connection.");
    } finally {
      setLoading(false);
    }
  };

  // 5. Handle user state transition ("What did you do?")
  const handleActionStateChange = async (newState: UserActionState) => {
    setUserActionState(newState);

    if (!result?.incident_id) return;

    setStateLoading(true);
    try {
      const res = await fetch(`/api/incidents/${result.incident_id}/action-state`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_action_state: newState }),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.action_codes) {
          setActionCodes(data.action_codes);
        }
      }
    } catch (err) {
      console.error("Failed to update action state", err);
    } finally {
      setStateLoading(false);
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Web Share Notification Banner */}
      {shareReceived && (
        <div className="bg-indigo-950/80 border-2 border-indigo-500 rounded-xl p-3.5 flex items-center gap-3 text-indigo-200 animate-fadeIn">
          <Share2 className="w-5 h-5 text-indigo-400 shrink-0" />
          <span className="text-sm font-semibold">
            {t(
              "home.shareReceivedBanner",
              "Message received via Share. Tap 'Check for Scam' to inspect."
            )}
          </span>
        </div>
      )}

      {/* Main Input Card */}
      <div className="bg-slate-900 border-2 border-slate-800 rounded-2xl p-4 md:p-6 shadow-xl">
        <label htmlFor="messageInput" className="sr-only">
          {t("home.inputPlaceholder", "Paste message here")}
        </label>
        <textarea
          id="messageInput"
          rows={5}
          value={content}
          onChange={(e) => {
            setContent(e.target.value);
            if (error) setError(null);
          }}
          placeholder={t(
            "home.inputPlaceholder",
            "Paste message text, link, or UPI message here..."
          )}
          className="w-full p-4 rounded-xl bg-slate-800/90 border-2 border-slate-700 text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 text-base md:text-lg resize-y min-h-[140px]"
        />

        {/* Quick Action Helper Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-2.5 mt-3">
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handlePaste}
              type="button"
              className="min-h-touch px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-semibold flex items-center gap-2 transition-colors"
            >
              <Clipboard className="w-4 h-4 text-indigo-400" />
              <span>{t("home.pasteButton", "Paste from Clipboard")}</span>
            </button>

            {content && (
              <button
                onClick={handleClear}
                type="button"
                className="min-h-touch px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 text-sm font-semibold flex items-center gap-1.5 transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                <span>{t("home.clearButton", "Clear")}</span>
              </button>
            )}
          </div>
        </div>

        {/* Error Notice */}
        {error && (
          <div className="mt-3.5 p-3 rounded-xl bg-red-950/80 border border-red-500 text-red-200 flex items-center gap-2 text-sm font-medium">
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Big Touch-Target Scan Button */}
        <div className="mt-5">
          <button
            onClick={handleAnalyze}
            disabled={loading || !content.trim()}
            className={`w-full min-h-[56px] py-3.5 px-6 rounded-2xl font-black text-lg md:text-xl flex items-center justify-center gap-3 transition-all shadow-lg ${
              loading || !content.trim()
                ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
                : "bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white shadow-emerald-900/30 active:scale-[0.99]"
            }`}
          >
            {loading ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin text-white" />
                <span>{t("home.analyzing", "Analyzing for threats...")}</span>
              </>
            ) : (
              <>
                <Search className="w-6 h-6 stroke-[2.5]" />
                <span>{t("home.checkButton", "Check for Scam")}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Result Verdict Card */}
      {result && (
        <div className="space-y-6 animate-fadeIn">
          <VerdictBanner result={result} />

          {/* "What did you do?" 3-Button Step */}
          <ActionStateSelector
            currentState={userActionState}
            onStateChange={handleActionStateChange}
            isLoading={stateLoading}
          />

          {/* Ordered Action Checklist & 1930 / WhatsApp helpers */}
          <ActionChecklist
            incidentId={result.incident_id}
            category={result.category}
            riskLevel={result.risk_level}
            actionCodes={actionCodes.length > 0 ? actionCodes : result.action_codes}
            userActionState={userActionState}
            extractedDomains={result.extracted_domains}
            reasonCodes={result.reason_codes}
          />
        </div>
      )}
    </div>
  );
}
