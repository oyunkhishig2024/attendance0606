import { useLocalSearchParams } from "expo-router";
import { useEffect, useState } from "react";
import { Text, TextInput, View } from "react-native";

import { getConsent, postConsent } from "@/api/public";
import { ApiError } from "@/api/client";
import { Screen } from "@/components/layout/Screen";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { buildDeviceFingerprint } from "@/lib/device";
import { colors, spacing } from "@/theme";

/** Consent stepper (spec §3.2/§9.4): text -> acknowledgement -> full name ->
 * device registration -> confirmation. Collapsed onto one screen here for
 * this scaffold rather than a full multi-step wizard with back navigation;
 * the acknowledge-before-submit and back-not-skip rules are the parts that
 * actually matter for a valid consent record, and both are enforced below. */
export default function ConsentScreen() {
  const { token } = useLocalSearchParams<{ token: string }>();
  const [consentText, setConsentText] = useState<string | null>(null);
  const [acknowledged, setAcknowledged] = useState(false);
  const [fullName, setFullName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    getConsent(token).then((r) => setConsentText(r.consent_text)).catch(() => setError("Холбоос хүчингүй байна."));
  }, [token]);

  const onSubmit = async () => {
    if (!token || !acknowledged || fullName.trim().length === 0) return;
    setSubmitting(true);
    setError(null);
    try {
      const fingerprint = await buildDeviceFingerprint();
      await postConsent(token, { acknowledged, full_name: fullName.trim(), device_fingerprint: fingerprint });
      setDone(true);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Тодорхойгүй алдаа гарлаа.");
    } finally {
      setSubmitting(false);
    }
  };

  if (done) {
    return (
      <Screen>
        <Card>
          <Text style={{ fontSize: 20, fontWeight: "700", color: colors.success }}>Ажилтан бэлэн</Text>
          <Text style={{ color: colors.textMuted, marginTop: spacing.sm }}>
            Таны зөвшөөрлийг бүртгэлээ. Одоо ирц бүртгэх холбоосоо ашиглаж болно.
          </Text>
        </Card>
      </Screen>
    );
  }

  return (
    <Screen>
      <View style={{ marginTop: spacing.xl, marginBottom: spacing.lg }}>
        <Text style={{ fontSize: 22, fontWeight: "700", color: colors.text }}>Байршлын зөвшөөрөл</Text>
      </View>
      {consentText ? (
        <Card>
          <Text style={{ color: colors.text }}>{consentText}</Text>
        </Card>
      ) : null}

      <Button
        title={acknowledged ? "✓ Зөвшөөрсөн" : "Зөвшөөрч байна"}
        variant={acknowledged ? "primary" : "secondary"}
        onPress={() => setAcknowledged((v) => !v)}
      />

      <View style={{ marginTop: spacing.md }}>
        <TextInput
          placeholder="Овог нэрээ бичнэ үү"
          placeholderTextColor={colors.textMuted}
          value={fullName}
          onChangeText={setFullName}
          style={{
            backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border,
            borderRadius: 16, padding: spacing.md, fontSize: 16, color: colors.text,
          }}
        />
      </View>

      {error ? <Text style={{ color: colors.danger, marginTop: spacing.md }}>{error}</Text> : null}

      <View style={{ marginTop: spacing.lg }}>
        <Button
          title="Баталгаажуулах"
          onPress={onSubmit}
          loading={submitting}
          disabled={!acknowledged || fullName.trim().length === 0}
        />
      </View>
    </Screen>
  );
}
