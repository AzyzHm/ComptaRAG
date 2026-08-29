import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { finalize } from 'rxjs';

import { ChatApiService } from '@core/services/chat-api.service';
import { ChatMessage } from '@core/models/chat.model';
import { MessageListComponent } from './components/message-list/message-list.component';
import { MessageComposerComponent } from './components/message-composer/message-composer.component';

let nextId = 0;

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [MessageListComponent, MessageComposerComponent],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChatComponent {
  private readonly chatApi = inject(ChatApiService);

  protected readonly messages = signal<ChatMessage[]>([]);
  protected readonly pending = signal(false);
  protected readonly error = signal<string | null>(null);

  protected submitQuery(query: string): void {
    const trimmed = query.trim();
    if (!trimmed || this.pending()) {
      return;
    }

    this.error.set(null);
    this.appendMessage({ role: 'user', content: trimmed });
    this.pending.set(true);

    this.chatApi
      .ask(trimmed)
      .pipe(finalize(() => this.pending.set(false)))
      .subscribe({
        next: (result) => {
          this.appendMessage({
            role: 'assistant',
            content: result.response,
            category: result.category
          });
        },
        error: () => {
          this.error.set('Something went wrong reaching ComptaRAG. Please try asking again.');
        }
      });
  }

  private appendMessage(message: Omit<ChatMessage, 'id' | 'createdAt'>): void {
    this.messages.update((current) => [
      ...current,
      { ...message, id: `msg-${++nextId}`, createdAt: Date.now() }
    ]);
  }
}
