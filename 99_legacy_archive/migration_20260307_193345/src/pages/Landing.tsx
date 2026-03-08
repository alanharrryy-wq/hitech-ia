<<<<<<< HEAD:src/pages/Landing.tsx
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

type Mod = {
  enabled: boolean;
  id: string;
  name: string;
  type: 'web' | 'desktop' | string;
  route: string;
  color?: string;
  healthUrl?: string;
  statusUrl?: string;
  demoUrl?: string;
};

type ModConfig = {
  version?: string;
  modules?: Mod[];
};

export default function Landing() {
  const [mods, setMods] = useState<Mod[]>([]);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}modules.config.json`)
      .then((r) => r.json())
      .then((cfg: ModConfig) => setMods((cfg.modules || []).filter((m) => m.enabled)))
      .catch(() => setMods([]));
  }, []);

  return (
    <div style={{ padding: '24px 24px 64px' }}>
      <h1 style={{ marginBottom: 12 }}>Bienvenido</h1>
      <p style={{ opacity: 0.8, marginBottom: 24 }}>
        Este es el Home base. Ve a <Link to="/modules">/modules</Link> para ver el panel de módulos.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 16 }}>
        {mods.map((m) => (
          <div
            key={m.id}
            style={{
              border: '1px solid rgba(255,255,255,0.12)',
              borderRadius: 14,
              padding: 16,
              background: 'rgba(255,255,255,0.03)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <strong>{m.name}</strong>
              <span style={{ fontSize: 12, opacity: 0.75 }}>{String(m.type).toUpperCase()}</span>
            </div>

            <div style={{ height: 4, borderRadius: 999, background: m.color || '#00F5D4', opacity: 0.9, marginBottom: 12 }} />

            {m.type === 'web' && m.route && m.route !== 'n/a' ? (
              <Link to={m.route} style={{ textDecoration: 'none' }}>
                <button style={{ padding: '8px 14px', borderRadius: 10, cursor: 'pointer' }}>Abrir</button>
              </Link>
            ) : (
              <span style={{ fontSize: 12, opacity: 0.7 }}>No tiene ruta web</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
=======
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { OlympusCard } from '../components/OlympusCard';

type Mod = {
  enabled: boolean;
  id: string;
  name: string;
  type: 'web' | 'desktop' | string;
  route: string;
  color?: string;
  description?: string;
  healthUrl?: string;
};

type ModConfig = {
  version: string;
  modules: Mod[];
};

export default function Landing() {
  const [mods, setMods] = useState<Mod[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    fetch(`${import.meta.env.BASE_URL}modules.config.json`)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((cfg: ModConfig) => {
        if (!active) return;
        setMods((cfg.modules || []).filter(m => m.enabled));
      })
      .catch((err) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : String(err));
        setMods([]);
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });
    return () => { active = false; };
  }, []);

  const modulesConfigUrl = `${import.meta.env.BASE_URL}modules.config.json`;

  return (
    <div style={{padding:'24px 24px 64px'}}>
      <div style={{maxWidth:1200, margin:'0 auto'}}>
        <h1 style={{marginBottom: 8}}>Bienvenido</h1>
        <p style={{opacity:.8, marginBottom: 12}}>Selecciona un módulo para abrir su interfaz.</p>
        <div style={{display:'flex', gap:12, margin:'0 0 20px'}}>
          <Link to="/modules" className="btn">Ver módulos</Link>
        </div>

        {loading && (
          <p style={{opacity:.8, marginBottom: 12}}>Cargando módulos...</p>
        )}

        {error && (
          <div style={{border:'1px solid #2b2b2b', borderRadius:12, padding:12, background:'rgba(255,255,255,0.02)', marginBottom:16}}>
            <div style={{fontWeight:600, marginBottom:6}}>
              No se pudo cargar modules.config.json. Verifica la ruta, GitHub Pages base-path, o si estás en local corre RUN_Local.ps1.
            </div>
            <details>
              <summary style={{cursor:'pointer'}}>Detalles</summary>
              <div style={{fontSize:12, opacity:.7, marginTop:6}}>{error}</div>
            </details>
          </div>
        )}

        {!loading && !error && mods.length === 0 && (
          <div style={{border:'1px solid #2b2b2b', borderRadius:12, padding:12, background:'rgba(255,255,255,0.02)', marginBottom:16}}>
            <div style={{marginBottom:8}}>No hay módulos habilitados.</div>
            <a className="btn" href={modulesConfigUrl}>Editar modules.config.json</a>
          </div>
        )}

        {!loading && !error && mods.length > 0 && (
          <div className="grid">
            {mods.map(m => (
              <OlympusCard key={m.id} title={m.name} subtitle={m.type.toUpperCase()} accent={m.color} description={m.description}>
                <div className="card-actions">
                  {m.type === 'web' && m.route && m.route !== 'n/a' ? (
                    <Link to={m.route} className="btn">Abrir</Link>
                  ) : (
                    <span className="card-muted">No tiene ruta web</span>
                  )}
                </div>
              </OlympusCard>
            ))}
          </div>
        )}

        <p style={{opacity:.6, marginTop:24, fontSize:12}}>Tip: edita <code>public/modules.config.json</code> para sumar módulos.</p>
      </div>
    </div>
  );
}
>>>>>>> fix/desktop-bridge:99_legacy_archive/migration_20260307_193345/src/pages/Landing.tsx
