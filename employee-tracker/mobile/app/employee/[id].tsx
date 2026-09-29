import { useQuery } from "@tanstack/react-query";
import { router, useLocalSearchParams } from "expo-router";
import { useState } from "react";
import { StyleSheet, Text, View } from "react-native";

import { getEmployeeMonthGrid, type MonthGridDay } from "@/api/attendance";
import { getEmployee } from "@/api/employees";
import { Screen } from "@/components/layout/Screen";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useRole } from "@/hooks/useRole";
import { STATUS_META } from "@/lib/status";
import { colors, radius, spacing } from "@/theme";

function shiftMonth(month: string, delta: number): string {
  const [y, m] = month.split("-").map(Number);
  const d = new Date(Date.UTC(y, m - 1 + delta, 1));
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
}

function DayCell({ day }: { day: MonthGridDay }) {
  const dayNumber = Number(day.date.slice(-2));
  const meta = day.status ? STATUS_META[day.status] : null;
  const background = meta ? `${meta.color}22` : colors.surfaceAlt;
  const textColor = meta ? meta.color : colors.textMuted;

  return (
    <View style={[styles.cell, { backgroundColor: background }]}>
      <Text style={[styles.cellDay, { color: textColor }]}>{dayNumber}</Text>
      {day.flagged ? <Text style={styles.flag}>⚑</Text> : null}
    </View>
  );
}

export default function EmployeeDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { can } = useRole();
  const [month, setMonth] = useState(() => new Date().toISOString().slice(0, 7));

  const { data: employee } = useQuery({ queryKey: ["employee", id], queryFn: () => getEmployee(id!) });
  const { data: grid, isLoading } = useQuery({
    queryKey: ["employee-month-grid", id, month],
    queryFn: () => getEmployeeMonthGrid(id!, month),
    enabled: !!id,
  });

  return (
    <Screen>
      <View style={{ marginTop: spacing.lg, marginBottom: spacing.md }}>
        <Text style={{ fontSize: 22, fontWeight: "700", color: colors.text }}>
          {employee?.full_name ?? "Ажилтан"}
        </Text>
        <Text style={{ color: colors.textMuted, marginTop: spacing.xs }}>
          {employee?.position ?? ""} {employee?.department ? `· ${employee.department}` : ""}
        </Text>
      </View>

      <View style={{ flexDirection: "row", justifyContent: "center", alignItems: "center", marginBottom: spacing.md }}>
        <Button title="‹" variant="secondary" onPress={() => setMonth((m) => shiftMonth(m, -1))} />
        <Text style={{ marginHorizontal: spacing.lg, fontWeight: "600", color: colors.text }}>{month}</Text>
        <Button title="›" variant="secondary" onPress={() => setMonth((m) => shiftMonth(m, 1))} />
      </View>

      {isLoading ? (
        <Text style={{ color: colors.textMuted }}>Уншиж байна…</Text>
      ) : (
        <Card>
          <View style={styles.grid}>
            {(grid?.days ?? []).map((day) => (
              <DayCell key={day.date} day={day} />
            ))}
          </View>
        </Card>
      )}

      {can("employees.write") ? (
        <Button
          title="Шалтгаан бүртгэх"
          onPress={() => router.push({ pathname: "/reasons/log", params: { employeeId: id } })}
        />
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  grid: { flexDirection: "row", flexWrap: "wrap" },
  cell: {
    width: "13%", aspectRatio: 1, margin: "0.5%", borderRadius: radius.card / 2,
    alignItems: "center", justifyContent: "center",
  },
  cellDay: { fontSize: 12, fontWeight: "600" },
  flag: { fontSize: 9, position: "absolute", top: 2, right: 2 },
});
