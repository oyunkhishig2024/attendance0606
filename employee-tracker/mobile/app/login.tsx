import { router } from "expo-router";
import { useState } from "react";
import { Text, View } from "react-native";

import { ApiError } from "@/api/client";
import { Screen } from "@/components/layout/Screen";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/context/auth";
import { colors, spacing } from "@/theme";

export default function LoginScreen() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async () => {
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
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
        <Text style={{ fontSize: 28, fontWeight: "700", color: colors.text }}>Тавтай морил</Text>
      </View>
      <Input label="Имэйл" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />
      <Input label="Нууц үг" value={password} onChangeText={setPassword} secureTextEntry />
      {error ? <Text style={{ color: colors.danger, marginBottom: spacing.md }}>{error}</Text> : null}
      <Button title="Нэвтрэх" onPress={onSubmit} loading={loading} />
      <View style={{ marginTop: spacing.lg, alignItems: "center" }}>
        <Button title="Бүртгүүлэх" variant="ghost" onPress={() => router.push("/signup")} />
      </View>
    </Screen>
  );
}
