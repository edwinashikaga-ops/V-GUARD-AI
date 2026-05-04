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
  const [user, setUser] = useState<ClientUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user from localStorage on mount
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
    } else {
      setUser(MOCK_USER);
    }
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
      if (typeof window !== "undefined") {
        localStorage.removeItem("vguard_user");
      }
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
        isAuthenticated: !!user,
        isLoading,
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
