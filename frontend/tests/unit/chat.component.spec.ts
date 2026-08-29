import { render, screen } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { of, throwError } from 'rxjs';

import { ChatComponent } from '@features/chat/chat.component';
import { ChatApiService } from '@core/services/chat-api.service';

describe('ChatComponent', () => {
  it('appends the question immediately, then the answer once it resolves', async () => {
    const ask = jest.fn().mockReturnValue(of({ response: 'It depends.', category: 'IFRS' }));

    await render(ChatComponent, {
      providers: [{ provide: ChatApiService, useValue: { ask } }]
    });

    const user = userEvent.setup();
    await user.type(screen.getByLabelText('Ask a question'), 'What is a provision?');
    await user.click(screen.getByRole('button', { name: /ask/i }));

    expect(screen.getByText('What is a provision?')).toBeTruthy();
    expect(await screen.findByText('It depends.')).toBeTruthy();
    expect(ask).toHaveBeenCalledWith('What is a provision?');
  });

  it('shows an error message when the request fails', async () => {
    const ask = jest.fn().mockReturnValue(throwError(() => new Error('network down')));

    await render(ChatComponent, {
      providers: [{ provide: ChatApiService, useValue: { ask } }]
    });

    const user = userEvent.setup();
    await user.type(screen.getByLabelText('Ask a question'), 'What is a provision?');
    await user.click(screen.getByRole('button', { name: /ask/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/something went wrong/i);
  });

  it('ignores an empty submission and never calls the API', async () => {
    const ask = jest.fn();

    await render(ChatComponent, {
      providers: [{ provide: ChatApiService, useValue: { ask } }]
    });

    expect(screen.getByRole('button', { name: /ask/i })).toBeDisabled();
    expect(ask).not.toHaveBeenCalled();
  });
});
