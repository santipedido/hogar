-- Crear tabla de historial de medicamentos
CREATE TABLE IF NOT EXISTS public.medication_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    medication_id UUID NOT NULL REFERENCES public.medications(id) ON DELETE CASCADE,
    resident_id UUID NOT NULL REFERENCES public.residents(id) ON DELETE CASCADE,
    med_name TEXT NOT NULL,
    dosage TEXT NOT NULL,
    administered_at TIMESTAMP WITH TIME ZONE NOT NULL,
    administered_by_user_id TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_medication_history_resident_id ON public.medication_history(resident_id);
CREATE INDEX IF NOT EXISTS idx_medication_history_medication_id ON public.medication_history(medication_id);
CREATE INDEX IF NOT EXISTS idx_medication_history_administered_at ON public.medication_history(administered_at);
CREATE INDEX IF NOT EXISTS idx_medication_history_date_range ON public.medication_history(resident_id, administered_at);

-- Habilitar RLS (Row Level Security)
ALTER TABLE public.medication_history ENABLE ROW LEVEL SECURITY;

-- Crear políticas de seguridad
CREATE POLICY "Enable read access for all users" ON public.medication_history
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON public.medication_history
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON public.medication_history
    FOR UPDATE USING (true);

CREATE POLICY "Enable delete access for all users" ON public.medication_history
    FOR DELETE USING (true); 