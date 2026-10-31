"use client";

import React from "react";
import Link from "next/link";
import { Header } from "../../components/Header";
import { ShieldCheck, Lock, EyeOff, Server, FileText, ArrowLeft, Phone } from "lucide-react";
import { useI18n } from "../../i18n/context";

export default function PrivacyPolicyPage() {
  const { t } = useI18n();

  return (
    <div className="flex-1 flex flex-col justify-between min-h-screen bg-slate-950 text-slate-100">
      <Header />

      <main className="flex-1 max-w-3xl w-full mx-auto px-4 py-8 md:py-10 space-y-8">
        {/* Navigation & Title */}
        <div className="space-y-3">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-white transition-colors py-1 px-2 rounded-lg bg-slate-900 border border-slate-800"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Scanner</span>
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
              <Lock className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
                Privacy Policy
              </h1>
              <p className="text-xs md:text-sm text-emerald-400 font-medium">
                Digital Personal Data Protection (DPDP) Act 2023 Compliant • Zero User Content Stored
              </p>
            </div>
          </div>
        </div>

        {/* DPDP Act 2023 Principles Card */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 md:p-6 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <EyeOff className="w-5 h-5 text-indigo-400" />
            <span>1. Zero-Retention Data Policy</span>
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            ScamShield India operates on a strict zero-retention architecture. When you paste message text, scan a QR code, upload a screenshot, or inspect an APK file:
          </p>
          <ul className="list-disc pl-5 space-y-2 text-sm text-slate-300">
            <li>
              <strong>In-Memory Processing:</strong> Content is analyzed strictly in volatile system memory (RAM).
            </li>
            <li>
              <strong>Instant Discard:</strong> The raw text, phone numbers, full URLs, screenshot images, and APK file bytes are permanently destroyed immediately upon classification completion.
            </li>
            <li>
              <strong>No Message Database:</strong> ScamShield has no database table storing user messages, personal chats, or confidential credentials.
            </li>
          </ul>
        </div>

        {/* Anonymous Telemetry & Cryptographic Hashes */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 md:p-6 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Server className="w-5 h-5 text-emerald-400" />
            <span>2. Anonymous Threat Telemetry</span>
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            To generate community defense statistics and track emerging fraud campaigns across India without compromising privacy, the system records only:
          </p>
          <ul className="list-disc pl-5 space-y-2 text-sm text-slate-300">
            <li>Primary fraud category (e.g. <code>FAKE_KYC</code>, <code>UPI_COLLECT_FRAUD</code>)</li>
            <li>Calculated risk score (e.g. <code>0.95</code>) and risk level (<code>critical</code>)</li>
            <li>Identified reason codes (e.g. <code>URGENCY</code>, <code>SUSPICIOUS_TLD</code>)</li>
            <li>A one-way irreversible SHA-256 cryptographic hash of domain names (no query strings or parameters).</li>
            <li>Timestamp and preferred language code (e.g. <code>hi</code>, <code>en</code>).</li>
          </ul>
        </div>

        {/* APK & Permissions Inspection Privacy */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 md:p-6 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-amber-400" />
            <span>3. APK File & Terms Inspection Safeguards</span>
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            When you upload an Android package (.apk) to check for suspicious behavior or inspect fine-print legal loopholes:
          </p>
          <ul className="list-disc pl-5 space-y-2 text-sm text-slate-300">
            <li>The file is parsed in-memory as a ZIP archive to read manifest permissions and internal terms strings.</li>
            <li>The APK file is never executed, installed, or retained on our servers.</li>
            <li>Extracted permission lists and loophole summaries are returned directly to your session and discarded from memory.</li>
          </ul>
        </div>

        {/* DPDP Act 2023 Rights & Grievance Redressal */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 md:p-6 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            <span>4. Your Rights Under DPDP Act 2023</span>
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            In compliance with India&apos;s Digital Personal Data Protection Act 2023:
          </p>
          <ul className="list-disc pl-5 space-y-2 text-sm text-slate-300">
            <li><strong>Right to Erasure:</strong> If you use optional sign-in, you can delete your account and associated telemetry with one click.</li>
            <li><strong>Zero Commercial Profiling:</strong> We do not serve commercial advertisements, sell data to advertisers, or track you across the web.</li>
            <li><strong>Grievance Redressal:</strong> For any privacy questions, contact our data protection team at <code>privacy@scamshield.org</code>.</li>
          </ul>
        </div>

        {/* Emergency Contact */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
          <div className="flex items-center gap-2.5">
            <Phone className="w-4 h-4 text-amber-400 shrink-0" />
            <span className="text-xs text-slate-400">
              National Cyber Crime Reporting Helpline: <a href="tel:1930" className="text-amber-400 font-bold underline">1930</a>
            </span>
          </div>
          <Link
            href="/terms"
            className="text-xs text-indigo-400 hover:text-indigo-300 font-bold underline"
          >
            Read Terms & Conditions
          </Link>
        </div>
      </main>

      <footer className="w-full bg-slate-950 border-t border-slate-900 py-6 text-center text-xs text-slate-500 space-y-2 px-4">
        <p>ScamShield India • DPDP Act 2023 Compliant • Free & Open Source</p>
      </footer>
    </div>
  );
}
