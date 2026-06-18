"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { Upload } from "lucide-react";

const ENTRY_TYPES = [
  { value: "blog", label: "Blog Post" },
  { value: "talk", label: "Presentation / Talk" },
  { value: "award", label: "Award / Recognition" },
  { value: "org_membership", label: "Organization Membership" },
  { value: "other", label: "Other" },
];

export function ManualEntryForm({ onCreated }: { onCreated: () => void }) {
  const [form, setForm] = useState({
    entry_type: "blog",
    title: "",
    description: "",
    proof_url: "",
    event_date: "",
  });
  const [photos, setPhotos] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const update = (field: string, value: string) => setForm((f) => ({ ...f, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const entry = await api.manualEntries.create({
        ...form,
        description: form.description || undefined,
        proof_url: form.proof_url || undefined,
        event_date: form.event_date || undefined,
      });
      if (photos.length > 0) {
        await api.manualEntries.uploadPhotos(entry.id, photos);
      }
      onCreated();
    } catch (err: any) {
      setError(err.message || "Failed to create entry");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <h3 className="font-semibold text-gray-900">Add Manual Entry</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select
            value={form.entry_type}
            onChange={(e) => update("entry_type", e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-500 bg-white"
          >
            {ENTRY_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Event Date</label>
          <input
            type="date"
            value={form.event_date}
            onChange={(e) => update("event_date", e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
        <input
          type="text"
          value={form.title}
          onChange={(e) => update("title", e.target.value)}
          placeholder="e.g. Published blog on Kubernetes security"
          className="w-full px-3 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          value={form.description}
          onChange={(e) => update("description", e.target.value)}
          rows={3}
          placeholder="Brief description of what you did..."
          className="w-full px-3 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Proof URL</label>
        <input
          type="url"
          value={form.proof_url}
          onChange={(e) => update("proof_url", e.target.value)}
          placeholder="https://blog.example.com/my-post"
          className="w-full px-3 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Event Photos</label>
        <label className="flex items-center gap-2 px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-brand-400 transition">
          <Upload className="w-5 h-5 text-gray-400" />
          <span className="text-sm text-gray-500">
            {photos.length > 0 ? `${photos.length} file(s) selected` : "Click to upload photos"}
          </span>
          <input
            type="file"
            multiple
            accept="image/*"
            className="hidden"
            onChange={(e) => setPhotos(Array.from(e.target.files || []))}
          />
        </label>
      </div>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      <div className="flex justify-end gap-3">
        <button
          type="submit"
          disabled={loading}
          className="bg-brand-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-brand-700 transition disabled:opacity-50"
        >
          {loading ? "Saving..." : "Add Entry"}
        </button>
      </div>
    </form>
  );
}
