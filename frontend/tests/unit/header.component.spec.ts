import { render, screen } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { provideRouter } from '@angular/router';

import { HeaderComponent } from '@app/layout/header/header.component';
import { AuthService } from '@core/services/auth.service';
import { UserProfile } from '@core/models/user.model';

const profile: UserProfile = {
  uid: 'u1',
  email: 'me@example.com',
  display_name: 'Me',
  role: 'USER'
};

function renderHeader(overrides: Partial<Record<keyof AuthService, unknown>> = {}) {
  return render(HeaderComponent, {
    providers: [
      provideRouter([]),
      {
        provide: AuthService,
        useValue: {
          isAuthenticated: () => true,
          isInitializing: () => false,
          profile: () => profile,
          role: () => profile.role,
          logout: jest.fn().mockResolvedValue(undefined),
          ...overrides
        }
      }
    ]
  });
}

describe('HeaderComponent', () => {
  it('shows the logo next to the brand title', async () => {
    const { container } = await renderHeader();

    const logo = container.querySelector('.app-header__logo') as HTMLImageElement;
    expect(logo.getAttribute('src')).toBe('/logo.png');
  });

  it('opens the profile modal when the user name is clicked', async () => {
    await renderHeader();

    expect(screen.queryByRole('heading', { name: 'Your profile' })).toBeNull();

    await userEvent.setup().click(screen.getByText('Me'));

    expect(await screen.findByRole('heading', { name: 'Your profile' })).toBeTruthy();
  });

  it('closes the profile modal when it emits closed', async () => {
    await renderHeader();

    await userEvent.setup().click(screen.getByText('Me'));
    expect(await screen.findByRole('heading', { name: 'Your profile' })).toBeTruthy();

    await userEvent.setup().click(screen.getByRole('button', { name: /^close$/i }));

    expect(screen.queryByRole('heading', { name: 'Your profile' })).toBeNull();
  });
});
