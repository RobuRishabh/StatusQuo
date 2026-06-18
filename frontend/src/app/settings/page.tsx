"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { Settings, Save, Check } from "lucide-react";

export default function SettingsPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({
    display_name: "",
    email: "",
    github_username: "",
    gitlab_username: "",
    jira_account_id: "",
    confluence_account_id: "",
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
    if (user) {
      setForm({
        display_name: user.display_name || "",
        email: user.email || "",
        github_username: user.github_username || "",
        gitlab_username: user.gitlab_username || "",
        jira_account_id: user.jira_account_id || "",
        confluence_account_id: user.confluence_account_id || "",
      });
    }
  }, [user, authLoading]);

  const update = (field: string, value: string) => setForm((f) => ({ ...f, [field]: value }));

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.users.update(form);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || !user) return null;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Settings className="w-6 h-6 text-gray-600" />
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
      </div>

      <form onSubmit={handleSave} className="bg-white rounded-xl border border-gray-200 p-6 space-y-5">
        <h2 className="font-semibold text-gray-800">Profile</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Display Name</label>
            <input type="text" value={form.display_name} onChange={(e) => update("display_name", e.target.value)} className="w-full px-3 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input type="email" value={form.email} onChange={(e) => update("email", e.target.value)} className="w-full px-3 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
        </div>

        <hr className="border-gray-100" />
        <h2 className="font-semibold text-gray-800">Connected Accounts</h2>
        <p className="text-sm text-gray-500">Link your accounts so StatusQuo can auto-collect your contributions.</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">GitHub Username</label>
            <input type="text" value={form.github_username} onChange={(e) => update("github_username", e.target.value)} className="w-full px-3 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-500" placeholder="octocat" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">GitLab Username</label>
            <input type="text" value={form.gitlab_username} onChange={(e) => update("gitlab_username", e.target.value)} className="w-full px-3 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-500" placeholder="gitlabuser" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Jira Account ID</label>
            <input type="text" value={form.jira_account_id} onChange={(e) => update("jira_account_id", e.target.value)} className="w-full px-3 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-500" placeholder="5a09xxxxxxxx" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Confluence Account ID</label>
            <input type="text" value={form.confluence_account_id} onChange={(e) => update("confluence_account_id", e.target.value)} className="w-full px-3 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-500" placeholder="5a09xxxxxxxx" />
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 bg-brand-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-brand-700 transition disabled:opacity-50"
          >
            {saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
            {saved ? "Saved!" : saving ? "Saving..." : "Save Settings"}
          </button>
        </div>
      </form>
    </div>
  );
}
