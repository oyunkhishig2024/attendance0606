import { useQuery } from "@tanstack/react-query";
import { router } from "expo-router";
import { useMemo, useState } from "react";
import { FlatList, Text, View } from "react-native";

import { listAttendance, type AttendanceRecord } from "@/api/attendance";
import { listEmployees } from "@/api/employees";
import { Screen } from "@/components/layout/Screen";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Chip } from "@/components/ui/Chip";
import { DateNavigator } from "@/components/ui/DateNavigator";
import { StatusPill } from "@/components/ui/StatusPill";
import { useRole } from "@/hooks/useRole";
import type { AttendanceStatus } from "@/lib/status";
import { colors, spacing } from "@/theme";

type Filter = "all" | AttendanceStatus | "flagged";

const FILTERS: { key: Filter; label: string }[] = [
  { key: "all", label: "Бүгд" },
  { key: "on_time", label: "Цагтаа" },
  { key: "late", label: "Хоцорсон" },
  { key: "reason", label: "Шалтгаантай" },
  { key: "absent", label: "Тасалсан" },
  { key: "flagged", label: "Флагтай" },
];

export default function AttendanceScreen() {
  const { can } = useRole();
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [filter, setFilter] = useState<Filter>("all");

  const { data: employeesData } = useQuery({ queryKey: ["employees"], queryFn: () => listEmployees() });
  const employeeById = useMemo(() => {
    const map = new Map<string, string>();
    for (const e of employeesData?.items ?? []) map.set(e.id, e.full_name);
    return map;
  }, [employeesData]);

  const { data, isLoading } = useQuery({
    queryKey: ["attendance", date, filter],
    queryFn: () => listAttendance({
      date,
      status: filter !== "all" && filter !== "flagged" ? (filter as AttendanceStatus) : undefined,
      flagged: filter === "flagged" ? true : undefined,
    }),
  });

  const renderRow = ({ item }: { item: AttendanceRecord }) => (
    <Card>
      <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" }}>
        <View style={{ flex: 1 }}>
          <Text style={{ fontWeight: "600", color: colors.text }}>
            {employeeById.get(item.employee_id) ?? item.employee_id}
          </Text>
          {item.check_in_time ? (
            <Text style={{ color: colors.textMuted, marginTop: spacing.xs }}>
              {new Date(item.check_in_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              {item.distance_m != null ? ` · ${Math.round(item.distance_m)} м` : ""}
            </Text>
          ) : null}
        </View>
        <StatusPill status={item.status} />
      </View>
      {item.flagged ? (
        <Text style={{ color: colors.warning, marginTop: spacing.sm }}>⚑ Анхаарал шаардсан</Text>
      ) : null}
      <Button
        title="Дэлгэрэнгүй"
        variant="ghost"
        onPress={() => router.push({ pathname: "/employee/[id]", params: { id: item.employee_id } })}
      />
    </Card>
  );

  return (
    <Screen scroll={false}>
      <View style={{ marginTop: spacing.lg }}>
        <Text style={{ fontSize: 22, fontWeight: "700", color: colors.text, marginBottom: spacing.md }}>Ирц</Text>
      </View>
      <DateNavigator date={date} onChange={setDate} />
      <View style={{ flexDirection: "row", flexWrap: "wrap" }}>
        {FILTERS.map((f) => (
          <Chip key={f.key} label={f.label} active={filter === f.key} onPress={() => setFilter(f.key)} />
        ))}
      </View>

      {can("employees.write") ? (
        <View style={{ marginVertical: spacing.sm }}>
          <Button title="+ Шалтгаан бүртгэх" variant="secondary" onPress={() => router.push("/reasons/log")} />
        </View>
      ) : null}

      {isLoading ? (
        <Text style={{ color: colors.textMuted, marginTop: spacing.lg }}>Уншиж байна…</Text>
      ) : (
        <FlatList
          data={data?.items ?? []}
          keyExtractor={(item) => item.id}
          renderItem={renderRow}
          contentContainerStyle={{ paddingBottom: spacing.xl }}
          ListEmptyComponent={
            <Text style={{ color: colors.textMuted, marginTop: spacing.lg }}>Энэ өдөр бүртгэл алга байна.</Text>
          }
        />
      )}
    </Screen>
  );
}
