import { setupZonelessTestEnv } from 'jest-preset-angular/setup-env/zoneless';
import '@testing-library/jest-dom';

setupZonelessTestEnv();

if (!window.matchMedia) {
  window.matchMedia = jest.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn()
  }));
}