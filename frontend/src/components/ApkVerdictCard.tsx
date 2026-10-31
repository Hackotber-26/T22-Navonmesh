"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  FileWarning,
  Lock,
  Phone,
  Trash2,
  Share2,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Info
} from "lucide-react";

export interface DangerousPermission {
  key: string;
  name: string;
  risk_level: string;
  description: string;
  abuse_scenario: string;
}

export interface FinePrintLoophole {
  category: string;
  title: string;
  risk_level: string;
  explanation: string;
  excerpt: string;
}

export interface ApkAnalyzeResult {
  incident_id?: string;
  app_name: string;
  package_name: string;
  risk_score: number;
  risk_level: "low" | "medium" | "high" | "critical";
  category: string;
  verdict_summary: string;
  dangerous_permissions: DangerousPermission[];
  fine_print_loopholes: FinePrintLoophole[];
  action_codes: string[];
}

interface ApkVerdictCardProps {
  result: ApkAnalyzeResult;
  onReset?: () => void;
}

export function ApkVerdictCard({ result, onReset }: ApkVerdictCardProps) {
  const [expandedLoophole, setExpandedLoophole] = useState<number | null>(0);
  const [copiedAction, setCopiedAction] = useState<boolean>(false);

  const isCritical = result.risk_level === "critical" || result.risk_level === "high";

  const handleShareWarning = async () => {
    const text = `🚨 SCAM ALERT: Be careful of "${result.app_name}" (${result.package_name}). It has dangerous permissions and predatory terms. Check before installing: https://scamshield.org`;
    if (navigator.share) {
      try {
        await navigator.share({ title: "APK Scam Alert", text, url: "https://scamshield.org" });
      } catch (e) {
        // Dismissed
      }
    } else if (navigator.clipboard) {
      await navigator.clipboard.writeText(text);
      setCopiedAction(true);
      setTimeout(() => setCopiedAction(false), 2500);
    }
  };

  return (
    <div className="w-full space-y-5 animate-fadeIn">
      {/* Top Verdict Banner */}
      <div
        className={`border-2 rounded-2xl p-5 md:p-6 shadow-xl ${
          isCritical
            ? "bg-red-950/70 border-red-500/80 text-red-100"
            : result.risk_level === "medium"
            ? "bg-amber-950/70 border-amber-500/80 text-amber-100"
            : "bg-emerald-950/70 border-emerald-500/80 text-emerald-100"
        }`}
      >
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div
              className={`w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 border ${
                isCritical
                  ? "bg-red-500/20 text-red-400 border-red-500/40"
                  : result.risk_level === "medium"
                  ? "bg-amber-500/20 text-amber-400 border-amber-500/40"
                  : "bg-emerald-500/20 text-emerald-400 border-emerald-500/40"
              }`}
            >
              {isCritical ? (
                <ShieldAlert className="w-8 h-8" />
              ) : result.risk_level === "medium" ? (
                <AlertTriangle className="w-8 h-8" />
              ) : (
                <ShieldCheck className="w-8 h-8" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase font-extrabold tracking-wider px-2.5 py-0.5 rounded-full bg-black/30 border border-white/10">
                  {result.category.replace(/_/g, " ")}
                </span>
                <span className="text-xs font-mono text-slate-300">
                  Risk Score: {(result.risk_score * 100).toFixed(0)}%
                </span>
              </div>
              <h2 className="text-xl sm:text-2xl font-black mt-1 text-white">
                {isCritical ? "DANGER: HIGH RISK / MALICIOUS APK" : result.risk_level === "medium" ? "SUSPICIOUS APK FILE" : "VERIFIED SAFE APK"}
              </h2>
            </div>
          </div>

          <div className="text-left sm:text-right shrink-0">
            <span className="text-xs text-slate-300 block">Package Identifier</span>
            <code className="text-xs font-mono text-amber-300 font-bold break-all">
              {result.package_name}
            </code>
          </div>
        </div>

        <p className="mt-3.5 text-sm sm:text-base text-slate-200 leading-relaxed font-medium">
          {result.verdict_summary}
        </p>
      </div>

      {/* Dangerous Permissions Card */}
      {result.dangerous_permissions.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 md:p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Lock className="w-5 h-5 text-red-400" />
              <h3 className="text-lg font-bold text-white">
                Dangerous Android Permissions Detected ({result.dangerous_permissions.length})
              </h3>
            </div>
            <span className="text-xs text-red-400 font-bold uppercase tracking-wider bg-red-950/80 px-2.5 py-1 rounded-md border border-red-500/30">
              High Threat
            </span>
          </div>

          <p className="text-xs sm:text-sm text-slate-400">
            These permissions are requested in the APK&apos;s manifest and can be abused to steal banking credentials, intercept OTPs, or access personal data without your awareness:
          </p>

          <div className="space-y-3">
            {result.dangerous_permissions.map((perm) => (
              <div
                key={perm.key}
                className="bg-slate-950/70 border border-red-500/30 rounded-xl p-3.5 space-y-2"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-bold text-red-300 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
                    {perm.name}
                  </span>
                  <code className="text-[11px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                    {perm.key}
                  </code>
                </div>
                <p className="text-xs sm:text-sm text-slate-300 leading-snug">
                  {perm.description}
                </p>
                <div className="bg-red-950/50 border border-red-900/60 rounded-lg p-2 text-xs text-red-200 flex items-start gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-red-400 shrink-0 mt-0.5" />
                  <span>
                    <strong>How Scammers Abuse It:</strong> {perm.abuse_scenario}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fine Print Terms & Loopholes Warning Card */}
      {result.fine_print_loopholes.length > 0 && (
        <div className="bg-slate-900 border-2 border-amber-500/60 rounded-2xl p-5 md:p-6 space-y-4 shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileWarning className="w-5 h-5 text-amber-400" />
              <h3 className="text-lg font-bold text-amber-300">
                Fine Print Loopholes & Predatory Clauses ({result.fine_print_loopholes.length})
              </h3>
            </div>
            <span className="text-xs font-bold uppercase tracking-wider text-amber-400 bg-amber-950/80 px-2.5 py-1 rounded-md border border-amber-500/30">
              Trap Alert
            </span>
          </div>

          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            We extracted and analyzed the legal terms and privacy strings inside this APK. The following loopholes and predatory clauses were found that can exploit users under Indian law:
          </p>

          <div className="space-y-3">
            {result.fine_print_loopholes.map((loophole, idx) => {
              const isExpanded = expandedLoophole === idx;
              return (
                <div
                  key={idx}
                  className="bg-slate-950 border border-amber-500/30 rounded-xl p-4 space-y-2 transition-all"
                >
                  <div
                    onClick={() => setExpandedLoophole(isExpanded ? null : idx)}
                    className="flex items-center justify-between cursor-pointer group"
                  >
                    <span className="text-sm font-bold text-amber-200 group-hover:text-amber-100 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-amber-400" />
                      {loophole.title}
                    </span>
                    <button
                      type="button"
                      aria-label="Toggle clause excerpt"
                      className="text-slate-400 hover:text-white p-1"
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>

                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-medium">
                    {loophole.explanation}
                  </p>

                  {isExpanded && (
                    <div className="mt-2.5 pt-2 border-t border-slate-800 space-y-1.5 animate-fadeIn">
                      <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                        <Info className="w-3 h-3 text-amber-400" />
                        Exact Excerpt Extracted from APK:
                      </span>
                      <blockquote className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 italic leading-relaxed">
                        &ldquo;{loophole.excerpt}&rdquo;
                      </blockquote>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Immediate Action Checklist Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 md:p-6 space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Trash2 className="w-5 h-5 text-red-400" />
          <span>What should you do right now?</span>
        </h3>

        <div className="space-y-2.5">
          <div className="p-3 bg-red-950/40 border border-red-500/30 rounded-xl flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-red-500/20 text-red-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
              1
            </span>
            <div className="text-xs sm:text-sm">
              <strong className="text-white block">Do NOT Install / Immediately Uninstall</strong>
              <span className="text-slate-300">
                If already installed, turn off Wi-Fi/Mobile Data, go to <em>Settings &rarr; Apps</em> and uninstall this application immediately.
              </span>
            </div>
          </div>

          <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
              2
            </span>
            <div className="text-xs sm:text-sm">
              <strong className="text-white block">Revoke Accessibility & Notification Access</strong>
              <span className="text-slate-300">
                Check <em>Settings &rarr; Accessibility</em> on Android to ensure this app does not have background control of your screen.
              </span>
            </div>
          </div>

          <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
              3
            </span>
            <div className="text-xs sm:text-sm">
              <strong className="text-white block">Check Bank & UPI Transaction History</strong>
              <span className="text-slate-300">
                Log in to your bank app directly to verify no unauthorized debit or collect requests occurred.
              </span>
            </div>
          </div>

          <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
              4
            </span>
            <div className="text-xs sm:text-sm">
              <strong className="text-white block">Call 1930 Cybercrime Helpline if Debited</strong>
              <span className="text-slate-300">
                Dial 1930 immediately to freeze fraudulent transfers within the golden hour.
              </span>
            </div>
          </div>
        </div>

        {/* Quick Actions Row */}
        <div className="pt-2 flex flex-wrap items-center gap-3">
          <a
            href="tel:1930"
            className="min-h-touch px-4 py-2.5 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-sm flex items-center gap-2 shadow-lg shadow-red-900/30 transition-colors"
          >
            <Phone className="w-4 h-4" />
            <span>Call 1930 Helpline</span>
          </a>

          <button
            onClick={handleShareWarning}
            type="button"
            className="min-h-touch px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold text-sm flex items-center gap-2 transition-colors"
          >
            <Share2 className="w-4 h-4 text-indigo-400" />
            <span>{copiedAction ? "Copied Warning!" : "Warn Family on WhatsApp"}</span>
          </button>

          <Link
            href="/thank-you"
            className="min-h-touch px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-emerald-400 border border-slate-700 font-bold text-sm flex items-center gap-2 transition-colors"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>I Finished These Steps</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
