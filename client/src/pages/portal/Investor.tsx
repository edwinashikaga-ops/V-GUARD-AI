import { useLanguage } from "@/contexts/LanguageContext";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { useState } from "react";
import { TrendingUp, AlertTriangle, ShieldCheck } from "lucide-react";

export default function Investor() {
  const { t, language } = useLanguage();
  const [revenue, setRevenue] = useState(100000000); // 100jt default
  const [leakageRate, setLeakageRate] = useState(5); // 5% default

  const leakageAmount = (revenue * leakageRate) / 100;
  const potentialSavings = leakageAmount * 0.9; // Assume 90% recovery

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">{t("roi.title")}</h1>
        <p className="text-slate-400">{t("roi.subtitle")}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="p-6 bg-slate-900 border-slate-800 space-y-8">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <label className="text-slate-300 font-medium">{t("roi.revenue")}</label>
              <span className="text-cyan-400 font-bold">Rp {revenue.toLocaleString("id-ID")}</span>
            </div>
            <Slider
              value={[revenue]}
              onValueChange={(val) => setRevenue(val[0])}
              max={1000000000}
              step={10000000}
              className="py-4"
            />
            <Input
              type="number"
              value={revenue}
              onChange={(e) => setRevenue(Number(e.target.value))}
              className="bg-slate-800 border-slate-700 text-white"
            />
          </div>

          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <label className="text-slate-300 font-medium">{t("roi.leakage")}</label>
              <span className="text-red-400 font-bold">{leakageRate}%</span>
            </div>
            <Slider
              value={[leakageRate]}
              onValueChange={(val) => setLeakageRate(val[0])}
              max={20}
              step={0.5}
              className="py-4"
            />
            <div className="flex justify-between text-xs text-slate-500">
              <span>0%</span>
              <span>10%</span>
              <span>20%</span>
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 gap-4">
          <Card className="p-6 bg-slate-900 border-slate-800 flex items-start gap-4">
            <div className="p-3 bg-red-500/10 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-red-500" />
            </div>
            <div>
              <p className="text-slate-400 text-sm mb-1">{t("roi.leakage")}</p>
              <p className="text-2xl font-bold text-white">Rp {leakageAmount.toLocaleString("id-ID")}</p>
              <p className="text-xs text-slate-500 mt-1">
                {language === "id" ? "Estimasi kerugian per bulan akibat kecurangan" : "Estimated monthly loss due to fraud"}
              </p>
            </div>
          </Card>

          <Card className="p-6 bg-cyan-500/10 border-cyan-500/20 flex items-start gap-4">
            <div className="p-3 bg-cyan-500/20 rounded-lg">
              <ShieldCheck className="w-6 h-6 text-cyan-400" />
            </div>
            <div>
              <p className="text-cyan-400 text-sm mb-1">{t("roi.result")}</p>
              <p className="text-3xl font-bold text-white">Rp {potentialSavings.toLocaleString("id-ID")}</p>
              <p className="text-xs text-cyan-500/60 mt-1">
                {language === "id" ? "Potensi dana yang dapat diselamatkan dengan V-Guard AI" : "Potential funds saved with V-Guard AI"}
              </p>
            </div>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-green-400" />
              <h3 className="text-white font-semibold">Analisis ROI</h3>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed">
              {language === "id" 
                ? "Dengan mengimplementasikan 6 aturan deteksi kecurangan (R1-R6) dan pemantauan langsung, bisnis Anda dapat menekan tingkat pembatalan (VOID) yang tidak wajar dan mengamankan margin keuntungan secara signifikan."
                : "By implementing 6 fraud detection rules (R1-R6) and real-time monitoring, your business can suppress unnatural void rates and significantly secure profit margins."}
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
