import type { Signal, Sentiment } from "../types";
import { SIGNAL_TYPE_LABELS, SENTIMENT_CONFIG } from "../types";
import { formatRelativeTime } from "../utils/format";

interface Props {
  signal: Signal;
}

export default function SignalCard({ signal }: Props) {
  const article = signal.sector_articles;
  const sentiment = (signal.sentiment ?? "neutral") as Sentiment;
  const sentimentCfg = SENTIMENT_CONFIG[sentiment] ?? SENTIMENT_CONFIG.neutral;
  const typeLabel =
    SIGNAL_TYPE_LABELS[signal.signal_type] ?? signal.signal_type;

  return (
    <div className="rounded-lg border border-blue-100 bg-white p-4">
      <div className="mb-2">
        {article?.url ? (
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-gray-900 hover:text-blue-700"
          >
            {article.title ?? "Untitled"}
          </a>
        ) : (
          <span className="text-sm font-medium text-gray-900">
            {article?.title ?? "Untitled"}
          </span>
        )}
      </div>

      <div className="mb-2 flex flex-wrap items-center gap-2 text-xs">
        {article?.source && (
          <span className="text-gray-500">{article.source}</span>
        )}
        <span className="text-gray-400">
          {formatRelativeTime(article?.published_at ?? signal.created_at)}
        </span>
        <span className="rounded-full bg-gray-100 px-2 py-0.5 font-medium text-gray-600">
          {typeLabel}
        </span>
        <span className="flex items-center gap-1">
          <span
            className={`inline-block h-2 w-2 rounded-full ${sentimentCfg.dotColor}`}
          />
          <span className={`font-medium ${sentimentCfg.textColor}`}>
            {sentimentCfg.label}
          </span>
        </span>
      </div>

      {signal.summary && (
        <p className="text-sm leading-relaxed text-gray-600">
          {signal.summary}
        </p>
      )}
    </div>
  );
}
