from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Device, Element
from .serializers import DeviceSerializer, ElementSerializer
import numpy as np

# CRUD para Device
class DeviceListCreateView(generics.ListCreateAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

class DeviceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

# CRUD para Element
class ElementListCreateView(generics.ListCreateAPIView):
    queryset = Element.objects.all()
    serializer_class = ElementSerializer

    def create(self, request, *args, **kwargs):
        # Procesamiento adicional para normalizar datos
        payload = request.data
        data = [float(num) for num in payload.get('data', "").split()]
        max_value = max(data)
        normalized_data = [x / max_value for x in data]
        average_before = sum(data) / len(data)
        average_after = sum(normalized_data) / len(normalized_data)

        payload['average_before_normalization'] = average_before
        payload['average_after_normalization'] = average_after
        payload['data_size'] = len(data)
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ElementRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Element.objects.all()
    serializer_class = ElementSerializer

# Vista para creación masiva de elementos (Bulk Create)
class BulkElementCreateView(APIView):
    def post(self, request):
        payload = request.data  # JSON completo
        elements = []

        for key, value in payload.items():
            device_name = value.get("deviceName")
            device, _ = Device.objects.get_or_create(device_name=device_name)

            raw_data = value.get("data", [])
            # Convertir las líneas de datos a una lista de números
            data = [list(map(float, line.split())) for line in raw_data]
            data_flat = [item for sublist in data for item in sublist]  # Aplanar lista

            # Normalización
            max_value = max(data_flat)
            normalized_data = [[x / max_value for x in line] for line in data]

            # Cálculos
            average_before = np.mean(data_flat)
            average_after = np.mean([x for sublist in normalized_data for x in sublist])

            # Crear el elemento
            element = Element(
                device=device,
                average_before_normalization=average_before,
                average_after_normalization=average_after,
                data_size=len(data_flat),
                data=normalized_data,
            )
            elements.append(element)

        # Guardar en la base de datos
        Element.objects.bulk_create(elements)

        return Response({"message": "Elements created successfully"}, status=status.HTTP_201_CREATED)
