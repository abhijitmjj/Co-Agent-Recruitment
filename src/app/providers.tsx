'use client';

import { SessionProvider } from 'next-auth/react';
import { AppProvider } from '@/contexts/app-context';
import React from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <AppProvider>{children}</AppProvider>
    </SessionProvider>
  );
}
