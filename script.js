"use strict";

// A regular script keeps the complete gallery usable when index.html is opened from disk.
(() => {
  // Keep media URLs off the player until an explicit click (including on file://).
  function prepareVideo(video, src, startTime = 0) {
    const player = element("div", "on-demand-player");
    video.replaceWith(player);
    player.append(video);
    video.controls = false;
    video.preload = "none";
    const button = element("button", "video-start");
    button.type = "button";
    button.setAttribute("aria-label", `Play: ${video.getAttribute("aria-label")}`);
    button.append(element("span", "video-start-label", "▶ Play video"));
    const error = element("p", "media-error", "This recording could not be played. ");
    error.hidden = true;
    error.setAttribute("role", "status");
    const link = element("a", "", "Open the video");
    link.href = startTime > 0 ? `${src}#t=${startTime}` : src;
    error.append(link);
    player.append(button);
    player.after(error);
    video.addEventListener("error", () => {
      if (video.hasAttribute("src")) error.hidden = false;
    });
    video.addEventListener("ended", () => {
      const restoreFocus = document.activeElement === video;
      video.pause();
      video.controls = false;
      video.removeAttribute("src");
      video.load(); // Restore the poster and release the completed recording.
      error.hidden = true;
      button.hidden = false;
      if (restoreFocus) button.focus({ preventScroll: true });
    });
    button.addEventListener("click", () => {
      if (button.hidden) return;
      button.hidden = true;
      error.hidden = true;
      video.controls = true;
      if (startTime > 0) {
        video.addEventListener("loadedmetadata", () => {
          // Skip this recording's model-loading pause without trimming the file.
          if (video.isConnected && startTime < video.duration) video.currentTime = startTime;
        }, { once: true });
      }
      video.src = src;
      video.focus({ preventScroll: true });
      // Native controls remain available if the browser declines playback.
      video.play().catch(() => {
        if (video.isConnected && video.error) error.hidden = false;
      });
    });
  }

  for (const video of document.querySelectorAll("video[data-src]")) {
    prepareVideo(video, video.dataset.src);
  }

  const data = window.VTBRIDGE_MEDIA;
  if (!data) return;

  const clips = new Map(data.clips.map(clip => [
    [clip.task, clip.backbone, clip.method, clip.view].join("/"), clip
  ]));
  const methodLabels = {
    vla_only: "VLA (Fine-tuned)",
    vla_touch: "VLA-Touch",
    residual: "VT-Bridge (ours)",
    follower: "Executed-Pose (Ablation)"
  };
  const cameraLabels = { wrist: "Wrist camera", left: "Third-person camera" };

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function choices(name, legend, options, selected, onChange) {
    const fieldset = element("fieldset", "gallery-selector");
    fieldset.append(element("legend", "selector-legend", legend));
    const optionsElement = element("div", "selector-options");
    for (const option of options) {
      const label = element("label", "selector-choice");
      const input = document.createElement("input");
      input.type = "radio";
      input.name = name;
      input.value = option.id;
      input.checked = option.id === selected;
      input.addEventListener("change", () => {
        if (input.checked) onChange(option.id);
      });
      label.append(input, element("span", "", option.label));
      optionsElement.append(label);
    }
    fieldset.append(optionsElement);
    return fieldset;
  }

  function stopVideos(container) {
    for (const video of container.querySelectorAll("video")) {
      video.pause();
      video.removeAttribute("src");
      video.load(); // Release the replaced recording and cancel its pending download.
    }
  }

  function videoFigure(clip, taskLabel, backboneLabel, isAblation) {
    const figure = element("figure", "gallery-video");
    figure.dataset.method = clip.method;
    const label = isAblation && clip.method === "residual" ? "Desired-Pose (Ours)" : methodLabels[clip.method];
    figure.append(element("h4", "", label));
    const video = document.createElement("video");
    video.controls = true;
    video.playsInline = true;
    video.preload = "none";
    video.width = clip.width;
    video.height = clip.height;
    video.poster = clip.poster;
    video.dataset.method = clip.method;
    video.dataset.view = clip.view;
    video.dataset.backbone = clip.backbone;
    video.dataset.startTime = clip.startTime ?? 0;
    video.setAttribute("aria-label", `${taskLabel}, ${backboneLabel}, ${label}, ${cameraLabels[clip.view]}`);
    const fallback = element("a", "", "Open this recording");
    fallback.href = clip.startTime > 0 ? `${clip.src}#t=${clip.startTime}` : clip.src;
    video.append(fallback);

    figure.append(video);
    prepareVideo(video, clip.src, clip.startTime);
    return figure;
  }

  function mount(root) {
    const kind = root.dataset.videoGallery;
    const isAblation = kind === "ablations";
    const methods = isAblation ? ["residual", "follower"] : ["vla_only", "vla_touch", "residual"];
    // Check every selectable combination before replacing the static fallback.
    for (const task of data.tasks) for (const backbone of data.backbones) {
      for (const method of methods) for (const view of Object.keys(cameraLabels)) {
        if (!clips.has([task.id, backbone.id, method, view].join("/"))) throw new Error("Incomplete video manifest");
      }
    }

    let backboneId = data.backbones[0].id;
    const rowStates = [];
    const announcement = element("p", "visually-hidden");
    announcement.setAttribute("role", "status");
    announcement.setAttribute("aria-live", "polite");
    const content = document.createDocumentFragment();
    const backboneControl = choices(`${kind}-backbone`, "Backbone", data.backbones, backboneId, id => {
      backboneId = id;
      for (const state of rowStates) renderRow(state);
      announcement.textContent = `${data.backbones.find(b => b.id === id).label} selected for ${isAblation ? "residual-target ablations" : "experiments"}.`;
    });
    backboneControl.classList.add("backbone-selector");
    content.append(backboneControl, announcement);

    function renderRow(state) {
      stopVideos(state.grid);
      const backbone = data.backbones.find(b => b.id === backboneId);
      const figures = methods.map(method => videoFigure(
        clips.get([state.task.id, backboneId, method, state.view].join("/")), state.task.label, backbone.label, isAblation
      ));
      state.grid.replaceChildren(...figures);
    }

    for (const task of data.tasks) {
      const article = element("article", "experiment gallery-task");
      article.dataset.task = task.id;
      const headingId = `${kind}-${task.id}-title`;
      article.setAttribute("aria-labelledby", headingId);
      const header = element("div", "gallery-task-header");
      const headingGroup = element("div", "gallery-task-heading");
      const heading = element("h3", "", task.label);
      heading.id = headingId;
      headingGroup.append(heading);
      if (!isAblation) headingGroup.append(element("p", "gallery-task-description", task.description));
      const grid = element("div", `comparison-grid${isAblation ? " gallery-pair" : ""}`);
      const state = { task, grid, view: "wrist" };
      const cameraControl = choices(`${kind}-${task.id}-camera`, `${task.label} camera`,
        Object.entries(cameraLabels).map(([id, label]) => ({ id, label })), state.view, view => {
          state.view = view;
          renderRow(state);
          announcement.textContent = `${task.label}: ${cameraLabels[view]} selected.`;
        });
      cameraControl.classList.add("camera-selector");
      header.append(headingGroup, cameraControl);
      article.append(header, grid);
      rowStates.push(state);
      renderRow(state);
      content.append(article);
    }
    root.replaceChildren(content);
  }

  for (const root of document.querySelectorAll("[data-video-gallery]")) {
    try { mount(root); }
    catch (error) { console.error("Could not initialize the video gallery:", error); }
  }

  // Select the matching experiment videos before the link scrolls to the gallery.
  const experimentGallery = document.getElementById("experiment-videos");
  for (const link of document.querySelectorAll("[data-video-backbone]")) {
    link.addEventListener("click", event => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const input = experimentGallery && Array.from(experimentGallery.querySelectorAll('input[name="experiments-backbone"]'))
        .find(radio => radio.value === link.dataset.videoBackbone);
      if (!input) return;
      input.click();
      input.focus({ preventScroll: true });
    });
  }
})();

// Keep the section navigation in step with the reader's position.
(() => {
  const nav = document.querySelector(".site-nav");
  if (!nav) return;
  const entries = Array.from(nav.querySelectorAll(".nav-links a"))
    .map(link => ({ link, section: document.querySelector(link.getAttribute("href")) }))
    .filter(entry => entry.section);
  if (!entries.length) return;
  let scheduled = false;
  function updateCurrentSection() {
    const threshold = nav.getBoundingClientRect().bottom + 100;
    let current = entries[0];
    for (const entry of entries) {
      if (entry.section.getBoundingClientRect().top <= threshold) current = entry;
    }
    for (const entry of entries) {
      if (entry === current) entry.link.setAttribute("aria-current", "location");
      else entry.link.removeAttribute("aria-current");
    }
    scheduled = false;
  }
  function scheduleUpdate() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(updateCurrentSection);
  }
  window.addEventListener("scroll", scheduleUpdate, { passive: true });
  window.addEventListener("resize", scheduleUpdate);
  window.addEventListener("load", scheduleUpdate);
  updateCurrentSection();
})();

const codeButton = document.getElementById("code-button");
const resourceNote = document.getElementById("resource-note");
if (codeButton && resourceNote) {
  codeButton.addEventListener("click", () => {
    resourceNote.textContent = "Coming soon";
  });
}

// Shared page visits; only published GitHub Pages URLs register hits.
(() => {
  const counter = document.getElementById("visit-counter");
  const badge = document.getElementById("visit-counter-badge");
  const status = document.getElementById("visit-counter-status");
  if (!counter || !badge || !status) return;
  if (location.protocol !== "https:" || !location.hostname.endsWith(".github.io")) return;

  // The directory URL and index.html share a counter; queries and anchors do not split it.
  const path = location.pathname.replace(/\/index\.html$/, "/").replace(/\/$/, "");
  const key = location.hostname + path;
  const options = new URLSearchParams({
    label: "Visits", color: "087f8c", labelColor: "203c40", style: "flat", view: "total"
  });
  status.textContent = "Visits …";
  badge.addEventListener("load", () => {
    badge.hidden = false;
    status.hidden = true;
    counter.href = `https://hits.sh/${key}/`;
    counter.target = "_blank";
    counter.rel = "noopener noreferrer";
    counter.title = "Total page visits · View statistics on Hits.sh";
  }, { once: true });
  badge.addEventListener("error", () => {
    badge.hidden = true;
    status.hidden = false;
    status.textContent = "Visits unavailable";
    counter.title = "The visit counter is temporarily unavailable.";
  }, { once: true });
  badge.src = `https://hits.sh/${key}.svg?${options}`;
})();
