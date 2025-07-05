// __tests__/auth.callbacks.test.ts
jest.mock('@/lib/env-check', () => ({
  checkAuthEnvironmentVariables: jest.fn(),
}));
import { authOptions } from '@/lib/auth'; // Corrected import path
import { ROLES } from '@/lib/constants';
import { Account, Session, User } from 'next-auth';
import { AdapterUser } from 'next-auth/adapters';
import { JWT } from 'next-auth/jwt';

// Stub environment variables
process.env.GOOGLE_CLIENT_ID = 'test-google-client-id';
process.env.GOOGLE_CLIENT_SECRET = 'test-google-client-secret';
process.env.GITHUB_CLIENT_ID = 'test-github-client-id';
process.env.GITHUB_CLIENT_SECRET = 'test-github-client-secret';
process.env.AUTH_SECRET = 'test-auth-secret';

describe('Auth.js Callbacks', () => {
  describe('jwt callback', () => {
    const mockUserBase: User = {
      id: 'test-user-id',
      name: 'Test User',
      email: 'test@gmail.com',
      role: 'candidate',
    };

    const mockAccount: Account = {
      provider: 'google',
      type: 'oauth',
      providerAccountId: '12345',
      access_token: 'test-access-token',
      expires_at: 12345,
      token_type: 'Bearer',
      scope: 'test-scope',
      id_token: 'test-id-token',
    };

    it('should assign "candidate" role for regular email', async () => {
      const token: JWT = { sub: 'test-sub', id: '', role: '' };
      const user: User = { ...mockUserBase, email: 'candidate@gmail.com' };
      
      if (!authOptions.callbacks?.jwt) throw new Error('JWT callback not defined');

      const result = await authOptions.callbacks.jwt({ token, user, account: mockAccount });
      expect(result.id).toBe('test-user-id');
      expect(result.role).toBe(ROLES.CANDIDATE);
    });

    it('should assign "enterprise" role for non-public email domains', async () => {
      const token: JWT = { sub: 'test-sub', id: '', role: '' };
      const user: User = { ...mockUserBase, email: 'user@company.com' };

      if (!authOptions.callbacks?.jwt) throw new Error('JWT callback not defined');

      const result = await authOptions.callbacks.jwt({ token, user, account: mockAccount });
      expect(result.id).toBe('test-user-id');
      expect(result.role).toBe(ROLES.ENTERPRISE);
    });
  });

  describe('session callback', () => {
    it('should transfer id and role from token to session', async () => {
      const mockSession: Session = {
        user: { name: 'Test User', email: 'test@example.com', id: '', role: '' },
        expires: '1',
      };
      const mockToken: JWT = {
        id: 'token-user-id',
        role: 'admin',
        sub: 'subject',
      };
      const mockAdapterUser: AdapterUser = {
        id: 'adapter-user-id',
        email: 'adapter@example.com',
        emailVerified: null,
        role: 'admin',
      };
      
      if (!authOptions.callbacks?.session) throw new Error('Session callback not defined');

      const result = await authOptions.callbacks.session({
        session: mockSession,
        token: mockToken,
        user: mockAdapterUser
      } as Parameters<NonNullable<typeof authOptions.callbacks.session>>[0]);
      
      expect(result.user).toBeDefined();
      if (result.user) {
        expect((result.user as { id: string; role: string }).id).toBe('token-user-id');
        expect((result.user as { id: string; role: string }).role).toBe('admin');
      }
    });
  });
});
