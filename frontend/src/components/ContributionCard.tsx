"use client";

import { Contribution } from "@/lib/api";
import { GitPullRequest, Eye, CheckSquare, BookOpen, ExternalLink } from "lucide-react";

const TYPE_CONFIG: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  pr_raised: { icon: <GitPullRequest className="w-4 h-4" />, color: "bg-green-100 text-green-700", label: "PR Raised" },
  mr_raised: { icon: <GitPullRequest className="w-4 h-4" />, color: "bg-green-100 text-green-700", label: "MR Raised" },
  pr_reviewed: { icon: <Eye className="w-4 h-4" />, color: "bg-blue-100 text-blue-700", label: "PR Reviewed" },
  mr_reviewed: { icon: <Eye className="w-4 h-4" />, color: "bg-blue-100 text-blue-700", label: "MR Reviewed" },
  ticket_created: { icon: <CheckSquare className="w-4 h-4" />, color: "bg-purple-100 text-purple-700", label: "Ticket" },
  ticket_assigned: { icon: <CheckSquare className="w-4 h-4" />, color: "bg-purple-100 text-purple-700", label: "Ticket" },
  doc_created: { icon: <BookOpen className="w-4 h-4" />, color: "bg-amber-100 text-amber-700", label: "Doc Created" },
  doc_updated: { icon: <BookOpen className="w-4 h-4" />, color: "bg-amber-100 text-amber-700", label: "Doc Updated" },
};

const SOURCE_LABELS: Record<string, string> = {
  github: "GitHub",
  gitlab: "GitLab",
  jira: "Jira",
  confluence: "Confluence",
};

export function ContributionCard({ contribution: c }: { contribution: Contribution }) {
  const config = TYPE_CONFIG[c.contribution_type] || { icon: null, color: "bg-gray-100 text-gray-700", label: c.contribution_type };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-sm transition">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 min-w-0">
          <div className={`flex-shrink-0 p-2 rounded-lg ${config.color}`}>
            {config.icon}
          </div>
          <div className="min-w-0">
            <a
              href={c.external_url}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-gray-900 hover:text-brand-600 flex items-center gap-1"
            >
              <span className="truncate">{c.title}</span>
              <ExternalLink className="w-3.5 h-3.5 flex-shrink-0 text-gray-400" />
            </a>
            {c.ai_summary && c.ai_summary !== c.title && (
              <p className="text-sm text-gray-600 mt-1">{c.ai_summary}</p>
            )}
            <div className="flex items-center gap-2 mt-2 text-xs text-gray-400">
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
                {config.label}
              </span>
              <span>{SOURCE_LABELS[c.source] || c.source}</span>
              {c.source_instance && c.source_instance !== "cloud" && (
                <span className="bg-gray-100 px-1.5 py-0.5 rounded text-gray-500">
                  {c.source_instance}
                </span>
              )}
              {c.status && <span>· {c.status}</span>}
              <span>· {c.external_id}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
