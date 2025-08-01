-- Modificar tabla activities para soportar múltiples participantes
ALTER TABLE activities ADD COLUMN participants_data JSONB DEFAULT '[]';

-- Comentario para documentar el nuevo campo
COMMENT ON COLUMN activities.participants_data IS 'Array de participantes con estructura: [{"type": "resident", "id": "uuid", "name": "nombre"}, {"type": "staff", "name": "nombre"}, {"type": "family", "name": "nombre"}]';
