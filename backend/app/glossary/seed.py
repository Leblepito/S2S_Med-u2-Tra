"""Glossary seed data — medikal + turizm başlangıç terimleri."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import GlossaryDomain, GlossaryTerm, GlossaryTranslation

logger = logging.getLogger(__name__)

MEDICAL_TERMS = [
    {"term": "botox", "cat": "procedure", "tr": "botoks", "ru": "ботокс", "en": "botox", "th": "โบท็อกซ์", "vi": "botox", "zh": "肉毒杆菌", "id": "botox"},
    {"term": "rhinoplasty", "cat": "procedure", "tr": "burun estetiği", "ru": "ринопластика", "en": "rhinoplasty", "th": "ศัลยกรรมจมูก", "vi": "nâng mũi", "zh": "隆鼻术", "id": "rinoplasti"},
    {"term": "dental implant", "cat": "procedure", "tr": "diş implantı", "ru": "зубной имплант", "en": "dental implant", "th": "รากฟันเทียม", "vi": "cấy ghép nha khoa", "zh": "牙科植入", "id": "implan gigi"},
    {"term": "liposuction", "cat": "procedure", "tr": "liposuction", "ru": "липосакция", "en": "liposuction", "th": "ดูดไขมัน", "vi": "hút mỡ", "zh": "吸脂术", "id": "sedot lemak"},
    {"term": "hair transplant", "cat": "procedure", "tr": "saç ekimi", "ru": "пересадка волос", "en": "hair transplant", "th": "ปลูกผม", "vi": "cấy tóc", "zh": "植发", "id": "transplantasi rambut"},
    {"term": "pain", "cat": "complaint", "tr": "ağrı", "ru": "боль", "en": "pain", "th": "ปวด", "vi": "đau", "zh": "疼痛", "id": "sakit"},
    {"term": "swelling", "cat": "complaint", "tr": "şişlik", "ru": "отёк", "en": "swelling", "th": "บวม", "vi": "sưng", "zh": "肿胀", "id": "bengkak"},
    {"term": "bruising", "cat": "complaint", "tr": "morluk", "ru": "синяк", "en": "bruising", "th": "ช้ำ", "vi": "bầm tím", "zh": "淤青", "id": "memar"},
    {"term": "allergy", "cat": "complaint", "tr": "alerji", "ru": "аллергия", "en": "allergy", "th": "แพ้", "vi": "dị ứng", "zh": "过敏", "id": "alergi"},
    {"term": "infection", "cat": "complaint", "tr": "enfeksiyon", "ru": "инфекция", "en": "infection", "th": "ติดเชื้อ", "vi": "nhiễm trùng", "zh": "感染", "id": "infeksi"},
    {"term": "anesthesia", "cat": "medication", "tr": "anestezi", "ru": "анестезия", "en": "anesthesia", "th": "ยาชา", "vi": "gây mê", "zh": "麻醉", "id": "anestesi"},
    {"term": "antibiotic", "cat": "medication", "tr": "antibiyotik", "ru": "антибиотик", "en": "antibiotic", "th": "ยาปฏิชีวนะ", "vi": "kháng sinh", "zh": "抗生素", "id": "antibiotik"},
    {"term": "painkiller", "cat": "medication", "tr": "ağrı kesici", "ru": "обезболивающее", "en": "painkiller", "th": "ยาแก้ปวด", "vi": "thuốc giảm đau", "zh": "止痛药", "id": "obat pereda nyeri"},
    {"term": "serum", "cat": "medication", "tr": "serum", "ru": "сыворотка", "en": "serum", "th": "เซรั่ม", "vi": "huyết thanh", "zh": "血清", "id": "serum"},
    {"term": "bandage", "cat": "medication", "tr": "bandaj", "ru": "бинт", "en": "bandage", "th": "ผ้าพันแผล", "vi": "băng", "zh": "绷带", "id": "perban"},
    {"term": "consultation", "cat": "process", "tr": "konsültasyon", "ru": "консультация", "en": "consultation", "th": "ปรึกษา", "vi": "tư vấn", "zh": "咨询", "id": "konsultasi"},
    {"term": "pre-op", "cat": "process", "tr": "ameliyat öncesi", "ru": "предоперационный", "en": "pre-operative", "th": "ก่อนผ่าตัด", "vi": "trước phẫu thuật", "zh": "术前", "id": "pra-operasi"},
    {"term": "post-op", "cat": "process", "tr": "ameliyat sonrası", "ru": "послеоперационный", "en": "post-operative", "th": "หลังผ่าตัด", "vi": "sau phẫu thuật", "zh": "术后", "id": "pasca-operasi"},
    {"term": "recovery", "cat": "process", "tr": "iyileşme", "ru": "восстановление", "en": "recovery", "th": "พักฟื้น", "vi": "hồi phục", "zh": "恢复", "id": "pemulihan"},
    {"term": "follow-up", "cat": "process", "tr": "kontrol", "ru": "контроль", "en": "follow-up", "th": "ติดตามผล", "vi": "tái khám", "zh": "复查", "id": "tindak lanjut"},
]

TOURISM_TERMS = [
    {"term": "check-in", "cat": "hotel", "tr": "giriş", "ru": "регистрация", "en": "check-in", "th": "เช็คอิน", "vi": "nhận phòng", "zh": "办理入住", "id": "check-in"},
    {"term": "check-out", "cat": "hotel", "tr": "çıkış", "ru": "выписка", "en": "check-out", "th": "เช็คเอาท์", "vi": "trả phòng", "zh": "退房", "id": "check-out"},
    {"term": "room service", "cat": "hotel", "tr": "oda servisi", "ru": "обслуживание номеров", "en": "room service", "th": "บริการห้องพัก", "vi": "dịch vụ phòng", "zh": "客房服务", "id": "layanan kamar"},
    {"term": "minibar", "cat": "hotel", "tr": "minibar", "ru": "минибар", "en": "minibar", "th": "มินิบาร์", "vi": "minibar", "zh": "迷你吧", "id": "minibar"},
    {"term": "safe", "cat": "hotel", "tr": "kasa", "ru": "сейф", "en": "safe", "th": "ตู้เซฟ", "vi": "két sắt", "zh": "保险箱", "id": "brankas"},
    {"term": "airport transfer", "cat": "transport", "tr": "havaalanı transferi", "ru": "трансфер из аэропорта", "en": "airport transfer", "th": "รถรับส่งสนามบิน", "vi": "đưa đón sân bay", "zh": "机场接送", "id": "transfer bandara"},
    {"term": "tour", "cat": "activity", "tr": "tur", "ru": "тур", "en": "tour", "th": "ทัวร์", "vi": "tour", "zh": "旅游", "id": "tur"},
    {"term": "spa", "cat": "activity", "tr": "spa", "ru": "спа", "en": "spa", "th": "สปา", "vi": "spa", "zh": "水疗", "id": "spa"},
    {"term": "massage", "cat": "activity", "tr": "masaj", "ru": "массаж", "en": "massage", "th": "นวด", "vi": "massage", "zh": "按摩", "id": "pijat"},
    {"term": "restaurant", "cat": "dining", "tr": "restoran", "ru": "ресторан", "en": "restaurant", "th": "ร้านอาหาร", "vi": "nhà hàng", "zh": "餐厅", "id": "restoran"},
    {"term": "menu", "cat": "dining", "tr": "menü", "ru": "меню", "en": "menu", "th": "เมนู", "vi": "thực đơn", "zh": "菜单", "id": "menu"},
    {"term": "bill", "cat": "dining", "tr": "hesap", "ru": "счёт", "en": "bill", "th": "บิล", "vi": "hóa đơn", "zh": "账单", "id": "tagihan"},
    {"term": "tip", "cat": "dining", "tr": "bahşiş", "ru": "чаевые", "en": "tip", "th": "ทิป", "vi": "tiền tip", "zh": "小费", "id": "tip"},
    {"term": "reservation", "cat": "general", "tr": "rezervasyon", "ru": "бронирование", "en": "reservation", "th": "การจอง", "vi": "đặt chỗ", "zh": "预订", "id": "reservasi"},
    {"term": "complaint", "cat": "general", "tr": "şikayet", "ru": "жалоба", "en": "complaint", "th": "ร้องเรียน", "vi": "khiếu nại", "zh": "投诉", "id": "keluhan"},
]

LANGS = ["tr", "ru", "en", "th", "vi", "zh", "id"]


async def seed_glossary_data(db: AsyncSession) -> None:
    """Glossary seed data yükle. Idempotent — varsa skip."""
    await _seed_domain(db, "medical", "Medikal terimler", MEDICAL_TERMS)
    await _seed_domain(db, "tourism", "Turizm & otelcilik terimleri", TOURISM_TERMS)


async def _seed_domain(
    db: AsyncSession, name: str, desc: str, terms: list[dict]
) -> None:
    """Tek domain seed et."""
    result = await db.execute(
        select(GlossaryDomain).where(GlossaryDomain.name == name)
    )
    domain = result.scalar_one_or_none()
    if domain:
        logger.info(f"[SEED] Domain '{name}' zaten var — skip")
        return

    domain = GlossaryDomain(name=name, description=desc)
    db.add(domain)
    await db.flush()

    for t in terms:
        term = GlossaryTerm(
            domain_id=domain.id,
            canonical_term=t["term"],
            category=t.get("cat", ""),
        )
        db.add(term)
        await db.flush()

        for lang in LANGS:
            if lang in t:
                translation = GlossaryTranslation(
                    term_id=term.id,
                    language=lang,
                    translation=t[lang],
                )
                db.add(translation)

    await db.commit()
    logger.info(f"[SEED] Domain '{name}': {len(terms)} terim yüklendi")
