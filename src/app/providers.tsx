'use client';

import { AppProvider } from '@/contexts/app-context';
import React from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  return <AppProvider>{children}</AppProvider>;
}
