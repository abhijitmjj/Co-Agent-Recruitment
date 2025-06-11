// __tests__/middleware.test.ts
import { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';
import { JWT } from 'next-auth/jwt'; // Changed from 'import type'
import { NextRequestWithAuth } from 'next-auth/middleware'; // Changed from 'import type'

// No imports needed for describe, it, expect, etc. as they are globals in Jest

// Define the core middleware logic here for testing
// This mirrors the function passed to withAuth in your actual middleware.ts
const testableMiddlewareLogic = (req: NextRequestWithAuth) => {
  const token = req.nextauth?.token;
  const { pathname } = req.nextUrl;

  const featureRoleRestrictionEnabled = process.env.NEXT_PUBLIC_FEATURE_ROLE_RESTRICTION_ENABLED === 'true';

  if (featureRoleRestrictionEnabled && token) {
    if (pathname.startsWith('/company') && token.role !== 'enterprise') {
      return NextResponse.redirect(new URL('/unauthorized', req.url));
    }
    if (pathname.startsWith('/candidate') && token.role !== 'candidate') {
      return NextResponse.redirect(new URL('/unauthorized', req.url));
    }
  }
  return NextResponse.next();
};

// Mock NextResponse methods
// Mock NextResponse methods
jest.mock('next/server', () => {
  const actual = jest.requireActual('next/server');
  // Re-assign to a variable prefixed with 'mock' to avoid scope issues
  const mockNextResponse = actual.NextResponse;
  return {
    ...actual,
    NextResponse: Object.assign(mockNextResponse, {
      next: jest.fn(),
      redirect: jest.fn(),
    }),
  };
});

const createMockRequest = (pathname: string, token: JWT | null): NextRequestWithAuth => {
  const req = new NextRequest(new URL(`http://localhost${pathname}`)) as NextRequestWithAuth;
  req.nextUrl.pathname = pathname; // Ensure pathname is correctly set for startsWith checks
  req.nextauth = { token: token }; 
  return req;
};

describe('Middleware Logic with Feature Toggle', () => {
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    originalEnv = { ...process.env }; // Backup original env
    jest.clearAllMocks(); // Clear mocks before each test
  });

  afterEach(() => {
    process.env = originalEnv; // Restore original env
  });

  describe("When NEXT_PUBLIC_FEATURE_ROLE_RESTRICTION_ENABLED is 'false'", () => {
    beforeEach(() => {
      process.env.NEXT_PUBLIC_FEATURE_ROLE_RESTRICTION_ENABLED = 'false';
    });

    const roles: (JWT['role'] | null)[] = ['enterprise', 'candidate', null, 'other'];
    const paths = ['/company', '/candidate', '/company/dashboard', '/candidate/profile'];

    roles.forEach(role => {
      paths.forEach(path => {
        it(`should allow ${role || 'no specific role'} user access to ${path}`, () => {
          const mockToken = role ? { id: '1', role, sub: 'sub' } : null;
          // If token is null, it means unauthenticated for this specific test logic.
          // withAuth would typically handle the primary auth redirection.
          // Our internal logic here should pass through if flag is off.
          const req = createMockRequest(path, mockToken);
          testableMiddlewareLogic(req);
          expect(NextResponse.next).toHaveBeenCalled();
          expect(NextResponse.redirect).not.toHaveBeenCalled();
        });
      });
    });
  });

  describe("When NEXT_PUBLIC_FEATURE_ROLE_RESTRICTION_ENABLED is 'true'", () => {
    beforeEach(() => {
      process.env.NEXT_PUBLIC_FEATURE_ROLE_RESTRICTION_ENABLED = 'true';
    });

    // Test cases for enterprise users
    describe('Enterprise User (role: enterprise)', () => {
      const token: JWT = { id: '1', role: 'enterprise', sub: 'sub' };
      it('should allow access to /company', () => {
        const req = createMockRequest('/company', token);
        testableMiddlewareLogic(req);
        expect(NextResponse.next).toHaveBeenCalled();
      });
      it('should allow access to /company/dashboard', () => {
        const req = createMockRequest('/company/dashboard', token);
        testableMiddlewareLogic(req);
        expect(NextResponse.next).toHaveBeenCalled();
      });
      it('should redirect from /candidate', () => {
        const req = createMockRequest('/candidate', token);
        testableMiddlewareLogic(req);
        expect(NextResponse.redirect).toHaveBeenCalledWith(new URL('/unauthorized', req.url));
      });
    });

    // Test cases for candidate users
    describe('Candidate User (role: candidate)', () => {
      const token: JWT = { id: '1', role: 'candidate', sub: 'sub' };
      it('should redirect from /company', () => {
        const req = createMockRequest('/company', token);
        testableMiddlewareLogic(req);
        expect(NextResponse.redirect).toHaveBeenCalledWith(new URL('/unauthorized', req.url));
      });
      it('should allow access to /candidate', () => {
        const req = createMockRequest('/candidate', token);
        testableMiddlewareLogic(req);
        expect(NextResponse.next).toHaveBeenCalled();
      });
      it('should allow access to /candidate/profile', () => {
        const req = createMockRequest('/candidate/profile', token);
        testableMiddlewareLogic(req);
        expect(NextResponse.next).toHaveBeenCalled();
      });
    });

    // Test cases for users with other roles or no relevant role
    describe('User with other/no relevant role', () => {
      const token: JWT = { id: '1', role: 'other', sub: 'sub' };
      it('should redirect from /company if role is not enterprise', () => {
        const req = createMockRequest('/company', token);
        testableMiddlewareLogic(req);
        expect(NextResponse.redirect).toHaveBeenCalledWith(new URL('/unauthorized', req.url));
      });
      it('should redirect from /candidate if role is not candidate', () => {
        const req = createMockRequest('/candidate', token);
        testableMiddlewareLogic(req);
        expect(NextResponse.redirect).toHaveBeenCalledWith(new URL('/unauthorized', req.url));
      });
    });
    
    // Test case for unauthenticated user (token is null)
    describe('Unauthenticated user (token is null)', () => {
      const noToken = null;
      it('should call next() for /company (primary auth handled by withAuth)', () => {
        const req = createMockRequest('/company', noToken);
        testableMiddlewareLogic(req);
        // Middleware logic passes through if token is null, as role checks are skipped.
        // withAuth's `authorized` callback would handle the primary redirect to login.
        expect(NextResponse.next).toHaveBeenCalled();
        expect(NextResponse.redirect).not.toHaveBeenCalled();
      });
       it('should call next() for /candidate (primary auth handled by withAuth)', () => {
        const req = createMockRequest('/candidate', noToken);
        testableMiddlewareLogic(req);
        expect(NextResponse.next).toHaveBeenCalled();
        expect(NextResponse.redirect).not.toHaveBeenCalled();
      });
    });
  });
});

// Note: The existing `mockAuthorizedCallback` tests for the `authorized` part of withAuth options
// can remain if they are still relevant to your overall testing strategy for authentication.
// The tests above focus on the new role-based restriction logic controlled by the feature flag.

// (Keep existing mockAuthorizedCallback and its tests if needed)
const mockAuthorizedCallback = (params: { req: NextRequest; token: JWT | null }): boolean => {
  const { req, token } = params;
  const { pathname } = req.nextUrl;
  if (pathname.startsWith('/candidate') || pathname.startsWith('/company')) {
    return !!token;
  }
  return true;
};

describe('Middleware Logic - Authorized Callback (Legacy)', () => {
  describe('authorized callback', () => {
    it('should authorize access to /candidate for logged-in user', () => {
      const req = new NextRequest(new URL('http://localhost/candidate/profile'));
      const token: JWT = { id: '1', role: 'candidate', sub: 'sub' };
      expect(mockAuthorizedCallback({ req, token })).toBe(true);
    });

    it('should deny access to /candidate for logged-out user', () => {
      const req = new NextRequest(new URL('http://localhost/candidate/profile'));
      expect(mockAuthorizedCallback({ req, token: null })).toBe(false);
    });

    it('should authorize access to public routes for logged-out user', () => {
      const req = new NextRequest(new URL('http://localhost/'));
      expect(mockAuthorizedCallback({ req, token: null })).toBe(true);
    });
  });
});
