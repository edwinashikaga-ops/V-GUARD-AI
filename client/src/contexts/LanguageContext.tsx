import React, { createContext, useContext, useState, useEffect } from "react";

export type Language = "id" | "en";

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(
  undefined
);

// Translation strings
const translations = {
  id: {
    // Navigation
    "nav.home": "Beranda",
    "nav.pricing": "Harga",
    "nav.roi": "ROI",
    "nav.portal": "Portal Klien",
    "nav.login": "Masuk",
    "nav.logout": "Keluar",
    "nav.language": "Bahasa",
    "nav.customer_service": "Layanan Pelanggan",

    // Home Page
    "home.hero.title": "Deteksi Kecurangan Real-Time untuk UMKM Indonesia",
    "home.hero.subtitle":
      "Lindungi bisnis Anda dengan AI-powered fraud detection dan business intelligence",
    "home.hero.cta": "Mulai Gratis",
    "home.hero.demo": "Lihat Demo",
    "home.trust": "Dipercaya oleh 500+ bisnis di Indonesia",
    "home.features.title": "Fitur Unggulan",
    "home.cta.title": "Siap Melindungi Bisnis Anda?",
    "home.cta.subtitle": "Mulai dengan demo gratis 15 menit hari ini",
    "home.cta.button": "Mulai Sekarang",

    // Features
    "feature.fraud.title": "Deteksi Kecurangan R1-R6",
    "feature.fraud.desc": "Deteksi kecurangan real-time dengan 6 aturan canggih",
    "feature.agents.title": "Tim Agen AI (10 Squad)",
    "feature.agents.desc": "10 agen AI untuk berbagai fungsi bisnis",
    "feature.monitoring.title": "Pemantauan Langsung",
    "feature.monitoring.desc": "Pantau transaksi dan anomali secara langsung",
    "feature.roles.title": "Akses Multi-Role",
    "feature.roles.desc": "Klien, agen referral, investor, admin",
    "feature.secure.title": "Aman & Terenkripsi",
    "feature.secure.desc": "Enkripsi end-to-end dan siap kepatuhan",
    "feature.analytics.title": "Analitik Lanjutan",
    "feature.analytics.desc": "Dashboard analitik dan pelaporan lengkap",

    // Pricing
    "pricing.title": "Paket Harga V-Guard AI",
    "pricing.subtitle": "Pilih paket yang sesuai dengan kebutuhan bisnis Anda",
    "pricing.monthly": "Per Bulan",
    "pricing.setup": "Biaya Setup",
    "pricing.features": "Fitur Unggulan",
    "pricing.cta": "Hubungi WhatsApp",
    "pricing.popular": "POPULER",
    "pricing.premium": "PREMIUM",
    "pricing.comparison": "Perbandingan Fitur Lengkap",

    // Portal
    "portal.dashboard": "Dashboard",
    "portal.roi": "ROI Calculator",
    "portal.produk": "Daftar Harga",
    "portal.transactions": "Transaksi",
    "portal.agents": "Tim Agen AI",
    "portal.referral": "Referral",
    "portal.investor": "Investor",
    "portal.admin": "Admin",
    "portal.welcome": "Selamat Datang",
    "portal.tier": "Paket",

    // ROI Calculator
    "roi.title": "Kalkulator Simulasi Keuntungan/Kebocoran Dana",
    "roi.subtitle": "Hitung potensi penghematan dengan V-Guard AI",
    "roi.revenue": "Omset Bulanan",
    "roi.leakage": "Estimasi Kebocoran (Fraud)",
    "roi.result": "Potensi Dana Terselamatkan",

    // Terms
    "term.fraud_detection": "Deteksi Kecurangan",
    "term.realtime_monitoring": "Pemantauan Langsung",
    "term.ai_agent_squad": "Tim Agen AI",
    "term.void_rate": "Tingkat Pembatalan (VOID)",

    // Common
    "common.loading": "Memuat...",
    "common.error": "Terjadi kesalahan",
    "common.success": "Berhasil",
    "common.save": "Simpan",
    "common.cancel": "Batal",
    "common.delete": "Hapus",
    "common.edit": "Edit",
    "common.view": "Lihat",
    "common.back": "Kembali",
  },
  en: {
    // Navigation
    "nav.home": "Home",
    "nav.pricing": "Pricing",
    "nav.roi": "ROI",
    "nav.portal": "Client Portal",
    "nav.login": "Login",
    "nav.logout": "Logout",
    "nav.language": "Language",
    "nav.customer_service": "Customer Service",

    // Home Page
    "home.hero.title": "Real-Time Fraud Detection for Indonesian SMEs",
    "home.hero.subtitle":
      "Protect your business with AI-powered fraud detection and business intelligence",
    "home.hero.cta": "Start Free",
    "home.hero.demo": "View Demo",
    "home.trust": "Trusted by 500+ businesses in Indonesia",
    "home.features.title": "Key Features",
    "home.cta.title": "Ready to Protect Your Business?",
    "home.cta.subtitle": "Start with a free 15-minute demo today",
    "home.cta.button": "Start Now",

    // Features
    "feature.fraud.title": "Fraud Detection R1-R6",
    "feature.fraud.desc": "Real-time fraud detection with 6 advanced rules",
    "feature.agents.title": "AI Agent Squad (10 Squad)",
    "feature.agents.desc": "10 AI agents for various business functions",
    "feature.monitoring.title": "Real-time Monitoring",
    "feature.monitoring.desc": "Monitor transactions and anomalies in real-time",
    "feature.roles.title": "Multi-Role Access",
    "feature.roles.desc": "Client, referral agent, investor, admin",
    "feature.secure.title": "Secure & Encrypted",
    "feature.secure.desc": "End-to-end encryption and compliance ready",
    "feature.analytics.title": "Advanced Analytics",
    "feature.analytics.desc": "Complete analytics dashboard and reporting",

    // Pricing
    "pricing.title": "V-Guard AI Pricing Plans",
    "pricing.subtitle": "Choose the plan that fits your business needs",
    "pricing.monthly": "Per Month",
    "pricing.setup": "Setup Fee",
    "pricing.features": "Key Features",
    "pricing.cta": "Contact WhatsApp",
    "pricing.popular": "POPULAR",
    "pricing.premium": "PREMIUM",
    "pricing.comparison": "Full Feature Comparison",

    // Portal
    "portal.dashboard": "Dashboard",
    "portal.roi": "ROI Calculator",
    "portal.produk": "Price List",
    "portal.transactions": "Transactions",
    "portal.agents": "AI Agent Squad",
    "portal.referral": "Referral",
    "portal.investor": "Investor",
    "portal.admin": "Admin",
    "portal.welcome": "Welcome",
    "portal.tier": "Plan",

    // ROI Calculator
    "roi.title": "Profit/Loss Simulation Calculator",
    "roi.subtitle": "Calculate potential savings with V-Guard AI",
    "roi.revenue": "Monthly Revenue",
    "roi.leakage": "Estimated Leakage (Fraud)",
    "roi.result": "Potential Funds Saved",

    // Terms
    "term.fraud_detection": "Fraud Detection",
    "term.realtime_monitoring": "Real-time Monitoring",
    "term.ai_agent_squad": "AI Agent Squad",
    "term.void_rate": "Void Rate",

    // Common
    "common.loading": "Loading...",
    "common.error": "An error occurred",
    "common.success": "Success",
    "common.save": "Save",
    "common.cancel": "Cancel",
    "common.delete": "Delete",
    "common.edit": "Edit",
    "common.view": "View",
    "common.back": "Back",
  },
};

interface LanguageProviderProps {
  children: React.ReactNode;
  defaultLanguage?: Language;
}

export function LanguageProvider({
  children,
  defaultLanguage = "id",
}: LanguageProviderProps) {
  const [language, setLanguageState] = useState<Language>(defaultLanguage);
  const [isMounted, setIsMounted] = useState(false);

  // Load from localStorage on mount (client-side only)
  useEffect(() => {
    if (typeof window === "undefined") return;
    
    const stored = localStorage.getItem("language") as Language | null;
    if (stored && (stored === "id" || stored === "en")) {
      setLanguageState(stored);
      setIsMounted(true);
      return;
    }

    // Check URL param
    const params = new URLSearchParams(window.location.search);
    const urlLang = params.get("lang") as Language | null;
    if (urlLang && (urlLang === "id" || urlLang === "en")) {
      setLanguageState(urlLang);
    }
    
    setIsMounted(true);
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    if (typeof window !== "undefined") {
      localStorage.setItem("language", lang);
    }
  };

  const t = (key: string): string => {
    const value = (translations[language] as any)[key];
    return value || key; // Return key if not found to help debugging
  };

  const contextValue = {
    language,
    setLanguage,
    t,
  };

  return (
    <LanguageContext.Provider value={contextValue}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within LanguageProvider");
  }
  return context;
}

export function getTranslation(key: string, language: Language = "id"): string {
  const value = (translations[language] as any)[key];
  return value || key;
}
