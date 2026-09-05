import { render, screen } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { ActivatedRoute, Router, convertToParamMap } from '@angular/router';
import { of } from 'rxjs';

import { ChatComponent } from '@features/chat/chat.component';

describe('Chat feature (integration)', () => {
  it('starts a new chat, sends the first question, and renders the categorized answer', async () => {
    const navigate = jest.fn().mockResolvedValue(true);

    await render(ChatComponent, {
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: ActivatedRoute, useValue: { paramMap: of(convertToParamMap({})) } },
        { provide: Router, useValue: { navigate } }
      ]
    });

    const httpMock = TestBed.inject(HttpTestingController);

    // The sidebar's chat list loads on init.
    httpMock.expectOne('http://localhost:8000/chats/').flush([]);

    const user = userEvent.setup();
    await user.type(
      screen.getByLabelText('Ask a question'),
      'Comment la TVA est-elle traitée sur les exportations ?'
    );
    await user.click(screen.getByRole('button', { name: /^ask$/i }));

    expect(screen.getByText('Comment la TVA est-elle traitée sur les exportations ?')).toBeTruthy();

    const createRequest = httpMock.expectOne('http://localhost:8000/chats/');
    expect(createRequest.request.method).toBe('POST');
    createRequest.flush({ id: 'chat-1', owner_uid: 'u1', title: 'New chat' });

    const messageRequest = await waitForRequest(
      httpMock,
      'http://localhost:8000/chats/chat-1/messages'
    );
    expect(messageRequest.request.method).toBe('POST');
    expect(messageRequest.request.body).toEqual({
      query: 'Comment la TVA est-elle traitée sur les exportations ?'
    });

    messageRequest.flush({
      response: 'Les exportations de biens sont exonérées de TVA.',
      category: 'Fiscalité Tunisienne',
      chat_id: 'chat-1'
    });

    expect(
      await screen.findByText('Les exportations de biens sont exonérées de TVA.')
    ).toBeTruthy();
    expect(screen.getByText('Fiscalité Tunisienne')).toBeTruthy();
    expect(navigate).toHaveBeenCalledWith(['/chat', 'chat-1'], { replaceUrl: true });

    // Sending a message refreshes the sidebar's chat list.
    httpMock.expectOne('http://localhost:8000/chats/').flush([
      {
        id: 'chat-1',
        owner_uid: 'u1',
        title: 'Comment la TVA est-elle traitée sur les exportations ?'
      }
    ]);

    httpMock.verify();
  });
});

async function waitForRequest(httpMock: HttpTestingController, url: string) {
  const deadline = Date.now() + 2000;
  for (;;) {
    try {
      return httpMock.expectOne(url);
    } catch (err) {
      if (Date.now() > deadline) {
        throw err;
      }
      await new Promise((resolve) => setTimeout(resolve, 10));
    }
  }
}
