"use client";

import React, { useState } from "react";
import { useI18n } from "../i18n/context";
import {
  ShieldAlert,
  AlertTriangle,
  HelpCircle,
  ShieldCheck,
  Volume2,
  VolumeX,
  ExternalLink,
  ChevronRight,
} from "lucide-react";

export interface AnalyzeResult {
  incident_id?: string;
  risk_score: number;
  risk_level: "low" | "medium" | "high" | "critical";
  category: string;
  reason_codes: string[];
  action_codes: string[];
  model_version: string;
  rules_version: string;
  extracted_domains: string[];
}

interface VerdictBannerProps {
  result: AnalyzeResult;
}

export function VerdictBanner({ result }: VerdictBannerProps) {
  const { t, language } = useI18n();
  const [isPlayingAudio, setIsPlayingAudio] = useState<boolean>(false);

  const { risk_level, risk_score, category, reason_codes, extracted_domains } = result;

  // Visual styling and configuration for traffic-light levels
  const levelConfig = {
    critical: {
      bgColor: "bg-red-950/90 border-red-600",
      accentBg: "bg-red-600",
      textColor: "text-red-200",
      iconColor: "text-red-400",
      icon: ShieldAlert,
      title: t("verdict.critical.label", "DANGER - DO NOT PROCEED"),
      tagline: t("verdict.critical.tagline", "Active phishing link or known fraud pattern. Stop immediately!"),
    },
    high: {
      bgColor: "bg-red-950/80 border-orange-600",
      accentBg: "bg-orange-600",
      textColor: "text-orange-200",
      iconColor: "text-orange-400",
      icon: AlertTriangle,
      title: t("verdict.high.label", "HIGH RISK - LIKELY SCAM"),
      tagline: t("verdict.high.tagline", "High probability of fraud. Do not tap any link or share PIN."),
    },
    medium: {
      bgColor: "bg-amber-950/80 border-amber-500",
      accentBg: "bg-amber-600",
      textColor: "text-amber-200",
      iconColor: "text-amber-400",
      icon: HelpCircle,
      title: t("verdict.medium.label", "SUSPICIOUS - BE CAREFUL"),
      tagline: t("verdict.medium.tagline", "Contains unverified links or urgent wording. Do not send money."),
    },
    low: {
      bgColor: "bg-emerald-950/80 border-emerald-500",
      accentBg: "bg-emerald-600",
      textColor: "text-emerald-200",
      iconColor: "text-emerald-400",
      icon: ShieldCheck,
      title: t("verdict.low.label", "SAFE - NO THREATS DETECTED"),
      tagline: t("verdict.low.tagline", "No obvious scam indicators detected. Stay alert."),
    },
  };

  const currentConfig = levelConfig[risk_level] || levelConfig.medium;
  const IconComponent = currentConfig.icon;

  // Handle voice playback (plays static audio if available, with SpeechSynthesis fallback)
  const handlePlayVoice = () => {
    if (isPlayingAudio) {
      window.speechSynthesis?.cancel();
      setIsPlayingAudio(false);
      return;
    }

    const audioPath = `/audio/${language}/verdict_${risk_level}.mp3`;
    const audio = new Audio(audioPath);

    setIsPlayingAudio(true);
    audio.play().catch(() => {
      // Fallback to browser SpeechSynthesis in selected language
      if ("speechSynthesis" in window) {
        const speechText = `${currentConfig.title}. ${currentConfig.tagline}`;
        const utterance = new SpeechSynthesisUtterance(speechText);
        utterance.lang = language === "en" ? "en-IN" : `${language}-IN`;
        utterance.rate = 0.9;
        utterance.onend = () => setIsPlayingAudio(false);
        utterance.onerror = () => setIsPlayingAudio(false);
        window.speechSynthesis.speak(utterance);
      } else {
        setIsPlayingAudio(false);
      }
    });

    audio.onended = () => setIsPlayingAudio(false);
    audio.onerror = () => {
      // SpeechSynthesis fallback
      if ("speechSynthesis" in window) {
        const speechText = `${currentConfig.title}. ${currentConfig.tagline}`;
        const utterance = new SpeechSynthesisUtterance(speechText);
        utterance.lang = language === "en" ? "en-IN" : `${language}-IN`;
        utterance.onend = () => setIsPlayingAudio(false);
        utterance.onerror = () => setIsPlayingAudio(false);
        window.speechSynthesis.speak(utterance);
      } else {
        setIsPlayingAudio(false);
      }
    };
  };

  // Translated category name
  const translatedCategory = t(`categories.${category}`, category);

  return (
    <div className={`w-full rounded-2xl border-4 p-5 md:p-6 shadow-2xl transition-all ${currentConfig.bgColor}`}>
      {/* Top Banner: Icon & Verdict */}
      <div className="flex flex-col sm:flex-row items-center sm:items-start gap-4 text-center sm:text-left">
        <div className={`w-20 h-20 rounded-2xl flex items-center justify-center shrink-0 shadow-lg ${currentConfig.accentBg} text-white`}>
          <IconComponent className="w-12 h-12 stroke-[2.5]" />
        </div>

        <div className="flex-1">
          <div className="flex flex-wrap items-center justify-center sm:justify-between gap-2 mb-1">
            <span className="text-xs uppercase tracking-widest font-black px-2.5 py-1 rounded-md bg-black/40 text-slate-300">
              {t("verdict.scoreLabel", "Risk Score")}: {Math.round(risk_score * 100)}%
            </span>
            <span className="text-xs font-bold px-3 py-1 rounded-full bg-slate-800 text-indigo-300 border border-slate-700">
              {t("verdict.categoryLabel", "Category")}: {translatedCategory}
            </span>
          </div>

          <h2 className="text-2xl md:text-3xl font-black tracking-tight text-white mt-1">
            {currentConfig.title}
          </h2>

          <p className={`text-base md:text-lg font-medium mt-1.5 ${currentConfig.textColor}`}>
            {currentConfig.tagline}
          </p>
        </div>
      </div>

      {/* Voice Guidance Button */}
      <div className="mt-4 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
        <button
          onClick={handlePlayVoice}
          className={`min-h-touch px-4 py-2.5 rounded-xl font-bold flex items-center gap-2 text-white shadow-md transition-all ${
            isPlayingAudio
              ? "bg-amber-600 animate-pulse"
              : "bg-indigo-600 hover:bg-indigo-500"
          }`}
        >
          {isPlayingAudio ? (
            <>
              <VolumeX className="w-5 h-5" />
              <span>{t("verdict.playingAudio", "Stop Voice")}</span>
            </>
          ) : (
            <>
              <Volume2 className="w-5 h-5" />
              <span>{t("verdict.listenAudio", "Listen Voice Alert")}</span>
            </>
          )}
        </button>

        {extracted_domains.length > 0 && (
          <div className="text-xs text-slate-400 flex items-center gap-1.5">
            <ExternalLink className="w-3.5 h-3.5 text-slate-500" />
            <span>
              {t("verdict.domainsDetected", "Analyzed:")}{" "}
              <strong className="text-slate-200">{extracted_domains.join(", ")}</strong>
            </span>
          </div>
        )}
      </div>

      {/* Reasons Bullet List */}
      {reason_codes.length > 0 && (
        <div className="mt-5 bg-black/40 rounded-xl p-4 border border-slate-800">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-2">
            {t("verdict.reasonsHeading", "Why this was flagged:")}
          </h3>
          <ul className="space-y-2">
            {reason_codes.map((code) => (
              <li key={code} className="flex items-start gap-2.5 text-sm md:text-base text-slate-200">
                <ChevronRight className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <span>{t(`reasons.${code}`, code)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

