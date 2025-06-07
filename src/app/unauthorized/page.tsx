import Link from 'next/link';

export default function UnauthorizedPage() {
  return (
    <div className="container mx-auto px-4 py-8 text-center">
      <h1 className="text-4xl font-bold mb-4">Unauthorized</h1>
      <p className="text-lg mb-8">You do not have permission to view this page.</p>
      <Link href="/" className="text-accent hover:underline">
        Go to Homepage
      </Link>
    </div>
  );
}
