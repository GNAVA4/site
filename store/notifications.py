"""Сборка текста заказа и доставка по выбранному каналу.

Сам заказ уже сохранён в БД (Order/OrderItem) — это лишь уведомление менеджера.
"""

import logging
from urllib.parse import quote

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def build_order_text(order):
    lines = [f"Заказ #{order.pk} — {order.customer_name}"]
    if order.customer_phone:
        lines.append(f"Телефон: {order.customer_phone}")
    lines.append("")
    for it in order.items.all():
        lines.append(
            f"- {it.product_title} ({it.size}) ×{it.quantity} = {it.sum_retail}р "
            f"(опт {it.sum_wholesale}р)"
        )
    lines.append("")
    lines.append(f"ИТОГО розница: {order.total_retail} р")
    lines.append(f"ИТОГО опт: {order.total_wholesale} р")
    if order.comment:
        lines.append("")
        lines.append(f"Комментарий: {order.comment}")
    lines.append("")
    lines.append(f"Для проверки статуса: заказ № {order.pk}, код {order.code}")
    return "\n".join(lines)


def telegram_link(site, text):
    if not site.telegram_username:
        return None
    return f"https://t.me/{site.telegram_username}?text={quote(text)}"


def whatsapp_link(site, text):
    if not site.whatsapp_phone:
        return None
    return f"https://wa.me/{site.whatsapp_phone}?text={quote(text)}"


def mailto_link(site, order, text):
    """Ссылка mailto: открывает почтовую программу клиента с письмом на адрес магазина."""
    if not site.email:
        return None
    subject = quote(f"Заказ #{order.pk}")
    body = quote(text)
    return f"mailto:{site.email}?subject={subject}&body={body}"


def send_order_email(site, order, text, admin_url=None):
    """Серверное уведомление магазина о новом заказе — на site.email.
    Шлётся при ЛЮБОМ канале (чтобы заказ не потерялся, если клиент не нажмёт ссылку на success).
    В DEBUG уходит в консоль (см. settings). Не роняет оформление: ошибки логируются.
    Возвращает True/False — отправлено ли."""
    recipient = site.email
    if not recipient:
        logger.warning("Заказ #%s: site.email пуст — уведомление магазину не отправлено.", order.pk)
        return False

    body = [text, "", f"Способ связи с клиентом: {order.get_contact_method_display()}"]
    if admin_url:
        body.append(f"Открыть заказ в админке: {admin_url}")

    try:
        send_mail(
            subject=f"Новый заказ #{order.pk} — {order.customer_name}",
            message="\n".join(body),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        return True
    except Exception:
        # Заказ уже сохранён — сбой уведомления не должен ломать оформление.
        logger.exception("Не удалось отправить уведомление о заказе #%s на %s", order.pk, recipient)
        return False
