import { useAuth } from "@/contexts/AuthContext";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertCircle, TrendingUp, Users, Activity, Clock } from "lucide-react";
import { useState, useEffect } from "react";

export default function ClientDashboard() {
  const { user } = useAuth();
  const [demoTimeLeft, setDemoTimeLeft] = useState(15 * 60);
  const isDemoMode = user?.tier === "DEMO";

  useEffect(() => {
    if (!isDemoMode) return;
    const interval = setInterval(() => {
      setDemoTimeLeft((prev) => (prev <= 1 ? 0 : prev - 1));
    }, 1000);
    return () => clearInterval(interval);
  }, [isDemoMode]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const mockAlerts = [
    { id: 1, rule: "R6", name: "Rapid VOID", severity: "CRITICAL", timestamp: new Date(), cashier: "Kasir 1" },
    { id: 2, rule: "R2", name: "VOID Rate Spike", severity: "HIGH", timestamp: new Date(Date.now() - 300000), cashier: "Kasir 3" },
    { id: 3, rule: "R4", name: "Balance Mismatch", severity: "MEDIUM", timestamp: new Date(Date.now() - 600000), cashier: "Kasir 2" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Dashboard Klien</h1>
            <p className="text-slate-400">Selamat datang, {user?.name || "Guest"}</p>
          </div>
          <div className="text-right">
            <Badge className="bg-cyan-600 text-white mb-2">Tier: {user?.tier || "DEMO"}</Badge>
            {isDemoMode && <div className="text-orange-400 font-semibold">Demo: {formatTime(demoTimeLeft)}</div>}
          </div>
        </div>

        {isDemoMode && (
          <Card className="bg-orange-900/20 border border-orange-700 p-4 mb-8">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-orange-400" />
              <div className="flex-1">
                <p className="text-orange-300 font-semibold">Mode Demo Aktif</p>
                <p className="text-orange-200 text-sm">Anda memiliki {formatTime(demoTimeLeft)} untuk mencoba semua fitur.</p>
              </div>
              <Button className="bg-orange-600 hover:bg-orange-700">Upgrade</Button>
            </div>
          </Card>
        )}

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-slate-800 border-slate-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Omset</p>
                <p className="text-3xl font-bold text-white">Rp 125.5M</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-400" />
            </div>
          </Card>
          <Card className="bg-slate-800 border-slate-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Transaksi Hari Ini</p>
                <p className="text-3xl font-bold text-white">1,247</p>
              </div>
              <Activity className="w-8 h-8 text-blue-400" />
            </div>
          </Card>
          <Card className="bg-slate-800 border-slate-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Anomali Terdeteksi</p>
                <p className="text-3xl font-bold text-white">12</p>
              </div>
              <AlertCircle className="w-8 h-8 text-red-400" />
            </div>
          </Card>
          <Card className="bg-slate-800 border-slate-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Kasir Aktif</p>
                <p className="text-3xl font-bold text-white">8</p>
              </div>
              <Users className="w-8 h-8 text-purple-400" />
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-slate-800 border-slate-700 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Clock className="w-5 h-5 text-cyan-400" />
              <h3 className="text-lg font-semibold text-white">Waktu Real-Time</h3>
            </div>
            <p className="text-3xl font-bold text-cyan-400">{new Date().toLocaleTimeString("id-ID")}</p>
          </Card>
          <Card className="bg-slate-800 border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Status Sistem</h3>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
              <span className="text-green-400">Online & Monitoring</span>
            </div>
          </Card>
          <Card className="bg-slate-800 border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Risk Level</h3>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-500 rounded-full" />
              <span className="text-yellow-400">Medium</span>
            </div>
          </Card>
        </div>

        <Card className="bg-slate-800 border-slate-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-6">Alert Terbaru</h2>
          <div className="space-y-4">
            {mockAlerts.map((alert) => (
              <div key={alert.id} className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                <div className="flex items-center gap-4">
                  <div className="text-2xl font-bold text-cyan-400">{alert.rule}</div>
                  <div>
                    <p className="font-semibold text-white">{alert.name}</p>
                    <p className="text-sm text-slate-400">{alert.cashier} • {alert.timestamp.toLocaleTimeString("id-ID")}</p>
                  </div>
                </div>
                <Badge className={alert.severity === "CRITICAL" ? "bg-red-600" : alert.severity === "HIGH" ? "bg-orange-600" : "bg-yellow-600"}>
                  {alert.severity}
                </Badge>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
