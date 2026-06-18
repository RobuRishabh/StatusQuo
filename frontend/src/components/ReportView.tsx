"use client";

import { WeeklyReport, ReportItem, ManualReportItem } from "@/lib/api";
import {
  GitPullRequest, Eye, CheckSquare, BookOpen, PenLine, Mic,
  Award, Building2, FileText, ExternalLink, Image,
} from "lucide-react";

export function ReportView({ report }: { report: WeeklyReport }) {
  const { report_data: data } = report;
  const { summary, sections } = data;

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="bg-gradient-to-r from-brand-600 to-brand-700 p-6 text-white">
        <div className="flex items-center gap-4">
          {data.user.avatar_url ? (
            <img src={data.user.avatar_url} alt="" className="w-12 h-12 rounded-full border-2 border-white/30" />
          ) : (
            <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center font-bold text-lg">
              {data.user.display_name.charAt(0)}
            </div>
          )}
          <div>
            <h2 className="text-xl font-bold">{data.user.display_name}</h2>
            <p className="text-brand-100">Week of {data.week_of}</p>
          </div>
        </div>
        <div className="grid grid-cols-5 gap-4 mt-6">
          <MiniStat label="PRs Raised" value={summary.total_prs_raised} />
          <MiniStat label="Reviews" value={summary.total_prs_reviewed} />
          <MiniStat label="Tickets" value={summary.total_tickets} />
          <MiniStat label="Docs" value={summary.total_docs} />
          <MiniStat label="Other" value={summary.total_manual_entries} />
        </div>
      </div>

      <div className="p-6 space-y-8">
        {sections.prs_raised.length > 0 && (
          <ReportSection
            title="Pull Requests Raised"
            icon={<GitPullRequest className="w-5 h-5 text-green-600" />}
            items={sections.prs_raised}
          />
        )}
        {sections.prs_reviewed.length > 0 && (
          <ReportSection
            title="Pull Requests Reviewed"
            icon={<Eye className="w-5 h-5 text-blue-600" />}
            items={sections.prs_reviewed}
          />
        )}
        {sections.jira_tickets.length > 0 && (
          <ReportSection
            title="Jira Tickets"
            icon={<CheckSquare className="w-5 h-5 text-purple-600" />}
            items={sections.jira_tickets}
          />
        )}
        {sections.confluence_docs.length > 0 && (
          <ReportSection
            title="Confluence Documents"
            icon={<BookOpen className="w-5 h-5 text-amber-600" />}
            items={sections.confluence_docs}
          />
        )}
        {sections.manual_entries.length > 0 && (
          <ManualSection items={sections.manual_entries} />
        )}
        {Object.values(sections).every((s) => s.length === 0) && (
          <p className="text-center text-gray-400 py-8">No contributions recorded for this week</p>
        )}
      </div>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="text-center">
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-xs text-brand-200">{label}</div>
    </div>
  );
}

function ReportSection({ title, icon, items }: { title: string; icon: React.ReactNode; items: ReportItem[] }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        {icon}
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{items.length}</span>
      </div>
      <div className="space-y-2">
        {items.map((item) => (
          <div key={item.id} className="flex items-start gap-3 pl-7">
            <span className="text-gray-400 mt-1.5">-</span>
            <div>
              <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-sm text-gray-800 hover:text-brand-600 inline-flex items-center gap-1">
                {item.summary}
                <ExternalLink className="w-3 h-3 text-gray-400" />
              </a>
              {item.status && (
                <span className="ml-2 text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">{item.status}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const MANUAL_ICONS: Record<string, React.ReactNode> = {
  blog: <PenLine className="w-4 h-4" />,
  talk: <Mic className="w-4 h-4" />,
  award: <Award className="w-4 h-4" />,
  org_membership: <Building2 className="w-4 h-4" />,
  other: <FileText className="w-4 h-4" />,
};

function ManualSection({ items }: { items: ManualReportItem[] }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <Award className="w-5 h-5 text-yellow-600" />
        <h3 className="font-semibold text-gray-900">Other Accomplishments</h3>
        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{items.length}</span>
      </div>
      <div className="space-y-2">
        {items.map((item) => (
          <div key={item.id} className="flex items-start gap-3 pl-7">
            <span className="text-gray-400 mt-0.5">{MANUAL_ICONS[item.type] || MANUAL_ICONS.other}</span>
            <div>
              <div className="text-sm text-gray-800">
                {item.title}
                {item.proof_url && (
                  <a href={item.proof_url} target="_blank" rel="noopener noreferrer" className="ml-1 inline-flex items-center text-brand-600 hover:underline">
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
              {item.description && (
                <p className="text-xs text-gray-500 mt-0.5">{item.description}</p>
              )}
              {item.photos.length > 0 && (
                <div className="flex gap-2 mt-1">
                  {item.photos.map((p, i) => (
                    <a key={i} href={p} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-xs text-brand-600 hover:underline">
                      <Image className="w-3 h-3" />
                      Photo {i + 1}
                    </a>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
