# Guardianas
Guardianas es una aplicación web diseñada para aumentar la percepción de seguridad en espacios públicos, especialmente en el contexto de la violencia de género, abordando situaciones en las que las mujeres pueden necesitar desplazarse solas, particularmente durante la noche.  
La plataforma permite a los usuarios solicitar un acompañamiento indicando la ubicación aproximada de origen y destino, así como la franja horaria del trayecto. Estas solicitudes se envían a personas registradas que se encuentren dentro de un radio cercano, que pueden aceptarlas y establecer el acompañamiento tras la confirmación de la solicitante, con el objetivo de reducir la necesidad de que las mujeres regresen solas a sus hogares.  
El sistema incluye tanto un modo de acompañamiento físico como virtual. En el modo físico, la persona acompañante y la solicitante acuerdan encontrarse para realizar el trayecto de forma conjunta, disponiendo de la información de origen, destino y franja horaria para facilitar la coordinación.   
En el modo virtual, la persona acompañante recibe información sobre el trayecto y puede actuar como apoyo remoto. En caso de emergencia, el usuario puede activar una alerta SOS, que notifica de forma inmediata a la persona acompañante y le muestra la última ubicación registrada, permitiéndole contactar con los servicios de emergencia a través de la aplicación y facilitar los datos disponibles.  
Con el fin de preservar la privacidad de los usuarios, el sistema gestiona distintos niveles de precisión en la ubicación compartida: incialmente se muestran ubicaciones aproximadas, mientras que la información más precisa solo se revela una vez confirmado el acompañamiento. Asimismo, la aplicación incorpora un mapa de calor colaborativo que representa visualmente las incidencias reportadas mediante un sistema de colores en función de su gravedad. Los usuarios pueden registrar y describir incidentes en zonas específicas, lo que permite a otras personas identificar áreas potencialmente inseguras y tomar precauciones. Esta funcionalidad no solo mejora la conciencia situacional, sino que también genera un registro de incidentes que puede servir de apoyo para la comunicación con las autoridades.  
En conjunto, Guardianas propone una solución tecnológica participativa que combina apoyo en tiempo real, prevención y datos generados por la comunidad para reforzar la seguridad de las mujeres en la movilidad urbana cotidiana.

## Ejecución de la aplicación. 
1. Crear el entorno virtual a partir del fichero requierements_full.txt y entrar en él
2. En una terminal ejecutar: 
     python3 manage.py runserver 0.0.0.0:8000
3. En otra terminal, ejecutar: npm run dev
4. En otra terminal, ejecutar: ngrok http 5173

Abrir en el móvil la url que proporciona ngrok
