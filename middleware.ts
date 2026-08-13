export { auth as middleware } from "@/lib/auth/config";

export const config = {
  matcher: ["/dashboard/:path*", "/api/export/:path*"],
};
