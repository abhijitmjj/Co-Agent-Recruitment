import { cert, getApps, getApp, initializeApp } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';

// Parse and validate the service account JSON from an env var (must be valid single-line JSON)
const _serviceKeyRaw = process.env.FIREBASE_SERVICE_ACCOUNT_KEY;
if (!_serviceKeyRaw) {
  throw new Error(
    '[firebase-admin] Missing environment variable FIREBASE_SERVICE_ACCOUNT_KEY; ' +
    'set it to your service account JSON as a single-line string'
  );
}
let serviceKey: Record<string, unknown>;
try {
  serviceKey = JSON.parse(_serviceKeyRaw);
  // Ensure the private key PEM has actual newlines (env var typically encodes them as literal \n)
  if (serviceKey.private_key && typeof serviceKey.private_key === 'string') {
    serviceKey.private_key = serviceKey.private_key.replace(/\\n/g, '\n');
  }
} catch (error) {
  console.error(
    '[firebase-admin] Invalid FIREBASE_SERVICE_ACCOUNT_KEY JSON:',
    _serviceKeyRaw,
    error
  );
  throw new Error(
    '[firebase-admin] Failed to parse FIREBASE_SERVICE_ACCOUNT_KEY; ' +
    'ensure it is valid JSON without line breaks'
  );
}

export const adminApp =
  getApps().length
    ? (console.debug('[firebase-admin] Using existing Firebase Admin app'), getApp())
    : (console.debug('[firebase-admin] Initializing Firebase Admin app'),
       initializeApp({ credential: cert(serviceKey) }));

export const adminAuth = getAuth(adminApp);
