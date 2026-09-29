import { apiFetch } from "@/api/client";

export type Employee = {
  id: string;
  full_name: string;
  position: string | null;
  department: string | null;
  location_id: string;
  is_active: boolean;
};

export function listEmployees(params: { location_id?: string; department?: string } = {}) {
  const query = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== undefined).map(([k, v]) => [k, String(v)]),
  ).toString();
  return apiFetch<{ items: Employee[] }>(`/api/employees${query ? `?${query}` : ""}`);
}

export function getEmployee(id: string) {
  return apiFetch<Employee>(`/api/employees/${id}`);
}
