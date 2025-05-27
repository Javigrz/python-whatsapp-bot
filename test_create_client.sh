#!/bin/bash

# ===== CONFIGURACIÓN - MODIFICA ESTOS VALORES =====

# URL de tu API
API_URL="http://localhost:8082"  # Cambiar a https://tu-dominio.com en producción

# Datos del cliente
CLIENT_NAME="Restaurante Demo"
PHONE_NUMBER="+34666111222"
PHONE_NUMBER_ID="123456789"  # El ID que te da Meta

# Mensaje de bienvenida (opcional)
WELCOME_MESSAGE="¡Hola! Bienvenido al Restaurante Demo. ¿En qué puedo ayudarte?"

# Horario (opcional)
BUSINESS_HOURS="L-V: 13:00-16:00 y 20:00-23:30, S-D: 13:00-16:30 y 20:00-00:00"

# ===== FIN DE CONFIGURACIÓN =====

echo "======================================"
echo "CREAR CLIENTE EN WHATSAPP BOT"
echo "======================================"
echo "Cliente: $CLIENT_NAME"
echo "Teléfono: $PHONE_NUMBER"
echo "Phone Number ID: $PHONE_NUMBER_ID"
echo "======================================"

# Crear el JSON con las FAQs
read -r -d '' JSON_DATA << EOF
{
  "name": "$CLIENT_NAME",
  "phone_number": "$PHONE_NUMBER",
  "phone_number_id": "$PHONE_NUMBER_ID",
  "welcome_message": "$WELCOME_MESSAGE",
  "business_hours": "$BUSINESS_HOURS",
  "faqs": [
    {
      "q": "¿Cuál es vuestro horario?",
      "a": "Abrimos de lunes a viernes de 13:00 a 16:00 y de 20:00 a 23:30. Sábados y domingos de 13:00 a 16:30 y de 20:00 a 00:00."
    },
    {
      "q": "¿Hacéis reservas?",
      "a": "Sí, puedes reservar llamando al $PHONE_NUMBER o a través de nuestra página web."
    },
    {
      "q": "¿Tenéis menú del día?",
      "a": "Sí, nuestro menú del día cuesta 14€ e incluye primer plato, segundo plato, postre o café y bebida."
    },
    {
      "q": "¿Tenéis opciones vegetarianas?",
      "a": "Por supuesto, tenemos varias opciones vegetarianas y veganas en nuestra carta."
    },
    {
      "q": "¿Dónde estáis ubicados?",
      "a": "Estamos en la Calle Mayor 123, en el centro de la ciudad."
    },
    {
      "q": "¿Tenéis servicio a domicilio?",
      "a": "Sí, realizamos entregas a domicilio en un radio de 5km. Pedido mínimo 20€."
    }
  ]
}
EOF

echo "Enviando petición a $API_URL/clients..."
echo ""

# Hacer la petición
curl -X POST "$API_URL/clients" \
  -H "Content-Type: application/json" \
  -d "$JSON_DATA" \
  --silent \
  --show-error \
  | python3 -m json.tool

echo ""
echo "======================================" 