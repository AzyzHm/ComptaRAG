import { render, screen } from '@testing-library/angular';

import { AppComponent } from '@app/app.component';

describe('AppComponent', () => {
  it('renders the header and footer', async () => {
    await render(AppComponent);

    expect(screen.getByText('Angular Custom Template')).toBeTruthy();
  });
});
