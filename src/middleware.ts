import { withAuth, NextRequestWithAuth } from 'next-auth/middleware';
import { NextResponse } from 'next/server';

export default withAuth(
  function middleware(req: NextRequestWithAuth) {
    const { token } = req.nextauth;
    const { pathname } = req.nextUrl;

    const featureFlagEnvVar = process.env.NEXT_PUBLIC_FEATURE_ROLE_RESTRICTION_ENABLED;
    const featureRoleRestrictionEnabled = featureFlagEnvVar === 'true';

    console.log('[Middleware] Path:', pathname);
    console.log('[Middleware] Feature Flag Env Var (NEXT_PUBLIC_FEATURE_ROLE_RESTRICTION_ENABLED):', featureFlagEnvVar);
    console.log('[Middleware] Is Role Restriction Enabled:', featureRoleRestrictionEnabled);
    console.log('[Middleware] Token:', JSON.stringify(token, null, 2));

    if (featureRoleRestrictionEnabled && token) {
      console.log('[Middleware] Role restriction is ON and token exists. Role:', token.role);
      // Restrict /company/** routes to users with the 'enterprise' role
      if (pathname.startsWith('/company') && token.role !== 'enterprise') {
        console.log('[Middleware] Redirecting from /company: role is not enterprise.');
        return NextResponse.redirect(new URL('/unauthorized', req.url));
      }

      // Restrict /candidate/** routes to users with the 'candidate' role
      if (pathname.startsWith('/candidate') && token.role !== 'candidate') {
        console.log('[Middleware] Redirecting from /candidate: role is not candidate.');
        return NextResponse.redirect(new URL('/unauthorized', req.url));
      }
      console.log('[Middleware] Role checks passed or not applicable for this path.');
    } else {
      console.log('[Middleware] Role restriction is OFF or no token.');
    }
    
    console.log('[Middleware] Proceeding with NextResponse.next()');
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
