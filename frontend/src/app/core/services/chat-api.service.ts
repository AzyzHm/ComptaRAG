import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from '@core/services/api.service';
import { ChatRequest, ChatResponse } from '@core/models/chat.model';

@Injectable({ providedIn: 'root' })
export class ChatApiService {
  private readonly api = inject(ApiService);

  ask(query: string): Observable<ChatResponse> {
    const body: ChatRequest = { query };
    return this.api.post<ChatResponse>('/chat/', body);
  }
}
