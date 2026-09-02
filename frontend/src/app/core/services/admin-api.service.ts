import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from '@core/services/api.service';
import { ChatDetail, ChatSummary, SendMessageResponse } from '@core/models/chat.model';

@Injectable({ providedIn: 'root' })
export class ChatApiService {
  private readonly api = inject(ApiService);

  listChats(): Observable<ChatSummary[]> {
    return this.api.get<ChatSummary[]>('/chats/');
  }

  createChat(): Observable<ChatSummary> {
    return this.api.post<ChatSummary>('/chats/', {});
  }

  getChat(chatId: string): Observable<ChatDetail> {
    return this.api.get<ChatDetail>(`/chats/${chatId}`);
  }

  renameChat(chatId: string, title: string): Observable<{ id: string; title: string }> {
    return this.api.patch<{ id: string; title: string }>(`/chats/${chatId}`, { title });
  }

  deleteChat(chatId: string): Observable<void> {
    return this.api.delete<void>(`/chats/${chatId}`);
  }

  sendMessage(chatId: string, query: string): Observable<SendMessageResponse> {
    return this.api.post<SendMessageResponse>(`/chats/${chatId}/messages`, { query });
  }
}
