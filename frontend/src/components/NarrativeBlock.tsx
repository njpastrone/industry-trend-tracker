import type { SectorNarrative, Sentiment } from "../types";
import { SENTIMENT_CONFIG } from "../types";

interface Props {
  narrative: SectorNarrative | null;
}

export default function NarrativeBlock({ narrative }: Props) {
  if (!narrative) {
    return (
      <div className="rounded-lg border border-blue-100 bg-white p-5 text-gray-500">
        No narrative available. Run the pipeline to generate one.
      </div>
    );
  }

  const sentiment = (narrative.sentiment ?? "neutral") as Sentiment;
  const sentimentCfg = SENTIMENT_CONFIG[sentiment] ?? SENTIMENT_CONFIG.neutral;
  const paragraphs = narrative.summary_full
    ? narrative.summary_full.split("\n\n").filter(Boolean)
    : [];

  return (
    <div className="rounded-lg border border-blue-100 bg-white p-5">
      <h3 className="mb-3 text-sm font-semibold text-gray-900">
        AI Narrative
      </h3>

      {narrative.key_themes && narrative.key_themes.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {narrative.key_themes.map((theme) => (
            <span
              key={theme}
              className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700"
            >
              {theme}
            </span>
          ))}
        </div>
      )}

      <div className="mb-3 flex items-center gap-1.5">
        <span
          className={`inline-block h-2.5 w-2.5 rounded-full ${sentimentCfg.dotColor}`}
        />
        <span className={`text-xs font-medium ${sentimentCfg.textColor}`}>
          {sentimentCfg.label}
        </span>
      </div>

      {paragraphs.length > 0 ? (
        <div className="space-y-3">
          {paragraphs.map((p, i) => (
            <p key={i} className="text-sm leading-relaxed text-gray-700">
              {p}
            </p>
          ))}
        </div>
      ) : (
        <p className="text-sm text-gray-500">
          {narrative.summary_short ?? "No narrative text available."}
        </p>
      )}

      {narrative.ir_talking_points && narrative.ir_talking_points.length > 0 && (
        <div className="mt-4 rounded-md bg-blue-50 p-3">
          <h4 className="mb-2 text-xs font-semibold text-blue-900">
            IR Talking Points
          </h4>
          <ul className="space-y-1.5">
            {narrative.ir_talking_points.map((point, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-sm text-blue-800"
              >
                <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-blue-400" />
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
