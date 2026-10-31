"use client";

import React, { useEffect, useState } from "react";
import { Header } from "../../components/Header";
import { LanguageModal } from "../../components/LanguageModal";
import { useI18n } from "../../i18n/context";
import Link from "next/link";
import {
  ShieldAlert,
  ShieldCheck,
  Activity,
  Layers,
  ArrowLeft,
  Calendar,
  Globe,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  PieChart,
  Pie,
  AreaChart,
  Area,
  CartesianGrid,
  Legend,
} from "recharts";

interface SummaryStats {
  total_scans: number;
  total_flagged: number;
  total_safe: number;
  flagged_percentage: number;
  by_risk_level: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
}

interface CategoryCount {
  category: string;
  count: number;
}

interface TimelinePoint {
  date: string;
  flagged: number;
  safe: number;
  total: number;
}

interface LanguageCount {
  language: string;
  count: number;
}

const RISK_COLORS: Record<string, string> = {
  critical: "#dc2626",
  high: "#f97316",
  medium: "#f59e0b",
  low: "#10b981",
};

export default function StatsPage() {
  const { t } = useI18n();
  const [summary, setSummary] = useState<SummaryStats | null>(null);
  const [categories, setCategories] = useState<CategoryCount[]>([]);
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  const [languages, setLanguages] = useState<LanguageCount[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchStats() {
      try {
        setLoading(true);
        const [sumRes, catRes, timeRes, langRes] = await Promise.all([
          fetch("/api/stats/summary").then((r) => r.json()),
          fetch("/api/stats/categories").then((r) => r.json()),
          fetch("/api/stats/timeline?days=7").then((r) => r.json()),
          fetch("/api/stats/by-language").then((r) => r.json()),
        ]);

        setSummary(sumRes);
        setCategories(catRes || []);
        setTimeline(timeRes || []);
        setLanguages(langRes || []);
      } catch (err: any) {
        setError("Unable to load threat intelligence telemetry.");
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  // Format data for Pie Chart
  const pieData = summary
    ? [
        { name: "Critical", value: summary.by_risk_level.critical, color: RISK_COLORS.critical },
        { name: "High", value: summary.by_risk_level.high, color: RISK_COLORS.high },
        { name: "Medium", value: summary.by_risk_level.medium, color: RISK_COLORS.medium },
        { name: "Safe", value: summary.by_risk_level.low, color: RISK_COLORS.low },
      ].filter((d) => d.value > 0)
    : [];

  return (
    <div className="min-h-screen flex flex-col justify-between bg-slate-950 text-white">
      <Header />
      <LanguageModal />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-6 md:py-8 space-y-6">
        {/* Navigation & Title */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link
            href="/"
            className="min-h-touch px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 flex items-center gap-2 text-sm font-bold transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Scanner</span>
          </Link>

          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            Live Threat Telemetry
          </span>
        </div>

        <div className="text-center space-y-1">
          <h2 className="text-2xl md:text-3xl font-black tracking-tight text-white">
            India Threat Intelligence Dashboard
          </h2>
          <p className="text-sm md:text-base text-slate-400">
            Real-time metadata on phishing, fake UPI requests, and SMS scams caught across India
          </p>
        </div>

        {loading ? (
          <div className="py-24 flex flex-col items-center justify-center gap-3">
            <Loader2 className="w-10 h-10 animate-spin text-indigo-400" />
            <p className="text-slate-400 font-medium">Loading telemetry analytics...</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-red-950/50 border border-red-800 rounded-2xl text-center text-red-300">
            {error}
          </div>
        ) : (
          <>
            {/* KPI Summary Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 md:p-5 shadow-lg">
                <div className="flex items-center justify-between text-slate-400 mb-1">
                  <span className="text-xs uppercase font-bold tracking-wider">Total Scans</span>
                  <Activity className="w-4 h-4 text-indigo-400" />
                </div>
                <div className="text-2xl md:text-4xl font-black text-white">
                  {summary?.total_scans || 0}
                </div>
                <div className="text-xs text-slate-400 mt-1">Zero raw data stored</div>
              </div>

              <div className="bg-slate-900 border border-red-900/40 rounded-2xl p-4 md:p-5 shadow-lg">
                <div className="flex items-center justify-between text-slate-400 mb-1">
                  <span className="text-xs uppercase font-bold tracking-wider">Scams Flagged</span>
                  <ShieldAlert className="w-4 h-4 text-red-400" />
                </div>
                <div className="text-2xl md:text-4xl font-black text-red-400">
                  {summary?.total_flagged || 0}
                </div>
                <div className="text-xs text-red-300/80 mt-1">
                  {summary?.flagged_percentage || 0}% threat rate
                </div>
              </div>

              <div className="bg-slate-900 border border-emerald-900/40 rounded-2xl p-4 md:p-5 shadow-lg">
                <div className="flex items-center justify-between text-slate-400 mb-1">
                  <span className="text-xs uppercase font-bold tracking-wider">Safe Messages</span>
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="text-2xl md:text-4xl font-black text-emerald-400">
                  {summary?.total_safe || 0}
                </div>
                <div className="text-xs text-emerald-300/80 mt-1">Verified legitimate</div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 md:p-5 shadow-lg">
                <div className="flex items-center justify-between text-slate-400 mb-1">
                  <span className="text-xs uppercase font-bold tracking-wider">Languages</span>
                  <Globe className="w-4 h-4 text-amber-400" />
                </div>
                <div className="text-2xl md:text-4xl font-black text-white">5</div>
                <div className="text-xs text-slate-400 mt-1">hi, bn, mr, kn, en</div>
              </div>
            </div>

            {/* Charts Row 1: 7-Day Trend Timeline & Risk Distribution */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* 7-Day Timeline Area Chart */}
              <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-indigo-400" />
                    <h3 className="font-bold text-lg text-white">7-Day Threat Timeline</h3>
                  </div>
                  <span className="text-xs text-slate-400">Daily Threat Volume</span>
                </div>

                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={timeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="flaggedGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                          <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0} />
                        </linearGradient>
                        <linearGradient id="safeGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 12 }} />
                      <YAxis stroke="#64748b" tick={{ fontSize: 12 }} allowDecimals={false} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#0f172a",
                          borderColor: "#334155",
                          borderRadius: "12px",
                          color: "#fff",
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="flagged"
                        name="Scams Caught"
                        stroke="#ef4444"
                        fillOpacity={1}
                        fill="url(#flaggedGrad)"
                      />
                      <Area
                        type="monotone"
                        dataKey="safe"
                        name="Safe Messages"
                        stroke="#10b981"
                        fillOpacity={1}
                        fill="url(#safeGrad)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Risk Distribution Donut Chart */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-amber-400" />
                  <h3 className="font-bold text-lg text-white">Risk Distribution</h3>
                </div>

                <div className="h-64 w-full flex items-center justify-center">
                  {pieData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={pieData}
                          cx="50%"
                          cy="50%"
                          innerRadius={55}
                          outerRadius={80}
                          paddingAngle={4}
                          dataKey="value"
                        >
                          {pieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#0f172a",
                            borderColor: "#334155",
                            borderRadius: "12px",
                            color: "#fff",
                          }}
                        />
                        <Legend
                          verticalAlign="bottom"
                          height={36}
                          formatter={(value) => <span className="text-xs text-slate-300 font-semibold">{value}</span>}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="text-xs text-slate-500">No threat distribution data yet</p>
                  )}
                </div>
              </div>
            </div>

            {/* Charts Row 2: Top Fraud Categories Bar Chart */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Layers className="w-5 h-5 text-indigo-400" />
                  <h3 className="font-bold text-lg text-white">Top Scams Caught by Category</h3>
                </div>
                <span className="text-xs text-slate-400">Medium & High Risk Incidents</span>
              </div>

              <div className="h-72 w-full">
                {categories.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={categories}
                      layout="vertical"
                      margin={{ top: 10, right: 20, left: 60, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                      <XAxis type="number" stroke="#64748b" tick={{ fontSize: 12 }} allowDecimals={false} />
                      <YAxis
                        type="category"
                        dataKey="category"
                        stroke="#94a3b8"
                        tick={{ fontSize: 11 }}
                        width={130}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#0f172a",
                          borderColor: "#334155",
                          borderRadius: "12px",
                          color: "#fff",
                        }}
                      />
                      <Bar dataKey="count" name="Incidents" fill="#6366f1" radius={[0, 8, 8, 0]}>
                        {categories.map((entry, index) => (
                          <Cell
                            key={`cat-${index}`}
                            fill={index === 0 ? "#ef4444" : index === 1 ? "#f97316" : "#6366f1"}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-slate-500 text-sm">
                    No confirmed threats recorded in database yet.
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </main>

      <footer className="w-full bg-slate-950 border-t border-slate-900 py-6 text-center text-xs text-slate-500 px-4">
        ScamShield India • DPDP Act 2023 Compliant • Anonymous Threat Telemetry Only
      </footer>
    </div>
  );
}

