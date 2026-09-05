export const getAuth = jest.fn(() => ({ currentUser: null }));

export const onAuthStateChanged = jest.fn((_auth: unknown, callback: (user: unknown) => void) => {
  callback(null);
  return () => undefined;
});

export const signInWithEmailAndPassword = jest.fn();
export const createUserWithEmailAndPassword = jest.fn();
export const signInWithPopup = jest.fn();
export const signOut = jest.fn();
export const updateProfile = jest.fn();
export const updateEmail = jest.fn();
export const updatePassword = jest.fn();
export const reauthenticateWithCredential = jest.fn();

export class GoogleAuthProvider {}

export class EmailAuthProvider {
  static credential = jest.fn();
}
