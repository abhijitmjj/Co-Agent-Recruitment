// __tests__/auth.callbacks.test.ts
import { authOptions } from '@/app/api/auth/[...nextauth]/route'; // Adjust path
import { User } from 'next-auth';
import { JWT } from 'next-auth/jwt';

describe('Auth.js Callbacks', () => {
  describe('jwt callback', () => {
    const mockUserBase: User = {
      id: 'test-user-id',
      name: 'Test User',
      email: 'test@gmail.com',
      role: 'candidate', // Add role to satisfy User type
    };

    it('should assign "candidate" role for regular email', async () => {
      const token: JWT = {
        id: '', // Initialize id as per JWT type
        role: '', // Initialize role as per JWT type
        sub: 'test-sub', // JWT requires a sub property
      };
      const user: User = { ...mockUserBase, email: 'candidate@gmail.com' };
      const result = await authOptions.callbacks.jwt({ token, user });
      expect(result.id).toBe('test-user-id');
      expect(result.role).toBe('candidate');
    });

    it('should assign "company" role if email contains "company"', async () => {
      const token: JWT = {
        id: '', // Initialize id as per JWT type
        role: '', // Initialize role as per JWT type
        sub: 'test-sub', // JWT requires a sub property
      };
      const user: User = { ...mockUserBase, email: 'user@company.com' };
      const result = await authOptions.callbacks.jwt({ token, user });
      expect(result.id).toBe('test-user-id');
      expect(result.role).toBe('enterprise');
    });
  });

  describe('session callback', () => {
    it('should transfer id and role from token to session', async () => {
      const mockSession = {
        user: { name: 'Test User', email: 'test@example.com' },
        expires: '1',
      };
      const mockToken: JWT = {
        id: 'token-user-id',
        role: 'admin',
        sub: 'subject', // JWT requires a sub
      };
      // @ts-expect-error // Assuming authOptions.callbacks.session exists
      const result = await authOptions.callbacks.session({ session: mockSession, token: mockToken });
      expect(result.user.id).toBe('token-user-id');
      expect(result.user.role).toBe('admin');
    });
  });
});
