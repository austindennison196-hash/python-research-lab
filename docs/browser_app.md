# Browser laboratory

The browser interface runs without installing Python or Jupyter on the user's computer. Its static assets contain no external font, charting, analytics, or runtime dependencies. Browsers fetch the small site and a bounded dataset as ordinary web pages; no ZIP or local environment is required.

## Interactive features

- Structural rules, generations 0–6, individual states, and exact original notation.
- Generation playback, clickable history nodes, highlighted ancestry, and ordered tree inspection.
- A maximum-depth stabilization constraint applied to permitted transitions and reachable states, not simply a filter on the final generation.
- Candidate-rule count comparisons and explicit Catalan indexing.
- JSON export, optional local view persistence, and shareable view URLs.
- Animated ideal harmonic oscillator with adjustable displacement/frequency, exact position curves, and energy.
- Binary-entropy exploration with adjustable event probability and a probability bar.
- Research definitions, the conditional tree/Catalan proof, ambiguity, and physical limitations.
- Responsive layout, keyboard controls, reduced-motion support, and dataset failure handling.

The structural dataset is built from `research_lab.structural_logic`. The site does not claim to run arbitrary Python or the full scientific toolkit in a browser. Its two numerical demonstrations implement the stated analytic models and are tested against known reference values. The Python package and notebooks remain the full research environment.

## Build and validation

From the repository root with the editable package installed:

```bash
python scripts/build_web.py
node --test tests/web_models.test.mjs
```

The output is `dist/site/`. It is suitable for a static host and uses relative asset URLs so it works under a repository subpath. Browser checks are in `scripts/check_web.cjs`; CI installs Playwright in a temporary directory, serves the static output for internal validation, and runs those checks. Node and Playwright are development tools, not runtime requirements for visitors.

## Hosting

The live app is available at https://austindennison196-hash.github.io/python-research-lab/. The deployment succeeded in [workflow run 40047630792](https://github.com/austindennison196-hash/python-research-lab/actions/runs/40047630792), and the public page and structural dataset returned HTTP 200.

The `Publish browser laboratory` workflow builds and deploys GitHub Pages when changes reach `main`, or when it is manually run. In the repository's **Settings → Pages**, the source must be **GitHub Actions**. Enabling Pages can require repository-administrator access and is subject to the account's plan and repository visibility. A public site exposes the app and its research notes; publication must be deliberate.

Saving a cloud environment or starting a server inside its private workspace does not publish this site. A deployment is only live after the host reports success and its public URL is checked. Do not describe an unverified URL or an internal server address as a working app link.
