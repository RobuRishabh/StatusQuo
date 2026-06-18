"use client";

import { ManualEntry } from "@/lib/api";
import { PenLine, Award, Mic, Building2, FileText, ExternalLink, Trash2, Image } from "lucide-react";

const TYPE_CONFIG: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  blog: { icon: <PenLine className="w-4 h-4" />, color: "bg-emerald-100 text-emerald-700", label: "Blog Post" },
  talk: { icon: <Mic className="w-4 h-4" />, color: "bg-orange-100 text-orange-700", label: "Talk" },
  award: { icon: <Award className="w-4 h-4" />, color: "bg-yellow-100 text-yellow-700", label: "Award" },
  org_membership: { icon: <Building2 className="w-4 h-4" />, color: "bg-sky-100 text-sky-700", label: "Org Membership" },
  other: { icon: <FileText className="w-4 h-4" />, color: "bg-gray-100 text-gray-700", label: "Other" },
};

export function ManualEntryCard({
  entry,
  isOwner,
  onDelete,
}: {
  entry: ManualEntry;
  isOwner: boolean;
  onDelete: () => void;
}) {
  const config = TYPE_CONFIG[entry.entry_type] || TYPE_CONFIG.other;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-sm transition">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 min-w-0">
          <div className={`flex-shrink-0 p-2 rounded-lg ${config.color}`}>
            {config.icon}
          </div>
          <div className="min-w-0">
            <div className="font-medium text-gray-900 flex items-center gap-2">
              <span className="truncate">{entry.title}</span>
              {entry.proof_url && (
                <a href={entry.proof_url} target="_blank" rel="noopener noreferrer" className="flex-shrink-0 text-gray-400 hover:text-brand-600">
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
            {entry.description && (
              <p className="text-sm text-gray-600 mt-1">{entry.description}</p>
            )}
            {entry.proof_photos && entry.proof_photos.length > 0 && (
              <div className="flex gap-2 mt-2">
                {entry.proof_photos.map((photo, i) => (
                  <a key={i} href={photo} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-xs text-brand-600 hover:underline">
                    <Image className="w-3 h-3" />
                    Photo {i + 1}
                  </a>
                ))}
              </div>
            )}
            <div className="flex items-center gap-2 mt-2 text-xs text-gray-400">
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
                {config.label}
              </span>
              {entry.event_date && <span>· {entry.event_date}</span>}
              <span>· Manual entry</span>
            </div>
          </div>
        </div>
        {isOwner && (
          <button onClick={onDelete} className="text-gray-400 hover:text-red-600 flex-shrink-0 p-1" title="Delete">
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}
