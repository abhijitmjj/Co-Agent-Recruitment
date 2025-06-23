"use client";
import React,
  {
    createContext,
    useContext,
    useEffect,
    useState,
    ReactNode,
    useMemo,
  } from 'react';
import {
  onAuthStateChanged,
  User,
  signInWithCustomToken,
} from 'firebase/auth';
import { getFirebase } from '../lib/firebase-client';
import { useSession } from 'next-auth/react';

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  signIn: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const { auth } = getFirebase();

  const signIn = async () => {
    console.debug('[AuthContext] Firebase: requesting custom token');
    try {
      const res = await fetch('/api/auth/firebase');
      console.debug('[AuthContext] Firebase: /api/auth/firebase status', res.status);
      if (!res.ok) {
        throw new Error('Failed to get custom token');
      }
      const { customToken } = await res.json();
      console.debug('[AuthContext] Firebase: received customToken');
      await signInWithCustomToken(auth, customToken);
      console.debug('[AuthContext] Firebase: signed in, user=', auth.currentUser);
    } catch (err) {
      console.error('[AuthContext] Firebase signIn error:', err);
    }
  };

  const { data: nextSession, status: nextStatus } = useSession();

  useEffect(() => {
    console.debug('[AuthContext] useEffect: subscribe to onAuthStateChanged, nextStatus=', nextStatus);
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      console.debug('[AuthContext] Firebase onAuthStateChanged:', firebaseUser);
      setUser(firebaseUser);
      setLoading(false);
    });

    if (nextStatus === 'authenticated' && !user) {
      console.debug('[AuthContext] NextAuth authenticated & no Firebase user, fetching custom token');
      signIn();
    }

    return unsubscribe;
  }, [nextStatus, user, auth, signIn]);

  const value = useMemo<AuthContextValue>(
    () => ({ user, loading, signIn }),
    [user, loading]
  );

  return (
    <AuthContext.Provider value={value}>
      {nextStatus !== 'loading' && !loading && children}
    </AuthContext.Provider>
  );
};

/**
 * Hook to access the AuthContext value.
 * Throws an error if used outside an AuthProvider.
 */
export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};