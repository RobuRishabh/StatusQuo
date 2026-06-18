"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, User } from "@/lib/api";
import { Search, BarChart3, GitPullRequest, BookOpen, CheckSquare, Award } from "lucide-react";

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<User[]>([]);
  const [searching, setSearching] = useState(false);
  const router = useRouter();

  const handleSearch = async (q: string) => {
    setQuery(q);
    if (q.length < 1) {
      setResults([]);
      return;
    }
    setSearching(true);
    try {
      const users = await api.users.search(q);
      setResults(users);
    } catch {
      setResults([]);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-12">
      <section className="text-center pt-12 pb-8">
        <div className="flex justify-center mb-6">
          <div className="bg-brand-100 p-4 rounded-2xl">
            <BarChart3 className="w-12 h-12 text-brand-600" />
          </div>
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">StatusQuo</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Automated weekly status reports. Track PRs, tickets, docs, and more
          across GitHub, GitLab, Jira, and Confluence.
        </p>
      </section>

      <section className="max-w-2xl mx-auto">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by username or name..."
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            className="w-full pl-12 pr-4 py-4 rounded-xl border border-gray-300 bg-white shadow-sm text-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
          />
        </div>

        {results.length > 0 && (
          <div className="mt-3 bg-white rounded-xl border border-gray-200 shadow-lg overflow-hidden">
            {results.map((user) => (
              <button
                key={user.id}
                onClick={() => router.push(`/users/${user.username}`)}
                className="w-full flex items-center gap-4 px-5 py-4 hover:bg-gray-50 transition border-b border-gray-100 last:border-b-0"
              >
                {user.avatar_url ? (
                  <img src={user.avatar_url} alt="" className="w-10 h-10 rounded-full" />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-brand-100 flex items-center justify-center text-brand-600 font-bold">
                    {user.display_name.charAt(0).toUpperCase()}
                  </div>
                )}
                <div className="text-left">
                  <div className="font-medium text-gray-900">{user.display_name}</div>
                  <div className="text-sm text-gray-500">@{user.username}</div>
                </div>
              </button>
            ))}
          </div>
        )}

        {query.length > 0 && !searching && results.length === 0 && (
          <p className="text-center text-gray-500 mt-6">No users found for &quot;{query}&quot;</p>
        )}
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 pt-8">
        <FeatureCard icon={<GitPullRequest className="w-6 h-6" />} title="PRs & MRs" desc="Auto-tracks pull requests raised and reviewed across GitHub and GitLab" />
        <FeatureCard icon={<CheckSquare className="w-6 h-6" />} title="Jira Tickets" desc="Captures tickets, progress, and proof from Git PR fields and comments" />
        <FeatureCard icon={<BookOpen className="w-6 h-6" />} title="Confluence Docs" desc="Tracks new and updated documentation pages per user" />
        <FeatureCard icon={<Award className="w-6 h-6" />} title="Manual Entries" desc="Add blogs, talks, awards, and org memberships with proof" />
      </section>
    </div>
  );
}

function FeatureCard({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition">
      <div className="text-brand-600 mb-3">{icon}</div>
      <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-500">{desc}</p>
    </div>
  );
}
