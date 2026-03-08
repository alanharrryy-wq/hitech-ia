<<<<<<< HEAD:src/pages/Home.tsx
import React from 'react';
export default function Home(){
  return (
    <div style={{padding:24}}>
      <h2>Bienvenido</h2>
      <p>Este es el Home base. Ve a <a href="/modules">/modules</a> para ver el panel de módulos.</p>
    </div>
  );
}
=======
import React from 'react';
import { Link } from 'react-router-dom';

export default function Home(){
  return (
    <div style={{padding:24}}>
      <h2>Bienvenido</h2>
      <p>Este es el Home base. Ve a <Link to="/modules">/modules</Link> para ver el panel de módulos.</p>
    </div>
  );
}
>>>>>>> fix/desktop-bridge:99_legacy_archive/migration_20260307_193345/src/pages/Home.tsx
