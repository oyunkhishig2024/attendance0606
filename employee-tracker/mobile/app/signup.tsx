import { router } from "expo-router";
import { useState } from "react";
import { Text, View } from "react-native";

import * as authApi from "@/api/auth";
import { ApiError } from "@/api/client";
import { Screen } from "@/components/layout/Screen";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { setToken } from "@/utils/storage/secure";
import { colors, spacing } from "@/theme";

export default function SignupScreen() {
  const [organizationName, setOrganizationName] = useState("");
  const [adminName, setAdminName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async () => {
    setError(null);
    if (password.length < 8 || !/\d/.test(password)) {
      setError("Нууц үг дор хаяж 8 тэмдэгттэй, дор хаяж 1 тоотой байх ёстой.");
      return;
    }
    setLoading(true);
    try {
      const { token } = await authApi.signup({
        organization_name: organizationName, admin_name: adminName, email, password,
      });
      await setToken(token);
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
        <Text style={{ fontSize: 28, fontWeight: "700", color: colors.text }}>Байгууллага бүртгүүлэх</Text>
      </View>
      <Input label="Байгууллагын нэр" value={organizationName} onChangeText={setOrganizationName} />
      <Input label="Таны нэр" value={adminName} onChangeText={setAdminName} />
      <Input label="Имэйл" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />
      <Input label="Нууц үг" value={password} onChangeText={setPassword} secureTextEntry />
      {error ? <Text style={{ color: colors.danger, marginBottom: spacing.md }}>{error}</Text> : null}
      <Button title="Бүртгүүлэх" onPress={onSubmit} loading={loading} />
    </Screen>
  );
}
