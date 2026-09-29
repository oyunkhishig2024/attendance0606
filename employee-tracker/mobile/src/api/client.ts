import { getToken } from "@/utils/storage/secure";

/** Point this at the deployed backend (spec §1.6: binds 0.0.0.0:8001, all
 * routes prefixed /api). Override with an env/config mechanism per build
 * channel (dev/preview/production, spec §8.6) rather than hardcoding. */
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://localhost:8001";

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string, public field?: string) {
    super(message);
  }
}

type RequestOptions = { method?: string; body?: unknown; auth?: boolean };

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (options.auth !== false) {
    const token = await getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await response.json() : undefined;

  if (!response.ok) {
    throw new ApiError(
      response.status,
      data?.code ?? "unknown_error",
      data?.detail ?? "Тодорхойгүй алдаа гарлаа.",
      data?.field,
    );
  }
  return data as T;
}
