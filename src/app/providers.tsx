'use client';
import { AuthProvider } from '@/contexts/AuthContext'; // 👈 Import your AuthProvider
import { SessionProvider } from 'next-auth/react';
import { AppProvider } from '@/contexts/app-context';
import React from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <AuthProvider>
        <AppProvider>{children}</AppProvider>
      </AuthProvider>
    </SessionProvider>
  );
}
