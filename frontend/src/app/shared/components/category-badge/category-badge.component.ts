import { ChangeDetectionStrategy, Component, Input, computed, signal } from '@angular/core';

export type CategoryVariant = 'ifrs' | 'fiscal' | 'other';

/**
 * The backend's router assigns a free-text category (e.g. "IFRS",
 * "Fiscalité Tunisienne", "Tax_code", "Web"). This maps that text to one of
 * three visual variants so the badge stays consistent even as the router's
 * exact labels evolve.
 */
export function categoryVariant(category: string | null | undefined): CategoryVariant {
  const normalized = (category ?? '').toLowerCase();

  if (normalized.includes('ifrs')) {
    return 'ifrs';
  }

  if (
    normalized.includes('fiscal') ||
    normalized.includes('tax') ||
    normalized.includes('tunisi')
  ) {
    return 'fiscal';
  }

  return 'other';
}

@Component({
  selector: 'app-category-badge',
  standalone: true,
  templateUrl: './category-badge.component.html',
  styleUrl: './category-badge.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class CategoryBadgeComponent {
  private readonly categorySignal = signal<string | null | undefined>(undefined);

  @Input()
  set category(value: string | null | undefined) {
    this.categorySignal.set(value);
  }
  get category(): string | null | undefined {
    return this.categorySignal();
  }

  protected readonly variant = computed(() => categoryVariant(this.categorySignal()));
  protected readonly label = computed(() => this.categorySignal() || 'Web');
}
