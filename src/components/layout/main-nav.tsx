'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Briefcase, Users } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

const navItems = [
  { href: '/company', label: 'Company Portal', icon: <Briefcase className="mr-2 h-5 w-5" /> },
  { href: '/candidate', label: 'Candidate Portal', icon: <Users className="mr-2 h-5 w-5" /> },
];

export default function MainNav() {
  const pathname = usePathname();

  return (
    <nav className="flex items-center space-x-2 sm:space-x-4">
      {navItems.map((item) => (
        <Button
          key={item.href}
          variant={pathname === item.href ? 'default' : 'ghost'}
          asChild
          className={cn(
            "transition-colors duration-300 ease-in-out text-sm sm:text-base",
            pathname === item.href
              ? 'bg-accent text-accent-foreground hover:bg-accent/90'
              : 'hover:bg-primary/10 hover:text-primary-foreground'
          )}
        >
          <Link href={item.href} className="flex items-center">
            {item.icon}
            <span className="hidden sm:inline">{item.label}</span>
            <span className="sm:hidden">{item.label.split(' ')[0]}</span>
          </Link>
        </Button>
      ))}
    </nav>
  );
}
