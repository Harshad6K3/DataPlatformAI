import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

type User = { id: string; name: string; email: string; role: string };
type AuthContextValue = { user: User | null; isLoading: boolean; isAuthenticated: boolean; logout: () => void };
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => import.meta.env.VITE_AUTH_MODE === "mock"
    ? { id: "dev-user", name: "Alex Morgan", email: "alex.morgan@jpmorgan.com", role: "Data Office" }
    : null);
  const value = useMemo(() => ({ user, isLoading: false, isAuthenticated: Boolean(user), logout: () => setUser(null) }), [user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}