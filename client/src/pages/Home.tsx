import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { SentinelChatbot } from "@/components/SentinelChatbot";
import LiveProofFraudDetection from "@/components/LiveProofFraudDetection";
import { useLocation } from "wouter";
import { Shield, TrendingUp, Zap, Users, Lock, BarChart3, MessageCircle } from "lucide-react";

export default function Home() {
  const { t } = useLanguage();
  const [, setLocation] = useLocation();

  const features = [
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Fraud Detection R1-R6",
      description: "Deteksi fraud real-time dengan 6 aturan canggih",
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: "AI Agents (10 Squad)",
      description: "10 AI agents untuk berbagai fungsi bisnis",
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: "Real-Time Monitoring",
      description: "Pantau transaksi dan anomali secara real-time",
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "Multi-Role Access",
      description: "Klien, referral agent, investor, admin",
    },
    {
      icon: <Lock className="w-8 h-8" />,
      title: "Secure & Encrypted",
      description: "Enkripsi end-to-end dan compliance ready",
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Advanced Analytics",
      description: "Dashboard analytics dan reporting lengkap",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800">
      {/* Navigation */}
      <nav className="border-b border-slate-700 bg-slate-900/50 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="text-2xl font-bold text-cyan-400">V-Guard AI</div>
          <div className="flex gap-4 items-center">
            <Button
              variant="ghost"
              onClick={() => setLocation("/pricing")}
              className="text-slate-300 hover:text-cyan-400"
            >
              {t("nav.pricing")}
            </Button>
            <Button
              onClick={() => setLocation("/portal/dashboard")}
              className="bg-cyan-500 hover:bg-cyan-600"
            >
              {t("nav.portal")}
            </Button>
            <Button
              variant="outline"
              className="border-cyan-500 text-cyan-400 hover:bg-cyan-500/10 gap-2"
              onClick={() => {
                // Open customer service chat or contact form
                window.open("https://wa.me/6282122190885", "_blank");
              }}
            >
              <MessageCircle className="w-4 h-4" />
              Customer Service
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            {t("home.hero.title")}
          </h1>
          <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
            {t("home.hero.subtitle")}
          </p>
          <div className="flex gap-4 justify-center">
            <Button
              size="lg"
              className="bg-cyan-500 hover:bg-cyan-600 text-white"
              onClick={() => setLocation("/portal/dashboard")}
            >
              {t("home.hero.cta")}
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-cyan-500 text-cyan-400 hover:bg-cyan-500/10"
            >
              {t("home.hero.demo")}
            </Button>
          </div>
        </div>

        {/* Trust Badge */}
        <div className="text-center mb-20">
          <p className="text-slate-400">
            Dipercaya oleh 500+ bisnis di Indonesia
          </p>
        </div>
      </section>

      {/* Live Proof: Fraud Detection in Action */}
      <LiveProofFraudDetection />

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-4xl font-bold text-white text-center mb-12">
          Fitur Unggulan
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="bg-slate-800 border-slate-700 p-6 hover:border-cyan-500 transition"
            >
              <div className="text-cyan-400 mb-4">{feature.icon}</div>
              <h3 className="text-lg font-semibold text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-slate-400">{feature.description}</p>
            </Card>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <Card className="bg-gradient-to-r from-cyan-600 to-blue-600 border-0 p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Siap Melindungi Bisnis Anda?
          </h2>
          <p className="text-cyan-100 mb-8">
            Mulai dengan demo gratis 15 menit hari ini
          </p>
          <Button
            size="lg"
            className="bg-white text-cyan-600 hover:bg-slate-100"
            onClick={() => setLocation("/portal/dashboard")}
          >
            Mulai Sekarang
          </Button>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-700 bg-slate-900 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <h3 className="text-white font-semibold mb-4">Produk</h3>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><a href="#" className="hover:text-cyan-400">Fraud Detection</a></li>
                <li><a href="#" className="hover:text-cyan-400">AI Agents</a></li>
                <li><a href="#" className="hover:text-cyan-400">Analytics</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Perusahaan</h3>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><a href="#" className="hover:text-cyan-400">Tentang Kami</a></li>
                <li><a href="#" className="hover:text-cyan-400">Blog</a></li>
                <li><a href="#" className="hover:text-cyan-400">Karir</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Hubungi Kami</h3>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><a href="tel:+6282122190885" className="hover:text-cyan-400">+62 821 2219 0885</a></li>
                <li><a href="mailto:support@vguard.ai" className="hover:text-cyan-400">support@vguard.ai</a></li>
                <li><a href="#" className="hover:text-cyan-400">Live Chat</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-700 pt-8 text-center text-slate-400">
            <p>&copy; 2026 V-Guard AI. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Sentinel Chatbot */}
      <SentinelChatbot />
    </div>
  );
}
