-- Viral Video Production Form — Supabase Schema
-- Run this in the Supabase SQL Editor

-- Master briefs table
CREATE TABLE IF NOT EXISTS briefs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  current_phase INTEGER DEFAULT 1,
  status TEXT DEFAULT 'Draft' CHECK (status IN ('Draft','In Progress','Pending Approval','Approved','Rejected','Deleted')),
  creator_name TEXT,
  creator_initials TEXT,
  on_camera_actor TEXT,
  brand_company TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS phase1_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id UUID UNIQUE REFERENCES briefs(id) ON DELETE CASCADE,
  platform TEXT,
  niche TEXT,
  sub_niche TEXT,
  topic TEXT,
  viral_reference_url TEXT,
  copy_elements TEXT[],
  time_to_value TEXT,
  content_style TEXT,
  hook_text TEXT,
  knowledge_nuggets JSONB,
  blacklist_words TEXT[],
  ai_generated BOOLEAN DEFAULT FALSE,
  batch_id TEXT,
  production_date DATE,
  on_camera_actor TEXT,
  brand_company TEXT,
  reference_description TEXT,
  selected_nugget_index INTEGER,
  nugget_rationale TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS phase2_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id UUID UNIQUE REFERENCES briefs(id) ON DELETE CASCADE,
  content_type TEXT,
  selected_format TEXT,
  selected_structure TEXT,
  format_tier TEXT,
  recommendation_level TEXT,
  platform_boost_applied BOOLEAN DEFAULT FALSE,
  data_citations JSONB,
  cta_type TEXT,
  cta_text TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS phase3_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id UUID UNIQUE REFERENCES briefs(id) ON DELETE CASCADE,
  total_runtime_sec NUMERIC,
  total_words INTEGER,
  cut_count INTEGER,
  scenes JSONB NOT NULL DEFAULT '[]',
  golden_rules_applied TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS phase4_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id UUID UNIQUE REFERENCES briefs(id) ON DELETE CASCADE,
  checks JSONB NOT NULL DEFAULT '[]',
  role_approvals JSONB NOT NULL DEFAULT '[]',
  revision_queue JSONB NOT NULL DEFAULT '[]',
  overall_verdict TEXT CHECK (overall_verdict IN ('SHIP','REVISE','REJECT')),
  quality_score INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS phase5_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id UUID UNIQUE REFERENCES briefs(id) ON DELETE CASCADE,
  active_tab TEXT DEFAULT 'all',
  meta JSONB,
  golden_rules JSONB DEFAULT '[]',
  export_history JSONB DEFAULT '[]',
  docx_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS phase6_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id UUID UNIQUE REFERENCES briefs(id) ON DELETE CASCADE,
  nodes JSONB NOT NULL DEFAULT '[]',
  edges JSONB NOT NULL DEFAULT '[]',
  active_scene TEXT DEFAULT 'all',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS
ALTER TABLE briefs ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase1_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase2_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase3_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase4_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase5_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase6_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all" ON briefs FOR ALL USING (true);
CREATE POLICY "Allow all" ON phase1_data FOR ALL USING (true);
CREATE POLICY "Allow all" ON phase2_data FOR ALL USING (true);
CREATE POLICY "Allow all" ON phase3_data FOR ALL USING (true);
CREATE POLICY "Allow all" ON phase4_data FOR ALL USING (true);
CREATE POLICY "Allow all" ON phase5_data FOR ALL USING (true);
CREATE POLICY "Allow all" ON phase6_data FOR ALL USING (true);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$ LANGUAGE plpgsql;

CREATE TRIGGER briefs_updated_at BEFORE UPDATE ON briefs FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER phase1_updated_at BEFORE UPDATE ON phase1_data FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER phase2_updated_at BEFORE UPDATE ON phase2_data FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER phase3_updated_at BEFORE UPDATE ON phase3_data FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER phase4_updated_at BEFORE UPDATE ON phase4_data FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER phase5_updated_at BEFORE UPDATE ON phase5_data FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER phase6_updated_at BEFORE UPDATE ON phase6_data FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Create storage bucket for production packs (run manually in Supabase dashboard)
-- INSERT INTO storage.buckets (id, name, public) VALUES ('production-packs', 'production-packs', true);
