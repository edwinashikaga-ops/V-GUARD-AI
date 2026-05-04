import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Check, X } from "lucide-react";
import { useLocation } from "wouter";
import { TIERS, AGENTS, FRAUD_RULE_TIERS } from "@shared/constants";

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
  const { t } = useLanguage();
  const [, setLocation] = useLocation();

  const hasFeature = (tier: string, feature: string) => {
    const tierFeatures: Record<string, string[]> = {
      "V-LITE": ["fraud_rules_r1_r2_r3"],
      "V-PRO": ["fraud_rules_r1_r2_r3", "fraud_rules_r4_r5_r6", "bank_audit", "ocr_invoice"],
      "V-ADVANCE": ["fraud_rules_r1_r2_r3", "fraud_rules_r4_r5_r6", "bank_audit", "ocr_invoice", "cctv_ai_live", "multi_branch"],
      "V-ELITE": ["fraud_rules_r1_r2_r3", "fraud_rules_r4_r5_r6", "bank_audit", "ocr_invoice", "cctv_ai_live", "multi_branch", "dedicated_server", "forensic_deep_scan"],
      "V-ULTRA": features.map((f) => f.key),
    };
    
    // Ensure tier exists in tierFeatures, otherwise default to V-LITE or empty
    const activeTier = tier && tierFeatures[tier] ? tier : "V-LITE";
    return tierFeatures[activeTier].includes(feature);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800">
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
                    {tier === "V-PRO" ? "POPULER" : "PREMIUM"}
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
                    {agentCount} AI Agents
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
                      `https://wa.me/62812345678?text=${encodeURIComponent(
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
          Perbandingan Fitur Lengkap
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
              q: "Apakah ada trial gratis?",
              a: "Ya, kami menyediakan demo 15 menit gratis untuk semua tier.",
            },
            {
              q: "Bagaimana cara upgrade tier?",
              a: "Hubungi tim support kami melalui WhatsApp untuk upgrade tier.",
            },
            {
              q: "Apakah ada kontrak jangka panjang?",
              a: "Tidak, semua paket bersifat bulanan dan dapat dibatalkan kapan saja.",
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
