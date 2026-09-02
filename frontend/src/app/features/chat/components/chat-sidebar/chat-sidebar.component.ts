import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Input,
  Output,
  signal
} from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ChatSummary } from '@core/models/chat.model';

@Component({
  selector: 'app-chat-sidebar',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './chat-sidebar.component.html',
  styleUrl: './chat-sidebar.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChatSidebarComponent {
  @Input() chats: ChatSummary[] = [];
  @Input() activeChatId: string | null = null;
  @Input() loading = false;
  @Input() collapsed = false;

  @Output() readonly newChat = new EventEmitter<void>();
  @Output() readonly selectChat = new EventEmitter<string>();
  @Output() readonly renameChat = new EventEmitter<{ id: string; title: string }>();
  @Output() readonly deleteChat = new EventEmitter<string>();
  @Output() readonly toggleCollapsed = new EventEmitter<void>();

  protected readonly editingChatId = signal<string | null>(null);
  protected readonly draftTitle = signal('');

  protected startRename(chat: ChatSummary, event: Event): void {
    event.stopPropagation();
    this.editingChatId.set(chat.id);
    this.draftTitle.set(chat.title);
  }

  protected confirmRename(chatId: string): void {
    const title = this.draftTitle().trim();
    this.editingChatId.set(null);
    if (title) {
      this.renameChat.emit({ id: chatId, title });
    }
  }

  protected cancelRename(): void {
    this.editingChatId.set(null);
  }

  protected confirmDelete(chatId: string, event: Event): void {
    event.stopPropagation();
    if (window.confirm('Delete this chat? This cannot be undone.')) {
      this.deleteChat.emit(chatId);
    }
  }
}
