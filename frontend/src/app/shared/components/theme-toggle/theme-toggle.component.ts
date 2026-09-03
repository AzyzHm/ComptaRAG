import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { ThemePreference, ThemeService } from '@core/services/theme.service';

@Component({
  selector: 'app-theme-toggle',
  standalone: true,
  templateUrl: './theme-toggle.component.html',
  styleUrl: './theme-toggle.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ThemeToggleComponent {
  protected readonly themeService = inject(ThemeService);

  protected select(preference: ThemePreference): void {
    this.themeService.setPreference(preference);
  }
}