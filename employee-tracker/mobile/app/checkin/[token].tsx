import { useLocalSearchParams } from "expo-router";
import { useEffect, useState } from "react";
import { ActivityIndicator, Text, View } from "react-native";

import { getPublicEmployee, type PublicEmployee } from "@/api/public";
import { Screen } from "@/components/layout/Screen";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { StatusPill } from "@/components/ui/StatusPill";
import { useCheckIn } from "@/hooks/useCheckIn";
import { colors, spacing } from "@/theme";

export default function CheckInScreen() {
  const { token } = useLocalSearchParams<{ token: string }>();
  const [employee, setEmployee] = useState<PublicEmployee | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const { state, start } = useCheckIn(token ?? "");

  useEffect(() => {
    if (!token) return;
    getPublicEmployee(token).then(setEmployee).catch(() => setLoadError("Холбоос хүчингүй байна."));
  }, [token]);

  if (loadError) {
    return (
      <Screen>
        <Card><Text style={{ color: colors.danger }}>{loadError}</Text></Card>
      </Screen>
    );
  }

  return (
    <Screen>
      <View style={{ marginTop: spacing.xl, marginBottom: spacing.lg }}>
        <Text style={{ fontSize: 24, fontWeight: "700", color: colors.text }}>
          {employee ? `Сайн байна уу, ${employee.first_name}` : "Ачааллаж байна…"}
        </Text>
        {employee ? (
          <Text style={{ color: colors.textMuted, marginTop: spacing.xs }}>
            {employee.branch_name} · {employee.today_shift_window ?? "Өнөөдөр ажлын өдөр биш"}
          </Text>
        ) : null}
      </View>

      {state.phase === "idle" || state.phase === "rationale" ? (
        <>
          <Card>
            <Text style={{ color: colors.text }}>
              Ажилд ирснээ бүртгэхийн тулд байршлыг ашиглана. Зөвхөн энэ мөчид, нэг удаа авна.
            </Text>
          </Card>
          <Button title="Ирц бүртгэх" onPress={start} disabled={!employee || !employee.branch_active} />
        </>
      ) : null}

      {state.phase === "acquiring" ? (
        <View style={{ alignItems: "center", marginTop: spacing.xl }}>
          <ActivityIndicator color={colors.primary} size="large" />
          <Text style={{ color: colors.textMuted, marginTop: spacing.md }}>Байршил тодорхойлж байна…</Text>
        </View>
      ) : null}

      {state.phase === "permission_denied" ? (
        <Card>
          <Text style={{ color: colors.danger }}>
            Байршлын зөвшөөрөл олгогдоогүй тул ирц бүртгэх боломжгүй байна. Тохиргоо руу орж зөвшөөрнө үү.
          </Text>
        </Card>
      ) : null}

      {state.phase === "success" ? (
        <Card>
          <StatusPill status={state.result.status} />
          <Text style={{ color: colors.text, marginTop: spacing.sm }}>
            Та {Math.round(state.result.distance_m)} м дотор байна.
          </Text>
          {state.result.flagged ? (
            <Text style={{ color: colors.warning, marginTop: spacing.xs }}>
              Энэ бүртгэл нэмэлт хяналтад орсон болно.
            </Text>
          ) : null}
        </Card>
      ) : null}

      {state.phase === "rejected" ? (
        <>
          <Card>
            <Text style={{ color: colors.danger }}>{state.message}</Text>
          </Card>
          <Button title="Дахин оролдох" onPress={start} />
        </>
      ) : null}
    </Screen>
  );
}
