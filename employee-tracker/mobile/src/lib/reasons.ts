/** Mirrors backend/app/reasons_catalog.py -- keep the two in sync. Fetched
 * fresh from GET /api/reasons/catalog at runtime; this is the offline/typed
 * fallback so the picker can render before that request resolves. */
export const REASON_CATALOG: { key: string; label: string }[] = [
  { key: "sick", label: "Өвчтэй" },
  { key: "medical_appointment", label: "Эмнэлэгт үзүүлэх" },
  { key: "annual_leave", label: "Ээлжийн амралт" },
  { key: "paid_leave", label: "Цалинтай чөлөө" },
  { key: "unpaid_leave", label: "Цалингүй чөлөө" },
  { key: "maternity_leave", label: "Жирэмсний амралт" },
  { key: "care_leave", label: "Асаргааны чөлөө" },
  { key: "family_reasons", label: "Ар гэрийн шалтгаан" },
  { key: "family_emergency", label: "Гэр бүлийн гачигдал" },
  { key: "funeral", label: "Оршуулга" },
  { key: "training", label: "Сургалт/семинар" },
  { key: "business_trip", label: "Томилолт" },
  { key: "off_site_work", label: "Ажлын шалтгаанаар гадуур" },
  { key: "legal", label: "Хууль/шүүхийн шалтгаан" },
  { key: "other", label: "Бусад" },
];
