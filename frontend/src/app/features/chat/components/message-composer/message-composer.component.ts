import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Input,
  Output,
  signal
} from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ButtonComponent } from '@shared/components/button/button.component';

@Component({
  selector: 'app-message-composer',
  standalone: true,
  imports: [FormsModule, ButtonComponent],
  templateUrl: './message-composer.component.html',
  styleUrl: './message-composer.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class MessageComposerComponent {
  @Input() disabled = false;
  @Output() readonly submitted = new EventEmitter<string>();

  protected readonly draft = signal('');

  protected submit(): void {
    const value = this.draft();
    if (!value.trim() || this.disabled) {
      return;
    }
    this.submitted.emit(value);
    this.draft.set('');
  }

  protected onEnter(event: Event): void {
    const keyboardEvent = event as KeyboardEvent;
    if (keyboardEvent.shiftKey) {
      return;
    }
    keyboardEvent.preventDefault();
    this.submit();
  }
}
