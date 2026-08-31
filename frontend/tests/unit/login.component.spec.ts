import { render, screen } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { Router } from '@angular/router';

import { LoginComponent } from '@features/auth/login/login.component';
import { AuthService } from '@core/services/auth.service';

describe('LoginComponent', () => {
  it('signs in with email and password, then navigates to /', async () => {
    const signInWithEmail = jest.fn().mockResolvedValue(undefined);
    const navigateByUrl = jest.fn().mockResolvedValue(true);

    await render(LoginComponent, {
      providers: [
        { provide: AuthService, useValue: { signInWithEmail } },
        { provide: Router, useValue: { navigateByUrl } }
      ]
    });

    const user = userEvent.setup();
    await user.type(screen.getByLabelText('Email'), 'demo@example.com');
    await user.type(screen.getByLabelText('Password'), 'hunter22');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(signInWithEmail).toHaveBeenCalledWith('demo@example.com', 'hunter22');
    expect(navigateByUrl).toHaveBeenCalledWith('/');
  });

  it('switches to register mode and calls registerWithEmail on submit', async () => {
    const registerWithEmail = jest.fn().mockResolvedValue(undefined);
    const navigateByUrl = jest.fn().mockResolvedValue(true);

    await render(LoginComponent, {
      providers: [
        { provide: AuthService, useValue: { registerWithEmail } },
        { provide: Router, useValue: { navigateByUrl } }
      ]
    });

    const user = userEvent.setup();
    await user.click(screen.getByText(/create one/i));
    await user.type(screen.getByLabelText('Email'), 'new@example.com');
    await user.type(screen.getByLabelText('Password'), 'hunter22');
    await user.click(screen.getByRole('button', { name: /create account/i }));

    expect(registerWithEmail).toHaveBeenCalledWith('new@example.com', 'hunter22');
    expect(navigateByUrl).toHaveBeenCalledWith('/');
  });

  it('shows a friendly message when sign-in fails', async () => {
    const signInWithEmail = jest.fn().mockRejectedValue({ code: 'auth/wrong-password' });

    await render(LoginComponent, {
      providers: [
        { provide: AuthService, useValue: { signInWithEmail } },
        { provide: Router, useValue: { navigateByUrl: jest.fn() } }
      ]
    });

    const user = userEvent.setup();
    await user.type(screen.getByLabelText('Email'), 'demo@example.com');
    await user.type(screen.getByLabelText('Password'), 'wrong');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/incorrect email or password/i);
  });

  it('signs in with Google', async () => {
    const signInWithGoogle = jest.fn().mockResolvedValue(undefined);
    const navigateByUrl = jest.fn().mockResolvedValue(true);

    await render(LoginComponent, {
      providers: [
        { provide: AuthService, useValue: { signInWithGoogle } },
        { provide: Router, useValue: { navigateByUrl } }
      ]
    });

    const user = userEvent.setup();
    await user.click(screen.getByRole('button', { name: /continue with google/i }));

    expect(signInWithGoogle).toHaveBeenCalled();
    expect(navigateByUrl).toHaveBeenCalledWith('/');
  });
});
