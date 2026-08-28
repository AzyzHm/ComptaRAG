import { render, screen } from '@testing-library/angular';

import {
  CategoryBadgeComponent,
  categoryVariant
} from '@shared/components/category-badge/category-badge.component';

describe('categoryVariant', () => {
  it('maps IFRS-flavoured labels to the ifrs variant', () => {
    expect(categoryVariant('IFRS')).toBe('ifrs');
    expect(categoryVariant('ifrs 15')).toBe('ifrs');
  });

  it('maps Tunisian fiscal/tax labels to the fiscal variant', () => {
    expect(categoryVariant('Fiscalité Tunisienne')).toBe('fiscal');
    expect(categoryVariant('Tax_code')).toBe('fiscal');
  });

  it('falls back to other for unknown or missing categories', () => {
    expect(categoryVariant('Web')).toBe('other');
    expect(categoryVariant(null)).toBe('other');
    expect(categoryVariant(undefined)).toBe('other');
  });
});

describe('CategoryBadgeComponent', () => {
  it('renders the given category label', async () => {
    await render(`<app-category-badge [category]="'IFRS'" />`, {
      imports: [CategoryBadgeComponent]
    });

    expect(screen.getByText('IFRS')).toBeTruthy();
  });

  it('falls back to "Web" when no category is provided', async () => {
    await render(`<app-category-badge [category]="null" />`, {
      imports: [CategoryBadgeComponent]
    });

    expect(screen.getByText('Web')).toBeTruthy();
  });
});
