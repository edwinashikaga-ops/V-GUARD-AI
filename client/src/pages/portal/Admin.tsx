import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function Admin() {
  const clients = [
    { id: 1, name: "PT Maju Jaya", tier: "V-LITE", status: "aktif", joined: "2026-01-15" },
    { id: 2, name: "CV Sukses Bersama", tier: "DEMO", status: "pending", joined: "2026-05-01" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">Admin Panel</h1>

        <Card className="bg-slate-800 border-slate-700 p-6">
          <h2 className="text-xl font-bold text-white mb-4">Daftar Klien</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="px-4 py-2 text-left text-slate-300">Nama</th>
                  <th className="px-4 py-2 text-left text-slate-300">Tier</th>
                  <th className="px-4 py-2 text-left text-slate-300">Status</th>
                  <th className="px-4 py-2 text-left text-slate-300">Bergabung</th>
                  <th className="px-4 py-2 text-left text-slate-300">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {clients.map((c) => (
                  <tr key={c.id} className="border-b border-slate-700 hover:bg-slate-700/50">
                    <td className="px-4 py-2 text-white">{c.name}</td>
                    <td className="px-4 py-2 text-slate-300">{c.tier}</td>
                    <td className="px-4 py-2">
                      <Badge className={c.status === "aktif" ? "bg-green-600" : "bg-yellow-600"}>
                        {c.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-2 text-slate-300">{c.joined}</td>
                    <td className="px-4 py-2">
                      <Button size="sm" className="bg-cyan-600 hover:bg-cyan-700">
                        Edit
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}
