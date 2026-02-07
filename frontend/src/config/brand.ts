const envName = import.meta.env.VITE_APP_NAME?.trim();
const envTagline = import.meta.env.VITE_APP_TAGLINE?.trim();

export const brandName = envName || "Studio AI";
export const brandTagline = envTagline || "Alpha v0.1";
export const brandShort = brandName;

export const setDocumentTitle = (suffix?: string) => {
  if (typeof document === "undefined") return;
  document.title = suffix ? `${brandName} – ${suffix}` : brandName;
};
