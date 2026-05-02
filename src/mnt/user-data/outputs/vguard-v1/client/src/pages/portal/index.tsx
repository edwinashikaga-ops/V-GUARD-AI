// client/src/pages/portal/index.tsx
// ─────────────────────────────────────────────────────────────
// V-Guard AI — Portal Login Gate
// Auth: UserID + Password → redirect to /portal/dashboard
// Bilingual: ID / EN
// ─────────────────────────────────────────────────────────────
import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { useLanguage } from "@/contexts/LanguageContext";
import { useAuth } from "@/contexts/AuthContext";

const T = {
  id: {
    title:       "Portal Klien V-Guard",
    subtitle:    "Masuk untuk mengakses dashboard, laporan fraud, dan plugin Anda.",
    userId:      "User ID",
    password:    "Password",
    phUserId:    "VG-XXXX-XXXXX",
    phPassword:  "Password Anda",
    login:       "Masuk ke Portal",
    logging:     "Memverifikasi...",
    forgot:      "Lupa password? Hubungi support via WhatsApp",
    noAccount:   "Belum punya akun?",
    register:    "Daftar sekarang",
    error:       "User ID atau password salah. Coba lagi.",
    secure:      "Koneksi terenkripsi SSL",
  },
  en: {
    title:       "V-Guard Client Portal",
    subtitle:    "Sign in to access your dashboard, fraud reports, and plugin.",
    userId:      "User ID",
    password:    "Password",
    phUserId:    "VG-XXXX-XXXXX",
    phPassword:  "Your password",
    login:       "Sign In to Portal",
    logging:     "Verifying...",
    forgot:      "Forgot password? Contact support via WhatsApp",
    noAccount:   "Don't have an account?",
    register:    "Register now",
    error:       "Invalid User ID or password. Please try again.",
    secure:      "SSL Encrypted Connection",
  },
};

export default function PortalLoginPage() {
  const { language }     = useLanguage();
  const { login, user }  = useAuth();
  const [, setLocation]  = useLocation();
  const lang = (language ?? "id") as "id" | "en";
  const t    = T[lang];

  const [userId,   setUserId]   = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error,    setError]    = useState("");

  // Already logged in → redirect
  useEffect(() => {
    if (user) setLocation("/portal/dashboard");
  }, [user, setLocation]);

  const handleLogin = async () => {
    if (!userId.trim() || !password.trim()) {
      setError(t.error);
      return;
    }
    setIsLoading(true);
    setError("");
    try {
      // TODO: replace with actual tRPC mutation
      // await trpc.auth.clientLogin.mutate({ userId, password });
      await new Promise((r) => setTimeout(r, 1500));
      // Mock success
      login?.({ id: 1, userId, businessName: "Demo Toko", tier: "V-ULTRA" } as any);
      setLocation("/portal/dashboard");
    } catch {
      setError(t.error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
      {/* Background grid */}
      <div className="fixed inset-0 opacity-[0.03]"
        style={{ backgroundImage: "linear-gradient(#06b6d4 1px,transparent 1px),linear-gradient(90deg,#06b6d4 1px,transparent 1px)", backgroundSize: "40px 40px" }} />

      <div className="relative w-full max-w-sm space-y-6">
        {/* Brand */}
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 text-2xl mb-4">
            🛡️
          </div>
          <h1 className="text-2xl font-black text-white">{t.title}</h1>
          <p className="text-sm text-slate-400 mt-2">{t.subtitle}</p>
        </div>

        {/* Form */}
        <div className="bg-slate-900/80 border border-slate-700/50 rounded-2xl p-6 space-y-4 backdrop-blur-md">
          {/* User ID */}
          <div className="space-y-1.5">
            <label className="text-sm text-slate-300 font-medium">{t.userId}</label>
            <input
              type="text"
              placeholder={t.phUserId}
              value={userId}
              onChange={(e) => { setUserId(e.target.value.toUpperCase()); setError(""); }}
              onKeyDown={(e) => e.key === "Enter" && handleLogin()}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white font-mono placeholder-slate-500 outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/30 transition-all"
            />
          </div>

          {/* Password */}
          <div className="space-y-1.5">
            <label className="text-sm text-slate-300 font-medium">{t.password}</label>
            <div className="relative">
              <input
                type={showPass ? "text" : "password"}
                placeholder={t.phPassword}
                value={password}
                onChange={(e) => { setPassword(e.target.value); setError(""); }}
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 pr-12 text-white placeholder-slate-500 outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/30 transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 text-sm"
              >
                {showPass ? "🙈" : "👁️"}
              </button>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 px-4 py-2.5 bg-red-500/10 border border-red-500/30 rounded-xl text-sm text-red-400">
              ⚠️ {error}
            </div>
          )}

          <button
            onClick={handleLogin}
            disabled={isLoading}
            className="w-full py-3 rounded-xl bg-cyan-500 hover:bg-cyan-600 disabled:opacity-60 disabled:cursor-not-allowed text-slate-950 font-bold transition-all active:scale-95 shadow-[0_0_20px_rgba(34,211,238,0.3)] flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <><div className="w-4 h-4 border-2 border-slate-900/40 border-t-slate-900 rounded-full animate-spin" /> {t.logging}</>
            ) : (
              <>{t.login}</>
            )}
          </button>

          <p className="text-xs text-slate-500 text-center">{t.forgot}</p>
        </div>

        {/* Register link */}
        <div className="text-center">
          <span className="text-sm text-slate-500">{t.noAccount} </span>
          <button
            onClick={() => setLocation("/register")}
            className="text-sm text-cyan-400 hover:text-cyan-300 font-semibold transition-colors"
          >
            {t.register} →
          </button>
        </div>

        {/* Security badge */}
        <div className="text-center">
          <span className="inline-flex items-center gap-1.5 text-xs text-slate-600">
            🔒 {t.secure}
          </span>
        </div>
      </div>
    </div>
  );
}
