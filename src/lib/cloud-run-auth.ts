/**
 * Get an authentication token for Cloud Run service invocation
 * Uses the same credentials as Firebase Admin (service account or ADC)
 * This function only works in server-side environments (Node.js)
 */
export async function getCloudRunAuthToken(targetUrl: string): Promise<string> {
  // Dynamic import to avoid bundling issues in client-side code
  const { GoogleAuth } = await import('google-auth-library');
  
  try {
    const auth = new GoogleAuth({
      scopes: ['https://www.googleapis.com/auth/cloud-platform']
    });

    // Get an authenticated client
    const client = await auth.getIdTokenClient(targetUrl);
    
    // Get the ID token for the target URL
    const token = await client.idTokenProvider.fetchIdToken(targetUrl);
    
    return token;
  } catch (error) {
    console.error('Failed to get Cloud Run auth token:', error);
    throw new Error('Failed to authenticate with Cloud Run service');
  }
}

/**
 * Get authentication headers for Cloud Run requests
 * This function only works in server-side environments (Node.js)
 */
export async function getCloudRunAuthHeaders(targetUrl: string): Promise<Record<string, string>> {
  const token = await getCloudRunAuthToken(targetUrl);
  
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}