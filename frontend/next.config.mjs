const API = process.env.NEXT_PUBLIC_API_BASE || "https://trading-platform-mv-1.onrender.com";
export default {
  reactStrictMode: true,
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API}/api/:path*` }];
  },
};

