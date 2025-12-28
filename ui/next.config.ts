import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,

  // Disable x-powered-by header for security
  poweredByHeader: false,

  // Environment variables available to the browser must be prefixed with NEXT_PUBLIC_
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Compiler options
  compiler: {
    // Remove console logs in production
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Output standalone for Docker deployment
  output: 'standalone',
} satisfies NextConfig;

export default nextConfig;
