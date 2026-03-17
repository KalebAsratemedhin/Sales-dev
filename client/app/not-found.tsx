import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-1 items-center justify-center p-8">
      <div className="max-w-md text-center space-y-6">
        <h2 className="text-xl font-bold text-slate-100">Page not found</h2>
        <p className="text-sm text-slate-500">
          The page you’re looking for doesn’t exist or was moved.
        </p>
        <Link
          href="/"
          className="inline-flex items-center justify-center rounded bg-primary text-primary-foreground px-4 py-2 text-sm font-bold hover:bg-primary/90 transition-colors"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
