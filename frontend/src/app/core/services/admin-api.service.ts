import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from '@core/services/api.service';
import { Role, UserProfile } from '@core/models/user.model';

@Injectable({ providedIn: 'root' })
export class AdminApiService {
  private readonly api = inject(ApiService);

  listUsers(): Observable<UserProfile[]> {
    return this.api.get<UserProfile[]>('/admin/users');
  }

  updateRole(uid: string, role: Role): Observable<UserProfile> {
    return this.api.patch<UserProfile>(`/admin/users/${uid}/role`, { role });
  }

  deleteUser(uid: string): Observable<void> {
    return this.api.delete<void>(`/admin/users/${uid}`);
  }
}
