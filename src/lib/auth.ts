import { AuthOptions, Session, User } from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import GitHubProvider from 'next-auth/providers/github';
import { JWT } from 'next-auth/jwt';
import { checkAuthEnvironmentVariables } from '@/lib/env-check';
import { ROLES } from './constants';

// Call the function to check environment variables during initialization
checkAuthEnvironmentVariables();

export const authOptions: AuthOptions = {
  providers: [
    // Google: force account chooser every time by using the `prompt`
    // parameter.  This prevents automatic re-login with the previous Google
    // account after signing out of the app.
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          // `select_account` makes Google always show the account-picker.
          // `consent` guarantees the refresh_token is returned on first login.
          prompt: 'select_account consent',
          access_type: 'offline',
          response_type: 'code',
        },
      },
    }),
    // GitHub: `prompt=login` forces GitHub to ask for credentials again.
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
      authorization: {
        params: {
          prompt: 'login',
        },
      },
    }),
  ],
  // Prefer the standard NEXTAUTH_SECRET but fall back to the historical
  // AUTH_SECRET so existing deployments & tests continue to work.
  secret: (process.env.NEXTAUTH_SECRET || process.env.AUTH_SECRET)!,
  callbacks: {
    async jwt({ token, user }: { token: JWT; user?: User | undefined }) {
      if (user && user.email) {
        token.id = user.id;
        const email = user.email.toLowerCase();
        const domain = email.substring(email.lastIndexOf("@") + 1);

        const publicDomains = [
          'gmail.com',
          'outlook.com',
          'yahoo.com',
          'hotmail.com',
          'aol.com',
          'icloud.com',
          'zoho.com',
          'protonmail.com',
          'gmx.com'
          // Add other public domains as needed
        ];

        if (publicDomains.includes(domain)) {
          token.role = ROLES.CANDIDATE; // User with a public email domain
        } else {
          token.role = ROLES.ENTERPRISE; // User with a non-public/enterprise domain
        }
      }
      return token;
    },
    async session({ session, token }: { session: Session; token: JWT }) {
      if (session.user) {
        session.user.id = token.id as string;
        session.user.role = token.role as string;
      }
      return session;
    },
  },
};
