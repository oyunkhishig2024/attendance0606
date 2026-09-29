import { Pressable, StyleSheet, Text, View } from "react-native";

import type { Employee } from "@/api/employees";
import { colors, radius, spacing } from "@/theme";

export function EmployeeMultiSelect({
  employees, selectedIds, onToggle,
}: { employees: Employee[]; selectedIds: Set<string>; onToggle: (id: string) => void }) {
  return (
    <View>
      {employees.map((e) => {
        const selected = selectedIds.has(e.id);
        return (
          <Pressable key={e.id} onPress={() => onToggle(e.id)} style={styles.row}>
            <View style={[styles.checkbox, selected && styles.checkboxChecked]}>
              {selected ? <Text style={styles.checkmark}>✓</Text> : null}
            </View>
            <Text style={styles.name}>{e.full_name}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: "row", alignItems: "center", paddingVertical: spacing.sm },
  checkbox: {
    width: 22, height: 22, borderRadius: 6, borderWidth: 1.5, borderColor: colors.border,
    alignItems: "center", justifyContent: "center", marginRight: spacing.md,
  },
  checkboxChecked: { backgroundColor: colors.primary, borderColor: colors.primary },
  checkmark: { color: "#fff", fontSize: 14, fontWeight: "700" },
  name: { color: colors.text, fontSize: 15 },
});
