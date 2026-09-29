import { Redirect, Tabs } from "expo-router";
import { ActivityIndicator, View } from "react-native";

import { useAuth } from "@/context/auth";
import { colors } from "@/theme";

/** Bottom tab bar (spec §9.3). Only the two tabs this scaffold's screens
 * cover are wired up; staff/analytics/more are deferred (see README). */
export default function AppGroupLayout() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.background }}>
        <ActivityIndicator color={colors.primary} />
      </View>
    );
  }
  if (!user) return <Redirect href="/login" />;
  if (user.must_change_password) return <Redirect href="/change-password" />;

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarStyle: { backgroundColor: colors.surface, borderTopColor: colors.border },
      }}
    >
      <Tabs.Screen name="index" options={{ title: "Хяналт" }} />
      <Tabs.Screen name="attendance" options={{ title: "Ирц" }} />
    </Tabs>
  );
}
