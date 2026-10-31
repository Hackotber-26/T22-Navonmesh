"use client";

import React from "react";
import Link from "next/link";
import { Header } from "../../components/Header";
import { ShieldCheck, Heart, Home, BarChart3, Phone, ExternalLink, Share2, ArrowRight } from "lucide-react";
import { useI18n } from "../../i18n/context";

export default function ThankYouPage() {
  const { t } = useI18n();

  const handleShareApp = async () => {
    const shareData = {
      title: "ScamShield India",
      text: "Check suspicious SMS, WhatsApp messages, UPI payment requests, and APKs before you click or send money!",
      url: typeof window !== "undefined" ? window.location.origin : "https://scamshield.org",
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
      } catch (err) {
        // User dismissed share dialog
      }
    } else if (navigator.clipboard) {
      await navigator.clipboard.writeText(shareData.url);
      alert("App link copied to clipboard! Share it with your family.");
    }
  };

  return (
    <div className="flex-1 flex flex-col justify-between min-h-screen bg-slate-950 text-slate-100">
      <Header />

      <main className="flex-1 max-w-2xl w-full mx-auto px-4 py-8 md:py-12 space-y-6">
        {/* Appreciation Hero Card */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 md:p-8 text-center space-y-5 shadow-2xl relative overflow-hidden">
          <div className="w-16 h-16 md:w-20 md:h-20 rounded-2xl bg-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center border border-emerald-500/30">
            <ShieldCheck className="w-9 h-9 md:w-11 md:h-11" />
          </div>

          <div className="space-y-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Heart className="w-3.5 h-3.5 text-red-400" />
              Community Cyber Defense
            </span>
            <h1 className="text-2xl md:text-4xl font-extrabold text-white tracking-tight">
              Thank You for Staying Vigilant!
            </h1>
            <p className="text-base text-slate-300 max-w-lg mx-auto">
              By inspecting suspicious messages, APKs, or links before acting, you help break the fraud cycle and protect your family from devastating financial losses.
            </p>
          </div>

          {/* Golden Hour Helpline Reminder */}
          <div className="bg-slate-950/80 border border-amber-500/40 rounded-2xl p-4 text-left flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
                <Phone className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs uppercase font-bold text-amber-300">Emergency Helpline (24x7 Toll Free)</p>
                <p className="text-base md:text-lg font-black text-white">
                  Dial <a href="tel:1930" className="text-amber-400 underline hover:text-amber-300">1930</a> within the 2-Hour Golden Period
                </p>
              </div>
            </div>
            <a
              href="https://cybercrime.gov.in"
              target="_blank"
              rel="noopener noreferrer"
              className="min-h-touch px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold flex items-center gap-1.5 shrink-0"
            >
              <span>cybercrime.gov.in</span>
              <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
            </a>
          </div>

          {/* Quick Action Navigation */}
          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              href="/"
              className="w-full sm:w-auto min-h-touch px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white font-bold text-base flex items-center justify-center gap-2 shadow-lg shadow-indigo-900/30 transition-transform active:scale-[0.98]"
            >
              <Home className="w-5 h-5" />
              <span>Scan Another Message or File</span>
            </Link>

            <button
              onClick={handleShareApp}
              className="w-full sm:w-auto min-h-touch px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold text-base flex items-center justify-center gap-2 transition-colors"
            >
              <Share2 className="w-5 h-5 text-indigo-400" />
              <span>Share App with Family</span>
            </button>

            <Link
              href="/stats"
              className="w-full sm:w-auto min-h-touch px-4 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/80 font-bold text-base flex items-center justify-center gap-1.5 transition-colors"
            >
              <BarChart3 className="w-5 h-5 text-emerald-400" />
              <span>Threat Stats</span>
            </Link>
          </div>
        </div>

        {/* 3 Pillars of Safety */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl text-center space-y-1">
            <p className="text-sm font-bold text-emerald-400">Never Enter PIN</p>
            <p className="text-xs text-slate-400">UPI PIN is ONLY required to send money, never to receive rewards or refunds.</p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl text-center space-y-1">
            <p className="text-sm font-bold text-indigo-400">Zero Message Storage</p>
            <p className="text-xs text-slate-400">We comply with DPDP Act 2023. Your message text is analyzed in-memory and wiped.</p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl text-center space-y-1">
            <p className="text-sm font-bold text-amber-400">No Third-Party APKs</p>
            <p className="text-xs text-slate-400">Never install .apk files received via WhatsApp, Telegram, or SMS links.</p>
          </div>
        </div>
      </main>

      <footer className="w-full bg-slate-950 border-t border-slate-900 py-6 text-center text-xs text-slate-500 space-y-2 px-4">
        <p>Built for Indian Digital Citizens • DPDP Act 2023 Compliant • 100% Free & Open Source</p>
      </footer>
    </div>
  );
}
