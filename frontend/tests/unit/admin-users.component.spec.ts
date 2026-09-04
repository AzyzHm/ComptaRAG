import { render, screen, within } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { of, throwError } from 'rxjs';

import { AdminUsersComponent } from '@features/admin/users/admin-users.component';
import { AdminApiService } from '@core/services/admin-api.service';
import { AuthService } from '@core/services/auth.service';
import { UserProfile } from '@core/models/user.model';

const usersForAdminViewer: UserProfile[] = [
  { uid: 'target-uid', email: 'them@example.com', display_name: 'Them', role: 'USER' }
];

const usersForSuperAdminViewer: UserProfile[] = [
  { uid: 'target-uid', email: 'them@example.com', display_name: 'Them', role: 'USER' },
  { uid: 'other-admin-uid', email: 'other-admin@example.com', display_name: 'Other', role: 'ADMIN' }
];

function renderPage(
  viewerRole: 'ADMIN' | 'SUPER_ADMIN',
  users: UserProfile[],
  overrides: Partial<{ listUsers: jest.Mock; updateRole: jest.Mock; deleteUser: jest.Mock }> = {}
) {
  const listUsers = overrides.listUsers ?? jest.fn().mockReturnValue(of(users));
  const updateRole = overrides.updateRole ?? jest.fn();
  const deleteUser = overrides.deleteUser ?? jest.fn().mockReturnValue(of(undefined));

  return render(AdminUsersComponent, {
    providers: [
      { provide: AdminApiService, useValue: { listUsers, updateRole, deleteUser } },
      {
        provide: AuthService,
        useValue: {
          profile: () => ({ uid: 'viewer-uid', role: viewerRole }),
          role: () => viewerRole
        }
      }
    ]
  }).then((result) => ({ result, listUsers, updateRole, deleteUser }));
}

describe('AdminUsersComponent', () => {
  it('lists the accounts the backend returned', async () => {
    await renderPage('ADMIN', usersForAdminViewer);

    expect(await screen.findByText('them@example.com')).toBeTruthy();
  });

  it('gives an ADMIN viewer no role selector or delete button at all', async () => {
    await renderPage('ADMIN', usersForAdminViewer);

    await screen.findByText('them@example.com');
    expect(screen.queryByRole('combobox')).toBeNull();
    expect(screen.queryByRole('button', { name: /delete/i })).toBeNull();
  });

  it('lets a SUPER_ADMIN promote a USER to ADMIN, offering only USER and ADMIN', async () => {
    const { updateRole } = await renderPage('SUPER_ADMIN', usersForSuperAdminViewer, {
      updateRole: jest.fn().mockReturnValue(of({ ...usersForSuperAdminViewer[0], role: 'ADMIN' }))
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

  it("does not offer a role selector or delete button for the SUPER_ADMIN's own row", async () => {
    await renderPage('SUPER_ADMIN', [
      ...usersForSuperAdminViewer,
      { uid: 'viewer-uid', email: 'me@example.com', display_name: 'Me', role: 'ADMIN' }
    ]);

    await screen.findByText('me@example.com');
    const ownRow = screen.getByText('me@example.com').closest('tr') as HTMLElement;
    expect(within(ownRow).queryByRole('combobox')).toBeNull();
    expect(within(ownRow).queryByRole('button', { name: /delete/i })).toBeNull();
  });

  it('shows an error message when the role update fails', async () => {
    await renderPage('SUPER_ADMIN', usersForSuperAdminViewer, {
      updateRole: jest.fn().mockReturnValue(throwError(() => new Error('nope')))
    });

    await screen.findByText('them@example.com');
    const targetRow = screen.getByText('them@example.com').closest('tr') as HTMLElement;
    const select = within(targetRow).getByRole('combobox');

    const user = userEvent.setup();
    await user.selectOptions(select, 'ADMIN');

    expect(await screen.findByRole('alert')).toHaveTextContent(/could not update/i);
  });

  it('lets a SUPER_ADMIN delete an account after confirming', async () => {
    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true);
    const { deleteUser } = await renderPage('SUPER_ADMIN', usersForSuperAdminViewer);

    await screen.findByText('them@example.com');
    const targetRow = screen.getByText('them@example.com').closest('tr') as HTMLElement;

    const user = userEvent.setup();
    await user.click(within(targetRow).getByRole('button', { name: /delete/i }));

    expect(confirmSpy).toHaveBeenCalled();
    expect(deleteUser).toHaveBeenCalledWith('target-uid');
    expect(screen.queryByText('them@example.com')).toBeNull();

    confirmSpy.mockRestore();
  });

  it('does not delete when the confirmation is declined', async () => {
    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(false);
    const { deleteUser } = await renderPage('SUPER_ADMIN', usersForSuperAdminViewer);

    await screen.findByText('them@example.com');
    const targetRow = screen.getByText('them@example.com').closest('tr') as HTMLElement;

    const user = userEvent.setup();
    await user.click(within(targetRow).getByRole('button', { name: /delete/i }));

    expect(deleteUser).not.toHaveBeenCalled();
    expect(screen.getByText('them@example.com')).toBeTruthy();

    confirmSpy.mockRestore();
  });

  it('shows an error message when the delete fails', async () => {
    jest.spyOn(window, 'confirm').mockReturnValue(true);
    await renderPage('SUPER_ADMIN', usersForSuperAdminViewer, {
      deleteUser: jest.fn().mockReturnValue(throwError(() => new Error('nope')))
    });

    await screen.findByText('them@example.com');
    const targetRow = screen.getByText('them@example.com').closest('tr') as HTMLElement;

    const user = userEvent.setup();
    await user.click(within(targetRow).getByRole('button', { name: /delete/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/could not delete/i);

    jest.restoreAllMocks();
  });

  it('shows a status message while loading', async () => {
    const listUsers = jest.fn().mockReturnValue(of(usersForAdminViewer));
    await renderPage('ADMIN', usersForAdminViewer, { listUsers });

    expect(listUsers).toHaveBeenCalled();
  });
});
