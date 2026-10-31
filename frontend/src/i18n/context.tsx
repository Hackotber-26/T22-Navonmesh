"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import enData from "./en.json";
import hiData from "./hi.json";
import bnData from "./bn.json";
import mrData from "./mr.json";
import knData from "./kn.json";

export type LanguageCode = "hi" | "bn" | "mr" | "kn" | "en";
export type TextSize = "normal" | "large";

export interface LanguageOption {
  code: LanguageCode;
  nativeName: string;
  englishName: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: "hi", nativeName: "हिन्दी", englishName: "Hindi" },
  { code: "bn", nativeName: "বাংলা", englishName: "Bengali" },
  { code: "mr", nativeName: "मराठी", englishName: "Marathi" },
  { code: "kn", nativeName: "ಕನ್ನಡ", englishName: "Kannada" },
  { code: "en", nativeName: "English", englishName: "English" },
];

const translations: Record<LanguageCode, any> = {
  en: enData,
  hi: hiData,
  bn: bnData,
  mr: mrData,
  kn: knData,
};

interface I18nContextType {
  language: LanguageCode;
  setLanguage: (lang: LanguageCode) => void;
  textSize: TextSize;
  setTextSize: (size: TextSize) => void;
  toggleTextSize: () => void;
  showPicker: boolean;
  setShowPicker: (show: boolean) => void;
  t: (path: string, fallback?: string) => string;
}

const I18nContext = createContext<I18nContextType | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLangState] = useState<LanguageCode>("hi");
  const [textSize, setTextSizeState] = useState<TextSize>("large"); // Default to large for elderly accessibility
  const [showPicker, setShowPicker] = useState<boolean>(false);
  const [mounted, setMounted] = useState<boolean>(false);

  useEffect(() => {
    // 1. Check if user already picked language
    const savedLang = localStorage.getItem("scamshield_lang") as LanguageCode;
    if (savedLang && translations[savedLang]) {
      setLangState(savedLang);
    } else {
      // First-time launch: display language selector modal
      setShowPicker(true);
    }

    // 2. Check font size preference
    const savedSize = localStorage.getItem("scamshield_font_size") as TextSize;
    if (savedSize === "normal" || savedSize === "large") {
      setTextSizeState(savedSize);
    }

    setMounted(true);
  }, []);

  const setLanguage = (lang: LanguageCode) => {
    setLangState(lang);
    localStorage.setItem("scamshield_lang", lang);
    setShowPicker(false);
  };

  const setTextSize = (size: TextSize) => {
    setTextSizeState(size);
    localStorage.setItem("scamshield_font_size", size);
  };

  const toggleTextSize = () => {
    const nextSize = textSize === "large" ? "normal" : "large";
    setTextSize(nextSize);
  };

  // Nested translation lookup with English fallback
  const t = (path: string, fallback: string = ""): string => {
    const keys = path.split(".");
    let current: any = translations[language];
    for (const key of keys) {
      if (current && typeof current === "object" && key in current) {
        current = current[key];
      } else {
        current = undefined;
        break;
      }
    }

    if (typeof current === "string") {
      return current;
    }

    // Fallback to English
    let fallbackCurr: any = translations["en"];
    for (const key of keys) {
      if (fallbackCurr && typeof fallbackCurr === "object" && key in fallbackCurr) {
        fallbackCurr = fallbackCurr[key];
      } else {
        fallbackCurr = undefined;
        break;
      }
    }

    if (typeof fallbackCurr === "string") {
      return fallbackCurr;
    }

    return fallback || path;
  };

  return (
    <I18nContext.Provider
      value={{
        language,
        setLanguage,
        textSize,
        setTextSize,
        toggleTextSize,
        showPicker,
        setShowPicker,
        t,
      }}
    >
      <div className={textSize === "large" ? "text-lg md:text-xl" : "text-base"}>
        {children}
      </div>
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used within an I18nProvider");
  }
  return context;
}

