import { useState } from "react";
import { Loader2, SendHorizonal, Sparkles } from "lucide-react";
import Navbar from "../components/Navbar";
import api from "../api";

// ── Tag color map ──────────────────────────────────────────────────────────
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
    <span className={`chip border ${colorClass}`}>{tag}</span>
  );
}

function SimilarCard({ question }) {
  const pct = Math.round(question.similarity_score * 100);
  return (
    <div className="card flex items-start justify-between gap-4">
      <div className="flex-1 min-w-0">
        <p className="text-white text-sm leading-relaxed mb-2 line-clamp-4">
          {question.text}
        </p>
        {question.tag && <TagChip tag={question.tag} />}
      </div>
      {/* Similarity badge */}
      <span
        className={`flex-shrink-0 text-xs font-bold px-2.5 py-1 rounded-full border
          ${pct >= 70
            ? "bg-green-500/15 text-green-400 border-green-500/30"
            : pct >= 50
            ? "bg-yellow-500/15 text-yellow-400 border-yellow-500/30"
            : "bg-muted/15 text-muted border-border"
          }`}
      >
        {pct}% match
      </span>
    </div>
  );
}

export default function Home() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null); // { tag, similar_questions, text }
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    setError("");
    setResult(null);
    setLoading(true);

    try {
      const { data } = await api.post("/questions/", { text: text.trim() });
      setResult(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-2xl w-full mx-auto px-4 sm:px-6 py-10">
        {/* Hero text */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white mb-1">
            Find Similar Study Questions
          </h1>
          <p className="text-muted text-sm">
            Type a question and instantly discover semantically related ones
            from the database.
          </p>
        </div>

        {/* Input form */}
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="card p-0 overflow-hidden">
            <textarea
              id="question-input"
              rows={5}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type your study question here…"
              className="w-full bg-transparent text-white placeholder-muted text-sm
                         px-5 pt-4 pb-3 resize-none focus:outline-none leading-relaxed"
            />
            <div className="flex items-center justify-between px-5 py-3 border-t border-border">
              <span className="text-muted text-xs">
                {text.length} / 2000 characters
              </span>
              <button
                id="find-similar-btn"
                type="submit"
                disabled={loading || !text.trim() || text.length > 2000}
                className="btn-primary flex items-center gap-2 text-sm"
              >
                {loading ? (
                  <>
                    <Loader2 size={15} className="animate-spin" />
                    Searching…
                  </>
                ) : (
                  <>
                    <SendHorizonal size={15} />
                    Find Similar
                  </>
                )}
              </button>
            </div>
          </div>
        </form>

        {/* Error */}
        {error && (
          <div className="mb-6 bg-red-500/10 border border-red-500/30 text-red-400
                          text-sm rounded-lg px-4 py-3">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <section id="results-section">
            {/* Submitted question summary */}
            <div className="flex items-center gap-3 mb-4">
              <Sparkles size={16} className="text-accent flex-shrink-0" />
              <span className="text-white text-sm font-medium">
                Auto-detected topic:
              </span>
              <TagChip tag={result.tag} />
            </div>

            <h2 className="text-base font-semibold text-white mb-3">
              Similar Questions
            </h2>

            {result.similar_questions && result.similar_questions.length > 0 ? (
              <div className="space-y-3">
                {result.similar_questions.map((q, idx) => (
                  <SimilarCard key={idx} question={q} />
                ))}
              </div>
            ) : (
              <div className="card text-center py-10">
                <p className="text-muted text-sm">
                  No similar questions yet.{" "}
                  <span className="text-white font-medium">
                    Yours is the first!
                  </span>
                </p>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
