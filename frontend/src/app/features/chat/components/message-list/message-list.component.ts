import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

import { ChatMessage } from '@core/models/chat.model';
import { CategoryBadgeComponent } from '@shared/components/category-badge/category-badge.component';

@Component({
  selector: 'app-message-list',
  standalone: true,
  imports: [CategoryBadgeComponent],
  templateUrl: './message-list.component.html',
  styleUrl: './message-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class MessageListComponent {
  @Input() messages: ChatMessage[] = [];
  @Input() pending = false;
}
