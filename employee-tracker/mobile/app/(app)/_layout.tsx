import { Redirect, Slot } from "expo-router";
import { ActivityIndicator, View } from "react-native";

import { useAuth } from "@/context/auth";
import { colors } from "@/theme";

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
  return <Slot />;
}
