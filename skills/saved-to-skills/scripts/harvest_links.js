// harvest_links.js
// Run on an open Instagram saved-collection page (instagram.com/<you>/saved/<collection>/<id>/).
// Scrolls the grid to the bottom and returns every post/reel link it saw.
// It reads links only. It never opens a reel, downloads media, or touches DMs.
// Usage: paste into the browser console, or have a browser agent evaluate it.
// Optional: set window.__S2S_MAX = 60 first to cap how many links come back.
await (async () => {
  const max = window.__S2S_MAX || 500;
  const seen = new Map();
  const grab = () => {
    for (const a of document.querySelectorAll('a[href*="/reel/"], a[href*="/p/"]')) {
      const m = (a.getAttribute('href') || '').match(/\/(reel|p)\/([A-Za-z0-9_-]+)/);
      if (m && !seen.has(m[2])) seen.set(m[2], { shortcode: m[2], kind: m[1], order: seen.size });
    }
  };
  let idle = 0;
  grab();
  while (idle < 4 && seen.size < max) {
    const before = seen.size;
    window.scrollBy(0, window.innerHeight * 2);
    await new Promise((r) => setTimeout(r, 1200));
    grab();
    idle = seen.size === before ? idle + 1 : 0;
  }
  window.scrollTo(0, 0);
  const items = [...seen.values()].slice(0, max);
  return {
    collection: decodeURIComponent(location.pathname.split('/saved/')[1] || '').split('/')[0],
    count: items.length,
    links: items.map((i) => `https://www.instagram.com/${i.kind}/${i.shortcode}/`),
  };
})()
