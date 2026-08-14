export { edgeAuth as middleware } from "@/lib/auth/edge-auth";

export const config = {
  matcher: ["/dashboard/:path*", "/api/export/:path*"],
};
