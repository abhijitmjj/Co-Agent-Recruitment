import { withAuth } from 'next-auth/middleware';
import { NextResponse } from 'next/server';

export default withAuth(
  function middleware(req) {
    const { token } = req.nextauth;
    const { pathname } = req.nextUrl;

    // If user is not logged in, withAuth will redirect to sign-in page for protected routes.

    // Example role-based protection:
    // Only users with the 'company' role can access /company/dashboard (hypothetical route)
    if (pathname.startsWith('/company/dashboard') && token?.role !== 'company') {
      return NextResponse.redirect(new URL('/unauthorized', req.url)); // Or new URL('/', req.url)
    }

    // Candidates should only see their profile page, not a generic /candidate page if it lists all candidates
    // This logic will be more refined in the page components themselves.
    // For now, middleware ensures they are logged in to access /candidate/**

    return NextResponse.next();
  },
  {
    callbacks: {
      authorized: ({ req, token }) => {
        const { pathname } = req.nextUrl;
        // Protect /candidate and /company routes
        if (pathname.startsWith('/candidate') || pathname.startsWith('/company')) {
          return !!token; // User is authorized if token exists (logged in)
        }
        // Other routes are public
        return true;
      },
    },
  }
);

// Optionally, specify which paths the middleware should run on:
// export const config = { matcher: ['/candidate/:path*', '/company/:path*'] };
// If not specified, it runs on all paths by default when using withAuth.
// The authorized callback already handles which paths are protected.
