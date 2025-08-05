# Xeguridad Bot Flask

Este proyecto es una plataforma inteligente de atención automatizada a través de WhatsApp, desarrollada con Flask. Está diseñada para responder a solicitudes relacionadas con seguridad logística, como ubicación de unidades, denuncias anónimas y consulta de vehículos asignados a usuarios. Integra bases de datos SQL y NoSQL, APIs de rastreo satelital (Xeguridad), automatización con Selenium y envíos de notificaciones multimedia.

## Funcionalidades

- Autenticación de usuarios con control de acceso basado en roles.
- Integración con la API de WhatsApp Business para interacción conversacional.
- Consulta de vehículos permitidos desde una base de datos SQL filtrada por usuario.
- Envío de comandos automáticos a un sistema GPS mediante web scraping con Selenium.
- Recolección de denuncias anónimas con imágenes, enviadas vía correo.
- Geolocalización de vehículos, gensets y chasis vía API o Tile.
- Interfaces específicas para administradores y usuarios regulares.

## Tecnologías Utilizadas

- Flask (servidor web)
- MongoDB + Pymongo
- MySQL + SQLAlchemy
- API de WhatsApp Business
- Python-dotenv (manejo de variables de entorno)
- Requests, Bcrypt, Selenium, AIOHTTP, SMTP
- WebDriver Manager (automatización de controladores)
- Servicio Tile (localización de objetos)

## Requisitos Previos

- Python 3.8 o superior
- MongoDB y MySQL configurados y accesibles
- Cuenta y credenciales para la API de WhatsApp y sistema Xeguridad
- Acceso al entorno Tile si se usa la localización por chasis
