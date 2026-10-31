"use client";

import React from "react";
import { useI18n, SUPPORTED_LANGUAGES, LanguageCode } from "../i18n/context";
import { Globe, Check } from "lucide-react";

export function LanguageModal() {
  const { language, setLanguage, showPicker, setShowPicker, t } = useI18n();

  if (!showPicker) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border-2 border-indigo-500/50 rounded-2xl w-full max-w-md p-6 shadow-2xl text-white">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-indigo-600/30 text-indigo-400 mb-3">
            <Globe className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight">
            {t("languagePicker.title", "Choose your language")}
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            {t("languagePicker.subtitle", "अपनी भाषा चुनें • আপনার ভাষা নির্বাচন করুন")}
          </p>
        </div>

        <div className="space-y-3">
          {SUPPORTED_LANGUAGES.map((item) => {
            const isSelected = language === item.code;
            return (
              <button
                key={item.code}
                onClick={() => setLanguage(item.code)}
                className={`w-full min-h-[56px] px-5 py-3 rounded-xl flex items-center justify-between transition-all border-2 text-left ${
                  isSelected
                    ? "bg-indigo-600/40 border-indigo-400 text-white font-bold shadow-lg shadow-indigo-500/20"
                    : "bg-slate-800/80 border-slate-700 hover:border-slate-500 text-slate-200"
                }`}
              >
                <div>
                  <span className="text-xl block">{item.nativeName}</span>
                  <span className="text-xs text-slate-400 block">{item.englishName}</span>
                </div>
                {isSelected && (
                  <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-white">
                    <Check className="w-5 h-5 stroke-[3]" />
                  </div>
                )}
              </button>
            );
          })}
        </div>

        <div className="mt-6 text-center">
          <button
            onClick={() => setShowPicker(false)}
            className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-lg shadow-md transition-colors"
          >
            {t("languagePicker.confirm", "Continue")}
          </button>
        </div>
      </div>
    </div>
  );
}

