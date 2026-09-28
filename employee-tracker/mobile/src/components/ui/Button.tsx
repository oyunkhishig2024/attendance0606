import { ActivityIndicator, Pressable, StyleSheet, Text } from "react-native";

import { colors, radius, spacing } from "@/theme";

type Variant = "primary" | "secondary" | "ghost" | "destructive";

export function Button({
  title, onPress, variant = "primary", loading = false, disabled = false,
}: { title: string; onPress: () => void; variant?: Variant; loading?: boolean; disabled?: boolean }) {
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || loading}
      style={({ pressed }) => [
        styles.base,
        variantStyles[variant],
        (disabled || loading) && styles.disabled,
        pressed && styles.pressed,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={variant === "primary" || variant === "destructive" ? "#fff" : colors.primary} />
      ) : (
        <Text style={[styles.text, textStyles[variant]]}>{title}</Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    paddingVertical: spacing.md, paddingHorizontal: spacing.lg, borderRadius: radius.card,
    alignItems: "center", justifyContent: "center", minHeight: 52,
  },
  text: { fontSize: 16, fontWeight: "600" },
  disabled: { opacity: 0.5 },
  pressed: { opacity: 0.85 },
});

const variantStyles = StyleSheet.create({
  primary: { backgroundColor: colors.primary },
  secondary: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border },
  ghost: { backgroundColor: "transparent" },
  destructive: { backgroundColor: colors.danger },
});

const textStyles = StyleSheet.create({
  primary: { color: "#fff" },
  secondary: { color: colors.text },
  ghost: { color: colors.primary },
  destructive: { color: "#fff" },
});
