# VT-Bridge Project Website

This repository hosts the static project website for VT-Bridge. The research code is maintained in a separate repository.

## Repository Structure

```text
.
├── index.html          # Project homepage, method overview, and results
├── styles.css          # Page styles and responsive layout
├── script.js           # Video selection, playback controls, and citation copying
├── video-data.js       # Data used by the video gallery
├── video-library.html  # Alternative index of recorded videos
├── assets/             # Images, videos, fonts, and papers used by the website
├── .nojekyll           # Allows GitHub Pages to serve static files directly
└── README.md
```

## Local Preview

Open `index.html` from the repository root directly in Firefox. No dependencies or backend server are required.

To preview the website over local HTTP, run the following command from the repository root:

```bash
python3 tools/serve.py
```

Then visit `http://127.0.0.1:8000/`.

The preview server supports HTTP Range requests, allowing the browser to seek directly to the start of the robot's motion in a video. Use `--port 8001` to specify a different port.

## Updating the Website

- Edit project content in `index.html` and adjust styles in `styles.css`.
- Store media files in `assets/` and use relative paths. Video gallery data is defined in `video-data.js`.
- Keep `.nojekyll` and check that pages, images, and videos load correctly before committing.
- Store only files needed by the website in this repository. Manage training code, model weights, and full datasets separately.

If you continue to use the existing `project-page` working directory and its publishing scripts, copy the **contents of the generated `dist/` directory** into this repository's root. Do not add an extra `vt-bridge-private/` or `dist/` directory level.

## On-Demand Video Loading

The page initially displays a poster image and assigns the original video URL to the player only after the visitor clicks Play video. Switching the backbone or camera view stops the previous player and releases its resources; the newly selected video also requires a click to play. Experiment videos, ablation comparisons, and additional analysis recordings follow the same behavior. All original recordings remain unchanged.

When adding an additional analysis recording, follow the `video[data-src]` pattern in `index.html`, including a poster image and a direct link inside `<noscript>`. Do not add a `src` or `<source src>` that would load the video prematurely. Continue to configure gallery videos in `video-data.js`. This feature reduces the amount of video data downloaded during a visit, but does not reduce the total size of the repository or deployment files.

Each gallery video's `startTime`, in seconds, marks a playback starting point just before the robot begins moving. These timestamps have been checked individually for four tasks, three backbones, four methods, and two camera views, covering 96 recordings. After the visitor clicks Play video, the player seeks to this timestamp when the metadata loads, skipping the initial wait for model loading. The original MP4 files, playback speed, and full timeline remain unchanged, and visitors can still seek back to the beginning manually. When playback ends, the poster image and Play video button return; clicking again starts playback from the same motion timestamp. The task onset includes the gripper's initial opening or closing motion, even if the robot arm has not yet moved. All recordings have been rechecked, including gripper close-ups at 0.1-second intervals around candidate starting points, with a short margin retained before the first movement. Camera exposure changes do not count as task motion. When replacing a recording, recheck its `startTime` and update the corresponding `#t=` timestamp in `video-library.html`.

## GitHub Pages

The website files are located at the root of the `main` branch. When you are ready to publish the website, open **Settings → Pages** in the GitHub repository and select **Deploy from a branch → main → / (root)**.

Pushing code, changing repository visibility, and publishing the website are separate operations. Reorganizing the directory does not automatically change repository visibility or enable Pages. Once the website is configured to deploy from `main`, subsequent pushes to that branch trigger updates.

Any project metadata that is still missing from the page should be filled in based on the paper and the actual code repository.

## Visit Counter

The right side of the footer uses [Hits.sh](https://github.com/silentsoft/hits) to display a cumulative visit count shared across all visitors. This is not a count of unique visitors. The counter is enabled automatically when the website is published over HTTPS on `*.github.io`; no backend or API key is required. Click the counter badge to view statistics. Counting begins when the feature is enabled, and earlier visits cannot be recovered.

Local previews display `Visits —` and do not send requests to the counting service. The counter identifier uses the published page's domain and path, excluding query parameters and fragments. A directory URL and its `index.html` URL share the same counter. If the service is unavailable, the page displays `Visits unavailable`. If you switch to a custom domain in the future, update the domain check in `script.js` and decide whether to retain the original counter identifier.

## Method Architecture Diagrams

The architecture diagrams are generated with Graphviz. After installing Graphviz, run the following command from the repository root:

```bash
python3 tools/render_method_diagrams.py
```

Edit the nodes and connections in the script to generate both desktop and mobile versions of the `.gv` source files and `.svg` images in `assets/diagrams/`. The website displays the SVG files directly, so visitors do not need Graphviz installed. The small feature cells in the diagrams are illustrative and do not represent specific hidden dimensions or numbers of network layers. Network connections follow the method section of the paper.
