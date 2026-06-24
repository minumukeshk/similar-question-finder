import { useEffect, useState } from "react";
import { Loader2, Inbox } from "lucide-react";
import Navbar from "../components/Navbar";
import api from "../api";

const TOPICS = [
  "All",
  "Biology",
  "Physics",
  "Chemistry",
  "Math",
  "History",
  "Geography",
  "Computer Science",
  "Economics",
];

const TAG_COLORS = {
  Biology:           "bg-green-500/15 text-green-400 border-green-500/30",
  Physics:           "bg-blue-500/15 text-blue-400 border-blue-500/30",
  Chemistry:         "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
  Math:              "bg-purple-500/15 text-purple-400 border-purple-500/30",
  History:           "bg-orange-500/15 text-orange-400 border-orange-500/30",
  Geography:         "bg-teal-500/15 text-teal-400 border-teal-500/30",
  "Computer Science":"bg-indigo-500/15 text-indigo-400 border-indigo-500/30",
  Economics:         "bg-pink-500/15 text-pink-400 border-pink-500/30",
};

const DEFAULT_TAG_COLOR = "bg-slate-500/15 text-slate-400 border-slate-500/30";

function TagChip({ tag }) {
  const colorClass = TAG_COLORS[tag] || DEFAULT_TAG_COLOR;
  return (
    <span className={`chip border ${colorClass}`}>{tag ?? "Untagged"}</span>
  );
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function History() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedTag, setSelectedTag] = useState("All");

  const fetchQuestions = async (tag) => {
    setLoading(true);
    setError("");
    try {
      const params = tag && tag !== "All" ? { tag } : {};
      const { data } = await api.get("/questions/", { params });
      setQuestions(data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to load questions."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions(selectedTag);
  }, [selectedTag]);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-2xl w-full mx-auto px-4 sm:px-6 py-10">
        {/* Header + filter */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-7">
          <div>
            <h1 className="text-2xl font-bold text-white mb-0.5">
              Your Question History
            </h1>
            <p className="text-muted text-sm">
              All questions you've submitted, newest first.
            </p>
          </div>

          {/* Topic filter */}
          <select
            id="topic-filter"
            value={selectedTag}
            onChange={(e) => setSelectedTag(e.target.value)}
            className="bg-card border border-border text-white text-sm rounded-lg
                       px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent
                       focus:border-accent cursor-pointer min-w-[160px]"
          >
            {TOPICS.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 size={28} className="animate-spin text-accent" />
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400
                          text-sm rounded-lg px-4 py-3">
            {error}
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && questions.length === 0 && (
          <div className="card flex flex-col items-center py-16 text-center">
            <Inbox size={40} className="text-muted mb-3" />
            <p className="text-white font-medium mb-1">
              {selectedTag !== "All"
                ? `No ${selectedTag} questions found.`
                : "You haven't asked any questions yet."}
            </p>
            <p className="text-muted text-sm">
              Head to the home page to submit your first question.
            </p>
          </div>
        )}

        {/* Question cards */}
        {!loading && !error && questions.length > 0 && (
          <div className="space-y-3">
            {questions.map((q) => (
              <div key={q.id} id={`question-${q.id}`} className="card">
                <p className="text-white text-sm leading-relaxed mb-3 line-clamp-4">
                  {q.text}
                </p>
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <TagChip tag={q.tag} />
                  <span className="text-muted text-xs">
                    {formatDate(q.created_at)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
