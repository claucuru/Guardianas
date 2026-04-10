from django.shortcuts import render, get_object_or_404
from .models import Canal

def canal_view(request, pk):
    try:
        canal = Canal.objects.get(pk=pk)
        suscripciones = canal.suscripcion_set.all()
        return render(request, 'canal.html', {
            'nombreCanal': canal.nombreCanal,
            'suscripciones': suscripciones
        })
    except Canal.DoesNotExist:
        return render(request, 'canal.html', {
            'error': f"No existe un canal con ID {pk}"
        })
