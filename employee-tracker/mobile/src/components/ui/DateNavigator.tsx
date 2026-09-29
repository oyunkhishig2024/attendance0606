import { Pressable, StyleSheet, Text, View } from "react-native";

import { colors, radius, spacing } from "@/theme";

function shiftDate(dateStr: string, days: number): string {
  const d = new Date(`${dateStr}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

export function DateNavigator({ date, onChange }: { date: string; onChange: (next: string) => void }) {
  const today = new Date().toISOString().slice(0, 10);
  const isToday = date === today;

  return (
    <View style={styles.row}>
      <Pressable style={styles.arrow} onPress={() => onChange(shiftDate(date, -1))}>
        <Text style={styles.arrowText}>‹</Text>
      </Pressable>
      <Text style={styles.date}>{date}</Text>
      <Pressable
        style={[styles.arrow, isToday && styles.disabled]}
        disabled={isToday}
        onPress={() => onChange(shiftDate(date, 1))}
      >
        <Text style={styles.arrowText}>›</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: "row", alignItems: "center", justifyContent: "center", marginBottom: spacing.md },
  arrow: {
    width: 40, height: 40, borderRadius: radius.pill, backgroundColor: colors.surface,
    alignItems: "center", justifyContent: "center", borderWidth: 1, borderColor: colors.border,
  },
  disabled: { opacity: 0.4 },
  arrowText: { fontSize: 20, color: colors.primary, fontWeight: "700" },
  date: { fontSize: 16, fontWeight: "600", color: colors.text, marginHorizontal: spacing.lg },
});
