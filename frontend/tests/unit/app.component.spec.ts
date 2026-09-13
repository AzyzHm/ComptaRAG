import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { render, screen } from '@testing-library/angular';

import { AppComponent } from '@app/app.component';

@Component({ selector: 'app-empty', template: '', standalone: true })
class EmptyComponent {}

describe('AppComponent', () => {
  it('renders the header and footer', async () => {
    await render(AppComponent);

    expect(screen.getByText('ComptaRAG')).toBeTruthy();
    expect(screen.getByText(/informational, not professional/i)).toBeTruthy();
  });

  it('locks page scrolling only while a /chat route is active', async () => {
    const { container, fixture } = await render(AppComponent, {
      providers: [
        provideRouter([
          { path: '', component: EmptyComponent },
          { path: 'chat', component: EmptyComponent },
          { path: 'login', component: EmptyComponent }
        ])
      ]
    });
    const router = TestBed.inject(Router);
    const host = container.querySelector('app-root') ?? container;

    expect(host.classList.contains('app-shell--locked')).toBe(false);

    await router.navigateByUrl('/chat');
    fixture.detectChanges();
    await fixture.whenStable();
    expect(host.classList.contains('app-shell--locked')).toBe(true);

    await router.navigateByUrl('/login');
    fixture.detectChanges();
    await fixture.whenStable();
    expect(host.classList.contains('app-shell--locked')).toBe(false);
  });
});
