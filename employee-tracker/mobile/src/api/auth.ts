import { apiFetch } from "@/api/client";

export type AuthUser = {
  id: string;
  name: string;
  email: string;
  role: "SystemAdmin" | "Admin" | "HR" | "Manager";
  organization_id: string | null;
  must_change_password: boolean;
};

export function signup(input: { organization_name: string; admin_name: string; email: string; password: string }) {
  return apiFetch<{ token: string; user: AuthUser }>("/api/auth/signup", {
    method: "POST", body: input, auth: false,
  });
}

export function login(input: { email: string; password: string }) {
  return apiFetch<{ token: string; user: AuthUser }>("/api/auth/login", {
    method: "POST", body: input, auth: false,
  });
}

export function me() {
  return apiFetch<AuthUser>("/api/auth/me");
}

export function changePassword(input: { current_password: string; new_password: string }) {
  return apiFetch<{ ok: true }>("/api/auth/change-password", { method: "POST", body: input });
}

export function deleteAccount(input: { password: string }) {
  return apiFetch<{ ok: true }>("/api/auth/delete-account", { method: "POST", body: input });
}
