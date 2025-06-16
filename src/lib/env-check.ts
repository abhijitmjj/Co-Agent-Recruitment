export function checkAuthEnvironmentVariables() {
  const requiredVars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET'];
  
  // Check for required OAuth variables
  for (const varName of requiredVars) {
    const value = process.env[varName];
    if (!value || value.length < 10) {
      throw new Error(`Missing or invalid ${varName} environment variable`);
    }
  }
  
  // NextAuth standard secret variable is NEXTAUTH_SECRET. Keep backward
  // compatibility with the legacy AUTH_SECRET name used in the code-base.
  const secret = process.env.AUTH_SECRET || process.env.NEXTAUTH_SECRET;
  if (!secret || secret.length < 32) {
    throw new Error('Missing or weak AUTH_SECRET/NEXTAUTH_SECRET environment variable (minimum 32 characters)');
  }

  // Validate NEXTAUTH_URL
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
      throw new Error('[Auth Env Check] NEXTAUTH_URL is required in production environment');
    }
  } else {
    // Validate URL format
    try {
      new URL(process.env.NEXTAUTH_URL);
    } catch {
      throw new Error('[Auth Env Check] NEXTAUTH_URL must be a valid URL');
    }
  }
  
  // Check for AI model configuration
  const modelName = process.env.GEMINI_MODEL;
  if (modelName && !/^[a-zA-Z0-9\-\.]+$/.test(modelName)) {
    throw new Error('Invalid GEMINI_MODEL format - only alphanumeric, hyphens, and dots allowed');
  }
  
  console.log('[Auth Env Check] All required auth environment variables are present.');
}
