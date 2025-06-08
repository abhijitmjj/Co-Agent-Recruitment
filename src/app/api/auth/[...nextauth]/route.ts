import NextAuth, { Session, User } from 'next-auth'; // Import Session and User
import GoogleProvider from 'next-auth/providers/google';
import GitHubProvider from 'next-auth/providers/github';
import { JWT } from 'next-auth/jwt'; // Import JWT
import { checkAuthEnvironmentVariables } from '@/lib/env-check'; // Import the new check function

// Call the function to check environment variables during initialization
checkAuthEnvironmentVariables();

// Add this export:
export const authOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
  ],
  secret: process.env.AUTH_SECRET!,
  callbacks: {
    async jwt({ token, user }: { token: JWT; user?: User | undefined }) { // Add types here
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
          token.role = 'candidate'; // User with a public email domain
        } else {
          token.role = 'enterprise'; // User with a non-public/company domain
        }
      }
      return token;
    },
    async session({ session, token }: { session: Session; token: JWT }) { // Add types here
      if (session.user) {
        session.user.id = token.id as string;
        session.user.role = token.role as string;
      }
      return session;
    },
  },
};

const handler = NextAuth(authOptions); // Use authOptions here

export { handler as GET, handler as POST };
