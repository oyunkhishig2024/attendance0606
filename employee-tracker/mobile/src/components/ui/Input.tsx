import { StyleSheet, Text, TextInput, TextInputProps, View } from "react-native";

import { colors, radius, spacing } from "@/theme";

export function Input({
  label, error, ...props
}: TextInputProps & { label: string; error?: string }) {
  return (
    <View style={styles.container}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        style={[styles.input, error && styles.inputError]}
        placeholderTextColor={colors.textMuted}
        {...props}
      />
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { marginBottom: spacing.md },
  label: { fontSize: 14, color: colors.textMuted, marginBottom: spacing.xs },
  input: {
    backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border,
    borderRadius: radius.card, paddingHorizontal: spacing.md, paddingVertical: spacing.md,
    fontSize: 16, color: colors.text,
  },
  inputError: { borderColor: colors.danger },
  error: { color: colors.danger, fontSize: 13, marginTop: spacing.xs },
});
