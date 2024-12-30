from django.db import models
import jsonfield  # Instalar con `pip install jsonfield`

class Device(models.Model):
    id = models.AutoField(primary_key=True)
    device_name = models.CharField(max_length=255)

    def __str__(self):
        return self.device_name

class Element(models.Model):
    id = models.AutoField(primary_key=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="elements")
    average_before_normalization = models.FloatField()
    average_after_normalization = models.FloatField()
    data_size = models.IntegerField()
    data = jsonfield.JSONField()  # Almacena el "data" normalizado
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Element {self.id} - Device {self.device.device_name}"
