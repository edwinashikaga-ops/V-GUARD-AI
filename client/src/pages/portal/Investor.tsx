import { Card } from "@/components/ui/card";
import { TrendingUp, BarChart3 } from "lucide-react";

export default function Investor() {
  const returns = [
    { month: "Januari", mrr: 5000000, roi: 15 },
    { month: "Februari", mrr: 5500000, roi: 18 },
    { month: "Maret", mrr: 6200000, roi: 22 },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">Area Investor</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-slate-800 border-slate-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">MRR Saat Ini</p>
                <p className="text-3xl font-bold text-white">Rp 6.2M</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-400" />
            </div>
          </Card>
          <Card className="bg-slate-800 border-slate-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">ROI YTD</p>
                <p className="text-3xl font-bold text-white">22%</p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-400" />
            </div>
          </Card>
          <Card className="bg-slate-800 border-slate-700 p-6">
            <p className="text-slate-400 text-sm">Total Return</p>
            <p className="text-3xl font-bold text-cyan-400">Rp 16.7M</p>
          </Card>
        </div>

        <Card className="bg-slate-800 border-slate-700 p-6">
          <h2 className="text-xl font-bold text-white mb-4">Riwayat Return</h2>
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="px-4 py-2 text-left text-slate-300">Bulan</th>
                <th className="px-4 py-2 text-left text-slate-300">MRR</th>
                <th className="px-4 py-2 text-left text-slate-300">ROI</th>
              </tr>
            </thead>
            <tbody>
              {returns.map((r) => (
                <tr key={r.month} className="border-b border-slate-700">
                  <td className="px-4 py-2 text-white">{r.month}</td>
                  <td className="px-4 py-2 text-green-400">Rp {r.mrr.toLocaleString("id-ID")}</td>
                  <td className="px-4 py-2 text-blue-400">{r.roi}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  );
}
