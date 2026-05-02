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

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<ClientUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user from localStorage on mount
  useEffect(() => {
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
  }, []);

  const login = async (clientId: string, password: string) => {
    setIsLoading(true);
    try {
      // TODO: Call tRPC endpoint
      // const result = await trpc.auth.loginClient.mutate({ clientId, password });
      // setUser(result);
      // localStorage.setItem("vguard_user", JSON.stringify(result));
      console.log("Login attempt:", clientId);
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
      // TODO: Call tRPC endpoint
      // await trpc.auth.logout.mutate();
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
