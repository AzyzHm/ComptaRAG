import { Injectable, computed, signal } from '@angular/core';

export type ThemePreference = 'light' | 'dark' | 'system';
type ResolvedTheme = 'light' | 'dark';

const STORAGE_KEY = 'comptarag-theme';

function isThemePreference(value: unknown): value is ThemePreference {
  return value === 'light' || value === 'dark' || value === 'system';
}

function readStoredPreference(): ThemePreference {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return isThemePreference(stored) ? stored : 'system';
  } catch {
    return 'system';
  }
}

function systemPrefersDark(): boolean {
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly preferenceSignal = signal<ThemePreference>(readStoredPreference());
  private readonly systemPrefersDarkSignal = signal(systemPrefersDark());

  readonly preference = this.preferenceSignal.asReadonly();
  readonly resolvedTheme = computed<ResolvedTheme>(() => {
    const preference = this.preferenceSignal();
    return preference === 'system'
      ? this.systemPrefersDarkSignal()
        ? 'dark'
        : 'light'
      : preference;
  });

  constructor() {
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    media.addEventListener('change', (event) => {
      this.systemPrefersDarkSignal.set(event.matches);
      this.applyTheme();
    });

    this.applyTheme();
  }

  setPreference(preference: ThemePreference): void {
    this.preferenceSignal.set(preference);
    try {
      localStorage.setItem(STORAGE_KEY, preference);
    } catch {
      // Storage can be unavailable (private browsing, quota); the
      // preference still applies for the current session either way.
    }
    this.applyTheme();
  }

  private applyTheme(): void {
    document.documentElement.setAttribute('data-theme', this.resolvedTheme());
  }
}
