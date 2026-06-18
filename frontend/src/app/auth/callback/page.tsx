"use client";

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

function CallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const code = searchParams.get("code");
    if (code) {
      fetch(`/api/auth/github/callback?code=${code}`)
        .then((r) => r.json())
        .then((data) => {
          if (data.access_token) {
            localStorage.setItem("token", data.access_token);
            router.push("/");
            window.location.reload();
          } else {
            router.push("/login?error=oauth_failed");
          }
        })
        .catch(() => router.push("/login?error=oauth_failed"));
    } else {
      router.push("/login");
    }
  }, [searchParams, router]);

  return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600 mx-auto mb-4"></div>
        <p className="text-gray-500">Completing sign in...</p>
      </div>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600 mx-auto"></div>
        </div>
      }
    >
      <CallbackHandler />
    </Suspense>
  );
}
