'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Briefcase, Users, BarChart3, Database } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useSession } from 'next-auth/react'; // Import useSession

const navItems = [
	{
		href: '/company',
		label: 'Company Portal',
		icon: <Briefcase className="mr-2 h-5 w-5" />,
		requiredRole: 'enterprise',
	},
	{
		href: '/company/dashboard',
		label: 'Company Dashboard',
		icon: <BarChart3 className="mr-2 h-5 w-5" />,
		requiredRole: 'enterprise',
	},
	{
		href: '/candidate',
		label: 'Candidate Portal',
		icon: <Users className="mr-2 h-5 w-5" />,
		requiredRole: 'candidate',
	},
	{
		href: '/candidate/profile',
		label: 'My Profile',
		icon: <BarChart3 className="mr-2 h-5 w-5" />,
		requiredRole: 'candidate',
	},
	{
		href: '/data',
		label: 'Data Showcase',
		icon: <Database className="mr-2 h-5 w-5" />,
		requiredRole: null, // Available to all authenticated users
	},
];

export default function MainNav() {
	const pathname = usePathname();
	const { data: session } = useSession();
	const userRole = session?.user?.role;
	const featureRoleRestrictionEnabled =
		process.env.NEXT_PUBLIC_FEATURE_ROLE_RESTRICTION_ENABLED === 'true';

	const filteredNavItems = navItems.filter((item) => {
		if (!featureRoleRestrictionEnabled || !session) {
			return true; // Show all items if flag is off or user is not logged in (auth will handle redirect)
		}
		// If flag is on and user is logged in, check role
		if (item.requiredRole === null) {
			return true; // Available to all authenticated users
		}
		if (item.requiredRole === 'enterprise' && userRole === 'enterprise') {
			return true;
		}
		if (item.requiredRole === 'candidate' && userRole === 'candidate') {
			return true;
		}
		// A general case: if an enterprise user should also see candidate portal, or vice-versa, adjust logic here.
		// For now, it's a strict match.
		return false;
	});

	return (
		<nav className="flex items-center space-x-2 sm:space-x-4">
			{filteredNavItems.map((item) => (
				<Button
					key={item.href}
					variant={pathname === item.href ? 'default' : 'ghost'}
					asChild
					className={cn(
						'transition-colors duration-300 ease-in-out text-sm sm:text-base',
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
