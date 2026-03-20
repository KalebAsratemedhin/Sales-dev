import { fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { BaseQueryFn, FetchArgs } from "@reduxjs/toolkit/query";
import { getApiBase } from "@/lib/apiBase";
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "@/lib/authStorage";

type TokenResponse = { access: string; refresh?: string };

function getUrlFromArgs(args: string | FetchArgs): string | undefined {
  if (typeof args === "string") return args;
  return (args as FetchArgs).url;
}

function getAuthBaseUrl(): string {
  const base = getApiBase();
  return base ? `${base}/api/auth` : "/api/auth";
}

let refreshInFlight: Promise<TokenResponse> | null = null;

function normalizeFetchArgs(args: string | FetchArgs, token: string | null): FetchArgs {
  if (typeof args === "string") {
    const headers = new Headers();
    if (token) headers.set("Authorization", `Bearer ${token}`);
    return { url: args, headers };
  }

  const normalizedHeaders = new Headers(args.headers as HeadersInit | undefined);
  if (token) normalizedHeaders.set("Authorization", `Bearer ${token}`);

  const body = (args as FetchArgs).body;
  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;
  const hasJsonBody = body !== undefined && body !== null && !isFormData;

  if (hasJsonBody && typeof body !== "string") {
    normalizedHeaders.set("Content-Type", "application/json");
  }

  const normalizedBody =
    hasJsonBody && typeof body !== "string" ? JSON.stringify(body) : body;

  return {
    ...args,
    headers: normalizedHeaders,
    body: normalizedBody,
  };
}

export function createBaseQueryWithReauth(baseUrl: string): BaseQueryFn<string | FetchArgs, unknown, unknown> {
  const authBaseUrl = getAuthBaseUrl();

  const responseHandler = async (response: Response) => {
    if (response.status === 204) return null;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json") || contentType.includes("+json")) {
      return response.json();
    }
    return response.blob();
  };

  const otherBaseQuery = fetchBaseQuery({ baseUrl, responseHandler });
  const refreshBaseQuery = fetchBaseQuery({ baseUrl: authBaseUrl, responseHandler });

  return async (args, api, extraOptions) => {
    const token = getAccessToken();
    const normalizedArgs = normalizeFetchArgs(args, token);
    const result = await otherBaseQuery(normalizedArgs, api, extraOptions);
    const status = (result as any)?.error?.status;
    if (status !== 401) return result;

    const url = getUrlFromArgs(args);
    if (url && url.includes("/refresh/")) return result;

    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      clearTokens();
      return result;
    }

    try {
      if (!refreshInFlight) {
        refreshInFlight = (async () => {
          const refreshResult = await refreshBaseQuery(
            normalizeFetchArgs({ url: "/refresh/", method: "POST", body: { refresh: refreshToken } }, null),
            api,
            extraOptions
          );

          const refreshData = (refreshResult as any)?.data as TokenResponse | undefined;
          const refreshStatus = (refreshResult as any)?.error?.status;
          if (!refreshData || refreshStatus) throw new Error("refresh_failed");

          setTokens(refreshData);
          return refreshData;
        })();
      }

      await refreshInFlight;

      return otherBaseQuery(normalizeFetchArgs(args, getAccessToken()), api, extraOptions);
    } catch {
      clearTokens();
      return result;
    } finally {
      refreshInFlight = null;
    }
  };
}

