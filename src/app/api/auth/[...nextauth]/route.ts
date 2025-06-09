import NextAuth from 'next-auth'; // Import Session and User
import { authOptions } from '@/lib/auth'; // Import authOptions from the new file

const handler = NextAuth(authOptions); // Use authOptions here

export { handler as GET, handler as POST };
