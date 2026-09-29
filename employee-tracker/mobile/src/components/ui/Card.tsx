import { ReactNode } from "react";
import { StyleSheet, View } from "react-native";

import { colors, radius, spacing } from "@/theme";

export function Card({ children }: { children: ReactNode }) {
  return <View style={styles.card}>{children}</View>;
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface, borderRadius: radius.card, padding: spacing.lg,
    marginBottom: spacing.md, shadowColor: "#000", shadowOpacity: 0.06, shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 }, elevation: 1,
  },
});
