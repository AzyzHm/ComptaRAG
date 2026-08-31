import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  OnInit,
  signal
} from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AdminApiService } from '@core/services/admin-api.service';
import { AuthService } from '@core/services/auth.service';
import { Role, UserProfile } from '@core/models/user.model';
import { RoleBadgeComponent } from '@shared/components/role-badge/role-badge.component';

const ALL_ROLES: Role[] = ['USER', 'ADMIN', 'SUPER_ADMIN'];

@Component({
  selector: 'app-admin-users',
  standalone: true,
  imports: [FormsModule, RoleBadgeComponent],
  templateUrl: './admin-users.component.html',
  styleUrl: './admin-users.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AdminUsersComponent implements OnInit {
  private readonly adminApi = inject(AdminApiService);
  private readonly authService = inject(AuthService);

  protected readonly users = signal<UserProfile[]>([]);
  protected readonly loading = signal(true);
  protected readonly error = signal<string | null>(null);
  protected readonly pendingUid = signal<string | null>(null);

  protected readonly viewerUid = computed(() => this.authService.profile()?.uid ?? null);
  protected readonly viewerIsSuperAdmin = computed(() => this.authService.role() === 'SUPER_ADMIN');

  ngOnInit(): void {
    this.load();
  }

  private load(): void {
    this.loading.set(true);
    this.error.set(null);

    this.adminApi.listUsers().subscribe({
      next: (users) => {
        this.users.set(users);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load the user list. Please try again.');
        this.loading.set(false);
      }
    });
  }

  protected canEditRole(user: UserProfile): boolean {
    if (user.uid === this.viewerUid()) {
      return false;
    }
    if (!this.viewerIsSuperAdmin() && user.role === 'SUPER_ADMIN') {
      return false;
    }
    return true;
  }

  protected availableRolesFor(_user: UserProfile): Role[] {
    if (this.viewerIsSuperAdmin()) {
      return ALL_ROLES;
    }
    return ALL_ROLES.filter((role) => role !== 'SUPER_ADMIN');
  }

  protected changeRole(user: UserProfile, role: Role): void {
    if (role === user.role || this.pendingUid()) {
      return;
    }

    this.pendingUid.set(user.uid);
    this.error.set(null);

    this.adminApi.updateRole(user.uid, role).subscribe({
      next: (updated) => {
        this.users.update((current) =>
          current.map((entry) => (entry.uid === updated.uid ? updated : entry))
        );
        this.pendingUid.set(null);
      },
      error: () => {
        this.error.set(`Could not update the role for ${user.email ?? user.uid}.`);
        this.pendingUid.set(null);
      }
    });
  }
}
