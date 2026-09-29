import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "employee_tracker.auth_token";
const INSTALLATION_ID_KEY = "employee_tracker.installation_id";

export async function getToken(): Promise<string | null> {
  return SecureStore.getItemAsync(TOKEN_KEY);
}

export async function setToken(token: string): Promise<void> {
  await SecureStore.setItemAsync(TOKEN_KEY, token);
}

export async function clearToken(): Promise<void> {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
}

export async function getOrCreateInstallationId(): Promise<string> {
  const existing = await SecureStore.getItemAsync(INSTALLATION_ID_KEY);
  if (existing) return existing;
  const generated = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  await SecureStore.setItemAsync(INSTALLATION_ID_KEY, generated);
  return generated;
}
