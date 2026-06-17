"use client";

import { useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useExchangeGoogleCodeMutation } from "@/store/outreachApi";
import { GOOGLE_OAUTH_STATE_KEY } from "@/lib/googleOAuth";
import { Card, CardContent } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";

export default function GoogleCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [exchangeCode, { isLoading, isError, isSuccess }] = useExchangeGoogleCodeMutation();
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    const code = searchParams.get("code") || "";
    const state = searchParams.get("state") || "";
    const storedState = sessionStorage.getItem(GOOGLE_OAUTH_STATE_KEY) || "";

    if (!code) {
      router.replace("/settings?google=error");
      return;
    }

    exchangeCode({ code, state: state || storedState })
      .unwrap()
      .then(() => {
        sessionStorage.removeItem(GOOGLE_OAUTH_STATE_KEY);
        router.replace("/settings?google=connected");
      })
      .catch(() => {
        router.replace("/settings?google=error");
      });
  }, [exchangeCode, router, searchParams]);

  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <Card className="w-full max-w-md">
        <CardContent className="py-10 text-center space-y-4">
          {isLoading && (
            <>
              <Skeleton className="h-8 w-48 mx-auto" />
              <p className="text-slate-400">Connecting Google…</p>
            </>
          )}
          {isError && <p className="text-red-400">Connection failed. Redirecting to Settings…</p>}
          {isSuccess && <p className="text-primary">Connected. Redirecting to Settings…</p>}
        </CardContent>
      </Card>
    </div>
  );
}
