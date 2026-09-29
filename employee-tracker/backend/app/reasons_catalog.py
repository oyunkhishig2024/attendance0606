"""15 preset Mongolian absence-reason types (spec §1.2 item 9, assumption
#6): a fixed catalogue shared across tenants rather than per-tenant custom
types. The spec names the capability but doesn't enumerate the 15 -- these
are a reasonable, generic HR set."""

REASON_CATALOG: dict[str, str] = {
    "sick": "Өвчтэй",
    "medical_appointment": "Эмнэлэгт үзүүлэх",
    "annual_leave": "Ээлжийн амралт",
    "paid_leave": "Цалинтай чөлөө",
    "unpaid_leave": "Цалингүй чөлөө",
    "maternity_leave": "Жирэмсний амралт",
    "care_leave": "Асаргааны чөлөө",
    "family_reasons": "Ар гэрийн шалтгаан",
    "family_emergency": "Гэр бүлийн гачигдал",
    "funeral": "Оршуулга",
    "training": "Сургалт/семинар",
    "business_trip": "Томилолт",
    "off_site_work": "Ажлын шалтгаанаар гадуур",
    "legal": "Хууль/шүүхийн шалтгаан",
    "other": "Бусад",
}

REASON_KEYS = frozenset(REASON_CATALOG.keys())
