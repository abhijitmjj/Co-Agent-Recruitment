'use client';

import Link from 'next/link';
import { Bot } from 'lucide-react';
import MainNav from './main-nav';
import { useSession, signIn, signOut } from 'next-auth/react';
import { Button } from '@/components/ui/button';
import Image from 'next/image';

export default function Header() {
  const { data: session, status } = useSession();
  const isLoading = status === 'loading';

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-20 items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <Bot className="h-8 w-8 text-accent" />
          <span className="font-headline text-2xl font-bold text-primary-foreground">A2A Hire</span>
        </Link>
        <div className="flex items-center space-x-4">
          <MainNav />
          {isLoading ? (
            <div className="h-8 w-20 animate-pulse rounded-md bg-muted"></div>
          ) : session ? (
            <>
              {session.user?.image && (
                <Image
                  src={session.user.image}
                  alt={session.user.name || 'User avatar'}
                  width={32}
                  height={32}
                  className="rounded-full"
                />
              )}
              {session.user?.name && (
                <span className="text-sm font-medium text-primary-foreground hidden sm:inline">
                  {session.user.name}
                </span>
              )}
              <Button variant="outline" size="sm" onClick={() => signOut()}>
                Sign Out
              </Button>
            </>
          ) : (
            <Button size="sm" onClick={() => signIn()}>
              Sign In
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}
