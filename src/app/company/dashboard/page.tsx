// src/app/company/dashboard/page.tsx
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth'; // Import authOptions from the new file
import SimpleDataDashboard from '@/components/simple-data-dashboard';

export default async function CompanyDashboardPage() {
  const session = await getServerSession(authOptions);

  if (!session) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <p className="text-lg mb-4">You must be logged in to view this page.</p>
        <a href="/api/auth/signin" className="text-accent hover:underline">Sign In</a>
      </div>
    );
  }

  if (session.user.role !== 'enterprise') {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-4xl font-bold mb-4">Access Denied</h1>
        <p className="text-lg mb-8">This page is for enterprise representatives only.</p>
        <a href="/" className="text-accent hover:underline">Go to Homepage</a>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-6">Company Dashboard</h1>
        <div className="bg-muted/50 p-4 rounded-lg space-y-2">
          <p><span className="font-semibold">Company User:</span> {session.user.name}</p>
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
