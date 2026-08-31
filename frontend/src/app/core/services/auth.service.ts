import { Injectable, inject, signal, computed } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { FirebaseApp, initializeApp } from 'firebase/app';
import {
  Auth,
  GoogleAuthProvider,
  User as FirebaseUser,
  createUserWithEmailAndPassword,
  getAuth,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut
} from 'firebase/auth';

import { environment } from '@env/environment';
import { ApiService } from '@core/services/api.service';
import { UserProfile } from '@core/models/user.model';

const firebaseApp: FirebaseApp = initializeApp(environment.firebase);
const firebaseAuth: Auth = getAuth(firebaseApp);

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly api = inject(ApiService);

  private readonly firebaseUserSignal = signal<FirebaseUser | null>(null);
  private readonly profileSignal = signal<UserProfile | null>(null);
  private readonly initializingSignal = signal(true);

  readonly firebaseUser = this.firebaseUserSignal.asReadonly();
  readonly profile = this.profileSignal.asReadonly();
  readonly isInitializing = this.initializingSignal.asReadonly();
  readonly role = computed(() => this.profileSignal()?.role ?? null);
  readonly isAuthenticated = computed(
    () => this.firebaseUserSignal() !== null && this.profileSignal() !== null
  );

  readonly ready: Promise<void>;

  constructor() {
    this.ready = new Promise((resolve) => {
      onAuthStateChanged(firebaseAuth, async (firebaseUser) => {
        this.firebaseUserSignal.set(firebaseUser);

        if (firebaseUser) {
          await this.syncProfile();
        } else {
          this.profileSignal.set(null);
        }

        this.initializingSignal.set(false);
        resolve();
      });
    });
  }

  async signInWithEmail(email: string, password: string): Promise<void> {
    await signInWithEmailAndPassword(firebaseAuth, email, password);
    await this.syncProfile();
  }

  async registerWithEmail(email: string, password: string): Promise<void> {
    await createUserWithEmailAndPassword(firebaseAuth, email, password);
    await this.syncProfile();
  }

  async signInWithGoogle(): Promise<void> {
    await signInWithPopup(firebaseAuth, new GoogleAuthProvider());
    await this.syncProfile();
  }

  async logout(): Promise<void> {
    await signOut(firebaseAuth);
    this.profileSignal.set(null);
  }

  getIdToken(): Promise<string | null> {
    const current = firebaseAuth.currentUser;
    if (!current) {
      return Promise.resolve(null);
    }
    return current.getIdToken();
  }

  private async syncProfile(): Promise<void> {
    try {
      const profile = await firstValueFrom(this.api.get<UserProfile>('/auth/me'));
      this.profileSignal.set(profile);
    } catch {
      this.profileSignal.set(null);
    }
  }
}
