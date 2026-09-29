import { useQuery } from "@tanstack/react-query";
import { router, useLocalSearchParams } from "expo-router";
import { useState } from "react";
import { Text, TextInput, View } from "react-native";

import { listEmployees } from "@/api/employees";
import { createReasons } from "@/api/reasons";
import { ApiError } from "@/api/client";
import { Screen } from "@/components/layout/Screen";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Chip } from "@/components/ui/Chip";
import { EmployeeMultiSelect } from "@/components/domain/EmployeeMultiSelect";
import { REASON_CATALOG } from "@/lib/reasons";
import { colors, spacing } from "@/theme";

const todayStr = () => new Date().toISOString().slice(0, 10);

/** Reason logging (spec §3.5 item 4 / §9.4 reasons.tsx): 15 preset reason
 * types, multi-employee selection, one row written per employee over a
 * date range. Preselects the employee when opened from their detail page. */
export default function ReasonLogScreen() {
  const { employeeId } = useLocalSearchParams<{ employeeId?: string }>();
  const { data: employeesData } = useQuery({ queryKey: ["employees"], queryFn: () => listEmployees() });

  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set(employeeId ? [employeeId] : []));
  const [reasonKey, setReasonKey] = useState<string>(REASON_CATALOG[0].key);
  const [startDate, setStartDate] = useState(todayStr());
  const [endDate, setEndDate] = useState(todayStr());
  const [note, setNote] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const toggle = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const onSubmit = async () => {
    setError(null);
    if (selectedIds.size === 0) {
      setError("Дор хаяж нэг ажилтан сонгоно уу.");
      return;
    }
    setSubmitting(true);
    try {
      await createReasons({
        employee_ids: Array.from(selectedIds), reason_key: reasonKey,
        start_date: startDate, end_date: endDate, note: note || undefined,
      });
      router.back();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Тодорхойгүй алдаа гарлаа.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Screen>
      <View style={{ marginTop: spacing.lg, marginBottom: spacing.md }}>
        <Text style={{ fontSize: 22, fontWeight: "700", color: colors.text }}>Шалтгаан бүртгэх</Text>
      </View>

      <Text style={{ color: colors.textMuted, marginBottom: spacing.sm }}>Шалтгааны төрөл</Text>
      <View style={{ flexDirection: "row", flexWrap: "wrap", marginBottom: spacing.md }}>
        {REASON_CATALOG.map((r) => (
          <Chip key={r.key} label={r.label} active={reasonKey === r.key} onPress={() => setReasonKey(r.key)} />
        ))}
      </View>

      <View style={{ flexDirection: "row", gap: spacing.md, marginBottom: spacing.md }}>
        <View style={{ flex: 1 }}>
          <Text style={{ color: colors.textMuted, marginBottom: spacing.xs }}>Эхлэх огноо</Text>
          <TextInput
            value={startDate} onChangeText={setStartDate} placeholder="YYYY-MM-DD"
            style={inputStyle}
          />
        </View>
        <View style={{ flex: 1 }}>
          <Text style={{ color: colors.textMuted, marginBottom: spacing.xs }}>Дуусах огноо</Text>
          <TextInput
            value={endDate} onChangeText={setEndDate} placeholder="YYYY-MM-DD"
            style={inputStyle}
          />
        </View>
      </View>

      <Text style={{ color: colors.textMuted, marginBottom: spacing.xs }}>Тэмдэглэл (заавал биш)</Text>
      <TextInput value={note} onChangeText={setNote} style={[inputStyle, { marginBottom: spacing.md }]} multiline />

      <Text style={{ color: colors.textMuted, marginBottom: spacing.xs }}>Ажилтан сонгох</Text>
      <Card>
        <EmployeeMultiSelect
          employees={employeesData?.items ?? []}
          selectedIds={selectedIds}
          onToggle={toggle}
        />
      </Card>

      {error ? <Text style={{ color: colors.danger, marginBottom: spacing.md }}>{error}</Text> : null}

      <Button title="Бүртгэх" onPress={onSubmit} loading={submitting} />
    </Screen>
  );
}

const inputStyle = {
  backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border,
  borderRadius: 16, padding: spacing.md, fontSize: 15, color: colors.text,
};
