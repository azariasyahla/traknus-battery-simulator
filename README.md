# Traknus Battery Simulator

**Repository name:** `traknus-battery-simulator`

**GitHub description:** Interactive forklift battery runtime simulator for shift schedules, breaks, charging, and battery comparisons.

An interactive estimate of forklift battery runtime based on truck model, battery capacity, work intensity, shift schedules, breaks, and charging opportunities. The start screen also captures the customer company, work location, and salesperson; these details appear in the simulation summary and PDF report.

## GitHub Pages

Upload the complete contents of this folder to the repository root, including `index.html`, `manifest.webmanifest`, `sw.js`, and the `assets` and `icons` folders. Transparent counterbalance and warehouse forklift WebP images are included in `assets`; the app displays them without white photo panels.

Then open **Settings → Pages**, select **Deploy from a branch**, choose branch `main` and folder `/(root)`, and save. After GitHub finishes publishing, open the Pages URL in a browser.

The simulator is a static HTML, CSS, and JavaScript application. Customers can use it in a browser without installing Python or Streamlit.
