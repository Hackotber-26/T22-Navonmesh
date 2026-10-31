"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useI18n, SUPPORTED_LANGUAGES } from "../i18n/context";
import { useAuth } from "../context/AuthContext";
import { ShieldCheck, Globe, Type, Lock, BarChart3, User as UserIcon } from "lucide-react";

export function Header() {
  const { language, setShowPicker, textSize, toggleTextSize, t } = useI18n();
  const { user, setShowAuthModal } = useAuth();
  const pathname = usePathname();

  const currentLang = SUPPORTED_LANGUAGES.find((l) => l.code === language);
  const isStatsPage = pathname === "/stats";

  return (
    <header className="w-full bg-slate-900/90 border-b border-slate-800 sticky top-0 z-40 backdrop-blur-md">
      <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* App Title & Shield */}
        <Link href="/" className="flex items-center space-x-3 group">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-emerald-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <ShieldCheck className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-black tracking-tight text-white flex items-center gap-2">
              {t("app.title", "ScamShield India")}
            </h1>
            <span className="hidden sm:inline-flex items-center gap-1 text-xs text-emerald-400 font-medium">
              <Lock className="w-3 h-3" />
              {t("app.privacy_badge", "100% Private • Zero Data Stored")}
            </span>
          </div>
        </Link>

        {/* Accessibility, Stats & Language Controls */}
        <div className="flex items-center space-x-2">
          {/* Stats Dashboard Link */}
          {!isStatsPage ? (
            <Link
              href="/stats"
              title="Threat Dashboard"
              aria-label="View Threat Dashboard"
              className="min-h-touch min-w-touch px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1.5 font-bold text-sm shadow-sm transition-colors"
            >
              <BarChart3 className="w-4 h-4 text-emerald-400" />
              <span className="hidden md:inline">Threat Stats</span>
            </Link>
          ) : (
            <Link
              href="/"
              title="Scanner"
              aria-label="Back to Scanner"
              className="min-h-touch min-w-touch px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1.5 font-bold text-sm shadow-sm transition-colors"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span className="hidden md:inline">Scanner</span>
            </Link>
          )}

          {/* Account / Sign-in */}
          <button
            onClick={() => setShowAuthModal(true)}
            aria-label="User Account and Scan History"
            className="min-h-touch min-w-touch px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1.5 font-bold text-sm shadow-sm transition-colors"
          >
            <UserIcon className="w-4 h-4 text-indigo-400" />
            <span className="hidden sm:inline">
              {user ? user.email?.split("@")[0] || "Account" : "Sign In"}
            </span>
          </button>

          {/* Text Size Accessibility Toggle */}
          <button
            onClick={toggleTextSize}
            title={t("app.fontSizeToggle", "Text Size")}
            aria-label="Toggle Font Size"
            className="min-h-touch min-w-touch px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1 font-bold text-sm shadow-sm"
          >
            <Type className="w-4 h-4 text-indigo-400" />
            <span>{textSize === "large" ? "A+" : "A"}</span>
          </button>

          {/* Language Switcher */}
          <button
            onClick={() => setShowPicker(true)}
            aria-label="Change Language"
            className="min-h-touch min-w-touch px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm shadow-md flex items-center gap-2 transition-colors"
          >
            <Globe className="w-4 h-4" />
            <span>{currentLang?.nativeName || "Language"}</span>
          </button>
        </div>
      </div>
    </header>
  );
}

