import { Pressable, StyleSheet, Text } from "react-native";

import { colors, radius, spacing } from "@/theme";

export function Chip({ label, active, onPress }: { label: string; active: boolean; onPress: () => void }) {
  return (
    <Pressable
      onPress={onPress}
      style={[styles.chip, active ? styles.chipActive : styles.chipInactive]}
    >
      <Text style={[styles.text, active && styles.textActive]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  chip: {
    paddingHorizontal: spacing.md, paddingVertical: spacing.sm, borderRadius: radius.pill,
    marginRight: spacing.sm, marginBottom: spacing.sm, borderWidth: 1,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipInactive: { backgroundColor: colors.surface, borderColor: colors.border },
  text: { fontSize: 13, fontWeight: "600", color: colors.text },
  textActive: { color: "#fff" },
});
