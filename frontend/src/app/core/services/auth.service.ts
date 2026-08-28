import { Injectable, signal } from '@angular/core';

/**
 * Minimal placeholder auth service backed by a signal.
 * Swap the internal logic for real token/session handling as needed.
 */
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly authenticated = signal<boolean>(false);

  readonly isAuthenticated = this.authenticated.asReadonly();

  login(): void {
    this.authenticated.set(true);
  }

  logout(): void {
    this.authenticated.set(false);
  }
}
