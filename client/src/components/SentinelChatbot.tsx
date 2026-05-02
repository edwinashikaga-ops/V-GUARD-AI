import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { MessageCircle, X, Send } from "lucide-react";

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
}

const quickReplies = [
  { label: "Tentang Produk", value: "product_info" },
  { label: "Hitung ROI", value: "roi_calc" },
  { label: "Demo Booking", value: "demo_booking" },
  { label: "Hubungi Support", value: "support" },
];

const botResponses: Record<string, string> = {
  product_info:
    "V-Guard AI adalah platform fraud detection real-time dengan 10 AI Agents. Kami menyediakan 6 fraud rules (R1-R6) untuk melindungi bisnis Anda dari fraud transaksi.",
  roi_calc:
    "ROI Calculator: Jika Anda memproses Rp 100M/bulan dengan fraud rate 2%, V-Guard AI bisa menghemat ~Rp 2M/bulan. Dengan biaya V-PRO Rp 450K/bulan, ROI Anda adalah 400%+",
  demo_booking:
    "Kami siap memberikan demo gratis 15 menit! Silakan hubungi tim kami melalui WhatsApp untuk mengatur jadwal demo.",
  support:
    "Tim support kami tersedia 24/7. Hubungi kami di WhatsApp: +62 812-3456-7890 atau email: support@v-guard-ai.com",
};

export function SentinelChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "Halo! Saya Sentinel, asisten AI V-Guard. Ada yang bisa saya bantu?",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");

  const handleQuickReply = (value: string) => {
    const response = botResponses[value] || "Maaf, saya tidak mengerti.";

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        text: quickReplies.find((r) => r.value === value)?.label || "",
        sender: "user",
        timestamp: new Date(),
      },
      {
        id: (Date.now() + 1).toString(),
        text: response,
        sender: "bot",
        timestamp: new Date(),
      },
    ]);
  };

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        text: inputValue,
        sender: "user",
        timestamp: new Date(),
      },
      {
        id: (Date.now() + 1).toString(),
        text: "Terima kasih atas pertanyaannya. Silakan hubungi support@v-guard-ai.com untuk informasi lebih lanjut.",
        sender: "bot",
        timestamp: new Date(),
      },
    ]);
    setInputValue("");
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-16 h-16 bg-cyan-500 hover:bg-cyan-600 text-white rounded-full flex items-center justify-center shadow-lg transition transform hover:scale-110"
      >
        <MessageCircle className="w-8 h-8" />
      </button>
    );
  }

  return (
    <Card className="fixed bottom-6 right-6 w-96 h-[600px] bg-slate-800 border-slate-700 flex flex-col shadow-2xl">
      {/* Header */}
      <div className="bg-cyan-600 p-4 flex items-center justify-between rounded-t-lg">
        <div>
          <h3 className="font-bold text-white">Sentinel CS</h3>
          <p className="text-xs text-cyan-100">Always here to help</p>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="text-white hover:bg-cyan-700 p-1 rounded"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                msg.sender === "user"
                  ? "bg-cyan-600 text-white"
                  : "bg-slate-700 text-slate-100"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      {/* Quick Replies */}
      <div className="px-4 py-2 space-y-2 border-t border-slate-700">
        {quickReplies.map((reply) => (
          <Button
            key={reply.value}
            size="sm"
            variant="outline"
            className="w-full text-xs justify-start border-slate-600 text-slate-300 hover:bg-slate-700"
            onClick={() => handleQuickReply(reply.value)}
          >
            {reply.label}
          </Button>
        ))}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-slate-700 flex gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
          placeholder="Tulis pesan..."
          className="flex-1 bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 text-sm focus:outline-none focus:border-cyan-500"
        />
        <Button
          size="sm"
          className="bg-cyan-600 hover:bg-cyan-700"
          onClick={handleSendMessage}
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </Card>
  );
}
