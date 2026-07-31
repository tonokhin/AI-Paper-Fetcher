CSS = """
:root {
  color-scheme: light;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f6f7f8;
  color: #1f2933;
}
body {
  margin: 0;
}
header {
  background: #ffffff;
  border-bottom: 1px solid #d9dee3;
  padding: 18px 28px;
}
h1 {
  font-size: 24px;
  margin: 0 0 4px;
}
header p {
  margin: 0;
  color: #65717c;
}
nav {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}
nav a {
  color: #2457a6;
  text-decoration: none;
  font-weight: 600;
}
.filters {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) repeat(3, minmax(150px, 220px)) auto auto;
  gap: 10px;
  padding: 16px 28px;
  background: #eef1f4;
  border-bottom: 1px solid #d9dee3;
}
input, select, textarea, button, .button {
  border: 1px solid #c5ccd3;
  border-radius: 6px;
  font: inherit;
  padding: 8px 10px;
  background: #ffffff;
}
button, .button {
  background: #2457a6;
  color: #ffffff;
  text-decoration: none;
  cursor: pointer;
}
.next {
  margin: 18px 28px 0;
  padding: 14px 16px;
  background: #fff7e6;
  border: 1px solid #e5c878;
  border-radius: 8px;
}
.next h2 {
  margin: 0 0 8px;
  font-size: 16px;
}
.next p {
  margin: 6px 0 0;
}
.paper-list {
  display: grid;
  gap: 14px;
  padding: 18px 28px 32px;
}
.pagination {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 28px 0;
}
.pagination span {
  color: #65717c;
}
.paper {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 18px;
  background: #ffffff;
  border: 1px solid #d9dee3;
  border-radius: 8px;
  padding: 16px;
}
.paper h2 {
  margin: 0 0 8px;
  font-size: 18px;
}
.meta {
  color: #65717c;
  font-size: 13px;
}
.links a {
  margin-right: 12px;
}
.notes {
  color: #3f4d5a;
  font-size: 13px;
}
.progress {
  display: grid;
  gap: 10px;
  align-content: start;
}
.progress label {
  display: grid;
  gap: 4px;
  font-size: 13px;
  color: #3f4d5a;
}
.log-grid {
  display: grid;
  gap: 18px;
  padding: 18px 28px 32px;
}
.log-panel {
  background: #ffffff;
  border: 1px solid #d9dee3;
  border-radius: 8px;
  padding: 16px;
}
.log-panel h2 {
  margin: 0 0 8px;
  font-size: 18px;
}
pre {
  margin: 0;
  max-height: 520px;
  overflow: auto;
  white-space: pre-wrap;
  background: #111827;
  color: #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
@media (max-width: 900px) {
  .filters, .paper {
    grid-template-columns: 1fr;
  }
}
"""
