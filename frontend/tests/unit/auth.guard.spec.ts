import { TestBed } from '@angular/core/testing';
import { Router, UrlTree } from '@angular/router';

import { authGuard, guestGuard } from '@core/guards/auth.guard';
import { AuthService } from '@core/services/auth.service';

function setup(isAuthenticated: boolean) {
  const authService = {
    ready: Promise.resolve(),
    isAuthenticated: () => isAuthenticated
  };
  const urlTree = {} as UrlTree;
  const router = { parseUrl: jest.fn().mockReturnValue(urlTree) };

  TestBed.configureTestingModule({
    providers: [
      { provide: AuthService, useValue: authService },
      { provide: Router, useValue: router }
    ]
  });

  return { router, urlTree };
}

describe('authGuard', () => {
  it('allows an authenticated user through', async () => {
    setup(true);

    const result = await TestBed.runInInjectionContext(() =>
      authGuard(null as never, null as never)
    );

    expect(result).toBe(true);
  });

  it('sends an unauthenticated user to /login', async () => {
    const { router, urlTree } = setup(false);

    const result = await TestBed.runInInjectionContext(() =>
      authGuard(null as never, null as never)
    );

    expect(router.parseUrl).toHaveBeenCalledWith('/login');
    expect(result).toBe(urlTree);
  });
});

describe('guestGuard', () => {
  it('allows a signed-out visitor through to /login', async () => {
    setup(false);

    const result = await TestBed.runInInjectionContext(() =>
      guestGuard(null as never, null as never)
    );

    expect(result).toBe(true);
  });

  it('redirects an already-signed-in user to /', async () => {
    const { router, urlTree } = setup(true);

    const result = await TestBed.runInInjectionContext(() =>
      guestGuard(null as never, null as never)
    );

    expect(router.parseUrl).toHaveBeenCalledWith('/');
    expect(result).toBe(urlTree);
  });
});
