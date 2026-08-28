import { render, screen } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { provideRouter } from '@angular/router';

import { HomeComponent } from '@features/home/home.component';

/**
 * Integration test: renders the real HomeComponent together with its
 * real child (ButtonComponent) and asserts on the resulting behavior,
 * rather than mocking collaborators the way the unit tests do.
 */
describe('HomeComponent (integration)', () => {
  it('increments the counter when the button is clicked', async () => {
    await render(HomeComponent, {
      providers: [provideRouter([])]
    });

    const user = userEvent.setup();
    expect(screen.getByText('Count: 0')).toBeTruthy();

    await user.click(screen.getByRole('button', { name: 'Increment' }));

    expect(screen.getByText('Count: 1')).toBeTruthy();
  });
});
