import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Check, X, Globe, MessageCircle } from "lucide-react";
import { useLocation } from "wouter";
import { TIERS } from "@shared/constants";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const tierOrder = ["V-LITE", "V-PRO", "V-ADVANCE", "V-ELITE", "V-ULTRA"];
const features = [
  { key: "fraud_rules_r1_r2_r3", label: "Fraud Rules R1-R3" },
  { key: "fraud_rules_r4_r5_r6", label: "Fraud Rules R4-R6" },
  { key: "bank_audit", label: "Bank Audit" },
  { key: "ocr_invoice", label: "OCR Invoice" },
  { key: "cctv_ai_live", label: "CCTV AI Live" },
  { key: "multi_branch", label: "Multi-Branch" },
  { key: "dedicated_server", label: "Dedicated Server" },
  { key: "forensic_deep_scan", label: "Forensic Deep Scan" },
  { key: "white_label", label: "White Label" },
  { key: "neural_network", label: "Neural Network" },
];

export default function Pricing() {
  const { t, language, setLanguage } = useLanguage();
  const [, setLocation] = useLocation();

  const hasFeature = (tier: string, feature: string) => {
    const tierFeatures: Record<string, string[]> = {
      "V-LITE": ["fraud_rules_r1_r2_r3"],
      "V-PRO": ["fraud_rules_r1_r2_r3", "fraud_rules_r4_r5_r6", "bank_audit", "ocr_invoice"],
      "V-ADVANCE": ["fraud_rules_r1_r2_r3", "fraud_rules_r4_r5_r6", "bank_audit", "ocr_invoice", "cctv_ai_live", "multi_branch"],
      "V-ELITE": ["fraud_rules_r1_r2_r3", "fraud_rules_r4_r5_r6", "bank_audit", "ocr_invoice", "cctv_ai_live", "multi_branch", "dedicated_server", "forensic_deep_scan"],
      "V-ULTRA": features.map((f) => f.key),
    };
    
    const activeTier = tier && tierFeatures[tier] ? tier : "V-LITE";
    return tierFeatures[activeTier].includes(feature);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800">
      {/* Navigation */}
      <nav className="border-b border-slate-700 bg-slate-900/50 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="text-2xl font-bold text-cyan-400 cursor-pointer" onClick={() => setLocation("/")}>V-Guard AI</div>
          <div className="flex gap-4 items-center">
            <Button
              variant="ghost"
              onClick={() => setLocation("/")}
              className="text-slate-300 hover:text-cyan-400"
            >
              {t("nav.home")}
            </Button>
            <Button
              variant="ghost"
              onClick={() => setLocation("/portal/investor")}
              className="text-slate-300 hover:text-cyan-400"
            >
              {t("nav.roi")}
            </Button>
            <Button
              onClick={() => setLocation("/portal/dashboard")}
              className="bg-cyan-500 hover:bg-cyan-600"
            >
              {t("nav.portal")}
            </Button>
            
            {/* Language Toggle */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="border-slate-700 text-slate-300 gap-2">
                  <Globe className="w-4 h-4" />
                  {language.toUpperCase()}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="bg-slate-900 border-slate-700 text-slate-300">
                <DropdownMenuItem onClick={() => setLanguage("id")} className="hover:bg-slate-800 cursor-pointer">
                  Bahasa Indonesia
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setLanguage("en")} className="hover:bg-slate-800 cursor-pointer">
                  English
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Button
              variant="outline"
              className="border-cyan-500 text-cyan-400 hover:bg-cyan-500/10 gap-2 hidden md:flex"
              onClick={() => {
                window.open("https://wa.me/6282122190885", "_blank");
              }}
            >
              <MessageCircle className="w-4 h-4" />
              {t("nav.customer_service")}
            </Button>
          </div>
        </div>
      </nav>

      {/* Header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-white text-center mb-4">
          {t("pricing.title")}
        </h1>
        <p className="text-xl text-slate-300 text-center">
          {t("pricing.subtitle")}
        </p>
      </div>

      {/* Pricing Cards */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          {tierOrder.map((tier) => {
            const tierInfo = TIERS[tier as keyof typeof TIERS];
            const agentCount = tierInfo.agents;
            const isPopular = tier === "V-PRO" || tier === "V-ULTRA";

            return (
              <Card
                key={tier}
                className={`relative bg-slate-800 border-slate-700 p-6 flex flex-col ${
                  isPopular ? "ring-2 ring-cyan-500 md:scale-105" : ""
                }`}
              >
                {isPopular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-cyan-500 text-white px-3 py-1 rounded-full text-xs font-semibold">
                    {tier === "V-PRO" ? t("pricing.popular") : t("pricing.premium")}
                  </div>
                )}

                <h3 className="text-xl font-bold text-white mb-2">{tier}</h3>
                <div className="mb-4">
                  <div className="text-3xl font-bold text-cyan-400">
                    Rp {tierInfo.monthlyPrice.toLocaleString("id-ID")}
                  </div>
                  <div className="text-sm text-slate-400">
                    {t("pricing.monthly")}
                  </div>
                  <div className="text-sm text-slate-500 mt-1">
                    {t("pricing.setup")}: Rp{" "}
                    {tierInfo.setupFee.toLocaleString("id-ID")}
                  </div>
                </div>

                <div className="mb-6 pb-6 border-b border-slate-700">
                  <p className="text-sm text-slate-300">
                    {agentCount} {t("portal.agents")}
                  </p>
                </div>

                <Button
                  className="w-full bg-cyan-500 hover:bg-cyan-600 text-white mb-6"
                  onClick={() => {
                    const message = `Saya tertarik dengan paket ${tier}. Biaya bulanan: Rp ${tierInfo.monthlyPrice.toLocaleString(
                      "id-ID"
                    )}, Biaya setup: Rp ${tierInfo.setupFee.toLocaleString(
                      "id-ID"
                    )}`;
                    window.open(
                      `https://wa.me/6282122190885?text=${encodeURIComponent(
                        message
                      )}`,
                      "_blank"
                    );
                  }}
                >
                  {t("pricing.cta")}
                </Button>

                <div className="space-y-3">
                  {features.slice(0, 4).map((feature) => (
                    <div key={feature.key} className="flex items-center gap-2">
                      {hasFeature(tier, feature.key) ? (
                        <Check className="w-4 h-4 text-green-400" />
                      ) : (
                        <X className="w-4 h-4 text-slate-600" />
                      )}
                      <span
                        className={`text-sm ${
                          hasFeature(tier, feature.key)
                            ? "text-slate-300"
                            : "text-slate-600"
                        }`}
                      >
                        {feature.label}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Feature Comparison */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-white mb-8">
          {t("pricing.comparison")}
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-4 px-4 text-slate-300">Fitur</th>
                {tierOrder.map((tier) => (
                  <th key={tier} className="text-center py-4 px-4 text-slate-300">
                    {tier}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {features.map((feature) => (
                <tr key={feature.key} className="border-b border-slate-700">
                  <td className="py-4 px-4 text-slate-300">{feature.label}</td>
                  {tierOrder.map((tier) => (
                    <td key={`${tier}-${feature.key}`} className="text-center py-4 px-4">
                      {hasFeature(tier, feature.key) ? (
                        <Check className="w-5 h-5 text-green-400 mx-auto" />
                      ) : (
                        <X className="w-5 h-5 text-slate-600 mx-auto" />
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* FAQ */}
      <section className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-white mb-8">FAQ</h2>
        <div className="space-y-4">
          {[
            {
              q: language === "id" ? "Apakah ada trial gratis?" : "Is there a free trial?",
              a: language === "id" ? "Ya, kami menyediakan demo 15 menit gratis untuk semua tier." : "Yes, we provide a free 15-minute demo for all tiers.",
            },
            {
              q: language === "id" ? "Bagaimana cara upgrade tier?" : "How to upgrade tier?",
              a: language === "id" ? "Hubungi tim support kami melalui WhatsApp untuk upgrade tier." : "Contact our support team via WhatsApp to upgrade your tier.",
            },
            {
              q: language === "id" ? "Apakah ada kontrak jangka panjang?" : "Is there a long-term contract?",
              a: language === "id" ? "Tidak, semua paket bersifat bulanan dan dapat dibatalkan kapan saja." : "No, all plans are monthly and can be cancelled at any time.",
            },
          ].map((faq, index) => (
            <div key={index} className="bg-slate-800 border border-slate-700 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-white mb-2">{faq.q}</h3>
              <p className="text-slate-400">{faq.a}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
