import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Search, TrendingUp, Star } from "lucide-react";
import { useState } from "react";
import { agentsApi } from "../lib/api";

const CATEGORIES = ["all", "utility", "content", "developer", "news", "marketing"];

export default function DiscoverPage() {
  const [category, setCategory] = useState("all");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<"popular" | "newest" | "top_rated">("popular");

  const { data: agents = [], isLoading } = useQuery({
    queryKey: ["agents", category, search, sort],
    queryFn: () => agentsApi.list({ category: category === "all" ? undefined : category, search: search || undefined, sort }),
  });

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Discover agents</h1>
        <p className="mt-2 text-zinc-400">Find the perfect AI agent for any task.</p>
      </div>

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search agents..." className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 pl-10 pr-4 text-sm text-zinc-100 placeholder-zinc-500 focus:border-violet-500 focus:outline-none" />
        </div>
        <div className="flex gap-1 rounded-lg border border-zinc-800 bg-zinc-900 p-1">
          {(["popular", "newest", "top_rated"] as const).map((s) => (
            <button key={s} onClick={() => setSort(s)} className={sort === s ? "rounded-md bg-violet-600 px-3 py-1 text-xs font-semibold" : "rounded-md px-3 py-1 text-xs text-zinc-400 hover:text-white"}>
              {s === "popular" ? "Popular" : s === "newest" ? "Newest" : "Top rated"}
            </button>
          ))}
        </div>
      </div>

      <div className="mb-6 flex flex-wrap gap-2">
        {CATEGORIES.map((c) => (
          <button key={c} onClick={() => setCategory(c)} className={category === c ? "rounded-full bg-violet-600 px-3 py-1 text-xs font-semibold capitalize" : "rounded-full bg-zinc-900 px-3 py-1 text-xs text-zinc-400 hover:bg-zinc-800 capitalize"}>
            {c}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="text-zinc-500">Loading...</div>
      ) : agents.length === 0 ? (
        <div className="rounded-lg border border-dashed border-zinc-800 p-10 text-center text-zinc-500">No agents found.</div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((a) => (
            <Link key={a.id} to={`/agents/${a.slug}`} className="card group">
              <div className="mb-2 flex items-start justify-between">
                <h3 className="font-semibold group-hover:text-violet-300">{a.name}</h3>
                <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-xs">{a.category}</span>
              </div>
              <p className="mb-4 line-clamp-2 text-sm text-zinc-400">{a.description}</p>
              <div className="flex items-center justify-between text-xs text-zinc-500">
                <span className="flex items-center gap-1"><TrendingUp className="h-3 w-3" /> {a.total_runs} runs</span>
                <span className="flex items-center gap-1"><Star className="h-3 w-3 text-yellow-500" /> {a.avg_rating.toFixed(1)} ({a.rating_count})</span>
                <span className="font-semibold text-violet-400">{a.price_cents === 0 ? "Free" : `$${(a.price_cents / 100).toFixed(2)}`}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}