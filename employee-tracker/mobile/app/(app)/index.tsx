import { useQuery } from "@tanstack/react-query";
import { Text, View } from "react-native";

import { apiFetch } from "@/api/client";
import { Screen } from "@/components/layout/Screen";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useAuth } from "@/context/auth";
import { ROLE_LABELS } from "@/lib/status";
import { colors, spacing } from "@/theme";

type OrgDaySummary = {
  date: string;
  branches: { location_name: string; on_time: number; late: number; reason: number; absent: number; off: number; flagged: number }[];
  not_checked_in: number;
};

export default function DashboardScreen() {
  const { user, logout } = useAuth();
  const today = new Date().toISOString().slice(0, 10);

  const { data, isLoading } = useQuery({
    queryKey: ["org-day-summary", user?.organization_id, today],
    queryFn: () => apiFetch<OrgDaySummary>(`/api/reports/org-day?date=${today}`),
    enabled: !!user,
  });

  return (
    <Screen>
      <View style={{ marginTop: spacing.xl, marginBottom: spacing.lg }}>
        <Text style={{ fontSize: 24, fontWeight: "700", color: colors.text }}>Хяналтын самбар</Text>
        <Text style={{ color: colors.textMuted, marginTop: spacing.xs }}>
          {user?.name} · {user ? ROLE_LABELS[user.role] : ""}
        </Text>
      </View>

      {isLoading ? (
        <Text style={{ color: colors.textMuted }}>Уншиж байна…</Text>
      ) : (
        (data?.branches ?? []).map((branch) => (
          <Card key={branch.location_name}>
            <Text style={{ fontWeight: "600", color: colors.text, marginBottom: spacing.sm }}>
              {branch.location_name}
            </Text>
            <Text style={{ color: colors.textMuted }}>
              Цагтаа {branch.on_time} · Хоцорсон {branch.late} · Тасалсан {branch.absent}
              {branch.flagged > 0 ? ` · Анхаарал ${branch.flagged}` : ""}
            </Text>
          </Card>
        ))
      )}

      <View style={{ marginTop: spacing.lg }}>
        <Button title="Гарах" variant="secondary" onPress={logout} />
      </View>
    </Screen>
  );
}
