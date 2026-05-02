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
    "nav.portal": "Portal",
    "nav.login": "Masuk",
    "nav.logout": "Keluar",
    "nav.language": "Bahasa",

    // Home Page
    "home.hero.title": "Deteksi Fraud Real-Time untuk UMKM Indonesia",
    "home.hero.subtitle":
      "Lindungi bisnis Anda dengan AI-powered fraud detection dan business intelligence",
    "home.hero.cta": "Mulai Gratis",
    "home.hero.demo": "Lihat Demo",

    // Pricing
    "pricing.title": "Paket Harga V-Guard AI",
    "pricing.subtitle": "Pilih paket yang sesuai dengan kebutuhan bisnis Anda",
    "pricing.monthly": "Per Bulan",
    "pricing.setup": "Biaya Setup",
    "pricing.features": "Fitur Unggulan",
    "pricing.cta": "Hubungi WhatsApp",

    // Portal
    "portal.dashboard": "Dashboard",
    "portal.transactions": "Transaksi",
    "portal.agents": "AI Agents",
    "portal.referral": "Referral",
    "portal.investor": "Investor",
    "portal.admin": "Admin",

    // Dashboard
    "dashboard.title": "Dashboard Klien",
    "dashboard.omset": "Total Omset",
    "dashboard.transactions": "Transaksi",
    "dashboard.anomalies": "Anomali",
    "dashboard.cashiers": "Kasir",
    "dashboard.status": "Status Sistem",

    // Fraud Rules
    "fraud.r1": "VOID Direct Flag",
    "fraud.r2": "VOID Rate Spike",
    "fraud.r3": "Duplicate Transaction",
    "fraud.r4": "Balance Mismatch",
    "fraud.r5": "Off-Hours Transaction",
    "fraud.r6": "Rapid VOID",

    // Tiers
    "tier.demo": "DEMO",
    "tier.vlite": "V-LITE",
    "tier.vpro": "V-PRO",
    "tier.vadvance": "V-ADVANCE",
    "tier.velite": "V-ELITE",
    "tier.vultra": "V-ULTRA",

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
    "nav.portal": "Portal",
    "nav.login": "Login",
    "nav.logout": "Logout",
    "nav.language": "Language",

    // Home Page
    "home.hero.title": "Real-Time Fraud Detection for Indonesian SMEs",
    "home.hero.subtitle":
      "Protect your business with AI-powered fraud detection and business intelligence",
    "home.hero.cta": "Start Free",
    "home.hero.demo": "View Demo",

    // Pricing
    "pricing.title": "V-Guard AI Pricing Plans",
    "pricing.subtitle": "Choose the plan that fits your business needs",
    "pricing.monthly": "Per Month",
    "pricing.setup": "Setup Fee",
    "pricing.features": "Key Features",
    "pricing.cta": "Contact WhatsApp",

    // Portal
    "portal.dashboard": "Dashboard",
    "portal.transactions": "Transactions",
    "portal.agents": "AI Agents",
    "portal.referral": "Referral",
    "portal.investor": "Investor",
    "portal.admin": "Admin",

    // Dashboard
    "dashboard.title": "Client Dashboard",
    "dashboard.omset": "Total Revenue",
    "dashboard.transactions": "Transactions",
    "dashboard.anomalies": "Anomalies",
    "dashboard.cashiers": "Cashiers",
    "dashboard.status": "System Status",

    // Fraud Rules
    "fraud.r1": "VOID Direct Flag",
    "fraud.r2": "VOID Rate Spike",
    "fraud.r3": "Duplicate Transaction",
    "fraud.r4": "Balance Mismatch",
    "fraud.r5": "Off-Hours Transaction",
    "fraud.r6": "Rapid VOID",

    // Tiers
    "tier.demo": "DEMO",
    "tier.vlite": "V-LITE",
    "tier.vpro": "V-PRO",
    "tier.vadvance": "V-ADVANCE",
    "tier.velite": "V-ELITE",
    "tier.vultra": "V-ULTRA",

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

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem("language") as Language | null;
    if (stored && (stored === "id" || stored === "en")) {
      setLanguageState(stored);
    }

    // Check URL param
    const params = new URLSearchParams(window.location.search);
    const urlLang = params.get("lang") as Language | null;
    if (urlLang && (urlLang === "id" || urlLang === "en")) {
      setLanguageState(urlLang);
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem("language", lang);
  };

  const t = (key: string): string => {
    const keys = key.split(".");
    let value: any = translations[language];

    for (const k of keys) {
      value = value?.[k];
    }

    return value || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
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
