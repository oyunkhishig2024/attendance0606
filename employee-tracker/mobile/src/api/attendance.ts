import { apiFetch } from "@/api/client";
import type { AttendanceStatus } from "@/lib/status";

export type AttendanceRecord = {
  id: string;
  employee_id: string;
  location_id: string;
  date: string;
  status: AttendanceStatus;
  check_in_time: string | null;
  distance_m: number | null;
  flagged: boolean;
};

export function listAttendance(params: {
  date?: string; location_id?: string; department?: string; status?: AttendanceStatus;
  flagged?: boolean; q?: string;
}) {
  const query = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== undefined).map(([k, v]) => [k, String(v)]),
  ).toString();
  return apiFetch<{ items: AttendanceRecord[] }>(`/api/attendance${query ? `?${query}` : ""}`);
}

export type MonthGridDay = {
  date: string;
  status: AttendanceStatus | null;
  check_in_time: string | null;
  distance_m: number | null;
  flagged: boolean;
  explanation: "holiday" | "rest_day" | "pending" | null;
};

export function getEmployeeMonthGrid(employeeId: string, month: string) {
  return apiFetch<{ days: MonthGridDay[] }>(`/api/employees/${employeeId}/month-grid?month=${month}`);
}
