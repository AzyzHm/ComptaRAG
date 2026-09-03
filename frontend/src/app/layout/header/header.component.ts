import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '@core/services/auth.service';
import { ProfileModalComponent } from '@features/account/profile-modal/profile-modal.component';
import { ButtonComponent } from '@shared/components/button/button.component';
import { RoleBadgeComponent } from '@shared/components/role-badge/role-badge.component';
import { ThemeToggleComponent } from '@shared/components/theme-toggle/theme-toggle.component';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [
    RouterLink,
    ButtonComponent,
    RoleBadgeComponent,
    ProfileModalComponent,
    ThemeToggleComponent
  ],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HeaderComponent {
  private readonly router = inject(Router);
  protected readonly authService = inject(AuthService);

  protected readonly profileModalOpen = signal(false);

  protected openProfileModal(): void {
    this.profileModalOpen.set(true);
  }

  protected closeProfileModal(): void {
    this.profileModalOpen.set(false);
  }

  protected async logout(): Promise<void> {
    await this.authService.logout();
    await this.router.navigateByUrl('/login');
  }
}
