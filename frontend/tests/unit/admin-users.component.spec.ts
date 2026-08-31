import { render, screen, within } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { of, throwError } from 'rxjs';

import { AdminUsersComponent } from '@features/admin/users/admin-users.component';
import { AdminApiService } from '@core/services/admin-api.service';
import { AuthService } from '@core/services/auth.service';
import { UserProfile } from '@core/models/user.model';

const users: UserProfile[] = [
  { uid: 'viewer-uid', email: 'me@example.com', display_name: 'Me', role: 'ADMIN' },
  { uid: 'target-uid', email: 'them@example.com', display_name: 'Them', role: 'USER' }
];

function renderPage(
  viewerRole: 'ADMIN' | 'SUPER_ADMIN',
  overrides: Partial<{ listUsers: jest.Mock; updateRole: jest.Mock }> = {}
) {
  const listUsers = overrides.listUsers ?? jest.fn().mockReturnValue(of(users));
  const updateRole = overrides.updateRole ?? jest.fn();

  return render(AdminUsersComponent, {
    providers: [
      { provide: AdminApiService, useValue: { listUsers, updateRole } },
      {
        provide: AuthService,
        useValue: {
          profile: () => ({ uid: 'viewer-uid', role: viewerRole }),
          role: () => viewerRole
        }
      }
    ]
  }).then((result) => ({ result, listUsers, updateRole }));
}

describe('AdminUsersComponent', () => {
  it('lists users with their roles', async () => {
    await renderPage('ADMIN');

    expect(await screen.findByText('me@example.com')).toBeTruthy();
    expect(screen.getByText('them@example.com')).toBeTruthy();
  });

  it("does not offer a role selector for the viewer's own row", async () => {
    await renderPage('ADMIN');

    await screen.findByText('me@example.com');
    const ownRow = screen.getByText('me@example.com').closest('tr') as HTMLElement;
    expect(within(ownRow).queryByRole('combobox')).toBeNull();
  });

  it('lets an ADMIN promote a USER to ADMIN, but not to SUPER_ADMIN', async () => {
    const { updateRole } = await renderPage('ADMIN', {
      updateRole: jest.fn().mockReturnValue(of({ ...users[1], role: 'ADMIN' }))
    });

    await screen.findByText('them@example.com');
    const targetRow = screen.getByText('them@example.com').closest('tr') as HTMLElement;
    const select = within(targetRow).getByRole('combobox') as HTMLSelectElement;

    const options = Array.from(select.options).map((o) => o.value);
    expect(options).toEqual(['USER', 'ADMIN']);

    const user = userEvent.setup();
    await user.selectOptions(select, 'ADMIN');

    expect(updateRole).toHaveBeenCalledWith('target-uid', 'ADMIN');
  });

  it('offers SUPER_ADMIN as an option when the viewer is a SUPER_ADMIN', async () => {
    await renderPage('SUPER_ADMIN');

    await screen.findByText('them@example.com');
    const targetRow = screen.getByText('them@example.com').closest('tr') as HTMLElement;
    const select = within(targetRow).getByRole('combobox') as HTMLSelectElement;

    const options = Array.from(select.options).map((o) => o.value);
    expect(options).toEqual(['USER', 'ADMIN', 'SUPER_ADMIN']);
  });

  it('shows an error message when the role update fails', async () => {
    await renderPage('SUPER_ADMIN', {
      updateRole: jest.fn().mockReturnValue(throwError(() => new Error('nope')))
    });

    await screen.findByText('them@example.com');
    const targetRow = screen.getByText('them@example.com').closest('tr') as HTMLElement;
    const select = within(targetRow).getByRole('combobox');

    const user = userEvent.setup();
    await user.selectOptions(select, 'ADMIN');

    expect(await screen.findByRole('alert')).toHaveTextContent(/could not update/i);
  });

  it('shows a status message while loading', async () => {
    const listUsers = jest.fn().mockReturnValue(of(users));
    await renderPage('ADMIN', { listUsers });

    expect(listUsers).toHaveBeenCalled();
  });
});
