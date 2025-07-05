// src/app/candidate/profile/page.tsx
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth'; // Adjust path to the new auth.ts file
import SimpleDataDashboard from '@/components/simple-data-dashboard';
import Link from 'next/link';

export default async function CandidateProfilePage() {
  const session = await getServerSession(authOptions);

  if (!session) {
    // Middleware should handle this, but as a fallback
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <p className="text-lg mb-4">You must be logged in to view this page.</p>
        <Link href="/api/auth/signin" className="text-accent hover:underline">Sign In</Link>
      </div>
    );
  }

  if (session.user.role !== 'candidate') {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-4xl font-bold mb-4">Access Denied</h1>
        <p className="text-lg mb-8">This page is for candidates only.</p>
        <Link href="/" className="text-accent hover:underline">Go to Homepage</Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-6">My Candidate Profile</h1>
        <div className="bg-muted/50 p-4 rounded-lg space-y-2">
          <p><span className="font-semibold">Name:</span> {session.user.name}</p>
          <p><span className="font-semibold">Email:</span> {session.user.email}</p>
          <p><span className="font-semibold">User ID:</span> {session.user.id}</p>
          <p><span className="font-semibold">Role:</span> {session.user.role}</p>
        </div>
      </div>
      
      {/* Data Dashboard */}
      <SimpleDataDashboard />
    </div>
  );
}
