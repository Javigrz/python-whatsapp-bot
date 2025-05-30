-- Script para añadir la tabla de mensajes para guardar conversaciones completas

-- Primero añadir la columna messages en threads si no existe
ALTER TABLE threads 
ADD COLUMN IF NOT EXISTS messages_count INTEGER DEFAULT 0;

-- Crear la tabla de mensajes
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    
    -- Información del mensaje
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    wa_id VARCHAR(255) NOT NULL,
    phone_number_id VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata adicional
    message_id VARCHAR(255),
    status VARCHAR(20),
    error_message TEXT,
    
    -- Índices
    FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
);

-- Crear índices para optimizar las consultas
CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_wa_id ON messages(wa_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- Comentarios para documentación
COMMENT ON TABLE messages IS 'Almacena todos los mensajes de las conversaciones de WhatsApp';
COMMENT ON COLUMN messages.role IS 'Rol del emisor: user (usuario) o assistant (bot)';
COMMENT ON COLUMN messages.content IS 'Contenido del mensaje';
COMMENT ON COLUMN messages.wa_id IS 'ID de WhatsApp del usuario';
COMMENT ON COLUMN messages.phone_number_id IS 'ID del número de WhatsApp Business';
COMMENT ON COLUMN messages.status IS 'Estado del mensaje: sent, delivered, read, failed';
COMMENT ON COLUMN messages.error_message IS 'Mensaje de error si falló el envío'; 