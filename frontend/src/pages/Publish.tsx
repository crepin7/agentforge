import { useState } from "react";

const CATEGORIES = ["utility", "content", "developer", "news", "marketing", "creative"];
const RUNTIMES = [
  { value: "llm_prompt", label: "LLM prompt (OpenAI / Anthropic / Google)" },
  { value: "webhook", label: "Webhook (appelle un endpoint HTTP)" },
  { value: "python", label: "Python (execute un script)" },
];

export default function PublishPage() {
  const [form, setForm] = useState({
    name: "",
    description: "",
    category: "utility",
    runtime_type: "llm_prompt",
    price_cents: 0,
    user_prompt: "",
  });

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-2 text-3xl font-bold">Publish an agent</h1>
      <p className="mb-6 text-zinc-400">Share your agent with the community and earn from every run.</p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          alert("Publication requires authentication (TODO: connect to /auth endpoints).");
        }}
        className="space-y-4"
      >
        <div>
          <label className="mb-1 block text-sm font-medium">Name</label>
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm focus:border-violet-500 focus:outline-none" required />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Description</label>
          <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={3} className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm focus:border-violet-500 focus:outline-none" required />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Category</label>
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm">
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Runtime</label>
            <select value={form.runtime_type} onChange={(e) => setForm({ ...form, runtime_type: e.target.value })} className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm">
              {RUNTIMES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
          </div>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Price (cents, 0 = free)</label>
          <input type="number" min="0" value={form.price_cents} onChange={(e) => setForm({ ...form, price_cents: Number(e.target.value) })} className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Prompt template</label>
          <textarea value={form.user_prompt} onChange={(e) => setForm({ ...form, user_prompt: e.target.value })} rows={4} placeholder="Translate the following text to {language}: {text}" className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 font-mono text-xs" />
        </div>
        <button type="submit" className="btn-primary w-full">Publish agent</button>
      </form>
    </div>
  );
}