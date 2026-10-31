"use client";

import React from "react";
import Link from "next/link";
import { Header } from "../components/Header";
import { ShieldAlert, Home, ArrowLeft, Phone } from "lucide-react";
import { useI18n } from "../i18n/context";

export default function NotFound() {
  const { t } = useI18n();

  return (
    <div className="flex-1 flex flex-col justify-between min-h-screen bg-slate-950 text-slate-100">
      <Header />

      <main className="flex-1 max-w-xl w-full mx-auto px-4 py-12 flex flex-col items-center justify-center text-center space-y-6">
        <div className="w-20 h-20 rounded-2xl bg-amber-500/10 border-2 border-amber-500/30 flex items-center justify-center text-amber-400">
          <ShieldAlert className="w-10 h-10" />
        </div>

        <div className="space-y-2">
          <span className="text-xs font-bold uppercase tracking-widest px-3 py-1 bg-amber-500/20 text-amber-300 rounded-full border border-amber-500/30">
            Error 404 • Page Not Found
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            {t("errors.notFoundTitle", "Looks like you reached an uncharted link")}
          </h1>
          <p className="text-sm sm:text-base text-slate-400 max-w-md mx-auto">
            {t(
              "errors.notFoundDesc",
              "The page or resource you are looking for does not exist or has been moved. Stay safe and return to the scam scanner."
            )}
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-3 w-full max-w-xs">
          <Link
            href="/"
            className="w-full min-h-touch py-3 px-5 rounded-xl bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-indigo-900/20 transition-all active:scale-[0.98]"
          >
            <Home className="w-4 h-4" />
            <span>{t("errors.backHome", "Back to Scam Scanner")}</span>
          </Link>
          <Link
            href="/stats"
            className="w-full min-h-touch py-3 px-5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold text-sm flex items-center justify-center gap-2 transition-colors"
          >
            <span>{t("errors.viewStats", "View Threat Stats")}</span>
          </Link>
        </div>

        <div className="w-full max-w-md p-3.5 bg-slate-900/60 border border-slate-800 rounded-xl flex items-center justify-center gap-2 text-xs text-slate-400">
          <Phone className="w-3.5 h-3.5 text-amber-400" />
          <span>If you are facing financial fraud right now, dial </span>
          <a href="tel:1930" className="text-amber-400 font-bold underline">
            1930
          </a>
        </div>
      </main>

      <footer className="w-full bg-slate-950 border-t border-slate-900 py-4 text-center text-xs text-slate-500 px-4">
        ScamShield India • DPDP Act 2023 Compliant • Free & Open Source
      </footer>
    </div>
  );
}
