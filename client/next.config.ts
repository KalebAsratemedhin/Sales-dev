import type { NextConfig } from "next";

const apiTarget = process.env.API_PROXY_TARGET || "http://localhost";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/api/leads", destination: `${apiTarget}/api/leads` },
      { source: "/api/leads/:path*", destination: `${apiTarget}/api/leads/:path*` },
      { source: "/api/outreach", destination: `${apiTarget}/api/outreach` },
      { source: "/api/outreach/:path*", destination: `${apiTarget}/api/outreach/:path*` },
    ];
  },
};

export default nextConfig;
