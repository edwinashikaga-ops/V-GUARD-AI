import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Copy, TrendingUp } from "lucide-react";

export default function Referral() {
  const referralLink = "https://v-guard-ai.com/?ref=VG-ABC123XYZ";
  const commissions = [
    { id: 1, partner: "PT Maju Jaya", tier: "V-PRO", commission: 450000, status: "PAID" },
    { id: 2, partner: "CV Sukses Bersama", tier: "V-LITE", commission: 150000, status: "PENDING" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">Program Referral</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-slate-800 border-slate-700 p-6">
            <p className="text-slate-400 text-sm">Total Komisi</p>
            <p className="text-3xl font-bold text-white">Rp 600.000</p>
          </Card>
          <Card className="bg-slate-800 border-slate-700 p-6">
            <p className="text-slate-400 text-sm">Partner Aktif</p>
            <p className="text-3xl font-bold text-white">2</p>
          </Card>
          <Card className="bg-slate-800 border-slate-700 p-6">
            <p className="text-slate-400 text-sm">Komisi Rate</p>
            <p className="text-3xl font-bold text-cyan-400">10%</p>
          </Card>
        </div>

        <Card className="bg-slate-800 border-slate-700 p-6 mb-8">
          <h2 className="text-xl font-bold text-white mb-4">Link Referral Anda</h2>
          <div className="flex gap-2">
            <input
              type="text"
              value={referralLink}
              readOnly
              className="flex-1 bg-slate-700 text-white px-4 py-2 rounded border border-slate-600"
            />
            <Button className="bg-cyan-500 hover:bg-cyan-600" onClick={() => navigator.clipboard.writeText(referralLink)}>
              <Copy className="w-4 h-4" />
            </Button>
          </div>
        </Card>

        <Card className="bg-slate-800 border-slate-700 p-6">
          <h2 className="text-xl font-bold text-white mb-4">Komisi Terbaru</h2>
          <div className="space-y-4">
            {commissions.map((c) => (
              <div key={c.id} className="flex items-center justify-between p-4 bg-slate-700/50 rounded">
                <div>
                  <p className="font-semibold text-white">{c.partner}</p>
                  <p className="text-sm text-slate-400">{c.tier}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-green-400">Rp {c.commission.toLocaleString("id-ID")}</p>
                  <p className="text-xs text-slate-400">{c.status}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
