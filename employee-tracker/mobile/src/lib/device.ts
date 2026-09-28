import * as Application from "expo-application";
import * as Device from "expo-device";
import { Platform } from "react-native";

import { getOrCreateInstallationId } from "@/utils/storage/secure";

/** Builds the raw fingerprint material (spec §8.3): a rotating per-vendor/
 * per-install identifier plus a stable per-install id plus coarse device
 * info. The server hashes this -- the app never stores or compares the raw
 * value itself, only sends it once per check-in. */
export async function buildDeviceFingerprint(): Promise<string> {
  const rotatingId =
    Platform.OS === "android" ? Application.getAndroidId() : await Application.getIosIdForVendorAsync();
  const installationId = await getOrCreateInstallationId();
  return [rotatingId ?? "unknown", installationId, Device.modelName, Device.osName, Device.osVersion].join("|");
}
