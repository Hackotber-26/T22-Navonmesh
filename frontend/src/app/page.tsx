"use client";

import React, { useEffect } from "react";
import { Header } from "../components/Header";
import { LanguageModal } from "../components/LanguageModal";
import { HomeScanner } from "../components/HomeScanner";
import { useI18n } from "../i18n/context";
import { Phone, Shield, ExternalLink, Heart } from "lucide-react";

export default function HomePage() {
  const { t } = useI18n();

  // Register service worker for PWA offline capabilities
  useEffect(() => {
    if ("serviceWorker" in navigator && process.env.NODE_ENV === "production") {
      navigator.serviceWorker
        .register("/sw.js")
        .then((reg) => console.log("ScamShield ServiceWorker registered:", reg.scope))
        .catch((err) => console.error("ScamShield ServiceWorker error:", err));
    }
  }, []);

  return (
    <div className="flex-1 flex flex-col justify-between">
      {/* Header with language and accessibility controls */}
      <Header />

      {/* Language Picker Modal for first-time launch or switching */}
      <LanguageModal />

      {/* Main Content Area */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6 md:py-8 space-y-6">
        {/* Hero Tagline for Elderly / First-Time Users */}
        <div className="text-center space-y-2">
          <h2 className="text-2xl md:text-4xl font-extrabold text-white tracking-tight">
            {t("app.tagline", "Protect your family from fake UPI, KYC & WhatsApp scams")}
          </h2>
          <p className="text-base md:text-lg text-slate-400 max-w-2xl mx-auto">
            {t("app.subtitle", "Check suspicious messages, links, and QR codes before you tap")}
          </p>
        </div>

        {/* Central Scanner Component */}
        <HomeScanner />

        {/* Emergency Helpline Strip */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
              <Phone className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs text-slate-400 font-bold uppercase tracking-wider">
                National Cyber Crime Helpline (India)
              </p>
              <p className="text-lg font-black text-amber-400">
                Dial <a href="tel:1930" className="underline hover:text-amber-300">1930</a> (Toll Free 24x7)
              </p>
            </div>
          </div>
          <a
            href="https://cybercrime.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="min-h-touch px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-semibold flex items-center gap-1.5 transition-colors"
          >
            <span>cybercrime.gov.in</span>
            <ExternalLink className="w-4 h-4 text-slate-400" />
          </a>
        </div>
      </main>

      {/* Accessible Footer with Privacy & Open Source notice */}
      <footer className="w-full bg-slate-950 border-t border-slate-900 py-6 text-center text-xs text-slate-500 space-y-2 px-4">
        <p className="flex items-center justify-center gap-1.5 font-medium text-slate-400">
          <Shield className="w-4 h-4 text-emerald-500" />
          <span>Zero User Content Stored • DPDP Act 2023 Compliant • Free & Open Source</span>
        </p>
        <p>
          Built for Hacktoberfest Hack Day 2026 with <Heart className="w-3 h-3 inline text-red-500" /> for Indian Digital Citizens.
        </p>
      </footer>
    </div>
  );
}
