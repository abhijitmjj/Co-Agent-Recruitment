export function checkAuthEnvironmentVariables() {
  if (!process.env.GOOGLE_CLIENT_ID || !process.env.GOOGLE_CLIENT_SECRET) {
    throw new Error('Missing Google OAuth environment variables');
  }
  if (!process.env.GITHUB_CLIENT_ID || !process.env.GITHUB_CLIENT_SECRET) {
    throw new Error('Missing GitHub OAuth environment variables');
  }
  // NextAuth standard secret variable is NEXTAUTH_SECRET. Keep backward
  // compatibility with the legacy AUTH_SECRET name used in the code-base.
  const secret = process.env.AUTH_SECRET || process.env.NEXTAUTH_SECRET;
  if (!secret) {
    throw new Error('Missing AUTH_SECRET or NEXTAUTH_SECRET environment variable');
  }

  if (!process.env.NEXTAUTH_URL) {
    // Provide a sensible default for local development to avoid the noisy
    // runtime warning.  In production this variable should always be set
    // explicitly so we only auto-fill when NODE_ENV !== 'production'.
    if (process.env.NODE_ENV !== 'production') {
      process.env.NEXTAUTH_URL = 'http://localhost:3000';
      console.warn(
        '[Auth Env Check] NEXTAUTH_URL was not set – defaulting to http://localhost:3000. '
        + 'Set NEXTAUTH_URL in your environment to silence this message.'
      );
    } else {
      console.warn('[Auth Env Check] Warning: NEXTAUTH_URL is not set.');
    }
  }
  console.log('[Auth Env Check] All required auth environment variables are present.');
}
