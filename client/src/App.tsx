import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import { LanguageProvider } from "./contexts/LanguageContext";
import { AuthProvider } from "./contexts/AuthContext";
import DashboardLayout from "./components/DashboardLayout";

// Public Pages
import Home from "./pages/Home";
import Pricing from "./pages/Pricing";
import NotFound from "./pages/NotFound";

// Portal Pages
import Portal from "./pages/Portal";
import ClientDashboard from "./pages/portal/ClientDashboard";
import Transactions from "./pages/portal/Transactions";
import Agents from "./pages/portal/Agents";
import Referral from "./pages/portal/Referral";
import Investor from "./pages/portal/Investor";
import Admin from "./pages/portal/Admin";

function Router() {
  return (
    <Switch>
      {/* Public Routes */}
      <Route path="/" component={Home} />
      <Route path="/pricing" component={Pricing} />

      {/* Portal Routes wrapped in DashboardLayout */}
      <Route path="/portal/:rest*">
        {(params) => (
          <DashboardLayout>
            <Switch>
              <Route path="/portal" component={Portal} />
              <Route path="/portal/dashboard" component={ClientDashboard} />
              <Route path="/portal/transactions" component={Transactions} />
              <Route path="/portal/agents" component={Agents} />
              <Route path="/portal/referral" component={Referral} />
              <Route path="/portal/investor" component={Investor} />
              <Route path="/portal/admin" component={Admin} />
              <Route component={NotFound} />
            </Switch>
          </DashboardLayout>
        )}
      </Route>

      {/* 404 */}
      <Route path="/404" component={NotFound} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="dark">
        <LanguageProvider defaultLanguage="id">
          <AuthProvider>
            <TooltipProvider>
              <Toaster />
              <Router />
            </TooltipProvider>
          </AuthProvider>
        </LanguageProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
