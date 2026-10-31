"use client";

import React from "react";
import Link from "next/link";
import { Header } from "../../components/Header";
import { FileText, AlertTriangle, Scale, ShieldAlert, ArrowLeft, Phone } from "lucide-react";

export default function TermsAndConditionsPage() {
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
            <div className="w-12 h-12 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center border border-indigo-500/30">
              <Scale className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
                Terms & Conditions
              </h1>
              <p className="text-xs md:text-sm text-slate-400 font-medium">
                Standard Usage Terms • Educational Guidance & Threat Prevention
              </p>
            </div>
          </div>
        </div>

        {/* 1. Nature of Service: Guidance Not Guarantee */}
        <div className="bg-slate-900/80 border border-amber-500/40 rounded-2xl p-5 md:p-6 space-y-4">
          <h2 className="text-lg font-bold text-amber-300 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <span>1. Guidance Only — Not a Financial or Legal Guarantee</span>
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            ScamShield India provides automated, heuristic, and open-source machine learning risk indicators to assist citizens in spotting fraud. Cyber fraud techniques evolve constantly. 
          </p>
          <p className="text-sm text-slate-300 leading-relaxed">
            <strong>Important:</strong> A &ldquo;Safe&rdquo; verdict indicates that no known phishing patterns, lookalike bank domains, or suspicious markers were detected in our rules and threat feeds. It does not constitute a warranty or legal guarantee of safety. If in doubt, always independently verify by calling the official phone number printed on your debit/ATM card.
          </p>
        </div>

        {/* 2. Emergency Protocol */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 md:p-6 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-red-400" />
            <span>2. Emergency Protocol if Money Was Debited</span>
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            If money was debited from your bank account or transferred via UPI:
          </p>
          <ul className="list-disc pl-5 space-y-2 text-sm text-slate-300">
            <li>Immediately call the <strong>National Cyber Crime Helpline at 1930</strong>. Reporting within the first 2 hours (&ldquo;Golden Hour&rdquo;) enables banks to freeze fund transfers.</li>
            <li>Call your bank&apos;s 24x7 toll-free helpline to freeze your netbanking, UPI, and debit cards.</li>
            <li>File an official police report at <a href="https://cybercrime.gov.in" target="_blank" rel="noopener noreferrer" className="text-indigo-400 underline">cybercrime.gov.in</a>.</li>
          </ul>
        </div>

        {/* 3. Acceptable Use Policy */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 md:p-6 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            <span>3. Acceptable Use Policy</span>
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            You agree to use ScamShield India solely for lawful, personal defensive cyber protection and fraud identification. You agree not to:
          </p>
          <ul className="list-disc pl-5 space-y-2 text-sm text-slate-300">
            <li>Subject the API to automated denial-of-service (DoS) attacks or automated scraping.</li>
            <li>Use the detection engine to optimize, test, or evade detection for malicious phishing or malware campaigns.</li>
            <li>Submit file payloads exceeding 10MB or containing malicious server exploits.</li>
          </ul>
        </div>

        {/* 4. Open Source & Intellectual Property */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 md:p-6 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Scale className="w-5 h-5 text-emerald-400" />
            <span>4. Open Source & License</span>
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            ScamShield India is licensed under the permissive MIT Open Source License. The AI models (IndicBERT v2 by AI4Bharat) and threat intelligence feeds (URLhaus, OpenPhish) belong to their respective creators under open-access community licenses.
          </p>
        </div>

        {/* Quick Footer Links */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
          <span className="text-xs text-slate-400">
            Last Updated: Hacktoberfest 2026 • Questions? Contact <code>legal@scamshield.org</code>
          </span>
          <Link
            href="/privacy"
            className="text-xs text-emerald-400 hover:text-emerald-300 font-bold underline"
          >
            Read Privacy Policy (DPDP Act)
          </Link>
        </div>
      </main>

      <footer className="w-full bg-slate-950 border-t border-slate-900 py-6 text-center text-xs text-slate-500 space-y-2 px-4">
        <p>ScamShield India • DPDP Act 2023 Compliant • Free & Open Source</p>
      </footer>
    </div>
  );
}
