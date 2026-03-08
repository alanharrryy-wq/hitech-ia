<<<<<<< HEAD:src/vite-env.d.ts
/// <reference types="vite/client" />
=======
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly MODE: string;
  readonly DEV: boolean;
  readonly PROD: boolean;

  // custom flags
  readonly PAGES_DEPLOY?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
>>>>>>> fix/desktop-bridge:99_legacy_archive/migration_20260307_193345/src/vite-env.d.ts
