import type { Config } from 'jest';

const config: Config = {
  preset: 'jest-preset-angular',
  setupFilesAfterEnv: ['<rootDir>/setup-jest.ts'],
  testPathIgnorePatterns: ['<rootDir>/node_modules/', '<rootDir>/tests/e2e/'],
  moduleNameMapper: {
    '^firebase/app$': '<rootDir>/tests/mocks/firebase-app.mock.ts',
    '^firebase/auth$': '<rootDir>/tests/mocks/firebase-auth.mock.ts',
    '^@app/(.*)$': '<rootDir>/src/app/$1',
    '^@core/(.*)$': '<rootDir>/src/app/core/$1',
    '^@shared/(.*)$': '<rootDir>/src/app/shared/$1',
    '^@features/(.*)$': '<rootDir>/src/app/features/$1',
    '^@env/(.*)$': '<rootDir>/src/environments/$1'
  },
  collectCoverage: true,
  coverageDirectory: '<rootDir>/coverage',
  collectCoverageFrom: [
    'src/app/**/*.ts',
    '!src/app/**/*.routes.ts',
    '!src/app/**/index.ts',
    '!src/main.ts'
  ],
  coverageReporters: ['text', 'html', 'lcov'],
  testMatch: ['<rootDir>/tests/unit/**/*.spec.ts', '<rootDir>/tests/integration/**/*.spec.ts']
};

export default config;
