"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useI18n, SUPPORTED_LANGUAGES } from "../i18n/context";
import { ShieldCheck, Globe, Type, Lock, BarChart3, Scale, FileText } from "lucide-react";

export function Header() {
  const { language, setShowPicker, textSize, toggleTextSize, t } = useI18n();
  const pathname = usePathname();

  const currentLang = SUPPORTED_LANGUAGES.find((l) => l.code === language);
  const isStatsPage = pathname === "/stats";
  const isPrivacyPage = pathname === "/privacy";
  const isTermsPage = pathname === "/terms";

  return (
    <header className="w-full bg-slate-900/90 border-b border-slate-800 sticky top-0 z-40 backdrop-blur-md">
      <div className="max-w-5xl mx-auto px-3 sm:px-4 py-2.5 sm:py-3 flex items-center justify-between gap-2">
        {/* App Title & Logo */}
        <Link
          href="/"
          className="flex items-center space-x-2.5 sm:space-x-3 group min-h-touch shrink-0"
          aria-label="ScamShield India Home - Scam and Fraud Detection"
        >
          <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-xl overflow-hidden bg-slate-800 border border-slate-700 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform shrink-0">
            <img
              src="/logo.png"
              alt="ScamShield India - Cybersecurity and Scam Prevention Logo"
              width={44}
              height={44}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.currentTarget.style.display = "none";
              }}
            />
          </div>
          <div>
            <h1 className="text-lg sm:text-xl md:text-2xl font-black tracking-tight text-white flex items-center gap-1.5 leading-tight">
              ScamShield India
            </h1>
            <span className="hidden sm:inline-flex items-center gap-1 text-[11px] text-emerald-400 font-medium leading-none">
              <Lock className="w-2.5 h-2.5" />
              {t("app.privacy_badge", "100% Private • Zero Data Stored")}
            </span>
          </div>
        </Link>

        {/* Navigation, Accessibility & Language Controls */}
        <div className="flex items-center space-x-1.5 sm:space-x-2">
          {/* Stats Link */}
          {!isStatsPage ? (
            <Link
              href="/stats"
              title="Threat Dashboard"
              aria-label="View Threat Statistics Dashboard"
              className="min-h-touch min-w-touch px-2.5 sm:px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1.5 font-bold text-xs sm:text-sm shadow-sm transition-colors"
            >
              <BarChart3 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span className="hidden md:inline">Stats</span>
            </Link>
          ) : (
            <Link
              href="/"
              title="Scanner"
              aria-label="Return to Main Scam Scanner"
              className="min-h-touch min-w-touch px-2.5 sm:px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1.5 font-bold text-xs sm:text-sm shadow-sm transition-colors"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
              <span className="hidden md:inline">Scanner</span>
            </Link>
          )}

          {/* Privacy Policy Link in Navbar */}
          <Link
            href="/privacy"
            title="Privacy Policy (DPDP Act 2023)"
            aria-label="View DPDP Act 2023 Privacy Policy"
            className={`min-h-touch min-w-touch px-2.5 sm:px-3 py-2 rounded-xl border flex items-center gap-1.5 font-bold text-xs sm:text-sm shadow-sm transition-colors ${
              isPrivacyPage
                ? "bg-slate-700 text-emerald-300 border-emerald-500/50"
                : "bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700"
            }`}
          >
            <Lock className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span className="hidden lg:inline">Privacy</span>
          </Link>

          {/* Terms & Conditions Link in Navbar */}
          <Link
            href="/terms"
            title="Terms and Conditions"
            aria-label="View Terms and Conditions"
            className={`min-h-touch min-w-touch px-2.5 sm:px-3 py-2 rounded-xl border flex items-center gap-1.5 font-bold text-xs sm:text-sm shadow-sm transition-colors ${
              isTermsPage
                ? "bg-slate-700 text-indigo-300 border-indigo-500/50"
                : "bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700"
            }`}
          >
            <Scale className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
            <span className="hidden lg:inline">Terms</span>
          </Link>

          {/* Text Size Accessibility Toggle */}
          <button
            onClick={toggleTextSize}
            type="button"
            title={t("app.fontSizeToggle", "Text Size")}
            aria-label={`Toggle Font Size. Currently ${textSize === "large" ? "Large A+" : "Normal A"}`}
            className="min-h-touch min-w-touch px-2.5 sm:px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1 font-bold text-xs sm:text-sm shadow-sm"
          >
            <Type className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
            <span>{textSize === "large" ? "A+" : "A"}</span>
          </button>

          {/* Language Switcher Button */}
          <button
            onClick={() => setShowPicker(true)}
            type="button"
            aria-label={`Change Language. Current language is ${currentLang?.nativeName || "English"}`}
            title="Change Language"
            className="min-h-touch min-w-touch px-3 sm:px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs sm:text-sm shadow-md flex items-center gap-1.5 transition-colors"
          >
            <Globe className="w-3.5 h-3.5 shrink-0" />
            <span className="text-xs sm:text-sm">{currentLang?.nativeName || "Language"}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
