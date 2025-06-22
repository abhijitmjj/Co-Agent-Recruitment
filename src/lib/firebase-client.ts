import { getApps, getApp, initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, GithubAuthProvider } from 'firebase/auth';
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

const firebaseConfig = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY!,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN!,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID!,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID!,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET!,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID!,
    measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID!
};
// Debugging: log firebase config loaded from environment (public values)
console.debug('[firebase-client] firebaseConfig:', {
  authDomain: firebaseConfig.authDomain,
  projectId: firebaseConfig.projectId,
  storageBucket: firebaseConfig.storageBucket,
  messagingSenderId: firebaseConfig.messagingSenderId,
  appId: firebaseConfig.appId,
  measurementId: firebaseConfig.measurementId,
});

// Prevent double-initialisation in dev/HMR
// Prevent double-initialisation in dev/HMR
export const firebaseApp =
  getApps().length
    ? (console.debug('[firebase-client] Using existing Firebase app'), getApp())
    : (console.debug('[firebase-client] Initializing new Firebase app'), initializeApp(firebaseConfig));

export const auth = (() => {
  const instance = getAuth(firebaseApp);
  console.debug('[firebase-client] Auth initialized:', instance);
  return instance;
})();

export const google = new GoogleAuthProvider();
export const github = new GithubAuthProvider();
export { firebaseConfig };

export const db = (() => {
  const instance = getFirestore(firebaseApp);
  console.debug('[firebase-client] Firestore initialized:', instance);
  return instance;
})();

export const storage = (() => {
  const instance = getStorage(firebaseApp);
  console.debug('[firebase-client] Storage initialized for bucket:', firebaseConfig.storageBucket, instance);
  return instance;
})();