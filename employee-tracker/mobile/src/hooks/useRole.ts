import { useAuth } from "@/context/auth";

/** Centralises role gating from the §2.2 capability matrix so UI and any
 * future tests read from one place instead of drifting apart. Only the
 * capabilities this scaffold's screens actually need are covered. */
const WRITE_CAPABILITIES = new Set([
  "locations.write", "employees.write", "shifts.write", "holidays.write", "users.write",
]);

export function useRole() {
  const { user } = useAuth();
  const role = user?.role;

  const can = (capability: string): boolean => {
    if (!role) return false;
    if (role === "Manager") return !WRITE_CAPABILITIES.has(capability);
    if (role === "SystemAdmin") return false; // 403 on every tenant-scoped route (spec §2.1).
    if (capability === "users.write") return role === "Admin";
    return role === "Admin" || role === "HR";
  };

  return { role, can };
}
