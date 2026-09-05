import { render, screen } from '@testing-library/angular';

import { MessageListComponent } from '@features/chat/components/message-list/message-list.component';
import { ChatMessage } from '@core/models/chat.model';

describe('MessageListComponent', () => {
  it('shows the empty-state invitation when there are no messages', async () => {
    await render(MessageListComponent, {
      componentInputs: { messages: [], pending: false }
    });

    expect(screen.getByText('Ask ComptaRAG')).toBeTruthy();
  });

  it('renders user and assistant entries with a category badge', async () => {
    const messages: ChatMessage[] = [
      { id: '1', role: 'user', content: 'What is IFRS 15?' },
      {
        id: '2',
        role: 'assistant',
        content: 'IFRS 15 governs revenue recognition.',
        category: 'IFRS'
      }
    ];

    await render(MessageListComponent, {
      componentInputs: { messages, pending: false }
    });

    expect(screen.getByText('What is IFRS 15?')).toBeTruthy();
    expect(screen.getByText('IFRS 15 governs revenue recognition.')).toBeTruthy();
    expect(screen.getByText('IFRS')).toBeTruthy();
    expect(screen.queryByText('Ask ComptaRAG')).toBeNull();
  });

  it('shows a pending indicator while waiting on a response', async () => {
    await render(MessageListComponent, {
      componentInputs: { messages: [], pending: true }
    });

    expect(screen.getByText(/checking the sources/i)).toBeTruthy();
  });
});
