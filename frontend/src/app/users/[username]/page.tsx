"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, User, Contribution, ManualEntry } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { ContributionCard } from "@/components/ContributionCard";
import { ManualEntryForm } from "@/components/ManualEntryForm";
import { ManualEntryCard } from "@/components/ManualEntryCard";
import {
  GitPullRequest, Eye, CheckSquare, BookOpen, Plus, RefreshCw, FileText,
} from "lucide-react";

export default function UserProfilePage() {
  const params = useParams();
  const username = params.username as string;
  const { user: currentUser } = useAuth();
  const isOwner = currentUser?.username === username;

  const [profile, setProfile] = useState<User | null>(null);
  const [contributions, setContributions] = useState<Contribution[]>([]);
  const [manualEntries, setManualEntries] = useState<ManualEntry[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [collecting, setCollecting] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState("all");

  useEffect(() => {
    loadData();
  }, [username]);

  async function loadData() {
    setLoading(true);
    try {
      const [u, c, m] = await Promise.all([
        api.users.get(username),
        isOwner ? api.contributions.mine() : api.contributions.forUser(username),
        isOwner ? api.manualEntries.mine() : api.manualEntries.forUser(username),
      ]);
      setProfile(u);
      setContributions(c);
      setManualEntries(m);
    } catch (err) {
      console.error("Failed to load user data", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCollect() {
    setCollecting(true);
    try {
      await api.reports.triggerCollection();
      await loadData();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setCollecting(false);
    }
  }

  async function handleGenerateReport() {
    setGenerating(true);
    try {
      await api.reports.triggerReport();
      alert("Report generated! Check the Reports page.");
    } catch (err: any) {
      alert(err.message);
    } finally {
      setGenerating(false);
    }
  }

  const prsRaised = contributions.filter((c) => ["pr_raised", "mr_raised"].includes(c.contribution_type));
  const prsReviewed = contributions.filter((c) => ["pr_reviewed", "mr_reviewed"].includes(c.contribution_type));
  const tickets = contributions.filter((c) => ["ticket_created", "ticket_assigned"].includes(c.contribution_type));
  const docs = contributions.filter((c) => ["doc_created", "doc_updated"].includes(c.contribution_type));

  const tabs = [
    { id: "all", label: "All", count: contributions.length + manualEntries.length },
    { id: "prs_raised", label: "PRs Raised", count: prsRaised.length, icon: <GitPullRequest className="w-4 h-4" /> },
    { id: "prs_reviewed", label: "Reviews", count: prsReviewed.length, icon: <Eye className="w-4 h-4" /> },
    { id: "tickets", label: "Tickets", count: tickets.length, icon: <CheckSquare className="w-4 h-4" /> },
    { id: "docs", label: "Docs", count: docs.length, icon: <BookOpen className="w-4 h-4" /> },
    { id: "manual", label: "Manual", count: manualEntries.length, icon: <Plus className="w-4 h-4" /> },
  ];

  const filteredContributions = activeTab === "all" ? contributions
    : activeTab === "prs_raised" ? prsRaised
    : activeTab === "prs_reviewed" ? prsReviewed
    : activeTab === "tickets" ? tickets
    : activeTab === "docs" ? docs
    : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600"></div>
      </div>
    );
  }

  if (!profile) {
    return <p className="text-center text-gray-500 mt-20">User not found</p>;
  }

  return (
    <div className="space-y-8">
      <div className="bg-white rounded-xl border border-gray-200 p-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          {profile.avatar_url ? (
            <img src={profile.avatar_url} alt="" className="w-16 h-16 rounded-full" />
          ) : (
            <div className="w-16 h-16 rounded-full bg-brand-100 flex items-center justify-center text-brand-600 font-bold text-2xl">
              {profile.display_name.charAt(0).toUpperCase()}
            </div>
          )}
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{profile.display_name}</h1>
            <p className="text-gray-500">@{profile.username}</p>
            <div className="flex gap-3 mt-1 text-xs text-gray-400">
              {profile.github_username && <span>GitHub: {profile.github_username}</span>}
              {profile.gitlab_username && <span>GitLab: {profile.gitlab_username}</span>}
            </div>
          </div>
        </div>
        {isOwner && (
          <div className="flex gap-3">
            <button
              onClick={handleCollect}
              disabled={collecting}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${collecting ? "animate-spin" : ""}`} />
              {collecting ? "Collecting..." : "Sync Data"}
            </button>
            <button
              onClick={handleGenerateReport}
              disabled={generating}
              className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg text-sm hover:bg-brand-700 transition disabled:opacity-50"
            >
              <FileText className="w-4 h-4" />
              {generating ? "Generating..." : "Generate Report"}
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard label="PRs Raised" value={prsRaised.length} />
        <StatCard label="PRs Reviewed" value={prsReviewed.length} />
        <StatCard label="Jira Tickets" value={tickets.length} />
        <StatCard label="Docs" value={docs.length} />
        <StatCard label="Other" value={manualEntries.length} />
      </div>

      <div className="flex items-center gap-2 border-b border-gray-200 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-1.5 px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap transition ${
              activeTab === tab.id
                ? "border-brand-600 text-brand-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {tab.icon}
            {tab.label}
            <span className="bg-gray-100 text-gray-600 text-xs px-1.5 py-0.5 rounded-full ml-1">
              {tab.count}
            </span>
          </button>
        ))}
      </div>

      {isOwner && (activeTab === "all" || activeTab === "manual") && (
        <div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 text-brand-600 hover:text-brand-700 text-sm font-medium"
          >
            <Plus className="w-4 h-4" />
            {showForm ? "Cancel" : "Add Manual Entry"}
          </button>
          {showForm && (
            <div className="mt-4">
              <ManualEntryForm
                onCreated={() => {
                  setShowForm(false);
                  loadData();
                }}
              />
            </div>
          )}
        </div>
      )}

      <div className="space-y-3">
        {(activeTab === "all" || activeTab === "manual") &&
          manualEntries.map((entry) => (
            <ManualEntryCard
              key={entry.id}
              entry={entry}
              isOwner={isOwner}
              onDelete={async () => {
                await api.manualEntries.delete(entry.id);
                loadData();
              }}
            />
          ))}
        {filteredContributions.map((c) => (
          <ContributionCard key={c.id} contribution={c} />
        ))}
        {filteredContributions.length === 0 && (activeTab !== "all" && activeTab !== "manual") && (
          <p className="text-center text-gray-400 py-12">No items in this category yet</p>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      <div className="text-xs text-gray-500 mt-1">{label}</div>
    </div>
  );
}
