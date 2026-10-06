import { Routes, Route, Link, NavLink } from "react-router-dom";
import { Sparkles, LayoutGrid, Upload, User } from "lucide-react";
import DiscoverPage from "./pages/Discover";
import AgentDetailPage from "./pages/AgentDetail";
import PublishPage from "./pages/Publish";

function NavBar() {
  return (
    <header className="sticky top-0 z-30 border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2 text-lg font-bold">
          <Sparkles className="h-5 w-5 text-violet-400" />
          <span>AgentForge</span>
        </Link>
        <nav className="flex items-center gap-6 text-sm">
          <NavLink to="/" className={({ isActive }) => isActive ? "text-white" : "text-zinc-400 hover:text-white"}>
            <LayoutGrid className="mr-1 inline h-4 w-4" /> Discover
          </NavLink>
          <NavLink to="/publish" className={({ isActive }) => isActive ? "text-white" : "text-zinc-400 hover:text-white"}>
            <Upload className="mr-1 inline h-4 w-4" /> Publish
          </NavLink>
          <button className="text-zinc-400 hover:text-white">
            <User className="h-4 w-4" />
          </button>
        </nav>
      </div>
    </header>
  );
}

export default function App() {
  return (
    <div className="min-h-screen">
      <NavBar />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <Routes>
          <Route path="/" element={<DiscoverPage />} />
          <Route path="/agents/:slug" element={<AgentDetailPage />} />
          <Route path="/publish" element={<PublishPage />} />
        </Routes>
      </main>
    </div>
  );
}