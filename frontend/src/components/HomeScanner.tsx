"use client";

import React, { useState, useEffect, useRef } from "react";
import { useI18n } from "../i18n/context";
import { VerdictBanner, AnalyzeResult } from "./VerdictBanner";
import { ActionStateSelector, UserActionState } from "./ActionStateSelector";
import { ActionChecklist } from "./ActionChecklist";
import { QRScannerModal } from "./QRScannerModal";
import { ApkVerdictCard, ApkAnalyzeResult } from "./ApkVerdictCard";
import {
  Clipboard,
  QrCode,
  Search,
  RotateCcw,
  Share2,
  AlertCircle,
  Loader2,
  CheckCircle2,
  Image as ImageIcon,
  Package,
  XCircle,
  RefreshCw
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
  const [showQRModal, setShowQRModal] = useState<boolean>(false);
  const [ocrLoading, setOcrLoading] = useState<boolean>(false);
  const [ocrProgress, setOcrProgress] = useState<string>("");
  const [ocrSuccessNotice, setOcrSuccessNotice] = useState<string | null>(null);
  const [lastInputType, setLastInputType] = useState<"text" | "url" | "qr">("text");

  // APK Scanning States
  const [apkLoading, setApkLoading] = useState<boolean>(false);
  const [apkProgress, setApkProgress] = useState<string>("");
  const [apkResult, setApkResult] = useState<ApkAnalyzeResult | null>(null);

  // Loading States & Timeout Handling
  const [isSlowChecking, setIsSlowChecking] = useState<boolean>(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const slowTimerRef = useRef<NodeJS.Timeout | null>(null);
  const timeoutTimerRef = useRef<NodeJS.Timeout | null>(null);

  const screenshotInputRef = useRef<HTMLInputElement | null>(null);
  const apkInputRef = useRef<HTMLInputElement | null>(null);

  // 1. Detect Web Share Target query params on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const sharedText = params.get("text") || params.get("url") || params.get("title");
      if (sharedText) {
        setContent(sharedText);
        setShareReceived(true);
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    }
  }, []);

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      if (slowTimerRef.current) clearTimeout(slowTimerRef.current);
      if (timeoutTimerRef.current) clearTimeout(timeoutTimerRef.current);
      if (abortControllerRef.current) abortControllerRef.current.abort();
    };
  }, []);

  // 2. Paste from clipboard helper
  const handlePaste = async () => {
    try {
      if (navigator.clipboard && navigator.clipboard.readText) {
        const text = await navigator.clipboard.readText();
        if (text) {
          setContent(text);
          setError(null);
          setOcrSuccessNotice(null);
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
    if (abortControllerRef.current) abortControllerRef.current.abort();
    if (slowTimerRef.current) clearTimeout(slowTimerRef.current);
    if (timeoutTimerRef.current) clearTimeout(timeoutTimerRef.current);
    setIsSlowChecking(false);
    setContent("");
    setResult(null);
    setApkResult(null);
    setError(null);
    setShareReceived(false);
    setOcrSuccessNotice(null);
    setOcrProgress("");
    setOcrLoading(false);
    setApkLoading(false);
    setApkProgress("");
    setUserActionState("not_acted");
    setActionCodes([]);
    setLastInputType("text");
    if (onReset) onReset();
  };

  // 4. Central analyze routine supporting text, url, or qr
  const executeAnalyze = async (rawContent: string, explicitInputType?: "text" | "url" | "qr") => {
    const trimmed = rawContent.trim();
    if (!trimmed) {
      setError("Please enter, paste, or scan a message, link, or QR code.");
      return;
    }

    setLoading(true);
    setIsSlowChecking(false);
    setError(null);
    setOcrSuccessNotice(null);
    setApkResult(null);

    // Setup 8s slow alert and 15s timeout
    const controller = new AbortController();
    abortControllerRef.current = controller;

    slowTimerRef.current = setTimeout(() => {
      setIsSlowChecking(true);
    }, 8000);

    timeoutTimerRef.current = setTimeout(() => {
      controller.abort();
      setLoading(false);
      setIsSlowChecking(false);
      setError("Analysis timed out. Please check your connection and tap Retry.");
    }, 15000);

    let inputType: "text" | "url" | "qr" = explicitInputType || lastInputType || "text";
    if (!explicitInputType) {
      if (
        trimmed.startsWith("http://") ||
        trimmed.startsWith("https://") ||
        trimmed.startsWith("www.") ||
        trimmed.includes(".xyz") ||
        trimmed.includes(".top") ||
        trimmed.includes(".click") ||
        trimmed.includes(".site")
      ) {
        inputType = "url";
      } else if (
        trimmed.startsWith("upi://") ||
        trimmed.includes("upi://pay") ||
        (trimmed.includes("pa=") && trimmed.includes("@"))
      ) {
        inputType = "qr";
      }
    }

    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (typeof window !== "undefined") {
        const token = localStorage.getItem("scamshield_token");
        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }
      }

      const response = await fetch("/api/analyze", {
        method: "POST",
        headers,
        signal: controller.signal,
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
      if (err.name === "AbortError") {
        return; // Handled by timeout
      }
      setError(err.message || "Network error. Please check your connection.");
    } finally {
      if (slowTimerRef.current) clearTimeout(slowTimerRef.current);
      if (timeoutTimerRef.current) clearTimeout(timeoutTimerRef.current);
      setLoading(false);
      setIsSlowChecking(false);
    }
  };

  // Cancel in-progress check
  const handleCancelCheck = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    if (slowTimerRef.current) clearTimeout(slowTimerRef.current);
    if (timeoutTimerRef.current) clearTimeout(timeoutTimerRef.current);
    setLoading(false);
    setIsSlowChecking(false);
    setError("Analysis cancelled.");
  };

  // 5. Handle QR scan callback
  const handleQRScan = (decodedText: string) => {
    setContent(decodedText);
    setLastInputType("qr");
    setOcrSuccessNotice(null);
    setApkResult(null);
    executeAnalyze(decodedText, "qr");
  };

  // 6. Handle Screenshot OCR upload
  const handleScreenshotUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      setError("Image size exceeds 10MB limit. Please choose a smaller screenshot.");
      if (screenshotInputRef.current) {
        screenshotInputRef.current.value = "";
      }
      return;
    }

    setOcrLoading(true);
    setOcrProgress("Preparing OCR engine...");
    setError(null);
    setOcrSuccessNotice(null);
    setResult(null);
    setApkResult(null);

    try {
      const Tesseract = (await import("tesseract.js")).default;
      setOcrProgress("Reading text from screenshot... 0%");
      const ocrResult = await Tesseract.recognize(
        file,
        "eng",
        {
          logger: (m) => {
            if (m.status === "recognizing text") {
              const pct = Math.round((m.progress || 0) * 100);
              setOcrProgress(`Reading text from screenshot... ${pct}%`);
            } else if (m.status) {
              setOcrProgress(`${m.status.replace(/_/g, " ")}...`);
            }
          },
        }
      );

      const extractedText = ocrResult?.data?.text?.trim() || "";
      if (!extractedText || extractedText.length < 3) {
        throw new Error(
          "Could not detect clear text in this screenshot. Please ensure the image is clear or type the message above."
        );
      }

      setContent(extractedText);
      setLastInputType("text");
      setOcrSuccessNotice(
        "Screenshot text extracted! Review the message in the box below, then tap 'Check for Scam' to analyze."
      );
    } catch (err: any) {
      try {
        setOcrProgress("Verifying text with server...");
        const formData = new FormData();
        formData.append("file", file);
        formData.append("language", language);

        const response = await fetch("/api/analyze/ocr", {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          if (data.extracted_text) {
            setContent(data.extracted_text);
            setLastInputType("text");
            setOcrSuccessNotice(
              "Screenshot text extracted! Review the message in the box below, then tap 'Check for Scam' to analyze."
            );
            return;
          }
        }
      } catch (fallbackErr) {
        // Fallback also failed
      }
      setError(err.message || "Failed to read text from screenshot. Please try pasting the text directly.");
    } finally {
      setOcrLoading(false);
      setOcrProgress("");
      if (screenshotInputRef.current) {
        screenshotInputRef.current.value = "";
      }
    }
  };

  // 7. Handle APK File Upload & Fine Print Loophole Inspection
  const handleApkUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 25 * 1024 * 1024) {
      setError("APK file size exceeds 25MB threshold for in-memory inspection. Please choose a smaller package.");
      if (apkInputRef.current) {
        apkInputRef.current.value = "";
      }
      return;
    }

    setApkLoading(true);
    setApkProgress("Reading APK archive in-memory...");
    setError(null);
    setResult(null);
    setApkResult(null);
    setOcrSuccessNotice(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      setApkProgress("Inspecting AndroidManifest permissions & legal fine print...");
      const response = await fetch("/api/analyze/apk", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Unable to inspect APK file. Ensure file is a valid Android package.");
      }

      const data: ApkAnalyzeResult = await response.json();
      setApkResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to inspect APK file.");
    } finally {
      setApkLoading(false);
      setApkProgress("");
      if (apkInputRef.current) {
        apkInputRef.current.value = "";
      }
    }
  };

  // 8. Handle user state transition ("What did you do?")
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
      {/* QR Scanner Modal */}
      <QRScannerModal
        isOpen={showQRModal}
        onClose={() => setShowQRModal(false)}
        onScan={handleQRScan}
      />

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

        {/* Quick Action Helper Buttons - Responsive for Small Mobile Displays */}
        <div className="flex flex-wrap items-center justify-between gap-2 mt-3">
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
            <button
              onClick={handlePaste}
              type="button"
              className="min-h-touch px-3 sm:px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs sm:text-sm font-semibold flex items-center gap-1.5 transition-colors"
            >
              <Clipboard className="w-4 h-4 text-indigo-400 shrink-0" />
              <span>{t("home.pasteButton", "Paste from Clipboard")}</span>
            </button>

            <button
              onClick={() => setShowQRModal(true)}
              type="button"
              className="min-h-touch px-3 sm:px-3.5 py-2 rounded-xl bg-indigo-950/80 hover:bg-indigo-900/80 text-indigo-300 border border-indigo-700/80 text-xs sm:text-sm font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <QrCode className="w-4 h-4 text-indigo-400 shrink-0" />
              <span>{t("home.scanQrButton", "Scan QR")}</span>
            </button>

            {/* Screenshot OCR Upload */}
            <input
              ref={screenshotInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleScreenshotUpload}
            />
            <button
              onClick={() => screenshotInputRef.current?.click()}
              type="button"
              className="min-h-touch px-3 sm:px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs sm:text-sm font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <ImageIcon className="w-4 h-4 text-amber-400 shrink-0" />
              <span>Upload Screenshot</span>
            </button>

            {/* APK File Scanner */}
            <input
              ref={apkInputRef}
              type="file"
              accept=".apk,application/vnd.android.package-archive"
              className="hidden"
              onChange={handleApkUpload}
            />
            <button
              onClick={() => apkInputRef.current?.click()}
              type="button"
              className="min-h-touch px-3 sm:px-3.5 py-2 rounded-xl bg-emerald-950/80 hover:bg-emerald-900/80 text-emerald-300 border border-emerald-700/80 text-xs sm:text-sm font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <Package className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Check APK File</span>
            </button>

            {content && (
              <button
                onClick={handleClear}
                type="button"
                className="min-h-touch px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 text-xs sm:text-sm font-semibold flex items-center gap-1 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>{t("home.clearButton", "Clear")}</span>
              </button>
            )}
          </div>
        </div>

        {/* OCR In-Progress Status Card */}
        {ocrLoading && (
          <div className="mt-3.5 p-4 rounded-xl bg-indigo-950/90 border-2 border-indigo-500/80 text-indigo-100 flex items-center gap-3 animate-pulse">
            <Loader2 className="w-6 h-6 animate-spin text-indigo-400 shrink-0" />
            <div>
              <p className="font-bold text-sm md:text-base">Reading Screenshot with AI OCR...</p>
              <p className="text-xs text-indigo-300 font-mono mt-0.5">{ocrProgress}</p>
            </div>
          </div>
        )}

        {/* APK Inspection In-Progress Status Card */}
        {apkLoading && (
          <div className="mt-3.5 p-4 rounded-xl bg-emerald-950/90 border-2 border-emerald-500/80 text-emerald-100 flex items-center gap-3 animate-pulse">
            <Loader2 className="w-6 h-6 animate-spin text-emerald-400 shrink-0" />
            <div>
              <p className="font-bold text-sm md:text-base">Inspecting APK File & Reading Fine Print...</p>
              <p className="text-xs text-emerald-300 font-mono mt-0.5">{apkProgress}</p>
            </div>
          </div>
        )}

        {/* OCR Success Banner */}
        {ocrSuccessNotice && (
          <div className="mt-3.5 p-4 rounded-xl bg-emerald-950/80 border-2 border-emerald-500 text-emerald-200 flex items-center gap-3 animate-fadeIn">
            <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
            <div className="text-sm font-semibold">
              <p>{ocrSuccessNotice}</p>
            </div>
          </div>
        )}

        {/* Error Notice with Retry Option */}
        {error && (
          <div className="mt-3.5 p-3.5 rounded-xl bg-red-950/80 border border-red-500 text-red-200 flex items-center justify-between gap-2 text-sm font-medium">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
              <span>{error}</span>
            </div>
            {content.trim() && (
              <button
                onClick={() => executeAnalyze(content, lastInputType)}
                type="button"
                className="px-3 py-1 rounded-lg bg-red-900/80 hover:bg-red-800 text-white text-xs font-bold flex items-center gap-1 shrink-0 border border-red-700"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Retry</span>
              </button>
            )}
          </div>
        )}

        {/* Slow Checking Alert (> 8 seconds) with Cancel option */}
        {isSlowChecking && loading && (
          <div className="mt-3.5 p-3 rounded-xl bg-amber-950/80 border border-amber-500 text-amber-200 flex items-center justify-between gap-3 text-xs sm:text-sm">
            <span>Still checking with threat intelligence feeds...</span>
            <button
              onClick={handleCancelCheck}
              type="button"
              className="px-2.5 py-1 rounded bg-amber-900 hover:bg-amber-800 text-amber-200 text-xs font-bold flex items-center gap-1 border border-amber-600 shrink-0"
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>Cancel</span>
            </button>
          </div>
        )}

        {/* Big Touch-Target Scan Button */}
        <div className="mt-5">
          <button
            onClick={() => {
              setOcrSuccessNotice(null);
              executeAnalyze(content, lastInputType);
            }}
            disabled={loading || ocrLoading || apkLoading || !content.trim()}
            className={`w-full min-h-[56px] py-3.5 px-6 rounded-2xl font-black text-lg md:text-xl flex items-center justify-center gap-3 transition-all shadow-lg ${
              loading || ocrLoading || apkLoading || !content.trim()
                ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
                : ocrSuccessNotice
                ? "bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white shadow-emerald-900/40 ring-4 ring-emerald-500/50 active:scale-[0.99] animate-pulse"
                : "bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white shadow-emerald-900/30 active:scale-[0.99]"
            }`}
          >
            {loading ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin text-white" />
                <span>{isSlowChecking ? "Still checking..." : t("home.analyzing", "Checking...")}</span>
              </>
            ) : ocrLoading ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin text-amber-400" />
                <span>Reading Screenshot...</span>
              </>
            ) : apkLoading ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin text-emerald-400" />
                <span>Inspecting APK Package...</span>
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

      {/* APK Security & Fine Print Loophole Verdict Card */}
      {apkResult && (
        <ApkVerdictCard result={apkResult} onReset={handleClear} />
      )}

      {/* Standard Result Verdict Card (Text, URL, QR, Screenshot) */}
      {result && !apkResult && (
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
            content={content}
            inputType={lastInputType}
          />
        </div>
      )}
    </div>
  );
}
