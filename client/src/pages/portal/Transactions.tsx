import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function Transactions() {
  const transactions = [
    { id: 1, type: "PENJUALAN", amount: 125000, cashier: "Kasir 1", time: "10:30", status: "OK" },
    { id: 2, type: "VOID", amount: 50000, cashier: "Kasir 2", time: "10:25", status: "FLAGGED" },
    { id: 3, type: "PENJUALAN", amount: 200000, cashier: "Kasir 3", time: "10:20", status: "OK" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">Riwayat Transaksi</h1>
        <Card className="bg-slate-800 border-slate-700 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700 bg-slate-900">
                <th className="px-6 py-3 text-left text-slate-300">ID</th>
                <th className="px-6 py-3 text-left text-slate-300">Tipe</th>
                <th className="px-6 py-3 text-left text-slate-300">Jumlah</th>
                <th className="px-6 py-3 text-left text-slate-300">Kasir</th>
                <th className="px-6 py-3 text-left text-slate-300">Waktu</th>
                <th className="px-6 py-3 text-left text-slate-300">Status</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.id} className="border-b border-slate-700 hover:bg-slate-700/50">
                  <td className="px-6 py-3 text-white">#{tx.id}</td>
                  <td className="px-6 py-3 text-slate-300">{tx.type}</td>
                  <td className="px-6 py-3 text-white">Rp {tx.amount.toLocaleString("id-ID")}</td>
                  <td className="px-6 py-3 text-slate-300">{tx.cashier}</td>
                  <td className="px-6 py-3 text-slate-300">{tx.time}</td>
                  <td className="px-6 py-3">
                    <Badge className={tx.status === "OK" ? "bg-green-600" : "bg-red-600"}>
                      {tx.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  );
}
