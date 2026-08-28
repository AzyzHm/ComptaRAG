import { render, screen } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';

import { ChatComponent } from '@features/chat/chat.component';

/**
 * Integration test: renders the real ChatComponent together with its real
 * children (message list, composer, category badge) and the real
 * ChatApiService/ApiService. Only the network boundary is mocked, via
 * HttpTestingController, matching the template's "no collaborator mocking"
 * convention for integration tests.
 */
describe('Chat feature (integration)', () => {
  it('sends a question, shows it immediately, then renders the categorized answer', async () => {
    await render(ChatComponent, {
      providers: [provideHttpClient(), provideHttpClientTesting()]
    });

    const httpMock = TestBed.inject(HttpTestingController);
    const user = userEvent.setup();

    await user.type(
      screen.getByLabelText('Ask a question'),
      'Comment la TVA est-elle traitée sur les exportations ?'
    );
    await user.click(screen.getByRole('button', { name: /ask/i }));

    expect(screen.getByText('Comment la TVA est-elle traitée sur les exportations ?')).toBeTruthy();

    const request = httpMock.expectOne('http://localhost:8000/chat/');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      query: 'Comment la TVA est-elle traitée sur les exportations ?'
    });

    request.flush({
      response: 'Les exportations de biens sont exonérées de TVA.',
      category: 'Fiscalité Tunisienne'
    });

    expect(
      await screen.findByText('Les exportations de biens sont exonérées de TVA.')
    ).toBeTruthy();
    expect(screen.getByText('Fiscalité Tunisienne')).toBeTruthy();

    httpMock.verify();
  });
});
