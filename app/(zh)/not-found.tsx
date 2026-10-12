import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center bg-bg px-4">
      <div className="card w-full max-w-md p-8 text-center">
        <h1 className="mb-3 text-4xl font-bold text-brand">404</h1>
        <h2 className="mb-2 text-xl font-semibold text-text">Page not found</h2>
        <Link href="/" className="btn-brand">Back to home</Link>
      </div>
    </div>
  );
}
