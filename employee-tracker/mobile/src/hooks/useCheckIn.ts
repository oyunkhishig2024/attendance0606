import * as Location from "expo-location";
import { useState } from "react";

import { ApiError } from "@/api/client";
import { postCheckIn, type CheckInResult } from "@/api/public";
import { buildDeviceFingerprint } from "@/lib/device";

const MAX_ACCURACY_M = 100;

type State =
  | { phase: "idle" }
  | { phase: "rationale" }
  | { phase: "acquiring"; elapsedSeconds: number }
  | { phase: "success"; result: CheckInResult }
  | { phase: "rejected"; message: string; code: string }
  | { phase: "permission_denied" };

/** The permission lifecycle contract from spec §8.1/§8.2: rationale shown
 * before the OS dialog, foreground one-shot high-accuracy fix (not
 * Highest -- Highest is slow and rarely needed), accuracy gate with a
 * retry affordance, then the server-authoritative check-in call. */
export function useCheckIn(token: string) {
  const [state, setState] = useState<State>({ phase: "idle" });

  const start = async () => {
    setState({ phase: "rationale" });
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== "granted") {
      setState({ phase: "permission_denied" });
      return;
    }

    setState({ phase: "acquiring", elapsedSeconds: 0 });
    const position = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.High });

    if (position.coords.accuracy != null && position.coords.accuracy > MAX_ACCURACY_M) {
      setState({
        phase: "rejected", code: "accuracy_too_low",
        message: `Байршлын нарийвчлал хангалтгүй байна (${Math.round(position.coords.accuracy)} м). Гадаа гарч дахин оролдоно уу.`,
      });
      return;
    }

    try {
      const fingerprint = await buildDeviceFingerprint();
      const result = await postCheckIn(token, {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy_m: position.coords.accuracy ?? 9999,
        captured_at: new Date(position.timestamp).toISOString(),
        device_fingerprint: fingerprint,
        mock_location_flag: (position.mocked as boolean | undefined) ?? false,
      });
      setState({ phase: "success", result });
    } catch (e) {
      if (e instanceof ApiError) {
        setState({ phase: "rejected", code: e.code, message: e.message });
      } else {
        setState({ phase: "rejected", code: "unknown_error", message: "Тодорхойгүй алдаа гарлаа." });
      }
    }
  };

  return { state, start };
}
