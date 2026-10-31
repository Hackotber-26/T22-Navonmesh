"use client";

import React, { useState } from "react";
import { useI18n } from "../i18n/context";
import { ShieldCheck, MousePointerClick, AlertOctagon, Check } from "lucide-react";

export type UserActionState = "not_acted" | "clicked" | "paid";

interface ActionStateSelectorProps {
  currentState: UserActionState;
  onStateChange: (newState: UserActionState) => void;
  isLoading?: boolean;
}

export function ActionStateSelector({
  currentState,
  onStateChange,
  isLoading = false,
}: ActionStateSelectorProps) {
  const { t } = useI18n();

  const options: {
    state: UserActionState;
    titleKey: string;
    descKey: string;
    icon: React.ElementType;
    activeBorder: string;
    activeBg: string;
    iconColor: string;
  }[] = [
    {
      state: "not_acted",
      titleKey: "actionState.not_acted.title",
      descKey: "actionState.not_acted.desc",
      icon: ShieldCheck,
      activeBorder: "border-emerald-500",
      activeBg: "bg-emerald-950/40",
      iconColor: "text-emerald-400",
    },
    {
      state: "clicked",
      titleKey: "actionState.clicked.title",
      descKey: "actionState.clicked.desc",
      icon: MousePointerClick,
      activeBorder: "border-amber-500",
      activeBg: "bg-amber-950/40",
      iconColor: "text-amber-400",
    },
    {
      state: "paid",
      titleKey: "actionState.paid.title",
      descKey: "actionState.paid.desc",
      icon: AlertOctagon,
      activeBorder: "border-red-500 animate-pulse",
      activeBg: "bg-red-950/50",
      iconColor: "text-red-400",
    },
  ];

  return (
    <div className="w-full bg-slate-900 border-2 border-slate-800 rounded-2xl p-5 md:p-6 shadow-xl space-y-4">
      <div>
        <h3 className="text-xl md:text-2xl font-black text-white flex items-center gap-2">
          {t("actionState.heading", "What did you do?")}
        </h3>
        <p className="text-sm md:text-base text-slate-400 mt-1">
          {t("actionState.prompt", "Choose your situation to see the exact steps to take:")}
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
        {options.map((opt) => {
          const isSelected = currentState === opt.state;
          const Icon = opt.icon;

          return (
            <button
              key={opt.state}
              disabled={isLoading}
              onClick={() => onStateChange(opt.state)}
              className={`min-h-[72px] p-4 rounded-xl border-2 text-left transition-all flex items-start justify-between gap-3 ${
                isSelected
                  ? `${opt.activeBorder} ${opt.activeBg} shadow-lg ring-2 ring-indigo-500/20`
                  : "border-slate-800 bg-slate-800/70 hover:border-slate-700 hover:bg-slate-800 text-slate-300"
              }`}
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Icon className={`w-5 h-5 ${opt.iconColor}`} />
                  <span className="font-bold text-base md:text-lg text-white">
                    {t(opt.titleKey, opt.state)}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  {t(opt.descKey, "")}
                </p>
              </div>

              {isSelected && (
                <div className="w-6 h-6 rounded-full bg-indigo-500 text-white flex items-center justify-center shrink-0 mt-0.5">
                  <Check className="w-4 h-4 stroke-[3]" />
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

