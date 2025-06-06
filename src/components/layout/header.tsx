import Link from 'next/link';
import { Briefcase, Users, Bot } from 'lucide-react';
import MainNav from './main-nav';

export default function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-20 items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <Bot className="h-8 w-8 text-accent" />
          <span className="font-headline text-2xl font-bold text-primary-foreground">A2A Hire</span>
        </Link>
        <MainNav />
      </div>
    </header>
  );
}
