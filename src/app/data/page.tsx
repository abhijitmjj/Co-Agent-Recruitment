// src/app/data/page.tsx
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import SimpleDataDashboard from '@/components/simple-data-dashboard';
import Link from 'next/link';

export default async function DataPage() {
  const session = await getServerSession(authOptions);

  if (!session) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-4xl font-bold mb-4">Authentication Required</h1>
        <p className="text-lg mb-4">You must be logged in to view this page.</p>
        <Link href="/api/auth/signin" className="text-accent hover:underline">Sign In</Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">Data Showcase</h1>
        <p className="text-lg text-muted-foreground mb-6">
          View all saved resumes, job postings, and compatibility scores from your recruitment activities.
        </p>
        <div className="bg-muted/50 p-4 rounded-lg">
          <p className="text-sm">
            <span className="font-semibold">Logged in as:</span> {session.user.name} ({session.user.role})
          </p>
        </div>
      </div>
      
      {/* Data Dashboard */}
      <SimpleDataDashboard />
    </div>
  );
}