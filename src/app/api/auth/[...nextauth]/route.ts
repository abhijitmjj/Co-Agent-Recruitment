import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import GitHubProvider from 'next-auth/providers/github';

if (!process.env.GOOGLE_CLIENT_ID || !process.env.GOOGLE_CLIENT_SECRET) {
  throw new Error('Missing Google OAuth environment variables');
}

if (!process.env.GITHUB_CLIENT_ID || !process.env.GITHUB_CLIENT_SECRET) {
  throw new Error('Missing GitHub OAuth environment variables');
}

if (!process.env.AUTH_SECRET) {
  throw new Error('Missing AUTH_SECRET environment variable');
}

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
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        // Placeholder role logic
        token.role = user.email?.includes('company') ? 'company' : 'candidate';
      }
      return token;
    },
    async session({ session, token }) {
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
