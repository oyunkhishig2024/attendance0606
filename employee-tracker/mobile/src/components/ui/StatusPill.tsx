import { StyleSheet, Text, View } from "react-native";

import { radius, spacing } from "@/theme";
import { STATUS_META, type AttendanceStatus } from "@/lib/status";

export function StatusPill({ status }: { status: AttendanceStatus }) {
  const meta = STATUS_META[status];
  return (
    <View style={[styles.pill, { backgroundColor: `${meta.color}22` }]}>
      <Text style={[styles.text, { color: meta.color }]}>{meta.label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  pill: { paddingHorizontal: spacing.md, paddingVertical: spacing.xs, borderRadius: radius.pill, alignSelf: "flex-start" },
  text: { fontWeight: "600", fontSize: 13 },
});
