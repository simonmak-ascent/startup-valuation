import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center bg-bg px-4">
      <div className="card max-w-md w-full p-8 text-center">
        <h1 className="text-4xl font-bold text-brand mb-3">404</h1>
        <h2 className="text-xl font-semibold text-text mb-2">Page not found</h2>
        <p className="text-muted mb-6">
          The page you&apos;re looking for doesn&apos;t exist or has moved.
        </p>
        <Link href="/" className="btn-brand">
          Back to home
        </Link>
      </div>
    </div>
  );
}
