import { router } from "expo-router";
import { useState } from "react";
import { Text, View } from "react-native";

import * as authApi from "@/api/auth";
import { ApiError } from "@/api/client";
import { Screen } from "@/components/layout/Screen";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/context/auth";
import { colors, spacing } from "@/theme";

export default function ChangePasswordScreen() {
  const { refresh } = useAuth();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async () => {
    setError(null);
    setLoading(true);
    try {
      await authApi.changePassword({ current_password: currentPassword, new_password: newPassword });
      await refresh();
      router.replace("/(app)");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Тодорхойгүй алдаа гарлаа.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen>
      <View style={{ marginTop: spacing.xxl, marginBottom: spacing.xl }}>
        <Text style={{ fontSize: 22, fontWeight: "700", color: colors.text }}>Нууц үгээ солино уу</Text>
      </View>
      <Input label="Одоогийн нууц үг" value={currentPassword} onChangeText={setCurrentPassword} secureTextEntry />
      <Input label="Шинэ нууц үг" value={newPassword} onChangeText={setNewPassword} secureTextEntry />
      {error ? <Text style={{ color: colors.danger, marginBottom: spacing.md }}>{error}</Text> : null}
      <Button title="Хадгалах" onPress={onSubmit} loading={loading} />
    </Screen>
  );
}
