import { cert, applicationDefault, getApps, getApp, initializeApp } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';

// Initialize Firebase Admin SDK, preferring explicit service account key if provided,
// otherwise falling back to Application Default Credentials (ADC).
let credentialConfig;
if (process.env.FIREBASE_SERVICE_ACCOUNT_KEY) {
  try {
    const serviceKey = JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT_KEY);
    if (serviceKey.private_key && typeof serviceKey.private_key === 'string') {
      serviceKey.private_key = serviceKey.private_key.replace(/\\n/g, '\n');
    }
    credentialConfig = { credential: cert(serviceKey) };
  } catch (error) {
    console.error(
      '[firebase-admin] Invalid FIREBASE_SERVICE_ACCOUNT_KEY JSON:',
      process.env.FIREBASE_SERVICE_ACCOUNT_KEY,
      error
    );
    throw new Error(
      '[firebase-admin] Failed to parse FIREBASE_SERVICE_ACCOUNT_KEY; ' +
      'ensure it is valid single-line JSON'
    );
  }
} else {
  console.warn(
    '[firebase-admin] FIREBASE_SERVICE_ACCOUNT_KEY not set; falling back to Application Default Credentials (ADC)'
  );
  credentialConfig = { credential: applicationDefault() };
}

export const adminApp =
  getApps().length
    ? (console.debug('[firebase-admin] Using existing Firebase Admin app'), getApp())
    : (console.debug('[firebase-admin] Initializing Firebase Admin app'),
       initializeApp(credentialConfig));

export const adminAuth = getAuth(adminApp);
