:root {
  --bg: #0e0f12;
  --fg: #e6e7eb;
  --muted: #a1a6b3;
  --accent: #8ab4ff;
  --border: #1e2230;
  --code: #0b0d13;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.6;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 3rem 1.5rem 5rem;
}

.hero {
  margin-bottom: 4rem;
}

h1 {
  font-size: 2.8rem;
  letter-spacing: -0.02em;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.25rem;
  color: var(--muted);
  margin-bottom: 1.5rem;
}

.thesis {
  font-size: 1.4rem;
  font-weight: 500;
  border-left: 4px solid var(--accent);
  padding-left: 1rem;
  margin-top: 2rem;
}

h2 {
  font-size: 1.6rem;
  margin-top: 4rem;
  margin-bottom: 1rem;
}

p {
  max-width: 70ch;
}

ul {
  padding-left: 1.2rem;
}

li {
  margin-bottom: 0.4rem;
}

.invariant {
  background: var(--code);
  border: 1px solid var(--border);
  padding: 1.2rem;
  margin: 1.5rem 0;
}

.invariant code {
  font-size: 1.2rem;
  color: var(--accent);
}

.diagram {
  background: var(--code);
  border: 1px solid var(--border);
  padding: 1.2rem;
  overflow-x: auto;
  font-size: 0.95rem;
}

.caption {
  color: var(--muted);
  font-size: 0.9rem;
  margin-top: 0.6rem;
}

a {
  color: var(--accent);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

footer {
  margin-top: 5rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border);
}

.footnote {
  color: var(--muted);
  font-size: 0.85rem;
  max-width: 75ch;
}
