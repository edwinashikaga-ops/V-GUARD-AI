import { getLoginUrl } from "@/const";
import { trpc } from "@/lib/trpc";
import { TRPCClientError } from "@trpc/client";
import { useCallback, useEffect, useMemo } from "react";

type UseAuthOptions = {
  redirectOnUnauthenticated?: boolean;
  redirectPath?: string;
};

// EMERGENCY: Mock user for client review when auth server is down
const MOCK_USER = {
  id: "mock-client-id",
  name: "Client Reviewer",
  email: "client@vguard.ai",
  role: "admin",
  tier: "V-ULTRA"
};

export function useAuth(options?: UseAuthOptions) {
  const { redirectOnUnauthenticated = false, redirectPath = getLoginUrl() } =
    options ?? {};
  const utils = trpc.useUtils();

  // meQuery disabled during emergency bypass
  /*
  const meQuery = trpc.auth.me.useQuery(undefined, {
    retry: false,
    refetchOnWindowFocus: false,
  });
  */

  const logoutMutation = trpc.auth.logout.useMutation({
    onSuccess: () => {
      // utils.auth.me.setData(undefined, null);
    },
  });

  const logout = useCallback(async () => {
    try {
      // await logoutMutation.mutateAsync();
      console.log("Logout disabled during bypass");
    } catch (error: unknown) {
      if (
        error instanceof TRPCClientError &&
        error.data?.code === "UNAUTHORIZED"
      ) {
        return;
      }
      throw error;
    } finally {
      // utils.auth.me.setData(undefined, null);
      // await utils.auth.me.invalidate();
    }
  }, [logoutMutation, utils]);

  const state = useMemo(() => {
    // localStorage.setItem(
    //   "manus-runtime-user-info",
    //   JSON.stringify(MOCK_USER)
    // );
    return {
      user: MOCK_USER,
      loading: false,
      error: null,
      isAuthenticated: true,
    };
  }, []);

  useEffect(() => {
    if (!redirectOnUnauthenticated) return;
    // Redirect logic disabled during bypass
    /*
    if (meQuery.isLoading || logoutMutation.isPending) return;
    if (state.user) return;
    if (typeof window === "undefined") return;
    if (window.location.pathname === redirectPath) return;

    window.location.href = redirectPath
    */
  }, [
    redirectOnUnauthenticated,
    redirectPath,
    state.user,
  ]);

  return {
    ...state,
    refresh: () => Promise.resolve(),
    logout,
  };
}
