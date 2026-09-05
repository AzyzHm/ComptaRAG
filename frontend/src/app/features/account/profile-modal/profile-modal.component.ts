import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Output,
  inject,
  signal
} from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AuthService } from '@core/services/auth.service';
import { ButtonComponent } from '@shared/components/button/button.component';
import { ModalComponent } from '@shared/components/modal/modal.component';

function friendlyProfileError(error: unknown): string {
  const code = (error as { code?: string })?.code ?? '';

  switch (code) {
    case 'auth/wrong-password':
    case 'auth/invalid-credential':
      return 'Your current password is incorrect.';
    case 'auth/requires-recent-login':
      return 'For your security, please sign out and back in, then try again.';
    case 'auth/email-already-in-use':
      return 'Another account already uses that email.';
    case 'auth/invalid-email':
      return 'Please enter a valid email address.';
    case 'auth/weak-password':
      return 'Please choose a new password with at least 6 characters.';
    default:
      return 'Something went wrong, please try again.';
  }
}

@Component({
  selector: 'app-profile-modal',
  standalone: true,
  imports: [FormsModule, ButtonComponent, ModalComponent],
  templateUrl: './profile-modal.component.html',
  styleUrl: './profile-modal.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ProfileModalComponent {
  private readonly authService = inject(AuthService);

  @Output() readonly closed = new EventEmitter<void>();

  protected readonly displayName = signal(this.authService.profile()?.display_name ?? '');
  protected readonly email = signal(this.authService.profile()?.email ?? '');
  protected readonly currentPassword = signal('');
  protected readonly newPassword = signal('');
  protected readonly confirmNewPassword = signal('');
  protected readonly passwordFieldsVisible = signal(false);

  protected readonly pending = signal(false);
  protected readonly error = signal<string | null>(null);
  protected readonly success = signal<string | null>(null);

  protected togglePasswordFieldsVisibility(): void {
    this.passwordFieldsVisible.update((visible) => !visible);
  }

  protected close(): void {
    this.closed.emit();
  }

  protected async submit(): Promise<void> {
    if (this.pending()) {
      return;
    }

    const profile = this.authService.profile();
    const nextDisplayName = this.displayName().trim();
    const nextEmail = this.email().trim();
    const newPassword = this.newPassword();
    const confirmNewPassword = this.confirmNewPassword();
    const currentPassword = this.currentPassword();

    const nameChanged = nextDisplayName !== (profile?.display_name ?? '');
    const emailChanged = nextEmail !== (profile?.email ?? '');
    const passwordChanged = newPassword.length > 0;

    this.error.set(null);
    this.success.set(null);

    if (!nameChanged && !emailChanged && !passwordChanged) {
      return;
    }

    if (passwordChanged && newPassword !== confirmNewPassword) {
      this.error.set('New password and confirmation do not match.');
      return;
    }

    if ((emailChanged || passwordChanged) && !currentPassword) {
      this.error.set('Please enter your current password to confirm this change.');
      return;
    }

    this.pending.set(true);

    try {
      if (nameChanged) {
        await this.authService.updateDisplayName(nextDisplayName);
      }
      if (emailChanged) {
        await this.authService.updateEmail(nextEmail, currentPassword);
      }
      if (passwordChanged) {
        await this.authService.updatePassword(newPassword, currentPassword);
      }

      this.currentPassword.set('');
      this.newPassword.set('');
      this.confirmNewPassword.set('');
      this.success.set('Your profile has been updated.');
    } catch (err) {
      this.error.set(friendlyProfileError(err));
    } finally {
      this.pending.set(false);
    }
  }
}
