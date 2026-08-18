"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  GraduationCap, DollarSign, MapPin, Target, Award, Brain,
  BookOpen, Lightbulb, ChevronRight, ChevronLeft, Loader2, CheckCircle
} from "lucide-react";

// ── Section types ─────────────────────────────────────────────────
interface IntakeFormData {
  // Section 1 — Academics
  tenth_pct: string;
  twelfth_pct: string;
  twelfth_stream: string;
  jee_rank: string;
  neet_score: string;
  backlog: string;
  learning_style: string;

  // Section 2 — Financial
  family_income: string;
  total_budget: number;
  loan_willingness: string;
  family_support_needed: string;

  // Section 3 — Geography
  home_state: string;
  relocation_india: string;
  relocation_abroad: string;
  return_home: string;

  // Section 4 — Goals
  primary_goals: string[];
  risk_appetite: number;
  wlb_priority: number;
  financial_independence_age: string;
  lower_pay_meaningful: string;

  // Section 5 — Extracurriculars
  sports_level: string;
  arts_level: string;
  coding_level: string;
  entrepreneurship_level: string;
  leadership_level: string;

  // Section 6 — Personality
  p_q1: string;
  p_q2: string;
  p_q3: string;

  // Section 7 — Degree interest
  fields_of_interest: string[];
  colleges_heard_of: string;
  fields_ruled_out: string;

  // Section 8 — Future
  future_vision: string;
  preferred_work_structure: string;
  exciting_industries: string[];
  one_thing_never: string;
}

const INITIAL_DATA: IntakeFormData = {
  tenth_pct: "", twelfth_pct: "", twelfth_stream: "", jee_rank: "",
  neet_score: "", backlog: "none", learning_style: "mixed",
  family_income: "", total_budget: 20, loan_willingness: "up-to-5l",
  family_support_needed: "no",
  home_state: "", relocation_india: "yes", relocation_abroad: "maybe",
  return_home: "no",
  primary_goals: [], risk_appetite: 5, wlb_priority: 5,
  financial_independence_age: "30", lower_pay_meaningful: "depends",
  sports_level: "none", arts_level: "none", coding_level: "none",
  entrepreneurship_level: "none", leadership_level: "none",
  p_q1: "", p_q2: "", p_q3: "",
  fields_of_interest: [], colleges_heard_of: "", fields_ruled_out: "",
  future_vision: "", preferred_work_structure: "", exciting_industries: [],
  one_thing_never: "",
};

const SECTIONS = [
  { id: 1, label: "Academics", icon: <GraduationCap size={16} /> },
  { id: 2, label: "Financial", icon: <DollarSign size={16} /> },
  { id: 3, label: "Geography", icon: <MapPin size={16} /> },
  { id: 4, label: "Goals", icon: <Target size={16} /> },
  { id: 5, label: "Activities", icon: <Award size={16} /> },
  { id: 6, label: "Personality", icon: <Brain size={16} /> },
  { id: 7, label: "Interests", icon: <BookOpen size={16} /> },
  { id: 8, label: "Future", icon: <Lightbulb size={16} /> },
];

const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
  "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
  "Delhi", "Chandigarh", "Jammu & Kashmir", "Ladakh", "Puducherry",
];

const DEGREE_FIELDS = [
  "Engineering — CS/IT", "Engineering — Non-CS", "Medicine / MBBS",
  "Law", "Design", "Management / MBA", "Commerce", "Pure Sciences",
  "Social Sciences", "Arts & Humanities", "Vocational", "Undecided",
];

const INDUSTRIES = [
  "Technology", "Healthcare", "Finance", "Education", "Media & Entertainment",
  "Manufacturing", "Climate & Energy", "Defence", "Sports", "Agriculture",
  "Real Estate", "Consulting",
];

// ── Slider component ───────────────────────────────────────────────
function Slider({ value, onChange, min = 1, max = 10, label }: {
  value: number; onChange: (v: number) => void;
  min?: number; max?: number; label: string;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span style={{ fontSize: 12, color: "#8B8BA7" }}>{label}</span>
        <span className="font-mono font-bold" style={{ color: "#4F6EF7", fontSize: 14 }}>
          {value}/{max}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        style={{ width: "100%", accentColor: "#4F6EF7" }}
      />
      <div className="flex justify-between mt-1">
        <span style={{ fontSize: 10, color: "#4A4A6A" }}>{min}</span>
        <span style={{ fontSize: 10, color: "#4A4A6A" }}>{max}</span>
      </div>
    </div>
  );
}

// ── Multi-select chips ─────────────────────────────────────────────
function MultiSelect({ options, value, onChange }: {
  options: string[]; value: string[]; onChange: (v: string[]) => void;
}) {
  const toggle = (opt: string) => {
    onChange(value.includes(opt) ? value.filter((v) => v !== opt) : [...value, opt]);
  };
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => {
        const selected = value.includes(opt);
        return (
          <button
            key={opt}
            type="button"
            onClick={() => toggle(opt)}
            style={{
              padding: "6px 12px",
              borderRadius: 999,
              fontSize: 12,
              fontWeight: 600,
              border: `1px solid ${selected ? "#4F6EF7" : "#1E1E2E"}`,
              background: selected ? "rgba(79,110,247,0.15)" : "transparent",
              color: selected ? "#7B96FF" : "#8B8BA7",
              cursor: "pointer",
              transition: "all 0.15s",
            }}
          >
            {opt}
          </button>
        );
      })}
    </div>
  );
}

// ── Radio group ────────────────────────────────────────────────────
function RadioGroup({ options, value, onChange }: {
  options: { value: string; label: string }[];
  value: string; onChange: (v: string) => void;
}) {
  return (
    <div className="flex flex-col gap-2">
      {options.map((opt) => {
        const selected = value === opt.value;
        return (
          <button
            key={opt.value}
            type="button"
            onClick={() => onChange(opt.value)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: "10px 14px",
              borderRadius: 8,
              border: `1px solid ${selected ? "#4F6EF7" : "#1E1E2E"}`,
              background: selected ? "rgba(79,110,247,0.08)" : "transparent",
              cursor: "pointer",
              textAlign: "left",
              transition: "all 0.15s",
            }}
          >
            <div
              style={{
                width: 16,
                height: 16,
                borderRadius: "50%",
                border: `2px solid ${selected ? "#4F6EF7" : "#4A4A6A"}`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              {selected && (
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#4F6EF7" }} />
              )}
            </div>
            <span style={{ fontSize: 13, color: selected ? "#F0F0F5" : "#8B8BA7" }}>
              {opt.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}

// ── Section components ─────────────────────────────────────────────
function Section1({ data, update }: { data: IntakeFormData; update: (k: string, v: unknown) => void }) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="form-label">10th Percentage</label>
          <input
            className="form-input"
            type="number"
            min={40}
            max={100}
            step={0.1}
            placeholder="e.g. 92.5"
            value={data.tenth_pct}
            onChange={(e) => update("tenth_pct", e.target.value)}
          />
        </div>
        <div>
          <label className="form-label">12th Percentage</label>
          <input
            className="form-input"
            type="number"
            min={40}
            max={100}
            step={0.1}
            placeholder="e.g. 88.0"
            value={data.twelfth_pct}
            onChange={(e) => update("twelfth_pct", e.target.value)}
          />
        </div>
      </div>

      <div>
        <label className="form-label">12th Stream</label>
        <select
          className="form-input form-select"
          value={data.twelfth_stream}
          onChange={(e) => update("twelfth_stream", e.target.value)}
          style={{ background: "#0A0A0F" }}
        >
          <option value="">Select stream...</option>
          <option>Science (PCM)</option>
          <option>Science (PCB)</option>
          <option>Science (PCMB)</option>
          <option>Commerce</option>
          <option>Arts / Humanities</option>
          <option>Vocational</option>
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="form-label">JEE Rank (optional)</label>
          <input
            className="form-input"
            type="number"
            placeholder="All India rank"
            value={data.jee_rank}
            onChange={(e) => update("jee_rank", e.target.value)}
          />
        </div>
        <div>
          <label className="form-label">NEET Score (optional)</label>
          <input
            className="form-input"
            type="number"
            placeholder="Out of 720"
            value={data.neet_score}
            onChange={(e) => update("neet_score", e.target.value)}
          />
        </div>
      </div>

      <div>
        <label className="form-label">Academic Gaps or Backlogs</label>
        <RadioGroup
          value={data.backlog}
          onChange={(v) => update("backlog", v)}
          options={[
            { value: "none", label: "None — straight through" },
            { value: "1yr", label: "1 year gap" },
            { value: "2yr", label: "2+ years gap" },
            { value: "ongoing", label: "Ongoing backlogs" },
          ]}
        />
      </div>

      <div>
        <label className="form-label">Preferred Learning Style</label>
        <RadioGroup
          value={data.learning_style}
          onChange={(v) => update("learning_style", v)}
          options={[
            { value: "self", label: "Self-directed — I learn best on my own" },
            { value: "structured", label: "Structured — I need clear frameworks" },
            { value: "project", label: "Project-based — learning by doing" },
            { value: "mixed", label: "Mixed — depends on the subject" },
          ]}
        />
      </div>
    </div>
  );
}

function Section2({ data, update }: { data: IntakeFormData; update: (k: string, v: unknown) => void }) {
  return (
    <div className="space-y-5">
      <div>
        <label className="form-label">Family Annual Income</label>
        <RadioGroup
          value={data.family_income}
          onChange={(v) => update("family_income", v)}
          options={[
            { value: "<3L", label: "Below ₹3 Lakh / year" },
            { value: "3-8L", label: "₹3 – 8 Lakh / year" },
            { value: "8-15L", label: "₹8 – 15 Lakh / year" },
            { value: "15-30L", label: "₹15 – 30 Lakh / year" },
            { value: "30L+", label: "Above ₹30 Lakh / year" },
          ]}
        />
      </div>

      <div>
        <label className="form-label">
          Max budget for full degree incl. living: ₹{data.total_budget} Lakh
        </label>
        <input
          type="range"
          min={2}
          max={80}
          step={1}
          value={data.total_budget}
          onChange={(e) => update("total_budget", parseInt(e.target.value))}
          style={{ width: "100%", accentColor: "#4F6EF7" }}
        />
        <div className="flex justify-between mt-1">
          <span style={{ fontSize: 11, color: "#4A4A6A" }}>₹2L</span>
          <span style={{ fontSize: 11, color: "#4A4A6A" }}>₹80L</span>
        </div>
      </div>

      <div>
        <label className="form-label">Education Loan Willingness</label>
        <RadioGroup
          value={data.loan_willingness}
          onChange={(v) => update("loan_willingness", v)}
          options={[
            { value: "none", label: "No loans — must be self-funded" },
            { value: "up-to-5l", label: "Up to ₹5 Lakh loan OK" },
            { value: "up-to-15l", label: "Up to ₹15 Lakh loan OK" },
            { value: "whatever", label: "Whatever it takes — ROI justifies it" },
          ]}
        />
      </div>

      <div>
        <label className="form-label">Do you need to financially support your family during studies?</label>
        <RadioGroup
          value={data.family_support_needed}
          onChange={(v) => update("family_support_needed", v)}
          options={[
            { value: "no", label: "No" },
            { value: "partially", label: "Partially — some contribution needed" },
            { value: "yes", label: "Yes — I'm the primary earner" },
          ]}
        />
      </div>
    </div>
  );
}

function Section3({ data, update }: { data: IntakeFormData; update: (k: string, v: unknown) => void }) {
  return (
    <div className="space-y-5">
      <div>
        <label className="form-label">Home State</label>
        <select
          className="form-input form-select"
          value={data.home_state}
          onChange={(e) => update("home_state", e.target.value)}
          style={{ background: "#0A0A0F" }}
        >
          <option value="">Select your state...</option>
          {INDIAN_STATES.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="form-label">Willing to relocate within India for studies?</label>
        <RadioGroup
          value={data.relocation_india}
          onChange={(v) => update("relocation_india", v)}
          options={[
            { value: "yes", label: "Yes — anywhere in India" },
            { value: "state-only", label: "Only within my state" },
            { value: "no", label: "No — must stay in home city" },
          ]}
        />
      </div>

      <div>
        <label className="form-label">Willing to relocate abroad for work after degree?</label>
        <RadioGroup
          value={data.relocation_abroad}
          onChange={(v) => update("relocation_abroad", v)}
          options={[
            { value: "yes", label: "Yes — actively want to work abroad" },
            { value: "maybe", label: "Open to it if opportunity is right" },
            { value: "no", label: "No — want to stay in India" },
          ]}
        />
      </div>

      <div>
        <label className="form-label">Do you need to return to your home city/state after degree?</label>
        <RadioGroup
          value={data.return_home}
          onChange={(v) => update("return_home", v)}
          options={[
            { value: "yes", label: "Yes — family or other obligations" },
            { value: "no", label: "No — I'll go where the opportunity is" },
          ]}
        />
      </div>
    </div>
  );
}

function Section4({ data, update }: { data: IntakeFormData; update: (k: string, v: unknown) => void }) {
  const GOALS = ["High Salary", "Job Stability", "Social Impact", "Prestige", "Creative Freedom", "Entrepreneurship"];

  return (
    <div className="space-y-6">
      <div>
        <label className="form-label">Primary goals (select all that apply)</label>
        <MultiSelect
          options={GOALS}
          value={data.primary_goals}
          onChange={(v) => update("primary_goals", v)}
        />
      </div>

      <Slider
        label="Risk Appetite — 1: Safe govt job, 10: Startup equity"
        value={data.risk_appetite}
        onChange={(v) => update("risk_appetite", v)}
      />

      <Slider
        label="Work-Life Balance Priority — 1: I'll work 80hrs/week, 10: Life > work"
        value={data.wlb_priority}
        onChange={(v) => update("wlb_priority", v)}
      />

      <div>
        <label className="form-label">Target age for financial independence</label>
        <RadioGroup
          value={data.financial_independence_age}
          onChange={(v) => update("financial_independence_age", v)}
          options={[
            { value: "25", label: "25 — FIRE aspirant" },
            { value: "30", label: "30 — early career target" },
            { value: "35", label: "35 — standard track" },
            { value: "40", label: "40 — comfortable pace" },
            { value: "none", label: "Not a priority for me" },
          ]}
        />
      </div>

      <div>
        <label className="form-label">Would you take lower pay for more meaningful work?</label>
        <RadioGroup
          value={data.lower_pay_meaningful}
          onChange={(v) => update("lower_pay_meaningful", v)}
          options={[
            { value: "yes", label: "Yes — meaning matters more than money" },
            { value: "no", label: "No — compensation is primary" },
            { value: "depends", label: "Depends on the gap — up to 20% cut, yes" },
          ]}
        />
      </div>
    </div>
  );
}

function Section5({ data, update }: { data: IntakeFormData; update: (k: string, v: unknown) => void }) {
  const levels = ["none", "school", "district", "state/national", "international"];
  const levels2 = ["none", "hobby", "trained", "performed publicly"];
  const codingLevels = ["none", "1-2 personal projects", "hackathon wins", "open source contributions"];
  const entrepLevels = ["none", "small hustle", "registered business", "funded"];
  const leaderLevels = ["none", "class rep", "school council", "NGO lead", "startup founder"];

  return (
    <div className="space-y-5">
      {[
        { label: "Sports Level", key: "sports_level", opts: levels },
        { label: "Performing Arts / Music / Dance", key: "arts_level", opts: levels2 },
        { label: "Coding & Tech Projects", key: "coding_level", opts: codingLevels },
        { label: "Entrepreneurship", key: "entrepreneurship_level", opts: entrepLevels },
        { label: "Leadership", key: "leadership_level", opts: leaderLevels },
      ].map((field) => (
        <div key={field.key}>
          <label className="form-label">{field.label}</label>
          <div className="flex flex-wrap gap-2">
            {field.opts.map((opt) => {
              const selected = (data as unknown as Record<string, unknown>)[field.key] === opt;
              return (
                <button
                  key={opt}
                  type="button"
                  onClick={() => update(field.key, opt)}
                  style={{
                    padding: "5px 12px",
                    borderRadius: 999,
                    fontSize: 12,
                    fontWeight: 500,
                    border: `1px solid ${selected ? "#4F6EF7" : "#1E1E2E"}`,
                    background: selected ? "rgba(79,110,247,0.15)" : "transparent",
                    color: selected ? "#7B96FF" : "#8B8BA7",
                    cursor: "pointer",
                    textTransform: "capitalize",
                    transition: "all 0.15s",
                  }}
                >
                  {opt}
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

function Section6({ data, update }: { data: IntakeFormData; update: (k: string, v: unknown) => void }) {
  const questions = [
    {
      key: "p_q1",
      q: "Your group project is falling behind. You:",
      opts: [
        { value: "A", label: "A) Take charge and redistribute tasks" },
        { value: "B", label: "B) Focus harder on your own part and trust others" },
        { value: "C", label: "C) Talk to everyone individually to understand blockers" },
        { value: "D", label: "D) Ask the professor for an extension" },
      ],
    },
    {
      key: "p_q2",
      q: "You get ₹8L at a stable MNC vs ₹4L + equity at a 10-person startup. You:",
      opts: [
        { value: "A", label: "A) Take the MNC — stability matters" },
        { value: "B", label: "B) Take the startup — equity upside is worth it" },
        { value: "C", label: "C) Negotiate with both and see what happens" },
        { value: "D", label: "D) Ask my parents" },
      ],
    },
    {
      key: "p_q3",
      q: "Six months into a degree and it's not what you expected. You:",
      opts: [
        { value: "A", label: "A) Push through — quitting is not an option" },
        { value: "B", label: "B) Start exploring how to switch or transfer" },
        { value: "C", label: "C) Do the degree but build parallel skills outside it" },
        { value: "D", label: "D) Drop out and figure it out" },
      ],
    },
  ];

  return (
    <div className="space-y-8">
      {questions.map((q) => (
        <div key={q.key}>
          <p style={{ fontSize: 15, fontWeight: 600, color: "#F0F0F5", marginBottom: 12, lineHeight: 1.5 }}>
            {q.q}
          </p>
          <RadioGroup
            value={(data as unknown as Record<string, unknown>)[q.key] as string}
            onChange={(v) => update(q.key, v)}
            options={q.opts}
          />
        </div>
      ))}
    </div>
  );
}

function Section7({ data, update }: { data: IntakeFormData; update: (k: string, v: unknown) => void }) {
  return (
    <div className="space-y-5">
      <div>
        <label className="form-label">Fields seriously considering (multi-select)</label>
        <MultiSelect
          options={DEGREE_FIELDS}
          value={data.fields_of_interest}
          onChange={(v) => update("fields_of_interest", v)}
        />
      </div>

      <div>
        <label className="form-label">Colleges you&apos;ve heard of and are interested in</label>
        <textarea
          className="form-input"
          rows={3}
          placeholder="e.g. IIT Bombay, VIT Vellore, NLSIU... (free text, we'll parse this)"
          value={data.colleges_heard_of}
          onChange={(e) => update("colleges_heard_of", e.target.value)}
          style={{ resize: "vertical" }}
        />
      </div>

      <div>
        <label className="form-label">Fields you&apos;ve already ruled out and why</label>
        <textarea
          className="form-input"
          rows={2}
          placeholder="e.g. Medicine — can't handle the 5.5yr commitment. MBA — want to work first..."
          value={data.fields_ruled_out}
          onChange={(e) => update("fields_ruled_out", e.target.value)}
          style={{ resize: "vertical" }}
        />
      </div>
    </div>
  );
}

function Section8({ data, update }: { data: IntakeFormData; update: (k: string, v: unknown) => void }) {
  return (
    <div className="space-y-5">
      <div>
        <label className="form-label">Where do you want to be professionally at age 30?</label>
        <textarea
          className="form-input"
          rows={3}
          placeholder="Be specific — role, company type, lifestyle, income target, geography..."
          value={data.future_vision}
          onChange={(e) => update("future_vision", e.target.value)}
          style={{ resize: "vertical" }}
        />
        <p style={{ fontSize: 11, color: "#4A4A6A", marginTop: 4 }}>
          Claude will parse this into structured aspiration tags for the model.
        </p>
      </div>

      <div>
        <label className="form-label">Preferred work structure</label>
        <RadioGroup
          value={data.preferred_work_structure}
          onChange={(v) => update("preferred_work_structure", v)}
          options={[
            { value: "large-company", label: "Large company (MNC / conglomerate)" },
            { value: "mid-size", label: "Mid-size company (100–2000 people)" },
            { value: "startup", label: "Startup (< 100 people)" },
            { value: "freelance", label: "Freelance / independent" },
            { value: "government", label: "Government / PSU" },
            { value: "academia", label: "Academia / research" },
            { value: "own-business", label: "Own business / entrepreneurship" },
          ]}
        />
      </div>

      <div>
        <label className="form-label">Industries that genuinely excite you</label>
        <MultiSelect
          options={INDUSTRIES}
          value={data.exciting_industries}
          onChange={(v) => update("exciting_industries", v)}
        />
      </div>

      <div>
        <label className="form-label">One thing you never want your career to be</label>
        <input
          className="form-input"
          placeholder="e.g. Boring. Isolated. Selling things I don't believe in..."
          value={data.one_thing_never}
          onChange={(e) => update("one_thing_never", e.target.value)}
        />
      </div>
    </div>
  );
}

// ── Loading messages ───────────────────────────────────────────────
const LOADING_MESSAGES = [
  "Parsing your academic profile...",
  "Scanning 847 college-degree programs...",
  "Running ROI formula across 6 dimensions...",
  "Computing 20-year salary trajectories...",
  "Assessing AI automation risk for your fields...",
  "Matching with 4,291 similar student profiles...",
  "Generating personalized risk dashboard...",
  "Calibrating confidence intervals...",
  "Compiling your report...",
];

// ── Main wizard ────────────────────────────────────────────────────
export default function AnalyzePage() {
  const [section, setSection] = useState(1);
  const [data, setData] = useState<IntakeFormData>(INITIAL_DATA);
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState(0);
  const [completedToken, setCompletedToken] = useState<string | null>(null);
  const [shareCopied, setShareCopied] = useState(false);
  const router = useRouter();

  const handleShare = () => {
    if (typeof window !== "undefined") {
      navigator.clipboard.writeText(`${window.location.origin}/report/${completedToken}`);
      setShareCopied(true);
      setTimeout(() => setShareCopied(false), 2000);
    }
  };

  const update = (key: string, value: unknown) => {
    setData((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    let i = 0;
    const interval = setInterval(() => {
      i = (i + 1) % LOADING_MESSAGES.length;
      setLoadingMsg(i);
    }, 900);

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const analyzeResult = await res.json();
      
      const saveRes = await fetch("/api/report/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(analyzeResult),
      });
      const savedData = await saveRes.json();
      
      clearInterval(interval);
      setLoading(false);
      setCompletedToken(savedData.token || analyzeResult.token);
    } catch {
      clearInterval(interval);
      setLoading(false);
    }
  };

  const SECTION_COMPONENTS: Record<number, React.FC<{ data: IntakeFormData; update: (k: string, v: unknown) => void }>> = {
    1: Section1, 2: Section2, 3: Section3, 4: Section4,
    5: Section5, 6: Section6, 7: Section7, 8: Section8,
  };

  const CurrentSection = SECTION_COMPONENTS[section];
  const progress = ((section - 1) / 8) * 100;

  if (completedToken) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6 p-6 text-center">
        <div className="w-16 h-16 bg-green-500/20 text-green-500 rounded-full flex items-center justify-center mb-2">
          <CheckCircle size={32} />
        </div>
        <h2 className="text-2xl font-bold font-display text-white">Analysis Complete</h2>
        
        <div className="glass-card p-4 border-l-4 border-green-500 flex flex-col sm:flex-row items-center gap-4 max-w-md w-full justify-between">
          <div className="text-left">
            <h3 className="font-semibold text-white">Shareable link created</h3>
            <p className="text-sm text-gray-400">Save this link to access your report later.</p>
          </div>
          <button onClick={handleShare} className="btn-secondary whitespace-nowrap">
            {shareCopied ? "Copied!" : "Copy Link"}
          </button>
        </div>

        <button 
          onClick={() => router.push(`/report/${completedToken}`)} 
          className="btn-primary mt-4 px-8 py-3 text-lg"
        >
          View Full Report
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div
        style={{
          minHeight: "80vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
        }}
      >
        <div style={{ textAlign: "center", maxWidth: 440 }}>
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: "50%",
              background: "rgba(79,110,247,0.1)",
              border: "2px solid rgba(79,110,247,0.3)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 24px",
            }}
          >
            <Loader2 size={28} style={{ color: "#4F6EF7", animation: "spin 1s linear infinite" }} />
          </div>
          <h2
            className="font-display font-bold mb-3"
            style={{ fontSize: 24, color: "#F0F0F5" }}
          >
            Generating your report
          </h2>
          <p
            className="font-mono text-sm"
            style={{ color: "#4F6EF7", height: 20, transition: "all 0.3s" }}
          >
            {LOADING_MESSAGES[loadingMsg]}
          </p>
          <div className="progress-bar mt-8">
            <div
              className="progress-bar-fill"
              style={{ width: `${((loadingMsg + 1) / LOADING_MESSAGES.length) * 100}%` }}
            />
          </div>
        </div>
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <div style={{ padding: "40px 0 80px" }}>
      <div className="container-lg" style={{ maxWidth: 680 }}>
        {/* Header */}
        <div className="mb-8">
          <h1
            className="font-display font-bold mb-2"
            style={{ fontSize: 28, color: "#F0F0F5", letterSpacing: "-0.02em" }}
          >
            Your ROI Analysis
          </h1>
          <p style={{ fontSize: 14, color: "#8B8BA7" }}>
            8 sections · ~3 minutes · personalized salary trajectories for your profile
          </p>
        </div>

        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-3">
            <span style={{ fontSize: 12, color: "#8B8BA7" }}>
              Section {section} of 8 — {SECTIONS[section - 1].label}
            </span>
            <span className="font-mono text-xs" style={{ color: "#4A4A6A" }}>
              {Math.round(progress)}% complete
            </span>
          </div>
          <div className="progress-bar">
            <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
          </div>

          {/* Section tabs */}
          <div className="flex gap-1 mt-3 overflow-x-auto pb-1">
            {SECTIONS.map((s) => (
              <button
                key={s.id}
                type="button"
                onClick={() => s.id < section && setSection(s.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 4,
                  padding: "4px 10px",
                  borderRadius: 999,
                  fontSize: 11,
                  fontWeight: 600,
                  border: "none",
                  background:
                    s.id === section
                      ? "rgba(79,110,247,0.2)"
                      : s.id < section
                      ? "rgba(34,197,94,0.1)"
                      : "rgba(30,30,46,0.5)",
                  color:
                    s.id === section
                      ? "#7B96FF"
                      : s.id < section
                      ? "#22C55E"
                      : "#4A4A6A",
                  cursor: s.id < section ? "pointer" : "default",
                  whiteSpace: "nowrap",
                  flexShrink: 0,
                }}
              >
                {s.id < section ? <CheckCircle size={10} /> : s.icon}
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {/* Section content */}
        <div className="glass-card p-6 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 8,
                background: "rgba(79,110,247,0.12)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#4F6EF7",
              }}
            >
              {SECTIONS[section - 1].icon}
            </div>
            <div>
              <h2
                className="font-display font-semibold"
                style={{ fontSize: 18, color: "#F0F0F5" }}
              >
                {SECTIONS[section - 1].label}
              </h2>
              <p style={{ fontSize: 12, color: "#4A4A6A" }}>
                Section {section} of 8
              </p>
            </div>
          </div>

          <CurrentSection data={data} update={update} />
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          {section > 1 ? (
            <button
              onClick={() => setSection((v) => v - 1)}
              className="btn-secondary"
            >
              <ChevronLeft size={16} />
              Back
            </button>
          ) : (
            <div />
          )}

          {section < 8 ? (
            <button
              onClick={() => setSection((v) => v + 1)}
              className="btn-primary"
            >
              Continue
              <ChevronRight size={16} />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              className="btn-primary"
              style={{ background: "#22C55E", fontSize: 15, padding: "13px 28px" }}
            >
              Generate My Report
              <ChevronRight size={16} />
            </button>
          )}
        </div>

        {/* Footer note */}
        <p
          className="text-xs text-center mt-6"
          style={{ color: "#4A4A6A" }}
        >
          No account required. Your data is used only to generate your report.
          Reports are shareable via a unique URL.
        </p>
      </div>
    </div>
  );
}
