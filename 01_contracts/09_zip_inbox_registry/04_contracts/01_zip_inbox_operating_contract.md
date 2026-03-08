# ZIP Inbox Operating Contract

All incoming ZIP packages enter through a single inbox tree rooted at:

`<contract-repo>/02_modules/_zip_inbox/`

Each project has its own subfolder. A ZIP must never be stored in the root of `_zip_inbox/`.

Only `.zip` files following the canonical filename rule are considered installable source packages.

Once a ZIP has been downloaded into the inbox, it must be treated as immutable. Any modifications require a new ZIP artifact with a new filename and, if needed, a higher sequence.

Extraction must happen in `_staging/` or another ignored temp location. ZIP contents must never be extracted directly into final repo targets without staging.
