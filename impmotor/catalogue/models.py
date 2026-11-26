from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    country = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} - {self.name}"
        return self.name


class Car(models.Model):
    FUEL_CHOICES = [
        ("petrol", "Petrol"),
        ("diesel", "Diesel"),
        ("hybrid", "Hybrid"),
        ("electric", "Electric"),
        ("other", "Other"),
    ]

    TRANSMISSION_CHOICES = [
        ("automatic", "Automatic"),
        ("manual", "Manual"),
        ("sequential", "Sequential"),
        ("other", "Other"),
    ]

    ENGINE_CHOICES = [
        ("I3", "I3"),
        ("I4", "I4"),
        ("I5", "I5"),
        ("I6", "I6"),
        ("V4", "V4"),
        ("V6", "V6"),
        ("V8", "V8"),
        ("V10", "V10"),
        ("V12", "V12"),
        ("F4", "F4"),
        ("F6", "F6"),
        ("F12", "F12"),
        ("W8", "W8"),
        ("W12", "W12"),
        ("W16", "W16"),
        ("rotary", "Rotary"),
        ("other", "Other"),
    ]

    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="cars",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="cars",
    )
    title = models.CharField(max_length=160)
    model_name = models.CharField(max_length=80)
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1885), MaxValueValidator(9999)],
        help_text="4-digit model year (minimum 1885).",
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    engine_displacement = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(15000)],
        help_text="Displacement in cc (e.g., 1998, 3996). Leave blank if N/A (e.g., EV).",
    )
    engine_type = models.CharField(
        max_length=12, choices=ENGINE_CHOICES, default="other"
    )
    fuel_type = models.CharField(
        max_length=20, choices=FUEL_CHOICES, default="other"
    )
    transmission = models.CharField(
        max_length=20, choices=TRANSMISSION_CHOICES, default="other"
    )
    color = models.CharField(max_length=50)
    mileage = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="cars/", blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "title"]

    def __str__(self):
        return f"{self.year} {self.brand.name} {self.model_name} ({self.title})"


class CarView(models.Model):
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="views",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="car_views",
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-viewed_at"]

    def __str__(self):
        viewer = self.user.username if self.user else "Guest"
        return f"{viewer} viewed {self.car}"


class SearchLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_logs",
    )
    query = models.CharField(max_length=120, blank=True)
    brand_filter = models.CharField(max_length=80, blank=True)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-searched_at"]

    def __str__(self):
        return f"Search '{self.query}' (brand: '{self.brand_filter}')"