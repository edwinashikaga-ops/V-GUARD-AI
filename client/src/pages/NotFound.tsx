import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";

export default function NotFound() {
  const [, setLocation] = useLocation();
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-4xl font-bold mb-4">404 - Not Found</h1>
      <p className="text-gray-600 mb-8">Halaman tidak ditemukan</p>
      <Button onClick={() => setLocation("/")}> Kembali ke Beranda</Button>
    </div>
  );
}
