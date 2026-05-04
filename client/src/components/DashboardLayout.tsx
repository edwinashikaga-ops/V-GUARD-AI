import { useAuth } from "@/_core/hooks/useAuth";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";
import { getLoginUrl } from "@/const";
import { useIsMobile } from "@/hooks/useMobile";
import { useLanguage } from "@/contexts/LanguageContext";
import { LayoutDashboard, LogOut, PanelLeft, Users, TrendingUp, Package, BarChart3, Lock, Globe, Home } from "lucide-react";
import { CSSProperties, useEffect, useRef, useState } from "react";
import { useLocation } from "wouter";
import { DashboardLayoutSkeleton } from './DashboardLayoutSkeleton';
import { Button } from "./ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

const getMenuItems = (t: (key: string) => string) => [
  { icon: LayoutDashboard, label: t("portal.dashboard"), path: "/portal/dashboard", key: "dashboard", requiresPassword: false },
  { icon: TrendingUp, label: t("portal.roi"), path: "/portal/investor", key: "roi", requiresPassword: false },
  { icon: Package, label: t("portal.produk"), path: "/portal/referral", key: "produk", requiresPassword: false },
  { icon: BarChart3, label: t("portal.transactions"), path: "/portal/transactions", key: "transactions", requiresPassword: false },
  { icon: Users, label: t("portal.agents"), path: "/portal/agents", key: "agents", requiresPassword: false },
  { icon: Lock, label: t("portal.admin"), path: "/portal/admin", key: "admin", requiresPassword: true },
];

const SIDEBAR_WIDTH_KEY = "sidebar-width";
const DEFAULT_WIDTH = 280;
const MIN_WIDTH = 200;
const MAX_WIDTH = 480;
const ADMIN_PASSWORD = "winbju 8282";

// EMERGENCY: Mock user for client review when auth server is down
const MOCK_USER = {
  id: "mock-client-id",
  name: "Client Reviewer",
  email: "client@vguard.ai",
  role: "admin",
  tier: "enterprise"
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarWidth, setSidebarWidth] = useState(DEFAULT_WIDTH);
  const [isMounted, setIsMounted] = useState(false);

  // Load sidebar width from localStorage on mount (client-side only)
  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem(SIDEBAR_WIDTH_KEY);
      if (saved) {
        const width = parseInt(saved, 10);
        if (width >= MIN_WIDTH && width <= MAX_WIDTH) {
          setSidebarWidth(width);
        }
      }
    }
    setIsMounted(true);
  }, []);
  
  // Disable auth loading and redirect for client review
  const loading = false;
  const user = MOCK_USER;
  
  const { t } = useLanguage();

  // Save sidebar width to localStorage on change (client-side only)
  useEffect(() => {
    if (isMounted && typeof window !== "undefined") {
      localStorage.setItem(SIDEBAR_WIDTH_KEY, sidebarWidth.toString());
    }
  }, [sidebarWidth, isMounted]);

  // Don't render until mounted to avoid hydration mismatch
  if (!isMounted || loading) {
    return <DashboardLayoutSkeleton />
  }

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": `${sidebarWidth}px`,
        } as CSSProperties
      }
    >
      <DashboardLayoutContent setSidebarWidth={setSidebarWidth} isMounted={isMounted}>
        {children}
      </DashboardLayoutContent>
    </SidebarProvider>
  );
}

type DashboardLayoutContentProps = {
  children: React.ReactNode;
  setSidebarWidth: (width: number) => void;
  isMounted: boolean;
};

function DashboardLayoutContent({
  children,
  setSidebarWidth,
  isMounted,
}: DashboardLayoutContentProps) {
  const user = MOCK_USER;
  const logout = () => { console.log("Logout disabled during emergency bypass"); };
  
  const { t, language, setLanguage } = useLanguage();
  const [location, setLocation] = useLocation();
  const { state, toggleSidebar } = useSidebar();
  const isCollapsed = state === "collapsed";
  const [isResizing, setIsResizing] = useState(false);
  const sidebarRef = useRef<HTMLDivElement>(null);
  const menuItems = getMenuItems(t);
  const activeMenuItem = menuItems.find(item => item.path === location);
  const isMobile = useIsMobile();
  
  // Admin password protection state
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [passwordInput, setPasswordInput] = useState("");
  const [adminAccessGranted, setAdminAccessGranted] = useState(false);
  const [pendingAdminPath, setPendingAdminPath] = useState("");

  useEffect(() => {
    if (isCollapsed) {
      setIsResizing(false);
    }
  }, [isCollapsed]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;

      const sidebarLeft = sidebarRef.current?.getBoundingClientRect().left ?? 0;
      const newWidth = e.clientX - sidebarLeft;
      if (newWidth >= MIN_WIDTH && newWidth <= MAX_WIDTH) {
        setSidebarWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
  }, [isResizing, setSidebarWidth]);

  const handleMenuClick = (item: typeof menuItems[0]) => {
    if (item.requiresPassword && !adminAccessGranted) {
      setPendingAdminPath(item.path);
      setShowPasswordDialog(true);
      setPasswordInput("");
    } else {
      setLocation(item.path);
    }
  };

  const handlePasswordSubmit = () => {
    if (passwordInput === ADMIN_PASSWORD) {
      setAdminAccessGranted(true);
      setShowPasswordDialog(false);
      if (pendingAdminPath) {
        setLocation(pendingAdminPath);
      }
    } else {
      setPasswordInput("");
      alert("Incorrect password. Please try again.");
    }
  };

  return (
    <>
      <Dialog open={showPasswordDialog} onOpenChange={setShowPasswordDialog}>
        <DialogContent className="sm:max-w-md bg-slate-900 border-slate-700 text-white">
          <DialogHeader>
            <DialogTitle>{language === "id" ? "Akses Admin Diperlukan" : "Admin Access Required"}</DialogTitle>
            <DialogDescription className="text-slate-400">
              {language === "id" ? "Masukkan kata sandi untuk mengakses panel Admin." : "Enter the password to access the Admin panel."}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Input
              type="password"
              placeholder={language === "id" ? "Masukkan kata sandi" : "Enter password"}
              value={passwordInput}
              onChange={(e) => setPasswordInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  handlePasswordSubmit();
                }
              }}
              className="bg-slate-800 border-slate-700 text-white"
            />
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setShowPasswordDialog(false)}
                className="flex-1 border-slate-700 text-slate-300"
              >
                {language === "id" ? "Batal" : "Cancel"}
              </Button>
              <Button
                onClick={handlePasswordSubmit}
                className="flex-1 bg-cyan-600 hover:bg-cyan-700 text-white"
              >
                {language === "id" ? "Buka" : "Unlock"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <div className="relative" ref={sidebarRef}>
        <Sidebar
          collapsible="icon"
          className="border-r border-slate-800 bg-slate-950"
          disableTransition={isResizing}
        >
          <SidebarHeader className="h-16 justify-center border-b border-slate-800">
            <div className="flex items-center gap-3 px-2 transition-all w-full">
              <button
                onClick={toggleSidebar}
                className="h-8 w-8 flex items-center justify-center hover:bg-slate-800 rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring shrink-0"
                aria-label="Toggle navigation"
              >
                <PanelLeft className="h-4 w-4 text-slate-400" />
              </button>
              {!isCollapsed ? (
                <div className="flex items-center gap-2 min-w-0">
                  <span className="font-semibold tracking-tight truncate text-cyan-400">
                    V-Guard AI
                  </span>
                </div>
              ) : null}
            </div>
          </SidebarHeader>

          <SidebarContent className="gap-0 bg-slate-950">
            <SidebarMenu className="px-2 py-4">
              {/* Home Link */}
              <SidebarMenuItem>
                <SidebarMenuButton
                  onClick={() => setLocation("/")}
                  tooltip={t("nav.home")}
                  className="h-10 transition-all font-normal text-slate-400 hover:text-slate-300 hover:bg-slate-800"
                >
                  <Home className="h-4 w-4" />
                  <span>{t("nav.home")}</span>
                </SidebarMenuButton>
              </SidebarMenuItem>

              {menuItems.map(item => {
                const isActive = location === item.path;
                return (
                  <SidebarMenuItem key={item.key}>
                    <SidebarMenuButton
                      isActive={isActive}
                      onClick={() => handleMenuClick(item)}
                      tooltip={item.label}
                      className={`h-10 transition-all font-normal ${
                        isActive ? "bg-cyan-400/10 text-cyan-400" : "text-slate-400 hover:text-slate-300 hover:bg-slate-800"
                      }`}
                    >
                      <item.icon
                        className={`h-4 w-4 ${
                          isActive ? "text-cyan-400" : "text-slate-400"
                        }`}
                      />
                      <span>{item.label}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarContent>

          <SidebarFooter className="p-3 bg-slate-950 border-t border-slate-800">
            <div className="flex flex-col gap-2">
              {/* Language Toggle in Sidebar */}
              {!isCollapsed && (
                <div className="flex gap-1 p-1 bg-slate-900 rounded-lg mb-2">
                  <button
                    onClick={() => setLanguage("id")}
                    className={`flex-1 py-1 text-xs rounded-md transition ${language === "id" ? "bg-cyan-500 text-white" : "text-slate-400 hover:text-slate-200"}`}
                  >
                    ID
                  </button>
                  <button
                    onClick={() => setLanguage("en")}
                    className={`flex-1 py-1 text-xs rounded-md transition ${language === "en" ? "bg-cyan-500 text-white" : "text-slate-400 hover:text-slate-200"}`}
                  >
                    EN
                  </button>
                </div>
              )}
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center gap-3 rounded-lg px-1 py-1 hover:bg-slate-800 transition-colors w-full text-left group-data-[collapsible=icon]:justify-center focus:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                    <Avatar className="h-9 w-9 border border-slate-700 shrink-0">
                      <AvatarFallback className="text-xs font-medium bg-slate-800 text-slate-300">
                        {user?.name?.charAt(0).toUpperCase() || "U"}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0 group-data-[collapsible=icon]:hidden">
                      <p className="text-sm font-medium truncate leading-none text-slate-200">
                        {user?.name || "User"}
                      </p>
                      <p className="text-xs text-slate-500 truncate mt-1.5">
                        {user?.email || "user@vguard.ai"}
                      </p>
                    </div>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48 bg-slate-900 border-slate-700 text-slate-300">
                  <DropdownMenuItem
                    onClick={logout}
                    className="cursor-pointer text-red-400 focus:text-red-400 hover:bg-slate-800"
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>{language === "id" ? "Keluar" : "Sign out"}</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </SidebarFooter>
        </Sidebar>
        <div
          className={`absolute top-0 right-0 w-1 h-full cursor-col-resize hover:bg-cyan-500/20 transition-colors ${isCollapsed ? "hidden" : ""}`}
          onMouseDown={() => {
            if (isCollapsed) return;
            setIsResizing(true);
          }}
          style={{ zIndex: 50 }}
        />
      </div>

      <SidebarInset className="bg-slate-950">
        {isMobile && (
          <div className="flex border-b border-slate-800 h-14 items-center justify-between bg-slate-900/95 px-2 backdrop-blur sticky top-0 z-40">
            <div className="flex items-center gap-2">
              <SidebarTrigger className="h-9 w-9 rounded-lg bg-slate-800 text-slate-300" />
              <div className="flex items-center gap-3">
                <div className="flex flex-col gap-1">
                  <span className="tracking-tight text-slate-200">
                    {activeMenuItem?.label ?? "Menu"}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex gap-2">
               <Button variant="ghost" size="sm" onClick={() => setLanguage(language === "id" ? "en" : "id")} className="text-slate-400">
                 {language.toUpperCase()}
               </Button>
            </div>
          </div>
        )}
        <main className="flex-1 p-4 bg-slate-950 text-slate-200">{children}</main>
      </SidebarInset>
    </>
  );
}
