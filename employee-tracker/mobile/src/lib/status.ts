import { colors } from "@/theme";

export type AttendanceStatus = "on_time" | "late" | "reason" | "absent" | "off";

/** Single source of truth for status labels/colours (spec §9.2) -- every
 * screen consumes this rather than defining its own mapping. */
export const STATUS_META: Record<AttendanceStatus, { label: string; color: string; icon: string }> = {
  on_time: { label: "Цагтаа", color: colors.success, icon: "check-circle" },
  late: { label: "Хоцорсон", color: colors.warning, icon: "clock" },
  reason: { label: "Шалтгаантай", color: colors.info, icon: "file-text" },
  absent: { label: "Тасалсан", color: colors.danger, icon: "x-circle" },
  off: { label: "Амралт", color: colors.neutral, icon: "moon" },
};

export const ROLE_LABELS: Record<string, string> = {
  SystemAdmin: "Систем администратор",
  Admin: "Админ",
  HR: "Хүний нөөц",
  Manager: "Менежер",
};
