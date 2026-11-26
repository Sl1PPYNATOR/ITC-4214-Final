from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxLengthValidator, MinValueValidator
from django.db import models

from catalogue.models import Car


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    full_name = models.CharField(max_length=120)
    email = models.EmailField(
        max_length=254,
        validators=[MaxLengthValidator(254)],
    )
    phone = models.CharField(max_length=25)
    delivery_city = models.CharField(max_length=80)
    delivery_address = models.CharField(max_length=255)
    notes = models.TextField(
        blank=True,
        validators=[MaxLengthValidator(500)],
        help_text="Optional delivery or dealership instructions (max 500 characters).",
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def recalculate_total(self):
        total = sum(
            (item.subtotal for item in self.items.all()),
            Decimal("0.00"),
        )
        self.total_price = total
        self.save(update_fields=["total_price"])
        return total

    def __str__(self):
        return f"Order #{self.pk} - {self.user.username} ({self.get_status_display()})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "car"],
                name="unique_order_car_item",
            )
        ]

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if self.unit_price is None and self.car_id:
            self.unit_price = self.car.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.car} (Order #{self.order.pk})"