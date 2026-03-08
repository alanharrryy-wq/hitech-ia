<<<<<<< HEAD:src/routes/Router.tsx
import React, { Suspense } from "react";
import { HashRouter, Routes, Route } from "react-router-dom";

import { NavBar } from "../components/NavBar";
import Home from "../pages/Home";
import NotFound from "../pages/NotFound";
import Olimpo5 from "../pages/Olimpo5";
import AresPanel from "../pages/AresPanel";

import { extraRoutes, extraNav } from "./register";

const ModulesDashboard = React.lazy(() => import("../pages/ModulesDashboard"));

export function AppRouter() {
  return (
    <HashRouter>
      <NavBar extra={extraNav} />
      <Suspense fallback={<div style={{ padding: 12 }}>Cargando...</div>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/modules" element={<ModulesDashboard />} />
          <Route path="/ares" element={<AresPanel />} />
          <Route path="/olimpo5" element={<Olimpo5 />} />

          {extraRoutes.map((r, idx) => (
            <Route key={idx} path={r.path} element={<r.element />} />
          ))}

          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </HashRouter>
  );
}
=======
import Olimpo5 from '../pages/Olimpo5';
import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { NavBar } from '../components/NavBar';
import Home from '../pages/Home';
const ModulesDashboard = React.lazy(() => import('../pages/ModulesDashboard'));
import NotFound from '../pages/NotFound';
import { extraRoutes, extraNav } from './register';

export function AppRouter(){
  return (
    <BrowserRouter>
      <NavBar extra={extraNav}/>
      <Suspense fallback={<div style={{padding:12}}>Cargando…</div>}>
        <Routes>
          <Route path="/" element={<Home/>} />
          <Route path="/modules" element={<ModulesDashboard/>} />
          {extraRoutes.map((r, idx) => (
            <Route key={idx} path={r.path} element={<r.element/>} />
          ))}
          <Route path="*" element={<NotFound/>} />
                <Route path="/olimpo5" element={<Olimpo5/>} />
      </Routes>
      </Suspense>
    </BrowserRouter>
  );
}


>>>>>>> fix/desktop-bridge:99_legacy_archive/migration_20260307_193345/src/routes/Router.tsx
