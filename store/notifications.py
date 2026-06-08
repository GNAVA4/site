"""Сборка текста заказа и доставка по выбранному каналу.

Сам заказ уже сохранён в БД (Order/OrderItem) — это лишь уведомление менеджера.
"""

from urllib.parse import quote

from django.conf import settings
from django.core.mail import send_mail


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


def send_order_email(site, order, text):
    """Отправляет заказ на почту магазина. В DEBUG уходит в консоль (см. settings)."""
    recipient = site.email
    if not recipient:
        return False
    send_mail(
        subject=f"Новый заказ #{order.pk}",
        message=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=True,
    )
    return True
