"use client";

import { useEffect, useState } from "react";
import { api, WeeklyReport } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { ReportView } from "@/components/ReportView";
import { FileText, Calendar } from "lucide-react";

export default function ReportsPage() {
  const { user } = useAuth();
  const [reports, setReports] = useState<WeeklyReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<WeeklyReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReports();
  }, [user]);

  async function loadReports() {
    setLoading(true);
    try {
      if (user) {
        const r = await api.reports.mine();
        setReports(r);
        if (r.length > 0) setSelectedReport(r[0]);
      }
    } catch (err) {
      console.error("Failed to load reports", err);
    } finally {
      setLoading(false);
    }
  }

  if (!user) {
    return (
      <div className="text-center py-20">
        <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-700 mb-2">Sign in to view reports</h2>
        <p className="text-gray-500">Your weekly status reports will appear here</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">My Weekly Reports</h1>
      </div>

      {reports.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-gray-200">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-gray-700 mb-2">No reports yet</h2>
          <p className="text-gray-500 mb-4">
            Reports are generated every Friday at 6 PM EST, or you can trigger one manually from your profile.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="p-4 border-b border-gray-100">
                <h3 className="font-medium text-gray-700 text-sm">Report History</h3>
              </div>
              {reports.map((r) => (
                <button
                  key={r.id}
                  onClick={() => setSelectedReport(r)}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left border-b border-gray-50 last:border-0 transition ${
                    selectedReport?.id === r.id ? "bg-brand-50 text-brand-700" : "hover:bg-gray-50"
                  }`}
                >
                  <Calendar className="w-4 h-4 flex-shrink-0" />
                  <div>
                    <div className="text-sm font-medium">Week of {r.week_of}</div>
                    <div className="text-xs text-gray-500">{r.status}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="lg:col-span-3">
            {selectedReport && <ReportView report={selectedReport} />}
          </div>
        </div>
      )}
    </div>
  );
}
