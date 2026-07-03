// Iconos SVG inline del shell (del prototipo App Ethos.dc.html).
import type { NavItem } from "./nav";

export function NavIcon({ name }: { name: NavItem["icon"] }) {
  switch (name) {
    case "grid":
      return (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="currentColor" aria-hidden="true">
          <rect x="1" y="1" width="7" height="7" rx="1.5" />
          <rect x="10" y="1" width="7" height="7" rx="1.5" />
          <rect x="1" y="10" width="7" height="7" rx="1.5" />
          <rect x="10" y="10" width="7" height="7" rx="1.5" />
        </svg>
      );
    case "nodes":
      return (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
          <circle cx="4" cy="4" r="2.3" />
          <circle cx="14" cy="9" r="2.3" />
          <circle cx="5" cy="14" r="2.3" />
          <path d="M6 5.3 11.6 7.9M6.2 12.9 12 10.6" strokeLinecap="round" />
        </svg>
      );
    case "star":
      return (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="currentColor" aria-hidden="true">
          <path d="M9 1.4 L10.55 6.75 L15.9 8.3 L10.55 9.85 L9 15.2 L7.45 9.85 L2.1 8.3 L7.45 6.75 Z" />
        </svg>
      );
    case "help":
      return (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
          <circle cx="9" cy="9" r="7.1" />
          <path d="M9 12.6v.01M7.2 7.1a1.9 1.9 0 0 1 3.6.8c0 1.3-1.8 1.5-1.8 2.5" strokeLinecap="round" />
        </svg>
      );
    default:
      return null;
  }
}

export function GearIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
      <circle cx="12" cy="12" r="3" />
      <path
        d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
