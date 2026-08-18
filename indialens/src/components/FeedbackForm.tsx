"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Send } from "lucide-react";
import { useState } from "react";

const feedbackSchema = z.object({
  collegeDegreeId: z.string().min(1, "Required"),
  fieldName: z.string().min(1, "Required"),
  oldValue: z.string().min(1, "Required"),
  newValue: z.string().min(1, "Required"),
  sourceUrl: z.string().url("Must be a valid URL"),
  confidence: z.enum(["high", "medium", "low"]),
  notes: z.string().optional(),
});

type FeedbackData = z.infer<typeof feedbackSchema>;

const FIELD_OPTIONS = [
  "annual_tuition_inr",
  "placement_rate_pct",
  "median_salary_inr",
  "highest_salary_inr",
  "financial_roi_pct",
  "risk_score",
  "satisfaction_score",
  "automation_probability",
  "companies_visited",
  "other",
];

interface FeedbackFormProps {
  defaultCollegeDegreeId?: string;
  onSuccess?: () => void;
}

export function FeedbackForm({ defaultCollegeDegreeId, onSuccess }: FeedbackFormProps) {
  const [submitted, setSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<FeedbackData>({
    resolver: zodResolver(feedbackSchema),
    defaultValues: {
      collegeDegreeId: defaultCollegeDegreeId || "",
      confidence: "medium",
    },
  });

  const onSubmit = async (data: FeedbackData) => {
    // In production: POST to /api/admin/feedback
    await new Promise((r) => setTimeout(r, 800));
    console.log("Feedback submitted:", data);
    setSubmitted(true);
    reset();
    onSuccess?.();
  };

  if (submitted) {
    return (
      <div
        style={{
          padding: "24px",
          borderRadius: 8,
          background: "rgba(34,197,94,0.08)",
          border: "1px solid rgba(34,197,94,0.2)",
          textAlign: "center",
        }}
      >
        <div style={{ color: "#22C55E", fontSize: 24, marginBottom: 8 }}>✓</div>
        <p style={{ color: "#F0F0F5", fontWeight: 600 }}>Feedback submitted</p>
        <p style={{ color: "#8B8BA7", fontSize: 13, marginTop: 4 }}>
          Your correction has been queued for review by our data team.
        </p>
        <button
          onClick={() => setSubmitted(false)}
          className="btn-secondary mt-4"
          style={{ fontSize: 13 }}
        >
          Submit another
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="form-label">Program ID</label>
          <input
            {...register("collegeDegreeId")}
            className="form-input"
            placeholder="e.g. iitb-btech-cse"
          />
          {errors.collegeDegreeId && (
            <p style={{ color: "#EF4444", fontSize: 11, marginTop: 4 }}>
              {errors.collegeDegreeId.message}
            </p>
          )}
        </div>

        <div>
          <label className="form-label">Field to Correct</label>
          <select {...register("fieldName")} className="form-input form-select">
            <option value="">Select field...</option>
            {FIELD_OPTIONS.map((f) => (
              <option key={f} value={f} style={{ background: "#13131A" }}>
                {f}
              </option>
            ))}
          </select>
          {errors.fieldName && (
            <p style={{ color: "#EF4444", fontSize: 11, marginTop: 4 }}>
              {errors.fieldName.message}
            </p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="form-label">Current (Wrong) Value</label>
          <input
            {...register("oldValue")}
            className="form-input"
            placeholder="What the model shows"
          />
          {errors.oldValue && (
            <p style={{ color: "#EF4444", fontSize: 11, marginTop: 4 }}>
              {errors.oldValue.message}
            </p>
          )}
        </div>
        <div>
          <label className="form-label">Correct Value</label>
          <input
            {...register("newValue")}
            className="form-input"
            placeholder="What it should be"
          />
          {errors.newValue && (
            <p style={{ color: "#EF4444", fontSize: 11, marginTop: 4 }}>
              {errors.newValue.message}
            </p>
          )}
        </div>
      </div>

      <div>
        <label className="form-label">Source URL</label>
        <input
          {...register("sourceUrl")}
          className="form-input"
          placeholder="https://nirfindia.org/... or official source"
          type="url"
        />
        {errors.sourceUrl && (
          <p style={{ color: "#EF4444", fontSize: 11, marginTop: 4 }}>
            {errors.sourceUrl.message}
          </p>
        )}
      </div>

      <div>
        <label className="form-label">Your Confidence</label>
        <div className="flex gap-2">
          {(["high", "medium", "low"] as const).map((level) => (
            <label key={level} className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                value={level}
                {...register("confidence")}
                style={{ accentColor: "#4F6EF7" }}
              />
              <span
                style={{
                  color: level === "high" ? "#22C55E" : level === "medium" ? "#F59E0B" : "#EF4444",
                  fontSize: 13,
                  fontWeight: 600,
                  textTransform: "capitalize",
                }}
              >
                {level}
              </span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className="form-label">Notes (optional)</label>
        <textarea
          {...register("notes")}
          className="form-input"
          rows={3}
          placeholder="Additional context, methodology notes, or caveats..."
          style={{ resize: "vertical" }}
        />
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="btn-primary w-full justify-center"
        style={{ opacity: isSubmitting ? 0.7 : 1 }}
      >
        <Send size={14} />
        {isSubmitting ? "Submitting..." : "Submit Correction"}
      </button>
    </form>
  );
}
