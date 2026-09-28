import { apiFetch } from "@/api/client";
import type { AttendanceStatus } from "@/lib/status";

export type PublicEmployee = {
  first_name: string;
  branch_name: string | null;
  branch_active: boolean;
  today_shift_window: string | null;
};

export function getPublicEmployee(token: string) {
  return apiFetch<PublicEmployee>(`/api/public/employee/${token}`, { auth: false });
}

export function getConsent(token: string) {
  return apiFetch<{ consent_text: string; consent_version: string }>(`/api/public/consent/${token}`, {
    auth: false,
  });
}

export function postConsent(token: string, input: { acknowledged: boolean; full_name: string; device_fingerprint: string }) {
  return apiFetch<{ ok: true; consent_version: string }>(`/api/public/consent/${token}`, {
    method: "POST", body: input, auth: false,
  });
}

export type CheckInResult = {
  status: AttendanceStatus;
  distance_m: number;
  check_in_time: string;
  flagged: boolean;
};

export function postCheckIn(token: string, input: {
  latitude: number; longitude: number; accuracy_m: number; captured_at: string;
  device_fingerprint: string; mock_location_flag: boolean;
}) {
  return apiFetch<CheckInResult>(`/api/public/checkin/${token}`, { method: "POST", body: input, auth: false });
}
