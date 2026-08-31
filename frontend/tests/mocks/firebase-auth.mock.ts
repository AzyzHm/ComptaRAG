export const getAuth = jest.fn(() => ({ currentUser: null }));

export const onAuthStateChanged = jest.fn((_auth: unknown, callback: (user: unknown) => void) => {
  callback(null);
  return () => undefined;
});

export const signInWithEmailAndPassword = jest.fn();
export const createUserWithEmailAndPassword = jest.fn();
export const signInWithPopup = jest.fn();
export const signOut = jest.fn();

export class GoogleAuthProvider {}
