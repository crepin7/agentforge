import { useQuery, useMutation } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { useState } from "react";
import { Play, Loader2 } from "lucide-react";
import { agentsApi, runsApi } from "../lib/api";

export default function AgentDetailPage() {
  const { slug = "" } = useParams();
  const { data: agent, isLoading } = useQuery({ queryKey: ["agent", slug], queryFn: () => agentsApi.get(slug) });
  const [inputJson, setInputJson] = useState('{\n  "city": "Lome"\n}');

  const mutation = useMutation({
    mutationFn: () => {
      const input_data = JSON.parse(inputJson);
      return runsApi.create(slug, input_data);
    },
  });

  if (isLoading) return <div className="text-zinc-500">Loading...</div>;
  if (!agent) return <div className="text-zinc-500">Agent not found.</div>;

  return (
    <div>
      <h1 className="mb-2 text-3xl font-bold">{agent.name}</h1>
      <p className="mb-6 text-zinc-400">{agent.description}</p>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div>
          <h2 className="mb-2 text-sm font-semibold text-zinc-300">Input (JSON)</h2>
          <textarea value={inputJson} onChange={(e) => setInputJson(e.target.value)} rows={10} className="w-full rounded-lg border border-zinc-800 bg-zinc-900 p-3 font-mono text-xs text-zinc-100 focus:border-violet-500 focus:outline-none" />
          <button onClick={() => mutation.mutate()} disabled={mutation.isPending} className="btn-primary mt-3">
            {mutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
            Run agent
          </button>
        </div>

        <div>
          <h2 className="mb-2 text-sm font-semibold text-zinc-300">Output</h2>
          <div className="min-h-[200px] rounded-lg border border-zinc-800 bg-zinc-900 p-4 text-sm">
            {mutation.isPending && <div className="text-zinc-500">Running...</div>}
            {mutation.isError && <div className="text-red-400">Error: {String(mutation.error)}</div>}
            {mutation.data && <pre className="overflow-x-auto text-xs text-zinc-200">{JSON.stringify(mutation.data, null, 2)}</pre>}
            {!mutation.data && !mutation.isPending && <div className="text-zinc-500">Output will appear here.</div>}
          </div>
        </div>
      </div>
    </div>
  );
}