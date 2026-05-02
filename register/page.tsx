// client/src/pages/register/index.tsx
// ─────────────────────────────────────────────────────────────
// V-Guard AI — Client Self-Registration & KYC Onboarding
// Flow: Form → Upload KTP → Accept T&C → Submit → Admin Review
// Bilingual: ID / EN via LanguageContext
// ─────────────────────────────────────────────────────────────
import { useState, useCallback, useRef } from "react";
import { useLocation } from "wouter";
import { useLanguage } from "@/contexts/LanguageContext";

// ── Types ─────────────────────────────────────────────────────

type Tier = "V-LITE" | "V-PRO" | "V-ULTRA";
type Step = 1 | 2 | 3 | 4; // Info → Package → KTP → Review

interface FormData {
  fullName:     string;
  businessName: string;
  whatsapp:     string;
  email:        string;
  address:      string;
  tier:         Tier | "";
  ktpFile:      File | null;
  agreeTC:      boolean;
  agreePrivacy: boolean;
}

// ── Package Config ────────────────────────────────────────────

const PACKAGES = {
  "V-LITE": {
    price:    149_000,
    setup:    0,
    color:    "#06b6d4",
    emoji:    "⚡",
    features: { id: ["Alert VOID real-time", "3 Aturan Deteksi (R1–R3)", "Dashboard teks", "2 AI Agents", "Support email"], en: ["Real-time VOID alerts", "3 Detection Rules (R1–R3)", "Text dashboard", "2 AI Agents", "Email support"] },
  },
  "V-PRO": {
    price:    399_000,
    setup:    500_000,
    color:    "#8b5cf6",
    emoji:    "🚀",
    features: { id: ["Semua fitur LITE", "6 Aturan Deteksi (R1–R6)", "Cloud Video Analytics", "ROI Dashboard", "4 AI Agents", "API Integration"], en: ["All LITE features", "6 Detection Rules (R1–R6)", "Cloud Video Analytics", "ROI Dashboard", "4 AI Agents", "API Integration"] },
  },
  "V-ULTRA": {
    price:    799_000,
    setup:    1_000_000,
    color:    "#f59e0b",
    emoji:    "👑",
    features: { id: ["Semua fitur PRO", "CCTV Visual Bridge (R5/R6)", "10 AI Agents penuh", "White-label", "Dedicated server", "Integrasi real-time"], en: ["All PRO features", "CCTV Visual Bridge (R5/R6)", "10 Full AI Agents", "White-label", "Dedicated server", "Real-time integration"] },
  },
} as const;

const STEPS = {
  id: ["Informasi Bisnis", "Pilih Paket", "Upload KTP", "Konfirmasi"],
  en: ["Business Info",   "Choose Plan",  "Upload ID",  "Confirm"],
};

// ── i18n ─────────────────────────────────────────────────────

const T = {
  id: {
    title:       "Daftar V-Guard AI",
    subtitle:    "Lindungi bisnis Anda dari kebocoran transaksi. Proses pendaftaran cepat & mudah.",
    fullName:    "Nama Lengkap *",
    bizName:     "Nama Usaha / Toko *",
    wa:          "Nomor WhatsApp *",
    email:       "Email (opsional)",
    address:     "Alamat Usaha",
    phName:      "Masukkan nama lengkap Anda",
    phBiz:       "Nama toko / bisnis",
    phWa:        "628xxxxxxxxxx",
    phEmail:     "email@usaha.com",
    phAddress:   "Jl. Contoh No. 1, Kota",
    choosePackage: "Pilih Paket Layanan",
    monthly:     "/bulan",
    setup:       "Setup Fee",
    free:        "GRATIS",
    uploadKtp:   "Upload Foto KTP",
    ktpDesc:     "Upload foto KTP yang jelas dan terbaca. Format: JPG/PNG, maks. 5MB.",
    dragDrop:    "Klik atau drag & drop file KTP di sini",
    fileSelected:"File dipilih:",
    agreeTC:     "Saya menyetujui Syarat & Ketentuan layanan V-Guard AI",
    agreePrivacy:"Saya menyetujui Kebijakan Privasi dan penggunaan data saya",
    review:      "Ringkasan Pendaftaran",
    submit:      "Kirim Pendaftaran",
    submitting:  "Mengirim...",
    next:        "Lanjut",
    back:        "Kembali",
    success:     "Pendaftaran Berhasil! 🎉",
    successDesc: "Tim V-Guard akan menghubungi Anda via WhatsApp dalam 1×24 jam untuk proses verifikasi KYC.",
    home:        "Kembali ke Beranda",
    required:    "Wajib diisi",
    termsLink:   "Baca Syarat & Ketentuan",
    privacyLink: "Baca Kebijakan Privasi",
  },
  en: {
    title:       "Register for V-Guard AI",
    subtitle:    "Protect your business from transaction leakage. Quick & easy registration.",
    fullName:    "Full Name *",
    bizName:     "Business Name *",
    wa:          "WhatsApp Number *",
    email:       "Email (optional)",
    address:     "Business Address",
    phName:      "Enter your full name",
    phBiz:       "Store / business name",
    phWa:        "628xxxxxxxxxx",
    phEmail:     "email@business.com",
    phAddress:   "123 Example St, City",
    choosePackage:"Choose Your Plan",
    monthly:     "/month",
    setup:       "Setup Fee",
    free:        "FREE",
    uploadKtp:   "Upload ID Card (KTP)",
    ktpDesc:     "Upload a clear, readable photo of your ID card. Format: JPG/PNG, max 5MB.",
    dragDrop:    "Click or drag & drop your ID file here",
    fileSelected:"File selected:",
    agreeTC:     "I agree to the V-Guard AI Terms & Conditions",
    agreePrivacy:"I agree to the Privacy Policy and use of my data",
    review:      "Registration Summary",
    submit:      "Submit Registration",
    submitting:  "Submitting...",
    next:        "Next",
    back:        "Back",
    success:     "Registration Successful! 🎉",
    successDesc: "The V-Guard team will contact you via WhatsApp within 24 hours for KYC verification.",
    home:        "Back to Home",
    required:    "Required",
    termsLink:   "Read Terms & Conditions",
    privacyLink: "Read Privacy Policy",
  },
};

// ── Helpers ───────────────────────────────────────────────────

function formatRupiah(n: number) {
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(n);
}

// ── Step Indicator ────────────────────────────────────────────

function StepIndicator({ current, labels }: { current: Step; labels: string[] }) {
  return (
    <div className="flex items-center justify-center gap-0 mb-10">
      {labels.map((label, i) => {
        const stepNum = (i + 1) as Step;
        const done    = stepNum < current;
        const active  = stepNum === current;
        return (
          <div key={i} className="flex items-center">
            <div className="flex flex-col items-center gap-1.5">
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all duration-300 ${
                  done   ? "bg-cyan-500 border-cyan-500 text-slate-950"
                  : active ? "bg-slate-900 border-cyan-400 text-cyan-400 shadow-[0_0_12px_rgba(34,211,238,0.4)]"
                  : "bg-slate-900 border-slate-700 text-slate-500"
                }`}
              >
                {done ? "✓" : stepNum}
              </div>
              <span className={`text-xs font-medium hidden sm:block ${active ? "text-cyan-400" : done ? "text-slate-400" : "text-slate-600"}`}>
                {label}
              </span>
            </div>
            {i < labels.length - 1 && (
              <div className={`w-12 sm:w-20 h-0.5 mx-1 mb-5 transition-all duration-300 ${done ? "bg-cyan-500" : "bg-slate-700"}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Package Card ──────────────────────────────────────────────

function PackageCard({
  tier, pkg, selected, lang, onClick,
}: {
  tier: Tier;
  pkg: typeof PACKAGES["V-LITE"];
  selected: boolean;
  lang: "id" | "en";
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`relative w-full text-left p-5 rounded-2xl border-2 transition-all duration-200 ${
        selected
          ? "border-cyan-400 bg-cyan-950/30 shadow-[0_0_24px_rgba(34,211,238,0.15)]"
          : "border-slate-700 bg-slate-900/60 hover:border-slate-500"
      }`}
    >
      {tier === "V-PRO" && (
        <div className="absolute -top-3 right-4 px-3 py-0.5 bg-purple-500 text-white text-xs font-bold rounded-full">
          POPULAR
        </div>
      )}
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="text-2xl mb-1">{pkg.emoji}</div>
          <h3 className="text-white font-bold text-lg">{tier}</h3>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold" style={{ color: pkg.color }}>
            {formatRupiah(pkg.price)}
          </div>
          <div className="text-xs text-slate-400">
            {lang === "id" ? "/bulan" : "/month"}
          </div>
          {pkg.setup > 0 && (
            <div className="text-xs text-slate-500 mt-0.5">
              + {formatRupiah(pkg.setup)} {lang === "id" ? "setup" : "setup fee"}
            </div>
          )}
        </div>
      </div>
      <ul className="space-y-1.5">
        {pkg.features[lang].map((f, i) => (
          <li key={i} className="flex items-center gap-2 text-sm text-slate-300">
            <span style={{ color: pkg.color }}>✓</span> {f}
          </li>
        ))}
      </ul>
      {selected && (
        <div className="mt-3 pt-3 border-t border-cyan-500/30">
          <div className="flex items-center gap-2 text-cyan-400 text-sm font-semibold">
            <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            {lang === "id" ? "Dipilih" : "Selected"}
          </div>
        </div>
      )}
    </button>
  );
}

// ── KTP Drop Zone ─────────────────────────────────────────────

function KTPDropZone({
  file, onChange, t,
}: {
  file: File | null;
  onChange: (f: File) => void;
  t: typeof T["id"];
}) {
  const inputRef  = useRef<HTMLInputElement>(null);
  const [drag, setDrag] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDrag(false);
    const f = e.dataTransfer.files[0];
    if (f && (f.type === "image/jpeg" || f.type === "image/png") && f.size <= 5_000_000) {
      onChange(f);
    }
  }, [onChange]);

  const preview = file ? URL.createObjectURL(file) : null;

  return (
    <div
      className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200 ${
        drag
          ? "border-cyan-400 bg-cyan-950/20"
          : file
          ? "border-green-500 bg-green-950/20"
          : "border-slate-600 bg-slate-900/50 hover:border-slate-500"
      }`}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) onChange(f);
        }}
      />

      {preview ? (
        <div className="space-y-3">
          <img src={preview} alt="KTP Preview" className="w-full max-w-sm mx-auto rounded-xl object-cover max-h-48" />
          <div className="flex items-center justify-center gap-2 text-green-400 text-sm font-medium">
            <span>✅</span>
            <span>{t.fileSelected} {file!.name}</span>
          </div>
          <div className="text-xs text-slate-400">
            {(file!.size / 1024).toFixed(0)} KB · {lang === "id" ? "Klik untuk ganti" : "Click to change"}
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="text-5xl">🪪</div>
          <p className="text-slate-300 text-sm font-medium">{t.dragDrop}</p>
          <p className="text-slate-500 text-xs">{t.ktpDesc}</p>
        </div>
      )}
    </div>
  );
}

// Temp fix for lang access inside KTPDropZone
let lang: "id" | "en" = "id";

// ── Main Component ────────────────────────────────────────────

export default function RegisterPage() {
  const { language } = useLanguage();
  lang = language as "id" | "en";
  const [, setLocation] = useLocation();
  const t = T[language as "id" | "en"] ?? T.id;
  const stepLabels = STEPS[language as "id" | "en"] ?? STEPS.id;

  const [step,        setStep]       = useState<Step>(1);
  const [submitted,   setSubmitted]  = useState(false);
  const [isLoading,   setIsLoading]  = useState(false);
  const [errors,      setErrors]     = useState<Partial<Record<keyof FormData, string>>>({});

  const [form, setForm] = useState<FormData>({
    fullName:     "",
    businessName: "",
    whatsapp:     "",
    email:        "",
    address:      "",
    tier:         "",
    ktpFile:      null,
    agreeTC:      false,
    agreePrivacy: false,
  });

  const set = (key: keyof FormData, value: unknown) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => ({ ...prev, [key]: undefined }));
  };

  const validateStep = (): boolean => {
    const newErrors: typeof errors = {};
    if (step === 1) {
      if (!form.fullName.trim())     newErrors.fullName     = t.required;
      if (!form.businessName.trim()) newErrors.businessName = t.required;
      if (!form.whatsapp.trim())     newErrors.whatsapp     = t.required;
    }
    if (step === 2 && !form.tier)    newErrors.tier = t.required;
    if (step === 3) {
      if (!form.ktpFile)             newErrors.ktpFile    = t.required;
      if (!form.agreeTC)             newErrors.agreeTC    = t.required;
      if (!form.agreePrivacy)        newErrors.agreePrivacy = t.required;
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep()) setStep((s) => Math.min(4, s + 1) as Step);
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      // TODO: Replace with actual API call / tRPC mutation
      // const fd = new FormData();
      // Object.entries(form).forEach(([k, v]) => fd.append(k, v as any));
      // await trpc.clients.register.mutate(fd);
      await new Promise((r) => setTimeout(r, 2000)); // Simulate API
      setSubmitted(true);
    } catch {
      // Handle error
    } finally {
      setIsLoading(false);
    }
  };

  // ── Success State ──────────────────────────────────────────

  if (submitted) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
        <div className="max-w-md w-full text-center space-y-6">
          <div className="w-24 h-24 rounded-full bg-green-500/10 border border-green-500/30 flex items-center justify-center mx-auto text-5xl animate-bounce">
            🎉
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white mb-3">{t.success}</h2>
            <p className="text-slate-400 leading-relaxed">{t.successDesc}</p>
          </div>
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5 text-left space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">{t.fullName.replace(" *","")}</span>
              <span className="text-white font-medium">{form.fullName}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">{t.bizName.replace(" *","")}</span>
              <span className="text-white font-medium">{form.businessName}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">{t.wa.replace(" *","")}</span>
              <span className="text-cyan-400 font-medium">{form.whatsapp}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Paket</span>
              <span className="text-amber-400 font-bold">{form.tier}</span>
            </div>
          </div>
          <button
            onClick={() => setLocation("/home")}
            className="w-full py-3 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-bold transition-colors"
          >
            {t.home}
          </button>
        </div>
      </div>
    );
  }

  // ── Render ─────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* ── Header ─────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 bg-slate-950/90 backdrop-blur-md border-b border-slate-800">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
          <button onClick={() => setLocation("/home")} className="flex items-center gap-3 group">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:bg-cyan-500/20 transition-colors">
              ←
            </div>
            <span className="font-bold text-lg tracking-tight">
              V<span className="text-cyan-400">Guard</span> AI
            </span>
          </button>
          <span className="text-xs text-slate-500 font-mono bg-slate-900 px-3 py-1 rounded-full border border-slate-700">
            🔒 SSL Secured
          </span>
        </div>
      </header>

      {/* ── Content ────────────────────────────────────────── */}
      <main className="max-w-3xl mx-auto px-6 py-12">

        {/* Hero */}
        <div className="text-center mb-10">
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight mb-3">
            {t.title}
          </h1>
          <p className="text-slate-400 max-w-lg mx-auto">{t.subtitle}</p>
        </div>

        {/* Step Indicator */}
        <StepIndicator current={step} labels={stepLabels} />

        {/* ── Step 1: Business Info ─────────────────────────── */}
        {step === 1 && (
          <div className="bg-slate-900/60 border border-slate-700/50 rounded-3xl p-6 sm:p-8 space-y-6 backdrop-blur-sm">
            <h2 className="text-xl font-bold text-white">📋 {stepLabels[0]}</h2>
            <div className="grid sm:grid-cols-2 gap-5">

              {/* Full Name */}
              <div className="space-y-1.5">
                <label className="text-sm text-slate-300 font-medium">{t.fullName}</label>
                <input
                  type="text"
                  placeholder={t.phName}
                  value={form.fullName}
                  onChange={(e) => set("fullName", e.target.value)}
                  className={`w-full bg-slate-800 border rounded-xl px-4 py-3 text-white placeholder-slate-500 outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/30 transition-all ${errors.fullName ? "border-red-500" : "border-slate-700"}`}
                />
                {errors.fullName && <p className="text-red-400 text-xs">{errors.fullName}</p>}
              </div>

              {/* Business Name */}
              <div className="space-y-1.5">
                <label className="text-sm text-slate-300 font-medium">{t.bizName}</label>
                <input
                  type="text"
                  placeholder={t.phBiz}
                  value={form.businessName}
                  onChange={(e) => set("businessName", e.target.value)}
                  className={`w-full bg-slate-800 border rounded-xl px-4 py-3 text-white placeholder-slate-500 outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/30 transition-all ${errors.businessName ? "border-red-500" : "border-slate-700"}`}
                />
                {errors.businessName && <p className="text-red-400 text-xs">{errors.businessName}</p>}
              </div>

              {/* WhatsApp */}
              <div className="space-y-1.5">
                <label className="text-sm text-slate-300 font-medium">{t.wa}</label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 text-sm">📱</span>
                  <input
                    type="tel"
                    placeholder={t.phWa}
                    value={form.whatsapp}
                    onChange={(e) => set("whatsapp", e.target.value.replace(/\D/g, ""))}
                    className={`w-full bg-slate-800 border rounded-xl pl-10 pr-4 py-3 text-white placeholder-slate-500 outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/30 transition-all ${errors.whatsapp ? "border-red-500" : "border-slate-700"}`}
                  />
                </div>
                {errors.whatsapp && <p className="text-red-400 text-xs">{errors.whatsapp}</p>}
              </div>

              {/* Email */}
              <div className="space-y-1.5">
                <label className="text-sm text-slate-300 font-medium">{t.email}</label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 text-sm">✉️</span>
                  <input
                    type="email"
                    placeholder={t.phEmail}
                    value={form.email}
                    onChange={(e) => set("email", e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl pl-10 pr-4 py-3 text-white placeholder-slate-500 outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/30 transition-all"
                  />
                </div>
              </div>

              {/* Address */}
              <div className="sm:col-span-2 space-y-1.5">
                <label className="text-sm text-slate-300 font-medium">{t.address}</label>
                <textarea
                  placeholder={t.phAddress}
                  value={form.address}
                  onChange={(e) => set("address", e.target.value)}
                  rows={2}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/30 transition-all resize-none"
                />
              </div>
            </div>
          </div>
        )}

        {/* ── Step 2: Choose Package ────────────────────────── */}
        {step === 2 && (
          <div className="space-y-5">
            <h2 className="text-xl font-bold text-white">📦 {stepLabels[1]}</h2>
            {errors.tier && (
              <div className="px-4 py-2 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                ⚠️ {errors.tier}
              </div>
            )}
            <div className="grid sm:grid-cols-3 gap-4">
              {(Object.entries(PACKAGES) as [Tier, typeof PACKAGES["V-LITE"]][]).map(([tier, pkg]) => (
                <PackageCard
                  key={tier}
                  tier={tier}
                  pkg={pkg}
                  selected={form.tier === tier}
                  lang={language as "id" | "en"}
                  onClick={() => set("tier", tier)}
                />
              ))}
            </div>

            {form.tier && (
              <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5">
                <h3 className="text-sm text-slate-400 mb-3">
                  {language === "id" ? "Estimasi Biaya Pertama" : "First Payment Estimate"}
                </h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">{language === "id" ? "Bulanan" : "Monthly"}</span>
                    <span className="text-white">{formatRupiah(PACKAGES[form.tier as Tier].price)}</span>
                  </div>
                  {PACKAGES[form.tier as Tier].setup > 0 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">Setup Fee</span>
                      <span className="text-white">{formatRupiah(PACKAGES[form.tier as Tier].setup)}</span>
                    </div>
                  )}
                  <div className="border-t border-slate-700 pt-2 flex justify-between font-bold">
                    <span className="text-white">Total</span>
                    <span className="text-cyan-400">
                      {formatRupiah(
                        PACKAGES[form.tier as Tier].price + PACKAGES[form.tier as Tier].setup
                      )}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Step 3: KTP Upload + Agreement ───────────────── */}
        {step === 3 && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-white">🪪 {stepLabels[2]}</h2>

            <KTPDropZone
              file={form.ktpFile}
              onChange={(f) => set("ktpFile", f)}
              t={t}
            />
            {errors.ktpFile && <p className="text-red-400 text-sm">⚠️ {errors.ktpFile}</p>}

            <div className="space-y-4">
              {/* T&C */}
              <label className={`flex items-start gap-3 p-4 rounded-xl border cursor-pointer transition-all ${form.agreeTC ? "border-cyan-500/50 bg-cyan-950/20" : "border-slate-700 bg-slate-900/50 hover:border-slate-600"}`}>
                <div
                  onClick={() => set("agreeTC", !form.agreeTC)}
                  className={`w-5 h-5 rounded flex-shrink-0 border-2 flex items-center justify-center mt-0.5 transition-all ${form.agreeTC ? "bg-cyan-500 border-cyan-500" : "border-slate-500"}`}
                >
                  {form.agreeTC && <span className="text-slate-950 text-xs font-bold">✓</span>}
                </div>
                <div>
                  <p className="text-sm text-slate-200">{t.agreeTC}</p>
                  <a href="/terms" target="_blank" className="text-xs text-cyan-400 hover:underline mt-0.5 block">
                    {t.termsLink} →
                  </a>
                </div>
              </label>
              {errors.agreeTC && <p className="text-red-400 text-xs">⚠️ {errors.agreeTC}</p>}

              {/* Privacy */}
              <label className={`flex items-start gap-3 p-4 rounded-xl border cursor-pointer transition-all ${form.agreePrivacy ? "border-cyan-500/50 bg-cyan-950/20" : "border-slate-700 bg-slate-900/50 hover:border-slate-600"}`}>
                <div
                  onClick={() => set("agreePrivacy", !form.agreePrivacy)}
                  className={`w-5 h-5 rounded flex-shrink-0 border-2 flex items-center justify-center mt-0.5 transition-all ${form.agreePrivacy ? "bg-cyan-500 border-cyan-500" : "border-slate-500"}`}
                >
                  {form.agreePrivacy && <span className="text-slate-950 text-xs font-bold">✓</span>}
                </div>
                <div>
                  <p className="text-sm text-slate-200">{t.agreePrivacy}</p>
                  <a href="/privacy" target="_blank" className="text-xs text-cyan-400 hover:underline mt-0.5 block">
                    {t.privacyLink} →
                  </a>
                </div>
              </label>
              {errors.agreePrivacy && <p className="text-red-400 text-xs">⚠️ {errors.agreePrivacy}</p>}
            </div>
          </div>
        )}

        {/* ── Step 4: Review & Submit ───────────────────────── */}
        {step === 4 && (
          <div className="space-y-5">
            <h2 className="text-xl font-bold text-white">✅ {stepLabels[3]}</h2>
            <div className="bg-slate-900 border border-slate-700 rounded-2xl divide-y divide-slate-800">
              {[
                { label: t.fullName.replace(" *",""),     value: form.fullName },
                { label: t.bizName.replace(" *",""),      value: form.businessName },
                { label: t.wa.replace(" *",""),           value: `+${form.whatsapp}` },
                { label: t.email,                         value: form.email || "—" },
                { label: t.address,                       value: form.address || "—" },
              ].map((row) => (
                <div key={row.label} className="flex justify-between px-5 py-3 text-sm">
                  <span className="text-slate-400">{row.label}</span>
                  <span className="text-white font-medium max-w-[55%] text-right">{row.value}</span>
                </div>
              ))}
              <div className="flex justify-between px-5 py-3 text-sm">
                <span className="text-slate-400">Paket</span>
                <div className="flex items-center gap-2">
                  <span className="text-amber-400 font-bold">{form.tier}</span>
                  <span className="text-slate-500">
                    ({formatRupiah(PACKAGES[form.tier as Tier]?.price ?? 0)}/bulan)
                  </span>
                </div>
              </div>
              <div className="flex justify-between px-5 py-3 text-sm">
                <span className="text-slate-400">KTP</span>
                <span className="text-green-400 font-medium flex items-center gap-1">
                  ✅ {form.ktpFile?.name}
                </span>
              </div>
            </div>

            <div className="bg-blue-950/30 border border-blue-500/30 rounded-xl p-4 text-sm text-blue-300">
              ℹ️ {language === "id"
                ? "Setelah submit, admin V-Guard akan memverifikasi data Anda dan menghubungi via WhatsApp dalam 1×24 jam."
                : "After submission, the V-Guard admin will verify your data and contact you via WhatsApp within 24 hours."}
            </div>
          </div>
        )}

        {/* ── Navigation Buttons ────────────────────────────── */}
        <div className="flex items-center justify-between mt-8 gap-4">
          {step > 1 ? (
            <button
              type="button"
              onClick={() => setStep((s) => Math.max(1, s - 1) as Step)}
              className="flex items-center gap-2 px-6 py-3 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800 transition-colors font-medium"
            >
              ← {t.back}
            </button>
          ) : (
            <div />
          )}

          {step < 4 ? (
            <button
              type="button"
              onClick={handleNext}
              className="flex items-center gap-2 px-8 py-3 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-bold transition-all active:scale-95 shadow-[0_0_20px_rgba(34,211,238,0.3)]"
            >
              {t.next} →
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={isLoading}
              className="flex items-center gap-2 px-8 py-3 rounded-xl bg-green-500 hover:bg-green-600 disabled:opacity-60 disabled:cursor-not-allowed text-white font-bold transition-all active:scale-95 shadow-[0_0_20px_rgba(34,197,94,0.3)]"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  {t.submitting}
                </>
              ) : (
                <>✅ {t.submit}</>
              )}
            </button>
          )}
        </div>
      </main>
    </div>
  );
}
