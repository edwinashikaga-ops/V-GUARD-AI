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
  const [user, setUser] = useState<ClientUser | null>(MOCK_USER);
  const [isLoading, setIsLoading] = useState(true);
  const [isMounted, setIsMounted] = useState(false);

  // Load user from localStorage on mount (client-side only)
  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("vguard_user");
      if (stored) {
        try {
          setUser(JSON.parse(stored));
        } catch (error) {
          console.error("Failed to parse stored user:", error);
          localStorage.removeItem("vguard_user");
          setUser(MOCK_USER);
        }
      } else {
        setUser(MOCK_USER);
      }
    }
    setIsMounted(true);
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
      setUser(MOCK_USER);
      if (typeof window !== "undefined") {
        localStorage.removeItem("vguard_user");
      }
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Provide stable context value
  const contextValue = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={contextValue}>
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

// Fallback function to get mock user outside of context
export function getMockUser(): ClientUser {
  return MOCK_USER;
}
