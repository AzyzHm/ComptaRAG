import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

import { Role } from '@core/models/user.model';

@Component({
  selector: 'app-role-badge',
  standalone: true,
  templateUrl: './role-badge.component.html',
  styleUrl: './role-badge.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class RoleBadgeComponent {
  @Input({ required: true }) role!: Role;
}
