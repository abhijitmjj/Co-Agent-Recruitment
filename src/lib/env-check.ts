export function checkAuthEnvironmentVariables() {
  if (!process.env.GOOGLE_CLIENT_ID || !process.env.GOOGLE_CLIENT_SECRET) {
    throw new Error('Missing Google OAuth environment variables');
  }
  if (!process.env.GITHUB_CLIENT_ID || !process.env.GITHUB_CLIENT_SECRET) {
    throw new Error('Missing GitHub OAuth environment variables');
  }
  if (!process.env.AUTH_SECRET) {
    throw new Error('Missing AUTH_SECRET environment variable');
  }
  console.log('[Auth Env Check] All required auth environment variables are present.');
}
