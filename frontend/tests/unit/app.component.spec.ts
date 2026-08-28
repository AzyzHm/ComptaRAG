import { render, screen } from '@testing-library/angular';

import { AppComponent } from '@app/app.component';

describe('AppComponent', () => {
  it('renders the header and footer', async () => {
    await render(AppComponent);

    expect(screen.getByText('ComptaRAG')).toBeTruthy();
    expect(screen.getByText(/informational, not professional/i)).toBeTruthy();
  });
});
