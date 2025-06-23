import { getApps, getApp, initializeApp, FirebaseApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, GithubAuthProvider, Auth } from 'firebase/auth';
import { getFirestore, Firestore } from "firebase/firestore";
import { getStorage, FirebaseStorage } from "firebase/storage";

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
let firebaseApp: FirebaseApp = getApps().length ? getApp() : initializeApp(firebaseConfig);
let auth: Auth;
let db: Firestore;
let storage: FirebaseStorage;

function getFirebase() {
  if (!auth) {
    auth = getAuth(firebaseApp);
  }
  if (!db) {
    db = getFirestore(firebaseApp);
  }
  if (!storage) {
    storage = getStorage(firebaseApp);
  }
  return { firebaseApp, auth, db, storage };
}

const google = new GoogleAuthProvider();
const github = new GithubAuthProvider();

export { getFirebase, firebaseApp, auth, db, storage, google, github, firebaseConfig };