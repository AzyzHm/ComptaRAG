import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  HostListener,
  Input,
  Output,
  signal
} from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ChatSummary } from '@core/models/chat.model';
import { AutofocusDirective } from '@shared/directives/autofocus.directive';

@Component({
  selector: 'app-chat-sidebar',
  standalone: true,
  imports: [FormsModule, AutofocusDirective],
  templateUrl: './chat-sidebar.component.html',
  styleUrl: './chat-sidebar.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChatSidebarComponent {
  @Input() chats: ChatSummary[] = [];
  @Input() activeChatId: string | null = null;
  @Input() loading = false;
  @Input() collapsed = false;
  @Input() mobileOpen = false;

  @Output() readonly newChat = new EventEmitter<void>();
  @Output() readonly selectChat = new EventEmitter<string>();
  @Output() readonly renameChat = new EventEmitter<{ id: string; title: string }>();
  @Output() readonly deleteChat = new EventEmitter<string>();
  @Output() readonly toggleCollapsed = new EventEmitter<void>();
  @Output() readonly closeMobile = new EventEmitter<void>();

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

  protected onSelect(chatId: string): void {
    this.selectChat.emit(chatId);
  }

  protected get expanded(): boolean {
    return !this.collapsed || this.mobileOpen;
  }

  @HostListener('document:keydown.escape')
  protected onEscape(): void {
    if (this.mobileOpen) {
      this.closeMobile.emit();
    }
  }
}
