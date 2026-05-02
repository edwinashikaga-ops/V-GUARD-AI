import { AGENTS, isAgentUnlocked } from "@shared/constants";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/contexts/AuthContext";

export default function Agents() {
  const { user } = useAuth();
  const userTier = user?.tier || "DEMO";

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-2">AI Agents Squad</h1>
        <p className="text-slate-400 mb-8">
          10 AI Agents siap membantu bisnis Anda. Tier Anda: <span className="text-cyan-400 font-semibold">{userTier}</span>
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {AGENTS.map((agent) => {
            const isUnlocked = isAgentUnlocked(agent.id, userTier);

            return (
              <Card
                key={agent.id}
                className={`p-6 flex flex-col items-center text-center transition ${
                  isUnlocked
                    ? "bg-slate-800 border-slate-700 hover:border-cyan-500"
                    : "bg-slate-900 border-slate-700 opacity-60"
                }`}
              >
                <div className="text-4xl mb-3">{agent.icon}</div>
                <h3 className="text-lg font-bold text-white mb-1">
                  {agent.name}
                </h3>
                <p className="text-xs text-slate-400 mb-3">{agent.role}</p>
                <p className="text-xs text-slate-500 mb-4 h-10">
                  {agent.description}
                </p>

                {isUnlocked ? (
                  <Badge className="bg-green-600 text-white">
                    Unlocked
                  </Badge>
                ) : (
                  <Badge className="bg-slate-700 text-slate-300">
                    {agent.minTier}+
                  </Badge>
                )}
              </Card>
            );
          })}
        </div>

        {/* Tier Comparison */}
        <div className="mt-12 bg-slate-800 border border-slate-700 p-8 rounded-lg">
          <h2 className="text-2xl font-bold text-white mb-6">
            Agents per Tier
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-cyan-400 font-bold mb-3">DEMO / V-LITE</h3>
              <ul className="text-slate-300 space-y-2">
                <li>✓ Concierge (CS)</li>
                <li>✓ Watchdog (Fraud)</li>
              </ul>
            </div>
            <div>
              <h3 className="text-cyan-400 font-bold mb-3">V-PRO / V-ADVANCE</h3>
              <ul className="text-slate-300 space-y-2">
                <li>✓ Semua V-LITE +</li>
                <li>✓ Liaison (POS)</li>
                <li>✓ Analyst (Finance)</li>
                <li>✓ Stockmaster (Inventory)</li>
                <li>✓ Sentinel (Monitor)</li>
                <li>✓ Legalist (Compliance)</li>
                <li>✓ Treasurer (Revenue)</li>
              </ul>
            </div>
            <div>
              <h3 className="text-cyan-400 font-bold mb-3">V-ELITE / V-ULTRA</h3>
              <ul className="text-slate-300 space-y-2">
                <li>✓ Semua V-PRO +</li>
                <li>✓ Visionary (CCTV)</li>
                <li>✓ GrowthHacker (Marketing)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
