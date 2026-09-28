import { ReactNode } from "react";
import { KeyboardAvoidingView, Platform, ScrollView, StyleSheet } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { colors, spacing } from "@/theme";

export function Screen({ children, scroll = true }: { children: ReactNode; scroll?: boolean }) {
  const Content = scroll ? ScrollView : ({ children: c }: { children: ReactNode }) => <>{c}</>;
  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <Content contentContainerStyle={scroll ? styles.scrollContent : undefined} style={scroll ? styles.flex : undefined}>
          {children}
        </Content>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: colors.background },
  flex: { flex: 1 },
  scrollContent: { padding: spacing.lg, flexGrow: 1 },
});
