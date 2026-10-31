"use client";

import React, { useState } from "react";
import { useI18n } from "../i18n/context";
import { UserActionState } from "./ActionStateSelector";
import {
  PhoneCall,
  ExternalLink,
  Copy,
  CheckCheck,
  Share2,
  AlertTriangle,
  Shield,
  CheckSquare,
  Square,
  Building2,
} from "lucide-react";

interface ActionChecklistProps {
  incidentId?: string;
  category: string;
  riskLevel: string;
  actionCodes: string[];
  userActionState: UserActionState;
  extractedDomains?: string[];
  reasonCodes?: string[];
}

export function ActionChecklist({
  incidentId,
  category,
  riskLevel,
  actionCodes,
  userActionState,
  extractedDomains = [],
  reasonCodes = [],
}: ActionChecklistProps) {
  const { t, language } = useI18n();
  const [copied, setCopied] = useState<boolean>(false);
  const [completedSteps, setCompletedSteps] = useState<Record<number, boolean>>({});

  const toggleStep = (index: number) => {
    setCompletedSteps((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const isEmergency = userActionState === "paid";

  // Build pre-formatted complaint summary
  const generateComplaintSummary = () => {
    const dateStr = new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });
    const categoryName = t(`categories.${category}`, category);

    return `[CYBERCRIME COMPLAINT SUMMARY - SCAMSHIELD INDIA]
Incident Ref ID: ${incidentId || "N/A"}
Date & Time: ${dateStr} IST
Suspected Fraud Type: ${categoryName} (${category})
User Action State: ${userActionState.toUpperCase()}
Risk Level: ${riskLevel.toUpperCase()}
Suspicious Domains / Links: ${extractedDomains.length > 0 ? extractedDomains.join(", ") : "None reported"}

Identified Threat Indicators:
${reasonCodes.map((rc) => `- ${t(`reasons.${rc}`, rc)}`).join("\n")}

Actions Initiated:
${actionCodes.map((ac, i) => `${i + 1}. ${t(`actions.${ac}`, ac)}`).join("\n")}

Note: This summary is prepared for submission to the National Cyber Crime Portal (https://cybercrime.gov.in) and Helpline 1930.`;
  };

  const handleCopyComplaint = async () => {
    try {
      const summary = generateComplaintSummary();
      await navigator.clipboard.writeText(summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    } catch (err) {
      console.error("Clipboard copy failed", err);
    }
  };

  // Build WhatsApp family warning share link
  const getWhatsAppShareUrl = () => {
    const categoryName = t(`categories.${category}`, category);
    let shareText = "";

    if (language === "hi") {
      shareText = `⚠️ *सावधान रहें! धोखाधड़ी की चेतावनी* ⚠️\n\nमुझे अभी एक फर्जी संदेश मिला है जो *${categoryName}* का प्रतीत होता है।\n\nअगर आपको भी ऐसा कोई संदेश, लिंक या QR कोड मिले तो उस पर क्लिक न करें और न ही किसी को OTP या UPI पिन बताएं। सतर्क रहें!\n\nजांचने के लिए देखें: https://scamshield.org`;
    } else if (language === "bn") {
      shareText = `⚠️ *সতর্ক থাকুন! প্রতারণার সতর্কতা* ⚠️\n\nআমি একটি ভুয়া মেসেজ পেয়েছি যা *${categoryName}* এর সাথে সম্পর্কিত।\n\nআপনাদের কাছে এমন কোনো মেসেজ বা লিংক আসলে ক্লিক করবেন না এবং ওটিপি বা পিন শেয়ার করবেন না!\n\nযাচাই করতে: https://scamshield.org`;
    } else if (language === "mr") {
      shareText = `⚠️ *सावध राहा! फसवणुकीचा इशारा* ⚠️\n\nमला आत्ताच एक बनावट मेसेज आला आहे जो *${categoryName}* चा वाटतो.\n\nतुम्हालाही असा कोणताही मेसेज किंवा लिंक आल्यास क्लिक करू नका आणि कोणालाही OTP किंवा UPI पिन सांगू नका.\n\nतपासण्यासाठी: https://scamshield.org`;
    } else if (language === "kn") {
      shareText = `⚠️ *ಎಚ್ಚರವಿರಲಿ! ವಂಚನೆಯ ಎಚ್ಚರಿಕೆ* ⚠️\n\nನನಗೆ ಈಗಷ್ಟೇ *${categoryName}* ಗೆ ಸಂಬಂಧಿಸಿದ ನಕಲಿ ಸಂದೇಶ ಬಂದಿದೆ.\n\nನಿಮಗೂ ಇಂತಹ ಯಾವುದೇ ಸಂದೇಶ ಅಥವಾ ಲಿಂಕ್ ಬಂದರೆ ಕ್ಲಿಕ್ ಮಾಡಬೇಡಿ ಮತ್ತು ಒಟಿಪಿ ಅಥವಾ ಪಿನ್ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.\n\nಪರಿಶೀಲಿಸಲು: https://scamshield.org`;
    } else {
      shareText = `⚠️ *SCAM ALERT: Stay Safe!* ⚠️\n\nI just detected a suspicious message regarding *${categoryName}*.\n\nIf you receive any similar SMS, link, or QR code, DO NOT click or share any OTP or UPI PIN.\n\nVerify threats free at: https://scamshield.org`;
    }

    return `https://wa.me/?text=${encodeURIComponent(shareText)}`;
  };

  return (
    <div className="w-full bg-slate-900 border-2 border-slate-800 rounded-2xl p-5 md:p-6 shadow-xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2.5">
          <Shield className="w-6 h-6 text-indigo-400" />
          <h3 className="text-xl md:text-2xl font-black text-white">
            {t("checklist.heading", "What to do right now")}
          </h3>
        </div>

        {isEmergency && (
          <span className="px-3 py-1 rounded-full bg-red-600/30 text-red-400 border border-red-500 font-black text-xs uppercase tracking-wider animate-pulse flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" />
            Urgent Response Mode
          </span>
        )}
      </div>

      {/* Emergency Banner when user sent money */}
      {isEmergency && (
        <div className="bg-red-950/90 border-2 border-red-600 rounded-xl p-4 md:p-5 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-lg shadow-red-950/50">
          <div className="space-y-1 text-center sm:text-left">
            <h4 className="text-lg md:text-xl font-black text-white flex items-center justify-center sm:justify-start gap-2">
              <PhoneCall className="w-5 h-5 text-red-400 animate-bounce" />
              Golden Hour: Dial 1930 Immediately
            </h4>
            <p className="text-sm text-red-200">
              National Cyber Crime Helpline can freeze the scammer's bank account within the first 2 hours!
            </p>
          </div>

          <a
            href="tel:1930"
            className="min-h-[52px] min-w-[200px] px-6 py-3 bg-red-600 hover:bg-red-500 text-white font-black text-lg rounded-xl flex items-center justify-center gap-2 shadow-lg transition-transform active:scale-95"
          >
            <PhoneCall className="w-5 h-5" />
            <span>Call 1930 Now</span>
          </a>
        </div>
      )}

      {/* Quick One-Tap Action Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* 1. Call 1930 */}
        <a
          href="tel:1930"
          className="min-h-touch p-3.5 rounded-xl bg-slate-800 hover:bg-red-950/70 border border-slate-700 hover:border-red-500 text-white font-bold flex items-center justify-center gap-2 text-sm md:text-base transition-colors shadow-sm"
        >
          <PhoneCall className="w-5 h-5 text-red-400" />
          <span>{t("checklist.call1930", "Call 1930 Helpline")}</span>
        </a>

        {/* 2. Open Cybercrime Portal */}
        <a
          href="https://cybercrime.gov.in"
          target="_blank"
          rel="noopener noreferrer"
          className="min-h-touch p-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-500 text-white font-bold flex items-center justify-center gap-2 text-sm md:text-base transition-colors shadow-sm"
        >
          <ExternalLink className="w-5 h-5 text-indigo-400" />
          <span>{t("checklist.openPortal", "cybercrime.gov.in")}</span>
        </a>

        {/* 3. Copy Complaint Summary */}
        <button
          onClick={handleCopyComplaint}
          className="min-h-touch p-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-500 text-white font-bold flex items-center justify-center gap-2 text-sm md:text-base transition-colors shadow-sm"
        >
          {copied ? (
            <>
              <CheckCheck className="w-5 h-5 text-emerald-400" />
              <span className="text-emerald-400">{t("checklist.copied", "Copied!")}</span>
            </>
          ) : (
            <>
              <Copy className="w-5 h-5 text-amber-400" />
              <span>{t("checklist.copyComplaint", "Copy Complaint")}</span>
            </>
          )}
        </button>

        {/* 4. Share with Family on WhatsApp */}
        <a
          href={getWhatsAppShareUrl()}
          target="_blank"
          rel="noopener noreferrer"
          className="min-h-touch p-3.5 rounded-xl bg-emerald-950/60 hover:bg-emerald-900/80 border border-emerald-600/70 text-emerald-200 font-bold flex items-center justify-center gap-2 text-sm md:text-base transition-colors shadow-sm"
        >
          <Share2 className="w-5 h-5 text-emerald-400" />
          <span>{t("checklist.shareFamily", "Warn Family")}</span>
        </a>
      </div>

      {/* Ordered Action Steps List */}
      <div className="space-y-3 pt-2">
        {actionCodes.map((code, index) => {
          const isDone = !!completedSteps[index];
          const is1930Step = code === "REPORT_1930";

          return (
            <div
              key={`${code}-${index}`}
              onClick={() => toggleStep(index)}
              className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex items-start gap-3.5 select-none ${
                isDone
                  ? "bg-slate-900/60 border-slate-800 opacity-60 line-through"
                  : is1930Step && isEmergency
                  ? "bg-red-950/50 border-red-500 shadow-md shadow-red-950/40"
                  : "bg-slate-800/80 border-slate-700 hover:border-slate-600"
              }`}
            >
              <div className="shrink-0 mt-0.5">
                {isDone ? (
                  <CheckSquare className="w-6 h-6 text-emerald-400" />
                ) : (
                  <Square className="w-6 h-6 text-slate-500" />
                )}
              </div>

              <div className="flex-1">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-xs font-black uppercase px-2 py-0.5 rounded bg-black/40 text-slate-400">
                    Step {index + 1}
                  </span>
                  {is1930Step && (
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-red-600 text-white">
                      Top Priority
                    </span>
                  )}
                </div>
                <p className={`text-base md:text-lg font-bold text-white ${isDone ? "text-slate-400" : ""}`}>
                  {t(`actions.${code}`, code)}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
