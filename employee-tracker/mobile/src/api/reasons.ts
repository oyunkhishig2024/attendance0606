import { apiFetch } from "@/api/client";

export type ReasonLog = {
  id: string;
  employee_id: string;
  reason_key: string;
  start_date: string;
  end_date: string;
  note: string | null;
};

export function listReasons(employeeId?: string) {
  const query = employeeId ? `?employee_id=${employeeId}` : "";
  return apiFetch<{ items: ReasonLog[] }>(`/api/reasons${query}`);
}

export function createReasons(input: {
  employee_ids: string[]; reason_key: string; start_date: string; end_date: string; note?: string;
}) {
  return apiFetch<{ items: ReasonLog[] }>("/api/reasons", { method: "POST", body: input });
}
