import React, { createContext, useContext, useState, useEffect } from "react";

export interface ClientUser {
  clientId: string;
  name: string;
  tier: string;
  token: string;
}

interface AuthContextType {
  user: ClientUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (clientId: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

// EMERGENCY: Mock user for client review when auth server is down
const MOCK_USER: ClientUser = {
  clientId: "mock-client-id",
  name: "Client Reviewer",
  tier: "V-ULTRA",
  token: "mock-token"
};

export function AuthProvider({ children }: AuthProviderProps) {
  // Force mock user and loading false for emergency bypass
  const [user, setUser] = useState<ClientUser | null>(MOCK_USER);
  const [isLoading, setIsLoading] = useState(false);

  // Load user from localStorage on mount (disabled for bypass)
  useEffect(() => {
    /*
    const stored = localStorage.getItem("vguard_user");
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch (error) {
        console.error("Failed to parse stored user:", error);
        localStorage.removeItem("vguard_user");
      }
    }
    setIsLoading(false);
    */
    setUser(MOCK_USER);
    setIsLoading(false);
  }, []);

  const login = async (clientId: string, password: string) => {
    setIsLoading(true);
    try {
      console.log("Login disabled during bypass:", clientId);
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      setUser(null);
      localStorage.removeItem("vguard_user");
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: true, // Always true for bypass
        isLoading: false,      // Always false for bypass
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
