"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
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
  Download,
  CheckCircle2,
  Phone,
  CreditCard,
  Globe,
  FileText,
  Lightbulb,
  ShieldAlert,
} from "lucide-react";

interface ActionChecklistProps {
  incidentId?: string;
  category: string;
  riskLevel: string;
  actionCodes: string[];
  userActionState: UserActionState;
  extractedDomains?: string[];
  reasonCodes?: string[];
  content?: string;
  inputType?: "text" | "url" | "qr";
}

export function ActionChecklist({
  incidentId,
  category,
  riskLevel,
  actionCodes,
  userActionState,
  extractedDomains = [],
  reasonCodes = [],
  content = "",
  inputType = "text",
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

  // 1. Extract contextual entities (phones, UPI handles, links) from user content
  const detectedEntities = useMemo(() => {
    const raw = content || "";
    
    // Indian mobile numbers (10 digits starting with 6-9, with optional +91 or 0 prefix)
    const phoneRegex = /(?:(?:\+91|0)[-.\s]?)?[6-9]\d{4}[-.\s]?\d{5}\b/g;
    const rawPhones = raw.match(phoneRegex) || [];
    const phones = Array.from(new Set(rawPhones.map((p) => p.trim())));

    // UPI handles (e.g., user@ybl, support@paytm, name@okhdfcbank)
    const upiRegex = /[a-zA-Z0-9.\-_]{2,256}@(okhdfcbank|okaxis|oksbi|okicici|paytm|ybl|ibl|axl|upi|apl|barodampay|federal|postbank|[a-zA-Z]{2,30})\b/gi;
    const rawUpis = raw.match(upiRegex) || [];
    const upiHandles = Array.from(new Set(rawUpis.map((u) => u.trim())));

    // Combine extracted domains from backend with any detected in content
    const domains = Array.from(new Set(extractedDomains));

    return {
      phones,
      upiHandles,
      domains,
      hasEntities: phones.length > 0 || upiHandles.length > 0 || domains.length > 0,
    };
  }, [content, extractedDomains]);

  // 2. Build pre-formatted complaint summary tailored to the specific content
  const generateComplaintSummary = () => {
    const dateStr = new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });
    const categoryName = t(`categories.${category}`, category);

    let detectedDetails = "";
    if (detectedEntities.phones.length > 0) {
      detectedDetails += `\nSuspect Contact Numbers: ${detectedEntities.phones.join(", ")}`;
    }
    if (detectedEntities.upiHandles.length > 0) {
      detectedDetails += `\nSuspect UPI Handles: ${detectedEntities.upiHandles.join(", ")}`;
    }
    if (detectedEntities.domains.length > 0) {
      detectedDetails += `\nSuspect URLs / Domains: ${detectedEntities.domains.join(", ")}`;
    }

    return `[CYBERCRIME COMPLAINT SUMMARY - SCAMSHIELD INDIA]
Incident Ref ID: ${incidentId || "N/A"}
Date & Time: ${dateStr} IST
Suspected Fraud Type: ${categoryName} (${category})
User Action State: ${userActionState.toUpperCase()}
Risk Level: ${riskLevel.toUpperCase()}${detectedDetails || "\nDetected Entities: None explicitly isolated"}

Uploaded Evidence / Message Excerpt:
"${content.slice(0, 300)}${content.length > 300 ? "..." : ""}"

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

  const handleDownloadComplaint = () => {
    const summary = generateComplaintSummary();
    const blob = new Blob([summary], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `cybercrime_complaint_${incidentId?.slice(0, 8) || "summary"}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // 3. Build WhatsApp family warning share link incorporating detected content
  const getWhatsAppShareUrl = () => {
    const categoryName = t(`categories.${category}`, category);
    const primaryDomain = detectedEntities.domains[0] || "";
    const primaryPhone = detectedEntities.phones[0] || "";

    let entitySnippet = "";
    if (primaryDomain) {
      entitySnippet = ` (Link: ${primaryDomain})`;
    } else if (primaryPhone) {
      entitySnippet = ` (Phone: ${primaryPhone})`;
    }

    let shareText = "";
    if (language === "hi") {
      shareText = `⚠️ *सावधान रहें! धोखाधड़ी की चेतावनी* ⚠️\n\nमुझे अभी *${categoryName}*${entitySnippet} से जुड़ा एक संदिग्ध संदेश मिला है।\n\nअगर आपको भी ऐसा संदेश, लिंक या कॉल आए तो बिल्कुल क्लिक न करें और न ही किसी को OTP या UPI पिन बताएं।\n\nमुफ्त जांचें: https://scamshield.org`;
    } else if (language === "bn") {
      shareText = `⚠️ *সতর্ক থাকুন! প্রতারণার সতর্কতা* ⚠️\n\nআমি এইমাত্র *${categoryName}*${entitySnippet} সম্পর্কিত একটি ভুয়া মেসেজ পেয়েছি।\n\nআপনাদের কাছে এমন কোনো মেসেজ বা লিংক আসলে ক্লিক করবেন না এবং ওটিপি বা পিন শেয়ার করবেন না!\n\nযাচাই করতে: https://scamshield.org`;
    } else if (language === "mr") {
      shareText = `⚠️ *सावध राहा! फसवणुकीचा इशारा* ⚠️\n\nमला आत्ताच *${categoryName}*${entitySnippet} चा एक बनावट मेसेज आला आहे.\n\nतुम्हाला असा मेसेज किंवा लिंक आल्यास क्लिक करू नका आणि कोणालाही OTP किंवा UPI पिन सांगू नका.\n\nतपासण्यासाठी: https://scamshield.org`;
    } else if (language === "kn") {
      shareText = `⚠️ *ಎಚ್ಚರವಿರಲಿ! ವಂಚನೆಯ ಎಚ್ಚರಿಕೆ* ⚠️\n\nನನಗೆ ಈಗಷ್ಟೇ *${categoryName}*${entitySnippet} ಗೆ ಸಂಬಂಧಿಸಿದ ನಕಲಿ ಸಂದೇಶ ಬಂದಿದೆ.\n\nನಿಮಗೂ ಇಂತಹ ಸಂದೇಶ ಅಥವಾ ಲಿಂಕ್ ಬಂದರೆ ಕ್ಲಿಕ್ ಮಾಡಬೇಡಿ ಮತ್ತು ಒಟಿಪಿ ಅಥವಾ ಪಿನ್ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.\n\nಪರಿಶೀಲಿಸಲು: https://scamshield.org`;
    } else {
      shareText = `⚠️ *SCAM ALERT: Stay Safe!* ⚠️\n\nI just detected a suspicious message regarding *${categoryName}*${entitySnippet}.\n\nIf you receive any similar SMS, link, or QR code, DO NOT click or share any OTP or UPI PIN.\n\nVerify threats free at: https://scamshield.org`;
    }

    return `https://wa.me/?text=${encodeURIComponent(shareText)}`;
  };

  // Safe helper to fetch contentAdvice category keys
  const categoryKey = category in {
    ELECTRICITY_BILL: 1,
    FAKE_KYC: 1,
    FAKE_BANK_LINK: 1,
    UPI_COLLECT_FRAUD: 1,
    MALICIOUS_QR: 1,
    PARCEL_DELIVERY: 1,
    JOB_SCAM: 1,
    LOTTERY_PRIZE: 1,
    OTHER: 1,
  } ? category : "OTHER";

  const customTitle = t(`contentAdvice.categories.${categoryKey}.title`, "Threat Playbook");
  const customBadge = t(`contentAdvice.categories.${categoryKey}.badge`, "Action Plan");
  const tip1 = t(`contentAdvice.categories.${categoryKey}.tip1`, "");
  const tip2 = t(`contentAdvice.categories.${categoryKey}.tip2`, "");
  const tip3 = t(`contentAdvice.categories.${categoryKey}.tip3`, "");

  return (
    <div className="w-full bg-slate-900 border-2 border-slate-800 rounded-2xl p-5 md:p-6 shadow-xl space-y-6">
      {/* 1. Header with title & Emergency Badge */}
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
            {t("checklist.urgentResponseMode", "Urgent Response Mode")}
          </span>
        )}
      </div>

      {/* 2. Contextual Incident Diagnostic Box (Tailored to the uploaded content) */}
      <div className="bg-slate-950 border-2 border-indigo-500/40 rounded-xl p-4 md:p-5 space-y-3 shadow-md">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-amber-400" />
            <h4 className="text-base md:text-lg font-bold text-white">
              {t("contentAdvice.diagnosticHeading", "Contextual Incident Diagnosis")}
            </h4>
          </div>
          <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs font-bold">
            {customBadge}
          </span>
        </div>

        <p className="text-xs sm:text-sm text-slate-300 font-medium leading-relaxed">
          {customTitle} — {t("contentAdvice.diagnosticSub", "Detected specific scam indicators from your uploaded content:")}
        </p>

        {/* Flagged entities pill tags */}
        {detectedEntities.hasEntities && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
            {/* Extracted Phone Numbers */}
            {detectedEntities.phones.map((phone) => (
              <div
                key={phone}
                className="bg-red-950/40 border border-red-500/40 rounded-lg p-2.5 flex items-start gap-2.5 text-xs"
              >
                <Phone className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-red-300 block">{phone}</span>
                  <span className="text-slate-400">
                    {t("contentAdvice.detectedPhoneDesc", "Do NOT call or text this number. Scammers use unregistered SIM cards.")}
                  </span>
                </div>
              </div>
            ))}

            {/* Extracted UPI Handles */}
            {detectedEntities.upiHandles.map((upi) => (
              <div
                key={upi}
                className="bg-amber-950/40 border border-amber-500/40 rounded-lg p-2.5 flex items-start gap-2.5 text-xs"
              >
                <CreditCard className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-amber-300 block">{upi}</span>
                  <span className="text-slate-400">
                    {t("contentAdvice.detectedUpiDesc", "Do NOT approve requests from or send funds to this payment address.")}
                  </span>
                </div>
              </div>
            ))}

            {/* Extracted Domains */}
            {detectedEntities.domains.map((dom) => (
              <div
                key={dom}
                className="bg-indigo-950/40 border border-indigo-500/40 rounded-lg p-2.5 flex items-start gap-2.5 text-xs sm:col-span-2"
              >
                <Globe className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-indigo-300 block font-mono">{dom}</span>
                  <span className="text-slate-400">
                    {t("contentAdvice.detectedDomainDesc", "Counterfeit web address designed to harvest credentials or install malware.")}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 3 Content-Specific Tactical Insights */}
        {(tip1 || tip2 || tip3) && (
          <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
              {t("contentAdvice.playbookHeading", "Content-Specific Action Playbook")}:
            </span>
            <ul className="space-y-1.5 text-xs sm:text-sm text-slate-200">
              {tip1 && (
                <li className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold shrink-0 mt-0.5">•</span>
                  <span>{tip1}</span>
                </li>
              )}
              {tip2 && (
                <li className="flex items-start gap-2">
                  <span className="text-amber-400 font-bold shrink-0 mt-0.5">•</span>
                  <span>{tip2}</span>
                </li>
              )}
              {tip3 && (
                <li className="flex items-start gap-2">
                  <span className="text-indigo-400 font-bold shrink-0 mt-0.5">•</span>
                  <span>{tip3}</span>
                </li>
              )}
            </ul>
          </div>
        )}
      </div>

      {/* 3. Emergency Banner when user sent money */}
      {isEmergency && (
        <div className="bg-red-950/90 border-2 border-red-600 rounded-xl p-4 md:p-5 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-lg shadow-red-950/50">
          <div className="space-y-1 text-center sm:text-left">
            <h4 className="text-lg md:text-xl font-black text-white flex items-center justify-center sm:justify-start gap-2">
              <PhoneCall className="w-5 h-5 text-red-400 animate-bounce" />
              {t("checklist.goldenHourHeading", "Golden Hour: Dial 1930 Immediately")}
            </h4>
            <p className="text-sm text-red-200">
              {t("checklist.goldenHourDesc", "National Cyber Crime Helpline can freeze the scammer's bank account within the first 2 hours!")}
            </p>
          </div>

          <a
            href="tel:1930"
            className="min-h-[52px] min-w-[200px] px-6 py-3 bg-red-600 hover:bg-red-500 text-white font-black text-lg rounded-xl flex items-center justify-center gap-2 shadow-lg transition-transform active:scale-95 shrink-0"
          >
            <PhoneCall className="w-5 h-5" />
            <span>{t("checklist.call1930Now", "Call 1930 Now")}</span>
          </a>
        </div>
      )}

      {/* 4. Quick One-Tap Action Grid */}
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

        {/* 3b. Download Formal Complaint */}
        <button
          onClick={handleDownloadComplaint}
          title={t("checklist.downloadComplaint", "Download Complaint")}
          className="min-h-touch p-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-500 text-white font-bold flex items-center justify-center gap-2 text-sm md:text-base transition-colors shadow-sm"
        >
          <Download className="w-5 h-5 text-indigo-400" />
          <span>{t("checklist.downloadComplaint", "Download Complaint")}</span>
        </button>

        {/* 4. Share with Family on WhatsApp */}
        <a
          href={getWhatsAppShareUrl()}
          target="_blank"
          rel="noopener noreferrer"
          className="min-h-touch p-3.5 rounded-xl bg-emerald-950/60 hover:bg-emerald-900/80 border border-emerald-600/70 text-emerald-200 font-bold flex items-center justify-center gap-2 text-sm md:text-base transition-colors shadow-sm sm:col-span-2 lg:col-span-4"
        >
          <Share2 className="w-5 h-5 text-emerald-400" />
          <span>{t("checklist.shareFamily", "Warn Family on WhatsApp")}</span>
        </a>
      </div>

      {/* 5. Ordered Action Steps List */}
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
                    {t("checklist.step", "Step")} {index + 1}
                  </span>
                  {is1930Step && (
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-red-600 text-white">
                      {t("checklist.topPriority", "Top Priority")}
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

      {/* 6. Safety Confirmation & Thank You Link */}
      <div className="pt-3">
        <Link
          href="/thank-you"
          className="w-full min-h-touch p-3.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 border border-slate-700 hover:border-slate-500 text-emerald-300 font-bold flex items-center justify-center gap-2 text-sm sm:text-base transition-colors shadow-sm"
        >
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <span>{t("checklist.viewConfirmation", "I Have Completed These Steps -> View Confirmation")}</span>
        </Link>
      </div>
    </div>
  );
}
