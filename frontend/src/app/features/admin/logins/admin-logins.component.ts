import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';

import { AdminApiService } from '@core/services/admin-api.service';
import { LoginEvent } from '@core/models/admin-stats.model';
import { RoleBadgeComponent } from '@shared/components/role-badge/role-badge.component';

@Component({
  selector: 'app-admin-logins',
  standalone: true,
  imports: [DatePipe, RoleBadgeComponent],
  templateUrl: './admin-logins.component.html',
  styleUrl: './admin-logins.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AdminLoginsComponent implements OnInit {
  private readonly adminApi = inject(AdminApiService);

  protected readonly events = signal<LoginEvent[]>([]);
  protected readonly loading = signal(true);
  protected readonly error = signal<string | null>(null);

  ngOnInit(): void {
    this.load();
  }

  private load(): void {
    this.loading.set(true);
    this.error.set(null);

    this.adminApi.listLoginEvents().subscribe({
      next: (events) => {
        this.events.set(events);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load login activity. Please try again.');
        this.loading.set(false);
      }
    });
  }
}
